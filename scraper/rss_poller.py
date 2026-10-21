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

import feedparser

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

def poll_feeds(
    feeds: dict[str, str] | None = None,
    rate_limit_s: float = 2.0,
) -> Iterator[Article]:
    """
    Poll all RSS feeds and yield new Article stubs (no body yet).

    Args:
        feeds: mapping of {name: url}. Defaults to RSS_FEEDS.
        rate_limit_s: seconds to sleep between feed requests.

    Yields:
        Article objects with metadata but empty body (to be filled by crawler).
    """
    if feeds is None:
        feeds = RSS_FEEDS

    seen = _load_seen()
    new_articles: list[Article] = []

    for feed_name, feed_url in feeds.items():
        logger.info("Polling %s — %s", feed_name, feed_url)
        try:
            parsed = feedparser.parse(feed_url)
        except Exception as exc:
            logger.error("Failed to parse %s: %s", feed_url, exc)
            time.sleep(rate_limit_s)
            continue

        for entry in parsed.entries:
            url: str = entry.get("link", "").strip()
            if not url or url in seen:
                continue

            article = Article(
                url=url,
                title=entry.get("title", "").strip(),
                summary=entry.get("summary", "").strip(),
                category=feed_name,
                published_date=_parse_date(entry),
                rss_feed_url=feed_url,
                tags=[t.get("term", "") for t in entry.get("tags", [])],
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
