"""
nlp/temporal.py
Task 2.5 — Temporal normalization.

Converts relative and ambiguous date expressions to ISO 8601 (YYYY-MM-DD).
Uses dateparser library with Bangladesh-specific overrides.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# ── dateparser config ─────────────────────────────────────────────────────────
DATEPARSER_SETTINGS = {
    "PREFER_DAY_OF_MONTH": "first",
    "PREFER_DATES_FROM":   "past",
    "RETURN_AS_TIMEZONE_AWARE": False,
    "TO_TIMEZONE": "Asia/Dhaka",
    "TIMEZONE": "Asia/Dhaka",
}

# BD-specific relative expressions → delta days (relative to article date)
BD_RELATIVE: dict[str, int] = {
    "yesterday":   -1,
    "day before":  -2,
    "last night":  -1,
    "early today":  0,
    "this morning": 0,
    "monday":    None,   # handled by dateparser
    "tuesday":   None,
    "wednesday": None,
    "thursday":  None,
    "friday":    None,
    "saturday":  None,
    "sunday":    None,
}

# Regex for "last <weekday>" / "this <weekday>" / "on <weekday>"
_WEEKDAY_PAT = re.compile(
    r"\b(last|this|previous|on)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    re.I,
)

@dataclass
class DateResult:
    raw:        str              # original string from article
    normalized: Optional[str]   # ISO 8601 date string, or None
    confidence: float           # 0.0 – 1.0
    method:     str             # "exact" | "relative" | "dateparser" | "failed"


def _try_dateparser(text: str, reference: Optional[date] = None) -> Optional[date]:
    """Attempt dateparser.parse; return date or None."""
    try:
        import dateparser
        settings = dict(DATEPARSER_SETTINGS)
        if reference:
            settings["RELATIVE_BASE"] = reference  # type: ignore[assignment]
        parsed = dateparser.parse(text, settings=settings)
        return parsed.date() if parsed else None
    except Exception as exc:
        logger.debug("dateparser failed for %r: %s", text, exc)
        return None


# ── Main normalizer ───────────────────────────────────────────────────────────

def normalize_date(
    raw: str,
    reference_date: Optional[date] = None,
) -> DateResult:
    """
    Normalize a raw date expression to ISO 8601.

    Args:
        raw:            The raw date string extracted from text.
        reference_date: The article's published date (anchor for relative refs).
                        Defaults to today if not provided.

    Returns:
        DateResult with normalized date string.
    """
    ref = reference_date or date.today()
    raw = raw.strip()

    # ── 1. Already ISO 8601? ──────────────────────────────────────────────────
    iso_match = re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw)
    if iso_match:
        return DateResult(raw=raw, normalized=raw, confidence=1.0, method="exact")

    # ── 2. Simple relative ────────────────────────────────────────────────────
    raw_lower = raw.lower()
    if "yesterday" in raw_lower:
        d = ref - timedelta(days=1)
        return DateResult(raw=raw, normalized=d.isoformat(), confidence=0.95, method="relative")
    if raw_lower in ("today", "this morning", "early today"):
        return DateResult(raw=raw, normalized=ref.isoformat(), confidence=0.9, method="relative")
    if "day before yesterday" in raw_lower:
        d = ref - timedelta(days=2)
        return DateResult(raw=raw, normalized=d.isoformat(), confidence=0.9, method="relative")

    # ── 3. "last/this <weekday>" ──────────────────────────────────────────────
    m = _WEEKDAY_PAT.search(raw_lower)
    if m:
        qualifier, weekday = m.group(1).lower(), m.group(2).lower()
        weekdays = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
        target_dow = weekdays.index(weekday)
        current_dow = ref.weekday()  # Monday=0
        if qualifier in ("last", "previous"):
            delta = (current_dow - target_dow) % 7 or 7
        else:  # "this"
            delta = (current_dow - target_dow) % 7
        d = ref - timedelta(days=delta)
        return DateResult(raw=raw, normalized=d.isoformat(), confidence=0.85, method="relative")

    # ── 4. dateparser (handles "March 13", "13 March 2025", etc.) ────────────
    parsed = _try_dateparser(raw, reference=ref)
    if parsed:
        # Sanity: don't return future dates unless explicitly stated
        if parsed > date.today() + timedelta(days=365):
            parsed = parsed.replace(year=parsed.year - 1)
        return DateResult(raw=raw, normalized=parsed.isoformat(), confidence=0.75, method="dateparser")

    # ── 5. Failed ─────────────────────────────────────────────────────────────
    logger.debug("Could not normalize date: %r", raw)
    return DateResult(raw=raw, normalized=None, confidence=0.0, method="failed")


# ── Date extraction from text ─────────────────────────────────────────────────

# Patterns that suggest a date expression in running text
_DATE_EXTRACT_PATS: list[re.Pattern] = [
    # "on March 13", "on 13 March 2025"
    re.compile(
        r"\bon\s+(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*(?:\s+\d{4})?)\b",
        re.I,
    ),
    # "last Thursday", "this Monday"
    re.compile(
        r"\b((?:last|this|previous)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b",
        re.I,
    ),
    # ISO date
    re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
    # "yesterday", "today", "Monday morning"
    re.compile(r"\b(yesterday|today|early\s+today|this\s+morning|last\s+night)\b", re.I),
]


def extract_dates(text: str, reference_date: Optional[date] = None) -> list[DateResult]:
    """
    Extract and normalize all date mentions in a text snippet.

    Returns a list of DateResult objects (may be empty).
    """
    results: list[DateResult] = []
    seen_starts: set[int] = set()

    for pat in _DATE_EXTRACT_PATS:
        for m in pat.finditer(text):
            if m.start() in seen_starts:
                continue
            seen_starts.add(m.start())
            raw = m.group(1) if m.lastindex else m.group(0)
            dr = normalize_date(raw, reference_date=reference_date)
            if dr.normalized:
                results.append(dr)

    return results
