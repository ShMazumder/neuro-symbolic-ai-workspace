"""
nlp/event_args.py
Task 2.3 — Event argument extraction.

Extracts structured event tuples: WHO did WHAT to WHOM, WHERE, WHEN.
Uses dependency parsing over trigger-containing sentences.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from nlp.ner import Entity, extract_entities
from nlp.event_triggers import TriggerSpan

logger = logging.getLogger(__name__)


@dataclass
class EventArguments:
    """Structured slot-filling result for one event trigger."""
    trigger:      TriggerSpan
    perpetrators: list[str] = field(default_factory=list)   # actor names
    victims:      list[str] = field(default_factory=list)
    locations:    list[str] = field(default_factory=list)
    dates:        list[str] = field(default_factory=list)
    instruments:  list[str] = field(default_factory=list)   # weapons, tools
    raw_sentence: str = ""
    method:       str = "dep"   # "dep" | "heuristic"


# Violence-instrument keywords
INSTRUMENTS = frozenset({
    "gun", "pistol", "rifle", "shotgun", "firearm", "weapon", "knife",
    "blade", "machete", "sword", "axe", "stick", "rod", "bomb", "grenade",
    "acid", "fire", "petrol bomb",
})


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
            except OSError:
                try:
                    _NLP = spacy.load("en_core_web_sm")
                except OSError:
                    logger.warning("spaCy models not found. Using regex argument extraction fallback.")
        except ImportError:
            logger.warning("spaCy not installed. Using regex argument extraction fallback.")
    return _NLP


def _dep_extract(sentence: str, trigger: TriggerSpan) -> EventArguments:
    """
    Use spaCy dependency parse to extract event arguments.

    Strategy:
    - Find trigger token in sentence
    - nsubj / agent → perpetrator
    - dobj / nsubjpass / patient → victim
    - prep_in / prep_at / npmod → location
    """
    nlp = _load_nlp()
    args = EventArguments(trigger=trigger, raw_sentence=sentence)

    if nlp is None:
        return _heuristic_extract(sentence, trigger)

    doc = nlp(sentence)
    entities = extract_entities(sentence)
    ent_by_start: dict[int, Entity] = {e.start: e for e in entities}

    # Find trigger token
    trigger_token = None
    for tok in doc:
        if tok.idx == trigger.start or tok.text.lower() == trigger.lemma:
            trigger_token = tok
            break

    if trigger_token is None:
        return _heuristic_extract(sentence, trigger)

    args.method = "dep"

    for tok in doc:
        dep = tok.dep_
        head = tok.head

        # Subject (active: who did it)
        if dep in ("nsubj",) and head == trigger_token:
            span = doc[tok.left_edge.i: tok.right_edge.i + 1]
            args.perpetrators.append(span.text)

        # Passive subject / object (who was affected)
        if dep in ("nsubjpass", "dobj", "attr") and head == trigger_token:
            span = doc[tok.left_edge.i: tok.right_edge.i + 1]
            args.victims.append(span.text)

        # Instrument / with-phrase
        if dep == "prep" and tok.text.lower() in ("with", "using") and head == trigger_token:
            for child in tok.children:
                if child.dep_ == "pobj":
                    if child.text.lower() in INSTRUMENTS:
                        args.instruments.append(child.text)

        # Location preps: in, at, near, from
        if dep == "prep" and tok.text.lower() in ("in", "at", "near", "from") and head == trigger_token:
            for child in tok.children:
                if child.dep_ == "pobj" and child.ent_type_ in ("GPE", "LOC", "FAC"):
                    args.locations.append(child.text)

    # Supplement with NER entities not captured by dep parse
    for ent in entities:
        if ent.label in ("SECURITY_FORCE", "POLITICAL_PARTY", "ARMED_GROUP", "ORG"):
            if ent.canonical not in args.perpetrators and ent.text not in args.perpetrators:
                args.perpetrators.append(ent.canonical or ent.text)
        elif ent.label == "PERSON":
            if ent.text not in args.victims and ent.text not in args.perpetrators:
                args.victims.append(ent.text)
        elif ent.label in ("GPE", "LOC"):
            if ent.text not in args.locations:
                args.locations.append(ent.text)
        elif ent.label == "DATE":
            args.dates.append(ent.text)

    return args


def _heuristic_extract(sentence: str, trigger: TriggerSpan) -> EventArguments:
    """
    Regex/NER-only fallback when spaCy dep parse is unavailable.
    """
    args = EventArguments(trigger=trigger, raw_sentence=sentence, method="heuristic")
    entities = extract_entities(sentence)

    for ent in entities:
        if ent.label in ("SECURITY_FORCE", "POLITICAL_PARTY", "ARMED_GROUP", "ORG"):
            args.perpetrators.append(ent.canonical or ent.text)
        elif ent.label == "PERSON":
            args.victims.append(ent.text)
        elif ent.label in ("GPE", "LOC"):
            args.locations.append(ent.text)
        elif ent.label == "DATE":
            args.dates.append(ent.text)

    return args


def extract_arguments(sentence: str, trigger: TriggerSpan) -> EventArguments:
    """
    Main entry point: extract event arguments from a sentence + trigger.

    Args:
        sentence: The sentence containing the trigger.
        trigger:  TriggerSpan detected by event_triggers module.

    Returns:
        EventArguments with perpetrators, victims, locations, dates.
    """
    return _dep_extract(sentence, trigger)
