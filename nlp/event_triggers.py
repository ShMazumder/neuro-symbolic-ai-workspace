"""
nlp/event_triggers.py
Task 2.2 — Violence event trigger detection.

Identifies violence trigger verbs and noun phrases in article text
and returns their spans for downstream argument extraction.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ── Trigger lexicon ───────────────────────────────────────────────────────────

# Verb-based triggers (lemmatized)
TRIGGER_VERBS: dict[str, str] = {
    # CAMEO 18x — Physical assault / killing
    "kill":       "182",
    "murder":     "182",
    "slay":       "182",
    "execute":    "182",
    "assassinate":"185",
    "shoot":      "182",
    "stab":       "182",
    "beat":       "182",
    "attack":     "182",
    "assault":    "182",
    "torture":    "182",
    "rape":       "182",
    "abduct":     "181",
    "kidnap":     "181",
    "hijack":     "181",

    # CAMEO 18x — Bombing
    "bomb":       "183",
    "explode":    "183",
    "detonate":   "183",
    "blast":      "183",

    # CAMEO 17x — Structural violence
    "arrest":     "173",
    "detain":     "173",
    "imprison":   "173",
    "deport":     "174",
    "expel":      "174",
    "demolish":   "171",
    "confiscate": "171",
    "loot":       "171",
    "torch":      "171",
    "vandalize":  "171",

    # CAMEO 14.5 — Violent protest
    "clash":      "145",
    "riot":       "145",

    # CAMEO 19x — Conventional force
    "fire":       "193",   # "fired upon"
    "blockade":   "191",
    "occupy":     "192",
    "storm":      "193",
    "raid":       "193",

    # CAMEO 13x — Threaten
    "threaten":   "134",
    "warn":       "131",
    "ultimatum":  "139",

    # BD-specific
    "disappear":  "SV02",   # maps to enforced disappearance
    "crossfire":  "SV01",
}

# Noun-based triggers (exact phrase → CAMEO code)
TRIGGER_NOUNS: dict[str, str] = {
    "crossfire":              "SV01",
    "gunfight":               "SV01",
    "encounter killing":      "SV01",
    "acid attack":            "GV01",
    "mob beating":            "OC03",
    "mob justice":            "OC03",
    "lynching":               "OC03",
    "enforced disappearance": "SV02",
    "custodial death":        "SV03",
    "custodial torture":      "SV03",
    "hartal violence":        "PV01",
    "election violence":      "PV03",
    "dowry violence":         "GV04",
    "dowry killing":          "GV04",
    "gang rape":              "GV03",
    "sexual assault":         "GV03",
    "bomb blast":             "183",
    "suicide bombing":        "183",
    "car bomb":               "183",
    "arson attack":           "171",
    "building collapse":      "LV02",
    "factory fire":           "LV02",
}

# Compiled noun trigger patterns (longest first to avoid partial matches)
_NOUN_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(rf"\b{re.escape(phrase)}\b", re.I), code)
    for phrase, code in sorted(TRIGGER_NOUNS.items(), key=lambda x: -len(x[0]))
]


@dataclass
class TriggerSpan:
    """A detected violence trigger with its position in the text."""
    text:       str          # surface form (e.g., "killed")
    lemma:      str          # lemmatized form (e.g., "kill")
    start:      int          # char offset in sentence
    end:        int
    cameo_code: str          # preliminary CAMEO code hint
    kind:       str          # "verb" | "noun"
    sentence:   str = ""     # surrounding sentence for context
    sentence_id: int = -1    # index in doc sentences


# ── spaCy-based detection ─────────────────────────────────────────────────────

_NLP = None   # lazy-loaded spaCy model
_NLP_LOAD_ATTEMPTED = False


def _load_nlp():
    global _NLP, _NLP_LOAD_ATTEMPTED
    if not _NLP_LOAD_ATTEMPTED:
        _NLP_LOAD_ATTEMPTED = True
        try:
            import spacy
            try:
                _NLP = spacy.load("en_core_web_trf")
                logger.info("Loaded spaCy en_core_web_trf.")
            except OSError:
                try:
                    _NLP = spacy.load("en_core_web_sm")
                    logger.info("Loaded spaCy en_core_web_sm.")
                except OSError:
                    logger.warning(
                        "spaCy model not found (run: python -m spacy download en_core_web_sm). "
                        "Using regex trigger extraction fallback."
                    )
        except ImportError:
            logger.warning("spaCy not installed. Using regex trigger extraction fallback.")
    return _NLP


def _sentence_of(doc, token_idx: int) -> tuple[str, int]:
    """Return (sentence text, sentence index) for a token index."""
    for i, sent in enumerate(doc.sents):
        if sent.start <= token_idx < sent.end:
            return sent.text, i
    return "", -1


def detect_triggers(text: str) -> list[TriggerSpan]:
    """
    Detect violence trigger verbs and noun phrases in text.

    Args:
        text: Article body or sentence.

    Returns:
        List of TriggerSpan objects, sorted by offset.
    """
    spans: list[TriggerSpan] = []

    # ── Noun phrase triggers (regex, fast) ────────────────────────────────────
    for pat, code in _NOUN_PATTERNS:
        for m in pat.finditer(text):
            spans.append(TriggerSpan(
                text=m.group(0),
                lemma=m.group(0).lower(),
                start=m.start(),
                end=m.end(),
                cameo_code=code,
                kind="noun",
            ))

    # ── Verb triggers (spaCy lemmatizer) ─────────────────────────────────────
    nlp = _load_nlp()
    if nlp is not None:
        doc = nlp(text)
        for token in doc:
            lemma = token.lemma_.lower()
            if lemma in TRIGGER_VERBS and token.pos_ in ("VERB", "AUX"):
                sent_text, sent_id = _sentence_of(doc, token.i)
                spans.append(TriggerSpan(
                    text=token.text,
                    lemma=lemma,
                    start=token.idx,
                    end=token.idx + len(token.text),
                    cameo_code=TRIGGER_VERBS[lemma],
                    kind="verb",
                    sentence=sent_text,
                    sentence_id=sent_id,
                ))
    else:
        # Fallback: simple regex on common inflections
        for lemma, code in TRIGGER_VERBS.items():
            pat = re.compile(rf"\b{re.escape(lemma)}(s|ed|ing|er)?\b", re.I)
            for m in pat.finditer(text):
                spans.append(TriggerSpan(
                    text=m.group(0),
                    lemma=lemma,
                    start=m.start(),
                    end=m.end(),
                    cameo_code=code,
                    kind="verb",
                ))

    # Sort, deduplicate overlapping spans (keep longer)
    spans.sort(key=lambda s: (s.start, -(s.end - s.start)))
    deduped: list[TriggerSpan] = []
    last_end = -1
    for span in spans:
        if span.start >= last_end:
            deduped.append(span)
            last_end = span.end

    return deduped


# Alias for import compatibility
extract_triggers = detect_triggers


def get_trigger_sentences(text: str) -> list[tuple[str, list[TriggerSpan]]]:
    """
    Split text into sentences and return only those containing triggers.

    Returns:
        List of (sentence_text, [TriggerSpan, ...]) tuples.
    """
    nlp = _load_nlp()
    if nlp is None:
        # Fallback: treat whole text as one sentence
        triggers = detect_triggers(text)
        return [(text, triggers)] if triggers else []

    doc = nlp(text)
    results = []
    for sent in doc.sents:
        sent_text = sent.text.strip()
        triggers = detect_triggers(sent_text)
        if triggers:
            results.append((sent_text, triggers))
    return results
