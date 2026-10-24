"""
nlp/pipeline.py
Task 2.9 — NLP pipeline orchestrator.

Runs an article through all NLP stages and produces structured event JSON
matching the output schema defined in ARCHITECTURE.md.

Stages:
  1. Relevance filter      (nlp/relevance_filter.py)
  2. Coreference resolve   (nlp/coref.py)
  3. NER                   (nlp/ner.py)
  4. Trigger detection     (nlp/event_triggers.py)
  5. Argument extraction   (nlp/event_args.py)
  6. CAMEO classification  (nlp/cameo_classifier.py)
  7. Temporal normalization (nlp/temporal.py)
  8. Geo normalization      (nlp/geo.py)
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path
from typing import Optional

from scraper.schema import Article
from nlp.relevance_filter import is_violence_related, Verdict
from nlp.coref import resolve_coreferences
from nlp.ner import extract_entities
from nlp.event_triggers import detect_triggers, TriggerSpan
from nlp.event_args import extract_arguments
from nlp.cameo_classifier import classify_event
from nlp.temporal import extract_dates, normalize_date
from nlp.geo import extract_locations, normalize_location

logger = logging.getLogger(__name__)


# ── Output schema ─────────────────────────────────────────────────────────────

@dataclass
class ActorRecord:
    name:  str
    role:  str            # "perpetrator" | "target"
    type:  str            # SECURITY_FORCE / CIVILIAN / POLITICAL_PARTY / etc.
    canonical: Optional[str] = None


@dataclass
class LocationRecord:
    raw:        str
    district:   Optional[str] = None
    division:   Optional[str] = None
    coordinates: Optional[list[float]] = None   # [lat, lon]


@dataclass
class DateRecord:
    raw:        str
    normalized: Optional[str] = None


@dataclass
class EventRecord:
    event_id:        str
    source_url:      str
    source_sentence: str
    sentence_offset: list[int]           # [start, end] char offsets in body
    trigger:         str
    cameo_code:      str
    cameo_label:     str
    bd_code:         Optional[str]
    actors:          list[ActorRecord]
    location:        LocationRecord
    date:            DateRecord
    confidence:      float
    extraction_method: str
    article_title:   str = ""
    article_published: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# ── Pipeline config ───────────────────────────────────────────────────────────

@dataclass
class PipelineConfig:
    use_model_filter:   bool = True    # use zero-shot model for uncertain articles
    use_neural_coref:   bool = True    # use fastcoref if available
    use_model_classifier: bool = True  # use zero-shot CAMEO classifier for low-conf
    min_confidence:     float = 0.5    # discard events below this threshold
    max_events_per_article: int = 20   # safety cap


DEFAULT_CONFIG = PipelineConfig()


# ── Pipeline stages ───────────────────────────────────────────────────────────

def _event_id(url: str, sentence: str, i: int) -> str:
    """Generate a stable event ID."""
    digest = hashlib.md5(f"{url}{sentence}".encode()).hexdigest()[:8]
    return f"evt_{digest}_{i:03d}"


def _find_offset(body: str, sentence: str) -> list[int]:
    """Return [start, end] char offset of sentence in body."""
    idx = body.find(sentence[:40])
    if idx >= 0:
        return [idx, idx + len(sentence)]
    return [-1, -1]


def _build_actors(args) -> list[ActorRecord]:
    actors: list[ActorRecord] = []
    for name in args.perpetrators:
        actors.append(ActorRecord(name=name, role="perpetrator", type="UNKNOWN"))
    for name in args.victims:
        actors.append(ActorRecord(name=name, role="target", type="CIVILIAN"))
    return actors


def process_article(
    article: Article,
    config: PipelineConfig = DEFAULT_CONFIG,
) -> list[EventRecord]:
    """
    Run article through the full NLP pipeline.

    Args:
        article: Fully-fetched Article with body populated.
        config:  Pipeline configuration options.

    Returns:
        List of EventRecord objects (may be empty if not violence-related).
    """
    t0 = time.time()

    # ── Stage 1: Relevance filter ─────────────────────────────────────────────
    filter_result = is_violence_related(
        title=article.title,
        body=article.body,
        use_model_for_uncertain=config.use_model_filter,
    )
    if filter_result.verdict != Verdict.VIOLENCE:
        logger.debug("Skipping %s — not violence-related (conf=%.2f)", article.url[:60], filter_result.confidence)
        return []

    logger.info("Processing: %s", article.title[:80])

    # ── Stage 2: Coreference resolution ──────────────────────────────────────
    coref_result = resolve_coreferences(
        article.body,
        use_neural=config.use_neural_coref,
    )
    resolved_body = coref_result.resolved

    # ── Stage 3: Trigger detection ────────────────────────────────────────────
    from nlp.event_triggers import get_trigger_sentences
    trigger_sentences = get_trigger_sentences(resolved_body)

    if not trigger_sentences:
        logger.debug("No triggers found in %s", article.url[:60])
        return []

    # ── Parse article date for temporal normalization ─────────────────────────
    ref_date: Optional[date] = None
    if article.published_date:
        try:
            ref_date = date.fromisoformat(article.published_date[:10])
        except ValueError:
            pass

    # ── Stages 4–8: Per-sentence event extraction ─────────────────────────────
    events: list[EventRecord] = []

    for sent_text, triggers in trigger_sentences:
        for i, trigger in enumerate(triggers):
            if len(events) >= config.max_events_per_article:
                break

            # Stage 4: Argument extraction
            args = extract_arguments(sent_text, trigger)

            # Stage 5: CAMEO classification
            classification = classify_event(
                trigger=trigger,
                sentence=sent_text,
                use_model=config.use_model_classifier,
            )

            if classification.confidence < config.min_confidence:
                logger.debug("Low-confidence event skipped (%.2f)", classification.confidence)
                continue

            # Stage 6: Temporal normalization
            date_results = extract_dates(sent_text, reference_date=ref_date)
            date_rec = DateRecord(
                raw=date_results[0].raw if date_results else "",
                normalized=date_results[0].normalized if date_results else (
                    ref_date.isoformat() if ref_date else None
                ),
            )

            # Stage 7: Geo normalization
            geo_results = extract_locations(sent_text)
            if geo_results:
                g = geo_results[0]
                loc_rec = LocationRecord(
                    raw=g.raw,
                    district=g.district,
                    division=g.division,
                    coordinates=[g.latitude, g.longitude] if g.latitude else None,
                )
            else:
                loc_rec = LocationRecord(raw="Bangladesh")

            # Stage 8: Build event record
            evt = EventRecord(
                event_id=_event_id(article.url, sent_text, i),
                source_url=article.url,
                source_sentence=sent_text,
                sentence_offset=_find_offset(resolved_body, sent_text),
                trigger=trigger.text,
                cameo_code=classification.cameo_code,
                cameo_label=classification.cameo_label,
                bd_code=classification.bd_code,
                actors=_build_actors(args),
                location=loc_rec,
                date=date_rec,
                confidence=round(classification.confidence, 3),
                extraction_method=f"trigger:{trigger.kind}|cameo:{classification.method}",
                article_title=article.title,
                article_published=article.published_date,
            )
            events.append(evt)

    elapsed = time.time() - t0
    logger.info(
        "Extracted %d events from '%s' in %.2fs",
        len(events), article.title[:60], elapsed,
    )
    return events


# ── Batch processing ──────────────────────────────────────────────────────────

def process_articles(
    articles: list[Article],
    output_dir: Optional[Path] = None,
    config: PipelineConfig = DEFAULT_CONFIG,
) -> list[EventRecord]:
    """
    Process a batch of articles and optionally persist events as JSON.

    Args:
        articles:   List of Article objects with body populated.
        output_dir: If set, writes one JSON file per article to this dir.
        config:     Pipeline config.

    Returns:
        Flat list of all EventRecord objects.
    """
    all_events: list[EventRecord] = []

    for i, article in enumerate(articles, 1):
        logger.info("[%d/%d] %s", i, len(articles), article.title[:70])
        try:
            events = process_article(article, config)
            all_events.extend(events)

            if output_dir and events:
                output_dir.mkdir(parents=True, exist_ok=True)
                slug = hashlib.md5(article.url.encode()).hexdigest()[:12]
                out_file = output_dir / f"{slug}_events.json"
                out_file.write_text(
                    json.dumps([e.to_dict() for e in events], ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
        except Exception as exc:
            logger.error("Pipeline failed for %s: %s", article.url[:60], exc, exc_info=True)

    logger.info("Pipeline complete. Total events: %d", len(all_events))
    return all_events


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from pathlib import Path

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )

    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    consolidated_path = Path("data/real_news_daily_star.json")

    articles: list[Article] = []
    seen_urls: set[str] = set()

    # 1. Load from consolidated dataset if available
    if consolidated_path.exists():
        try:
            items = json.loads(consolidated_path.read_text(encoding="utf-8"))
            if isinstance(items, list):
                for item in items:
                    art = Article.from_dict(item)
                    if art.url and art.url not in seen_urls:
                        articles.append(art)
                        seen_urls.add(art.url)
                logger.info("Loaded %d articles from %s", len(articles), consolidated_path)
        except Exception as e:
            logger.warning("Error reading %s: %s", consolidated_path, e)

    # 2. Also load individual files from data/raw/
    for f in raw_dir.rglob("*.json"):
        if f.name == ".gitkeep":
            continue
        try:
            art = Article.from_json(f.read_text(encoding="utf-8"))
            if art.url and art.url not in seen_urls:
                articles.append(art)
                seen_urls.add(art.url)
        except Exception as e:
            logger.warning("Skipping %s: %s", f, e)

    if not articles:
        print(f"No articles found in {raw_dir} or {consolidated_path}. Run scraper first.")
        sys.exit(1)

    logger.info("Loaded %d total unique articles for processing.", len(articles))
    events = process_articles(articles, output_dir=processed_dir)
    logger.info("Done. %d events written to %s", len(events), processed_dir)
