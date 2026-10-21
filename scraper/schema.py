"""
scraper/schema.py
Article data schema for The Daily Star ingestion pipeline.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import json
import uuid


@dataclass
class Article:
    """Canonical representation of a scraped Daily Star article."""

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    url: str = ""

    # Content
    title: str = ""
    body: str = ""
    summary: str = ""          # First paragraph or meta description
    category: str = ""         # e.g. "frontpage", "country", "politics"
    tags: list = field(default_factory=list)

    # Temporal
    published_date: Optional[str] = None   # ISO 8601: "2025-03-13T14:00:00+06:00"
    scraped_at: str = field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    # Source metadata
    author: Optional[str] = None
    source: str = "thedailystar.net"
    rss_feed_url: Optional[str] = None    # Which RSS feed produced this entry

    # Processing flags
    is_violence_related: Optional[bool] = None   # Set by NLP relevance filter
    raw_html: Optional[str] = None               # Stored separately if needed

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: dict) -> "Article":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, json_str: str) -> "Article":
        return cls.from_dict(json.loads(json_str))

    def __repr__(self) -> str:
        return f"Article(id={self.id[:8]}, title={self.title[:60]!r})"


# ── RSS feed registry ──────────────────────────────────────────────────────────

RSS_FEEDS = {
    "frontpage":  "https://www.thedailystar.net/frontpage/rss.xml",
    "country":    "https://www.thedailystar.net/country/rss.xml",
    "politics":   "https://www.thedailystar.net/politics/rss.xml",
    "crime":      "https://www.thedailystar.net/crime/rss.xml",
    "law":        "https://www.thedailystar.net/law-our-rights/rss.xml",
    "city":       "https://www.thedailystar.net/city/rss.xml",
    "back-page":  "https://www.thedailystar.net/back-page/rss.xml",
}
