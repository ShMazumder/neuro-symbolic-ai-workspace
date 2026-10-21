"""
knowledge_graph/entity_resolution.py
Task 3.3 — Entity resolution and deduplication across articles.

Identifies when the same actor/location appears under different surface
forms across articles and merges them into a canonical entity.

Strategy:
  1. Exact canonical name match (from NER gazetteer)
  2. Fuzzy string similarity (Levenshtein / token sort ratio)
  3. Type-constrained matching (only merge entities of same type)
  4. Emit owl:sameAs triples to BlazeGraph for dedup
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class EntityRecord:
    uri:        str
    name:       str
    entity_type: str       # SECURITY_FORCE, PERSON, POLITICAL_PARTY, …
    aliases:    list[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class MergeDecision:
    source_uri:    str
    target_uri:    str    # canonical (kept)
    source_name:   str
    target_name:   str
    similarity:    float
    method:        str    # "exact" | "fuzzy" | "manual"


# ── Canonical registry ────────────────────────────────────────────────────────
# Loaded once; updated as new entities are resolved.

class EntityRegistry:
    """
    In-memory registry of resolved entities.
    Backed by a JSON file for persistence between pipeline runs.
    """

    def __init__(self, registry_path: Path = Path("data/entity_registry.json")):
        self.path = registry_path
        self._entities: dict[str, EntityRecord] = {}   # uri → EntityRecord
        self._name_index: dict[str, str] = {}           # name_lower → uri
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            for uri, rec in raw.items():
                entity = EntityRecord(**rec)
                self._entities[uri] = entity
                self._name_index[entity.name.lower()] = uri
                for alias in entity.aliases:
                    self._name_index[alias.lower()] = uri
            logger.info("Loaded %d entities from registry.", len(self._entities))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        raw = {uri: vars(rec) for uri, rec in self._entities.items()}
        self.path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Saved %d entities to registry.", len(self._entities))

    def lookup(self, name: str) -> Optional[EntityRecord]:
        """Find entity by name (exact, case-insensitive)."""
        uri = self._name_index.get(name.lower())
        return self._entities.get(uri) if uri else None

    def register(self, entity: EntityRecord) -> None:
        """Add or update entity in registry."""
        self._entities[entity.uri] = entity
        self._name_index[entity.name.lower()] = entity.uri
        for alias in entity.aliases:
            self._name_index[alias.lower()] = entity.uri

    def all_entities(self) -> list[EntityRecord]:
        return list(self._entities.values())

    def __len__(self) -> int:
        return len(self._entities)


# ── Similarity helpers ────────────────────────────────────────────────────────

def _token_sort_ratio(a: str, b: str) -> float:
    """
    Compute normalized token-sort similarity (0–1).
    Falls back to simple character overlap if rapidfuzz unavailable.
    """
    try:
        from rapidfuzz import fuzz
        return fuzz.token_sort_ratio(a, b) / 100.0
    except ImportError:
        # Simple fallback: Jaccard on character trigrams
        def trigrams(s: str) -> set:
            s = s.lower()
            return {s[i:i+3] for i in range(len(s)-2)}
        t_a, t_b = trigrams(a), trigrams(b)
        if not t_a or not t_b:
            return 1.0 if a.lower() == b.lower() else 0.0
        return len(t_a & t_b) / len(t_a | t_b)


# ── Resolution logic ──────────────────────────────────────────────────────────

SIMILARITY_THRESHOLD = 0.85   # minimum similarity to merge
SAME_TYPE_REQUIRED   = True   # only merge entities of the same type


def resolve_actors(
    actors: list[dict],
    registry: EntityRegistry,
    similarity_threshold: float = SIMILARITY_THRESHOLD,
) -> tuple[list[dict], list[MergeDecision]]:
    """
    Resolve a list of actor dicts to canonical entities.

    Args:
        actors:  Raw actor records from EventRecord.
        registry: Entity registry to look up and update.
        similarity_threshold: Minimum similarity for fuzzy merge.

    Returns:
        (resolved_actors, merge_decisions)
    """
    from knowledge_graph.rdf_generator import _actor_uri, _slug

    resolved: list[dict] = []
    decisions: list[MergeDecision] = []

    for actor in actors:
        name = (actor.get("canonical") or actor.get("name", "")).strip()
        if not name:
            resolved.append(actor)
            continue

        entity_type = actor.get("type", "UNKNOWN")

        # ── 1. Exact lookup ───────────────────────────────────────────────────
        existing = registry.lookup(name)
        if existing:
            actor["canonical"] = existing.name
            resolved.append(actor)
            continue

        # ── 2. Fuzzy lookup ───────────────────────────────────────────────────
        best_score = 0.0
        best_match: Optional[EntityRecord] = None

        for candidate in registry.all_entities():
            if SAME_TYPE_REQUIRED and candidate.entity_type != entity_type:
                continue
            score = _token_sort_ratio(name, candidate.name)
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_match and best_score >= similarity_threshold:
            uri = str(_actor_uri(name))
            decision = MergeDecision(
                source_uri=uri,
                target_uri=str(_actor_uri(best_match.name)),
                source_name=name,
                target_name=best_match.name,
                similarity=round(best_score, 3),
                method="fuzzy",
            )
            decisions.append(decision)
            # Add alias to existing entity
            best_match.aliases.append(name)
            registry.register(best_match)
            actor["canonical"] = best_match.name
            resolved.append(actor)
            continue

        # ── 3. New entity — register ──────────────────────────────────────────
        uri = str(_actor_uri(name))
        new_entity = EntityRecord(
            uri=uri,
            name=name,
            entity_type=entity_type,
            aliases=[actor.get("name", name)],
        )
        registry.register(new_entity)
        resolved.append(actor)

    return resolved, decisions


def generate_sameas_triples(decisions: list[MergeDecision]) -> str:
    """
    Generate owl:sameAs Turtle triples for merge decisions.
    Suitable for POSTing to BlazeGraph.
    """
    lines = [
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "",
    ]
    for d in decisions:
        lines.append(f"<{d.source_uri}> owl:sameAs <{d.target_uri}> .")
    return "\n".join(lines)


def resolve_events_batch(
    events: list[dict],
    registry: Optional[EntityRegistry] = None,
) -> tuple[list[dict], list[MergeDecision]]:
    """
    Run entity resolution over a batch of events.

    Args:
        events:   List of EventRecord dicts.
        registry: Shared entity registry (created fresh if None).

    Returns:
        (resolved_events, all_merge_decisions)
    """
    if registry is None:
        registry = EntityRegistry()

    all_decisions: list[MergeDecision] = []
    resolved_events: list[dict] = []

    for event in events:
        actors = event.get("actors", [])
        resolved_actors, decisions = resolve_actors(actors, registry)
        event["actors"] = resolved_actors
        all_decisions.extend(decisions)
        resolved_events.append(event)

    registry.save()
    logger.info(
        "Entity resolution: %d events, %d merges.",
        len(events), len(all_decisions),
    )
    return resolved_events, all_decisions
