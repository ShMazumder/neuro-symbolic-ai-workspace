"""
nlp/ner.py
Task 2.1 — Named Entity Recognition for Bangladesh-specific entities.

Extends spaCy's standard NER with:
  - Bangladesh-specific gazetteer (political parties, security forces, NGOs)
  - Custom entity types: POLITICAL_PARTY, SECURITY_FORCE, ARMED_GROUP
  - Entity normalization (aliases → canonical names)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ── Bangladesh-specific entity gazetteers ─────────────────────────────────────

BD_SECURITY_FORCES: dict[str, str] = {
    # Canonical name → canonical name (aliases below)
    "Bangladesh Police":              "Bangladesh Police",
    "Rapid Action Battalion":         "RAB",
    "RAB":                            "RAB",
    "Border Guard Bangladesh":        "BGB",
    "BGB":                            "BGB",
    "Directorate General of Forces Intelligence": "DGFI",
    "DGFI":                           "DGFI",
    "Detective Branch":               "Detective Branch",
    "DB":                             "Detective Branch",
    "Criminal Investigation Department": "CID",
    "CID":                            "CID",
    "Armed Police Battalion":         "APBn",
    "APBn":                           "APBn",
    "Ansar":                          "Ansar",
    "Bangladesh Army":                "Bangladesh Army",
    "Bangladesh Navy":                "Bangladesh Navy",
    "Bangladesh Air Force":           "Bangladesh Air Force",
}

BD_POLITICAL_PARTIES: dict[str, str] = {
    "Awami League":                   "Awami League",
    "AL":                             "Awami League",
    "Bangladesh Nationalist Party":   "BNP",
    "BNP":                            "BNP",
    "Jamaat-e-Islami":                "Jamaat-e-Islami",
    "Jamaat":                         "Jamaat-e-Islami",
    "Jatiya Party":                   "Jatiya Party",
    "JP":                             "Jatiya Party",
    "Bangladesh Jamaat-e-Islami":     "Jamaat-e-Islami",
    "Hefazat-e-Islam":                "Hefazat-e-Islam",
    "Chhatra League":                 "Bangladesh Chhatra League",
    "BCL":                            "Bangladesh Chhatra League",
    "Chhatra Dal":                    "Bangladesh Jatiyatabadi Chhatra Dal",
    "Shibir":                         "Islami Chhatra Shibir",
    "Islami Chhatra Shibir":          "Islami Chhatra Shibir",
}

BD_ARMED_GROUPS: dict[str, str] = {
    "Jumma":                          "UPDF",
    "UPDF":                           "UPDF",
    "Parbatya Chattagram Jana Samhati Samiti": "PCJSS",
    "PCJSS":                          "PCJSS",
    "Kuki-Chin National Front":       "KNF",
    "KNF":                            "KNF",
    "Mog":                            "Marma armed group",
}

# All gazetteers merged for fast lookup
_ALL_ENTITIES: dict[str, tuple[str, str]] = {}   # surface_lower → (canonical, type)

for name, canonical in BD_SECURITY_FORCES.items():
    _ALL_ENTITIES[name.lower()] = (canonical, "SECURITY_FORCE")
for name, canonical in BD_POLITICAL_PARTIES.items():
    _ALL_ENTITIES[name.lower()] = (canonical, "POLITICAL_PARTY")
for name, canonical in BD_ARMED_GROUPS.items():
    _ALL_ENTITIES[name.lower()] = (canonical, "ARMED_GROUP")


# ── Entity dataclass ──────────────────────────────────────────────────────────

@dataclass
class Entity:
    text:      str             # surface form in text
    label:     str             # NER label: PERSON, ORG, GPE, NORP, SECURITY_FORCE, etc.
    canonical: Optional[str]   # normalized name from gazetteer
    start:     int             # char offset
    end:       int
    confidence: float = 1.0


# ── spaCy NER pipeline ────────────────────────────────────────────────────────

_NLP = None
_NLP_LOAD_ATTEMPTED = False


def _load_nlp():
    global _NLP, _NLP_LOAD_ATTEMPTED
    if not _NLP_LOAD_ATTEMPTED:
        _NLP_LOAD_ATTEMPTED = True
        try:
            import spacy
            try:
                _NLP = spacy.load("en_core_web_trf")
                logger.info("Loaded spaCy transformer model for NER.")
            except OSError:
                try:
                    _NLP = spacy.load("en_core_web_sm")
                    logger.info("Loaded spaCy en_core_web_sm for NER.")
                except OSError:
                    logger.warning("spaCy models not found. Using gazetteer regex NER fallback.")
        except ImportError:
            logger.warning("spaCy not installed. Using gazetteer regex NER fallback.")
    return _NLP


def _normalize(text: str) -> tuple[Optional[str], Optional[str]]:
    """Return (canonical_name, entity_type) from gazetteer, or (None, None)."""
    key = text.lower().strip()
    result = _ALL_ENTITIES.get(key)
    if result:
        return result
    # Partial match for longer surface forms
    for k, v in _ALL_ENTITIES.items():
        if k in key or key in k:
            return v
    return None, None


# ── Main extraction function ──────────────────────────────────────────────────

def extract_entities(text: str) -> list[Entity]:
    """
    Extract named entities from text, augmented with BD-specific gazetteer.

    Recognized labels:
      Standard spaCy: PERSON, ORG, GPE, NORP, FAC, EVENT
      BD extensions:  SECURITY_FORCE, POLITICAL_PARTY, ARMED_GROUP

    Args:
        text: Article sentence or paragraph.

    Returns:
        List of Entity objects.
    """
    entities: list[Entity] = []
    nlp = _load_nlp()

    if nlp is not None:
        doc = nlp(text)
        for ent in doc.ents:
            canonical, bd_type = _normalize(ent.text)
            label = bd_type if bd_type else ent.label_
            entities.append(Entity(
                text=ent.text,
                label=label,
                canonical=canonical,
                start=ent.start_char,
                end=ent.end_char,
                confidence=0.9 if bd_type else 0.8,
            ))
    else:
        # Fallback: gazetteer-only extraction via substring scan
        text_lower = text.lower()
        for surface, (canonical, label) in sorted(
            _ALL_ENTITIES.items(), key=lambda x: -len(x[0])
        ):
            idx = text_lower.find(surface)
            if idx >= 0:
                entities.append(Entity(
                    text=text[idx: idx + len(surface)],
                    label=label,
                    canonical=canonical,
                    start=idx,
                    end=idx + len(surface),
                    confidence=0.7,
                ))

    # Deduplicate overlapping spans (keep higher confidence)
    entities.sort(key=lambda e: (e.start, -(e.end - e.start), -e.confidence))
    deduped: list[Entity] = []
    last_end = -1
    for ent in entities:
        if ent.start >= last_end:
            deduped.append(ent)
            last_end = ent.end

    return deduped


def extract_actors(entities: list[Entity]) -> dict[str, list[Entity]]:
    """
    Group entities by role-relevant types.

    Returns:
        {
          "perpetrators": [...],   # SECURITY_FORCE, POLITICAL_PARTY, ARMED_GROUP, ORG
          "victims":      [...],   # PERSON, NORP (nationality / group)
          "locations":    [...],   # GPE, LOC, FAC
        }
    """
    perp_labels = {"SECURITY_FORCE", "POLITICAL_PARTY", "ARMED_GROUP", "ORG"}
    victim_labels = {"PERSON", "NORP"}
    loc_labels = {"GPE", "LOC", "FAC"}

    return {
        "perpetrators": [e for e in entities if e.label in perp_labels],
        "victims":      [e for e in entities if e.label in victim_labels],
        "locations":    [e for e in entities if e.label in loc_labels],
    }
