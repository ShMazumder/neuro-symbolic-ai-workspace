"""
nlp/relevance_filter.py
Task 2.8 — Binary violence relevance filter.

Quickly decides whether an article is violence-related before
sending it through the expensive NLP pipeline.

Strategy (hybrid, configurable):
  - FAST: keyword/regex check (no model needed) → very high recall
  - CONFIRM: zero-shot classifier (HuggingFace) for borderline cases
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# ── Violence keyword lexicon ───────────────────────────────────────────────────

VIOLENCE_KEYWORDS: frozenset[str] = frozenset({
    # Death / killing
    "kill", "killed", "killing", "murder", "murdered", "death", "dead",
    "died", "fatality", "casualties", "casualty", "slain", "slay",
    "execution", "executed", "lynching", "lynched",

    # Physical violence
    "attack", "attacked", "assault", "assaulted", "beat", "beaten",
    "stab", "stabbed", "shot", "shoot", "shooting", "fire", "fired",
    "wound", "wounded", "injure", "injured", "injury", "injuries",
    "torture", "tortured", "rape", "raped", "abduct", "abducted",
    "kidnap", "kidnapped",

    # Conflict events
    "clash", "clashed", "clashes", "riot", "rioting", "unrest",
    "protest violence", "crackdown", "siege", "blockade", "explosion",
    "blast", "bomb", "bombing", "arson", "vandalism",

    # BD-specific
    "crossfire", "gunfight", "encounter", "disappearance", "disappeared",
    "custodial", "hartal violence", "acid attack", "dowry", "mob justice",
    "extrajudicial", "enforced disappearance",

    # Arrest / detention (structural violence)
    "arrested", "detained", "detain", "crackdown",
})

# Regex patterns for multi-word / contextual signals
VIOLENCE_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b(kill|murder|shot|stab)(ed|ing|s)?\b", re.I),
    re.compile(r"\b(dead|death|fatal|casualt)(y|ies|s)?\b", re.I),
    re.compile(r"\b(clash|riot|unrest|protest\s+violence)\b", re.I),
    re.compile(r"\b(crossfire|gunfight|encounter\s+killing)\b", re.I),
    re.compile(r"\b(acid\s+attack|mob\s+(justice|beating|lynching))\b", re.I),
    re.compile(r"\b(enforced\s+disappear|custodial\s+(death|torture))\b", re.I),
    re.compile(r"\b(rape|sexual\s+assault)\b", re.I),
    re.compile(r"\b(bomb(ing|blast)?|explosion|arson)\b", re.I),
    re.compile(r"\bdowny\s+(killing|violence|murder)\b", re.I),
]


class Verdict(str, Enum):
    VIOLENCE    = "violence"
    NOT_VIOLENCE = "not_violence"
    UNCERTAIN   = "uncertain"


@dataclass
class FilterResult:
    verdict:    Verdict
    confidence: float           # 0.0 – 1.0
    method:     str             # "keyword" | "model" | "combined"
    signals:    list[str]       # matched keywords / patterns


# ── Keyword filter ────────────────────────────────────────────────────────────

def keyword_filter(text: str) -> FilterResult:
    """
    Fast keyword/regex pass. O(n) in text length.

    Returns VIOLENCE if ≥2 signals, UNCERTAIN if 1, NOT_VIOLENCE if 0.
    """
    text_lower = text.lower()
    signals: list[str] = []

    # Token-level check
    tokens = re.findall(r"\b\w+\b", text_lower)
    for token in tokens:
        if token in VIOLENCE_KEYWORDS:
            signals.append(token)

    # Pattern-level check
    for pat in VIOLENCE_PATTERNS:
        m = pat.search(text)
        if m:
            signals.append(m.group(0).lower())

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_signals: list[str] = []
    for s in signals:
        if s not in seen:
            seen.add(s)
            unique_signals.append(s)

    n = len(unique_signals)
    if n >= 2:
        return FilterResult(
            verdict=Verdict.VIOLENCE,
            confidence=min(0.5 + n * 0.05, 0.95),
            method="keyword",
            signals=unique_signals[:10],
        )
    elif n == 1:
        return FilterResult(
            verdict=Verdict.UNCERTAIN,
            confidence=0.45,
            method="keyword",
            signals=unique_signals,
        )
    else:
        return FilterResult(
            verdict=Verdict.NOT_VIOLENCE,
            confidence=0.85,
            method="keyword",
            signals=[],
        )


# ── Model-based filter (zero-shot) ────────────────────────────────────────────

_CLASSIFIER = None   # lazy-loaded

ZERO_SHOT_LABELS = [
    "violence, conflict, or crime report",
    "general news, politics, or economics",
]

VIOLENCE_LABEL = ZERO_SHOT_LABELS[0]


def _load_classifier():
    global _CLASSIFIER
    if _CLASSIFIER is None:
        try:
            from transformers import pipeline as hf_pipeline
            _CLASSIFIER = hf_pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1,   # CPU; set to 0 for GPU
            )
            logger.info("Zero-shot classifier loaded.")
        except ImportError:
            logger.warning("transformers not installed; model filter unavailable.")
    return _CLASSIFIER


def model_filter(text: str, max_chars: int = 512) -> Optional[FilterResult]:
    """
    Zero-shot violence classifier. Returns None if model unavailable.
    """
    clf = _load_classifier()
    if clf is None:
        return None

    snippet = text[:max_chars]
    try:
        result = clf(snippet, candidate_labels=ZERO_SHOT_LABELS, multi_label=False)
        scores = dict(zip(result["labels"], result["scores"]))
        violence_score = scores.get(VIOLENCE_LABEL, 0.0)

        if violence_score >= 0.6:
            verdict = Verdict.VIOLENCE
        elif violence_score <= 0.35:
            verdict = Verdict.NOT_VIOLENCE
        else:
            verdict = Verdict.UNCERTAIN

        return FilterResult(
            verdict=verdict,
            confidence=round(violence_score, 3),
            method="model",
            signals=[f"zero-shot score={violence_score:.3f}"],
        )
    except Exception as exc:
        logger.error("Model filter failed: %s", exc)
        return None


# ── Combined filter ───────────────────────────────────────────────────────────

def is_violence_related(
    title: str,
    body: str = "",
    use_model_for_uncertain: bool = True,
) -> FilterResult:
    """
    Main entry point. Combines keyword and (optionally) model filter.

    Args:
        title: Article title.
        body:  Article body (first 1000 chars used).
        use_model_for_uncertain: If True, run model on UNCERTAIN keyword results.

    Returns:
        FilterResult with final verdict.
    """
    text = f"{title}. {body[:1000]}"
    kw = keyword_filter(text)

    if kw.verdict in (Verdict.VIOLENCE, Verdict.NOT_VIOLENCE):
        return kw   # Confident — skip model

    # UNCERTAIN → try model
    if use_model_for_uncertain:
        mdl = model_filter(text)
        if mdl is not None:
            mdl.signals = kw.signals + mdl.signals
            mdl.method = "combined"
            return mdl

    return kw   # Fall back to keyword result


# ── Batch helper ──────────────────────────────────────────────────────────────

def filter_batch(articles: list[dict]) -> list[dict]:
    """
    Tag a list of article dicts with violence relevance.

    Each dict must have 'title' key; 'body' is optional.
    Adds 'is_violence_related' (bool) and 'filter_confidence' (float).
    """
    tagged = []
    for art in articles:
        result = is_violence_related(
            title=art.get("title", ""),
            body=art.get("body", ""),
        )
        art["is_violence_related"] = result.verdict == Verdict.VIOLENCE
        art["filter_confidence"] = result.confidence
        art["filter_signals"] = result.signals
        tagged.append(art)
    return tagged
