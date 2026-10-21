"""
nlp/geo.py
Task 2.6 — Geospatial extraction and normalization for Bangladesh.

Maps location mentions (districts, upazilas, landmarks) to canonical
geographic records with coordinates.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ── Bangladesh geographic gazetteer ──────────────────────────────────────────
# District → { division, lat, lon, aliases }

BD_DISTRICTS: dict[str, dict] = {
    # Dhaka division
    "dhaka":        {"division": "Dhaka",     "lat": 23.8103, "lon": 90.4125},
    "gazipur":      {"division": "Dhaka",     "lat": 23.9999, "lon": 90.4203},
    "narayanganj":  {"division": "Dhaka",     "lat": 23.6238, "lon": 90.5000},
    "narsingdi":    {"division": "Dhaka",     "lat": 23.9200, "lon": 90.7167},
    "manikganj":    {"division": "Dhaka",     "lat": 23.8640, "lon": 90.0007},
    "munshiganj":   {"division": "Dhaka",     "lat": 23.5422, "lon": 90.5300},
    "kishoreganj":  {"division": "Dhaka",     "lat": 24.4439, "lon": 90.7766},
    "tangail":      {"division": "Dhaka",     "lat": 24.2513, "lon": 89.9167},
    "faridpur":     {"division": "Dhaka",     "lat": 23.6070, "lon": 89.8420},
    "gopalganj":    {"division": "Dhaka",     "lat": 23.0051, "lon": 89.8268},
    "madaripur":    {"division": "Dhaka",     "lat": 23.1641, "lon": 90.1988},
    "shariatpur":   {"division": "Dhaka",     "lat": 23.2422, "lon": 90.4350},
    "rajbari":      {"division": "Dhaka",     "lat": 23.7573, "lon": 89.6437},
    # Savar (upazila within Dhaka district)
    "savar":        {"division": "Dhaka",     "lat": 23.8500, "lon": 90.2667, "district": "Dhaka"},

    # Chittagong division
    "chittagong":   {"division": "Chittagong", "lat": 22.3569, "lon": 91.7832},
    "cox's bazar":  {"division": "Chittagong", "lat": 21.4272, "lon": 92.0058},
    "rangamati":    {"division": "Chittagong", "lat": 22.6415, "lon": 92.1722},
    "bandarban":    {"division": "Chittagong", "lat": 22.1953, "lon": 92.2184},
    "khagrachhari": {"division": "Chittagong", "lat": 23.1193, "lon": 91.9847},
    "feni":         {"division": "Chittagong", "lat": 23.0159, "lon": 91.3976},
    "comilla":      {"division": "Chittagong", "lat": 23.4607, "lon": 91.1809},
    "brahmanbaria": {"division": "Chittagong", "lat": 23.9570, "lon": 91.1112},
    "chandpur":     {"division": "Chittagong", "lat": 23.2333, "lon": 90.6500},
    "lakshmipur":   {"division": "Chittagong", "lat": 22.9447, "lon": 90.8416},
    "noakhali":     {"division": "Chittagong", "lat": 22.8696, "lon": 91.0995},

    # Rajshahi division
    "rajshahi":     {"division": "Rajshahi",  "lat": 24.3745, "lon": 88.6042},
    "chapai nawabganj": {"division": "Rajshahi", "lat": 24.5975, "lon": 88.2737},
    "natore":       {"division": "Rajshahi",  "lat": 24.4203, "lon": 89.0001},
    "bogura":       {"division": "Rajshahi",  "lat": 24.8465, "lon": 89.3773},
    "joypurhat":    {"division": "Rajshahi",  "lat": 25.1000, "lon": 89.0167},
    "naogaon":      {"division": "Rajshahi",  "lat": 24.8130, "lon": 88.9316},
    "pabna":        {"division": "Rajshahi",  "lat": 24.0063, "lon": 89.2372},
    "sirajganj":    {"division": "Rajshahi",  "lat": 24.4535, "lon": 89.7006},

    # Khulna division
    "khulna":       {"division": "Khulna",    "lat": 22.8456, "lon": 89.5403},
    "bagerhat":     {"division": "Khulna",    "lat": 22.6602, "lon": 89.7854},
    "satkhira":     {"division": "Khulna",    "lat": 22.7185, "lon": 89.0705},
    "jessore":      {"division": "Khulna",    "lat": 23.1667, "lon": 89.2167},
    "narail":       {"division": "Khulna",    "lat": 23.1726, "lon": 89.5121},
    "magura":       {"division": "Khulna",    "lat": 23.4879, "lon": 89.4199},
    "jhenaidah":    {"division": "Khulna",    "lat": 23.5449, "lon": 89.1520},
    "kushtia":      {"division": "Khulna",    "lat": 23.9012, "lon": 89.1210},
    "meherpur":     {"division": "Khulna",    "lat": 23.7621, "lon": 88.6317},
    "chuadanga":    {"division": "Khulna",    "lat": 23.6402, "lon": 88.8417},

    # Sylhet division
    "sylhet":       {"division": "Sylhet",    "lat": 24.8949, "lon": 91.8687},
    "moulvibazar":  {"division": "Sylhet",    "lat": 24.4826, "lon": 91.7774},
    "habiganj":     {"division": "Sylhet",    "lat": 24.3745, "lon": 91.4158},
    "sunamganj":    {"division": "Sylhet",    "lat": 25.0658, "lon": 91.3950},

    # Barisal division
    "barisal":      {"division": "Barisal",   "lat": 22.7010, "lon": 90.3535},
    "bhola":        {"division": "Barisal",   "lat": 22.6860, "lon": 90.6486},
    "patuakhali":   {"division": "Barisal",   "lat": 22.3596, "lon": 90.3298},
    "pirojpur":     {"division": "Barisal",   "lat": 22.5831, "lon": 89.9759},
    "barguna":      {"division": "Barisal",   "lat": 22.1503, "lon": 90.1264},
    "jhalokathi":   {"division": "Barisal",   "lat": 22.6375, "lon": 90.2019},

    # Rangpur division
    "rangpur":      {"division": "Rangpur",   "lat": 25.7439, "lon": 89.2752},
    "dinajpur":     {"division": "Rangpur",   "lat": 25.6279, "lon": 88.6332},
    "thakurgaon":   {"division": "Rangpur",   "lat": 26.0336, "lon": 88.4616},
    "panchagarh":   {"division": "Rangpur",   "lat": 26.3411, "lon": 88.5542},
    "nilphamari":   {"division": "Rangpur",   "lat": 25.9316, "lon": 88.8564},
    "lalmonirhat":  {"division": "Rangpur",   "lat": 25.9923, "lon": 89.2848},
    "kurigram":     {"division": "Rangpur",   "lat": 25.8074, "lon": 89.6366},
    "gaibandha":    {"division": "Rangpur",   "lat": 25.3288, "lon": 89.5283},

    # Mymensingh division
    "mymensingh":   {"division": "Mymensingh", "lat": 24.7471, "lon": 90.4203},
    "netrokona":    {"division": "Mymensingh", "lat": 24.8710, "lon": 90.7269},
    "jamalpur":     {"division": "Mymensingh", "lat": 24.9049, "lon": 89.9378},
    "sherpur":      {"division": "Mymensingh", "lat": 25.0204, "lon": 90.0152},
}

# Location aliases (common spellings / abbreviations → canonical district key)
LOCATION_ALIASES: dict[str, str] = {
    "coxs bazar":  "cox's bazar",
    "cox bazar":   "cox's bazar",
    "ctg":         "chittagong",
    "comilla":     "comilla",
    "cumilla":     "comilla",
    "bogra":       "bogura",
    "jessore":     "jessore",
    "jashore":     "jessore",
    "barisal":     "barisal",
    "barishal":    "barisal",
    "noakhali":    "noakhali",
    "feni":        "feni",
    "dhaka city":  "dhaka",
    "old dhaka":   "dhaka",
    "new dhaka":   "dhaka",
}

# Regex for GPE NER fallback (capitalized sequences)
_GPE_REGEX = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b")


@dataclass
class GeoResult:
    raw:        str
    district:   Optional[str]  = None
    division:   Optional[str]  = None
    latitude:   Optional[float] = None
    longitude:  Optional[float] = None
    confidence: float = 0.0
    method:     str = "failed"


def _lookup(name: str) -> Optional[dict]:
    """Lookup a location name in the gazetteer. Returns record or None."""
    key = name.lower().strip()
    key = LOCATION_ALIASES.get(key, key)
    return BD_DISTRICTS.get(key)


def normalize_location(raw: str) -> GeoResult:
    """
    Normalize a raw location string to canonical BD geographic record.

    Args:
        raw: Location mention (e.g., "Savar", "Cox's Bazar", "Sylhet district").

    Returns:
        GeoResult with district/division/coordinates if found.
    """
    # Strip common suffixes
    cleaned = re.sub(
        r"\b(district|upazila|union|city|town|thana|municipality)\b", "", raw, flags=re.I
    ).strip()

    record = _lookup(cleaned)
    if record:
        district = record.get("district", cleaned.title())
        return GeoResult(
            raw=raw,
            district=district,
            division=record.get("division"),
            latitude=record.get("lat"),
            longitude=record.get("lon"),
            confidence=0.9,
            method="gazetteer",
        )

    # Partial match on longer expressions (e.g. "Savar upazila of Dhaka")
    for part in cleaned.split():
        record = _lookup(part)
        if record:
            return GeoResult(
                raw=raw,
                district=record.get("district", part.title()),
                division=record.get("division"),
                latitude=record.get("lat"),
                longitude=record.get("lon"),
                confidence=0.7,
                method="gazetteer_partial",
            )

    logger.debug("Location not in gazetteer: %r", raw)
    return GeoResult(raw=raw, confidence=0.0, method="failed")


# ── spaCy-based extraction ────────────────────────────────────────────────────

def extract_locations(text: str, nlp=None) -> list[GeoResult]:
    """
    Extract and normalize all location mentions in text.

    Args:
        text: Article sentence or paragraph.
        nlp:  Optional pre-loaded spaCy model.

    Returns:
        List of GeoResult objects (deduplicated by district).
    """
    raw_mentions: list[str] = []

    if nlp is not None:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in ("GPE", "LOC", "FAC"):
                raw_mentions.append(ent.text)
    else:
        # Fallback regex: capitalized words
        raw_mentions = _GPE_REGEX.findall(text)

    results: list[GeoResult] = []
    seen_districts: set[str] = set()

    for mention in raw_mentions:
        geo = normalize_location(mention)
        if geo.district and geo.district not in seen_districts:
            seen_districts.add(geo.district)
            results.append(geo)
        elif not geo.district and geo.confidence == 0.0:
            results.append(geo)

    return results


def extract_districts(text: str, nlp=None) -> list[str]:
    """Helper to extract distinct district names mentioned in text."""
    results = extract_locations(text, nlp=nlp)
    districts = []
    for r in results:
        if r.district and r.district not in districts:
            districts.append(r.district)
    return districts

