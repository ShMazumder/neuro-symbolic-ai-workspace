"""
scraper/rss_poller.py
Task 1.1 — Poll Daily Star RSS feeds and return new Article stubs.
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

try:
    import feedparser
except ImportError:
    feedparser = None

import requests
import xml.etree.ElementTree as ET

from scraper.schema import Article, RSS_FEEDS

logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
RAW_DIR = Path("data/raw")
SEEN_FILE = Path("data/.seen_urls.json")   # URL dedup cache


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_seen() -> set[str]:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    return set()


def _save_seen(seen: set[str]) -> None:
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(sorted(seen), indent=2), encoding="utf-8")


def _parse_date(entry) -> str | None:
    """Return ISO 8601 string from feedparser entry, or None."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def _article_path(article: Article) -> Path:
    date_prefix = (article.published_date or article.scraped_at)[:10]   # YYYY-MM-DD
    slug = hashlib.md5(article.url.encode()).hexdigest()[:12]
    return RAW_DIR / date_prefix / f"{slug}.json"


# ── Core poller ────────────────────────────────────────────────────────────────

def _poll_xml_feed(feed_url: str) -> list[dict]:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(feed_url, headers=headers, timeout=12)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    entries = []
    for it in root.findall(".//item"):
        title_el = it.find("title")
        title = "".join(title_el.itertext()).strip() if title_el is not None else ""
        link_el = it.find("link")
        link = link_el.text.strip() if link_el is not None and link_el.text else ""
        desc_el = it.find("description")
        desc = "".join(desc_el.itertext()).strip() if desc_el is not None else ""
        pub_el = it.find("pubDate")
        pub = pub_el.text.strip() if pub_el is not None and pub_el.text else None
        if link:
            entries.append({
                "link": link,
                "title": title,
                "summary": desc,
                "published": pub,
            })
    return entries


def poll_feeds(
    feeds: dict[str, str] | None = None,
    rate_limit_s: float = 2.0,
) -> Iterator[Article]:
    """
    Poll all RSS feeds and yield new Article stubs (no body yet).
    """
    if feeds is None:
        feeds = RSS_FEEDS

    seen = _load_seen()
    new_articles: list[Article] = []

    for feed_name, feed_url in feeds.items():
        logger.info("Polling %s — %s", feed_name, feed_url)
        entries: list[dict] = []

        if feedparser is not None:
            try:
                parsed = feedparser.parse(feed_url)
                for entry in parsed.entries:
                    entries.append({
                        "link": entry.get("link", "").strip(),
                        "title": entry.get("title", "").strip(),
                        "summary": entry.get("summary", "").strip(),
                        "published_date": _parse_date(entry),
                        "tags": [t.get("term", "") for t in entry.get("tags", [])],
                    })
            except Exception as exc:
                logger.warning("Feedparser failed for %s: %s — trying native XML fallback", feed_url, exc)

        # Fallback to direct XML parsing if feedparser unavailable or returned empty
        if not entries:
            try:
                xml_entries = _poll_xml_feed(feed_url)
                for e in xml_entries:
                    entries.append({
                        "link": e["link"],
                        "title": e["title"],
                        "summary": e["summary"],
                        "published_date": e.get("published"),
                        "tags": [],
                    })
            except Exception as exc:
                logger.error("XML parse failed for %s: %s", feed_url, exc)
                time.sleep(rate_limit_s)
                continue

        for entry in entries:
            url: str = entry.get("link", "").strip()
            if not url or url in seen:
                continue

            article = Article(
                url=url,
                title=entry.get("title", "").strip(),
                summary=entry.get("summary", "").strip(),
                category=feed_name,
                published_date=entry.get("published_date"),
                rss_feed_url=feed_url,
                tags=entry.get("tags", []),
            )

            seen.add(url)
            new_articles.append(article)
            yield article

        time.sleep(rate_limit_s)

    _save_seen(seen)
    logger.info("Polled %d feeds — %d new articles found.", len(feeds), len(new_articles))



def save_article_stub(article: Article) -> Path:
    """Persist an Article (stub or full) as JSON. Creates parent dirs."""
    path = _article_path(article)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(article.to_json(), encoding="utf-8")
    logger.debug("Saved %s → %s", article.id[:8], path)
    return path


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for article in poll_feeds():
        save_article_stub(article)
        count += 1
        logger.info("[%d] %s", count, article.title[:80])

    logger.info("Done. %d new article stubs written to %s", count, RAW_DIR)
