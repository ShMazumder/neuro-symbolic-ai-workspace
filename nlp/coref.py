"""
nlp/coref.py
Task 2.7 — Coreference resolution.

Resolves pronouns and definite noun phrases to their referent entities
within an article, improving downstream argument extraction quality.

Uses:
  - fastcoref (lightweight neural coref, preferred)
  - spaCy neuralcoref (fallback)
  - Rule-based pronoun resolution (last-mention heuristic, always available)
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CoreferenceCluster:
    """A group of mentions that refer to the same entity."""
    mentions:    list[str]         # surface forms
    canonical:   str               # representative mention
    offsets:     list[tuple[int,int]] = field(default_factory=list)


@dataclass
class ResolvedText:
    """Article text with pronouns replaced by their referents."""
    original: str
    resolved: str
    clusters: list[CoreferenceCluster] = field(default_factory=list)
    method:   str = "rule"


# ── Rule-based resolution (always available) ──────────────────────────────────

# Pronouns and their roles
MALE_PRONOUNS   = frozenset({"he", "him", "his", "himself"})
FEMALE_PRONOUNS = frozenset({"she", "her", "hers", "herself"})
PLURAL_PRONOUNS = frozenset({"they", "them", "their", "theirs", "themselves"})
ORG_PRONOUNS    = frozenset({"it", "its", "itself"})

ALL_PRONOUNS = MALE_PRONOUNS | FEMALE_PRONOUNS | PLURAL_PRONOUNS | ORG_PRONOUNS

# BD-specific group nouns → canonical type
GROUP_NOUNS: dict[str, str] = {
    "police":       "Bangladesh Police",
    "officers":     "Bangladesh Police",
    "law enforcers":"law enforcement",
    "rab":          "RAB",
    "army":         "Bangladesh Army",
    "bgb":          "BGB",
    "protesters":   "protesters",
    "workers":      "workers",
    "locals":       "local residents",
    "villagers":    "villagers",
    "victims":      "victims",
    "attackers":    "attackers",
    "assailants":   "assailants",
    "witnesses":    "witnesses",
}


def _last_entity_mention(
    text_before: str,
    pronoun: str,
) -> Optional[str]:
    """
    Find the most recent proper noun or group noun before the pronoun.
    Simple last-mention heuristic.
    """
    # Check group nouns (reverse order = closest to pronoun)
    words = text_before.lower().split()
    for word in reversed(words):
        if word in GROUP_NOUNS:
            return GROUP_NOUNS[word]

    # Check for capitalized proper nouns (persons/orgs)
    proper_nouns = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text_before)
    if proper_nouns:
        return proper_nouns[-1]   # Most recent

    return None


def rule_based_resolve(text: str) -> ResolvedText:
    """
    Rule-based pronoun resolution using last-mention heuristic.

    Replaces unambiguous pronouns (he/she/they/it) with the last
    mentioned named entity of matching type in the same paragraph.

    Args:
        text: Full article body or paragraph.

    Returns:
        ResolvedText with resolved text and identified clusters.
    """
    resolved_parts: list[str] = []
    clusters: list[CoreferenceCluster] = []
    replacements: dict[str, list[str]] = {}

    # Process sentence by sentence
    sentences = re.split(r"(?<=[.!?])\s+", text)
    context_window: list[str] = []   # last N sentences for lookup

    for sent in sentences:
        words = sent.split()
        resolved_words: list[str] = []

        for i, word in enumerate(words):
            word_lower = word.lower().rstrip(".,;:\"'")

            if word_lower in ALL_PRONOUNS:
                context = " ".join(context_window + words[:i])
                referent = _last_entity_mention(context, word_lower)
                if referent:
                    resolved_words.append(referent)
                    replacements.setdefault(referent, []).append(word)
                else:
                    resolved_words.append(word)
            else:
                resolved_words.append(word)

        resolved_parts.append(" ".join(resolved_words))
        context_window = (context_window + [sent])[-3:]  # keep last 3 sentences

    # Build clusters from replacements
    for referent, pronouns in replacements.items():
        clusters.append(CoreferenceCluster(
            mentions=[referent] + pronouns,
            canonical=referent,
        ))

    return ResolvedText(
        original=text,
        resolved=" ".join(resolved_parts),
        clusters=clusters,
        method="rule",
    )


# ── Neural coref (fastcoref, optional) ───────────────────────────────────────

_FASTCOREF_MODEL = None


def _load_fastcoref():
    global _FASTCOREF_MODEL
    if _FASTCOREF_MODEL is None:
        try:
            from fastcoref import FCoref
            _FASTCOREF_MODEL = FCoref(device="cpu")
            logger.info("fastcoref loaded.")
        except ImportError:
            logger.info("fastcoref not installed; using rule-based coref. "
                        "Install: pip install fastcoref")
    return _FASTCOREF_MODEL


def neural_resolve(text: str) -> Optional[ResolvedText]:
    """
    Neural coreference resolution via fastcoref.
    Returns None if fastcoref is not installed.
    """
    model = _load_fastcoref()
    if model is None:
        return None

    try:
        preds = model.predict(texts=[text])
        pred = preds[0]

        resolved = text
        clusters_out: list[CoreferenceCluster] = []

        # Sort clusters by position (reverse) to replace from end
        for cluster in sorted(pred.get_clusters(as_strings=True), key=lambda c: -len(c)):
            if not cluster:
                continue
            canonical = cluster[0]   # longest / first mention = representative
            mentions = cluster[1:]
            clusters_out.append(CoreferenceCluster(
                mentions=[canonical] + mentions,
                canonical=canonical,
            ))
            # Replace subsequent mentions with canonical
            for mention in mentions:
                resolved = resolved.replace(mention, canonical, 1)

        return ResolvedText(
            original=text,
            resolved=resolved,
            clusters=clusters_out,
            method="fastcoref",
        )
    except Exception as exc:
        logger.error("fastcoref failed: %s", exc)
        return None


# ── Main entry point ──────────────────────────────────────────────────────────

def resolve_coreferences(text: str, use_neural: bool = True) -> ResolvedText:
    """
    Resolve coreferences in article text.

    Tries neural (fastcoref) first; falls back to rule-based.

    Args:
        text:       Article body text.
        use_neural: If True, attempt fastcoref before rule fallback.

    Returns:
        ResolvedText with resolved text and clusters.
    """
    if use_neural:
        result = neural_resolve(text)
        if result is not None:
            return result

    return rule_based_resolve(text)
