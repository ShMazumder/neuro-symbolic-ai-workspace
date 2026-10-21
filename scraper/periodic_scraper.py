"""
scraper/periodic_scraper.py
Automated periodic news scraper and archive crawler for The Daily Star.

Usage:
    # 1. Single-shot run (poll all feeds, crawl full text, update real_news_daily_star.json)
    python -m scraper.periodic_scraper --once

    # 2. Run periodically every N seconds (e.g., every hour = 3600s, every 15 min = 900s)
    python -m scraper.periodic_scraper --interval 3600

    # 3. Bulk fetch historical news from category archives (crime, politics)
    python -m scraper.periodic_scraper --bulk --pages 3
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests

from scraper.article_crawler import fetch_article
from scraper.rss_poller import poll_feeds, save_article_stub
from scraper.schema import Article, RSS_FEEDS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("periodic_scraper")

REAL_NEWS_PATH = Path("data/real_news_daily_star.json")
RAW_DIR = Path("data/raw")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def load_dataset() -> list[dict]:
    """Load existing real_news_daily_star.json records."""
    if REAL_NEWS_PATH.exists():
        try:
            data = json.loads(REAL_NEWS_PATH.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception as exc:
            logger.warning("Could not read %s: %s", REAL_NEWS_PATH, exc)
    return []


def save_dataset(records: list[dict]) -> None:
    """Save records to real_news_daily_star.json deduplicated by URL."""
    REAL_NEWS_PATH.parent.mkdir(parents=True, exist_ok=True)
    seen_urls = set()
    deduped = []
    for r in records:
        url = r.get("url")
        if url and url not in seen_urls:
            seen_urls.add(url)
            deduped.append(r)
    REAL_NEWS_PATH.write_text(
        json.dumps(deduped, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    logger.info("Saved %d unique articles to %s", len(deduped), REAL_NEWS_PATH)


def scrape_cycle(limit_new: int = 25, rate_limit_s: float = 1.0) -> int:
    """
    Run one complete cycle: poll RSS feeds, crawl bodies, and update dataset.
    """
    logger.info("=== Starting Scrape Cycle ===")
    dataset = load_dataset()
    existing_urls = {r.get("url") for r in dataset if r.get("url")}
    
    new_articles: list[Article] = []
    for stub in poll_feeds(rate_limit_s=rate_limit_s):
        if stub.url in existing_urls:
            continue
        try:
            logger.info("Crawling body: %s", stub.title[:70])
            full_art = fetch_article(stub, rate_limit_s=rate_limit_s)
            save_article_stub(full_art)
            if full_art.body:
                dataset.append(full_art.to_dict())
                existing_urls.add(full_art.url)
                new_articles.append(full_art)
            if len(new_articles) >= limit_new:
                break
        except Exception as exc:
            logger.warning("Failed to fetch %s: %s", stub.url, exc)

    if new_articles:
        save_dataset(dataset)
        logger.info("Cycle complete: %d new articles added (Total: %d)", len(new_articles), len(dataset))
    else:
        logger.info("Cycle complete: No new articles found in feeds.")

    return len(new_articles)


def scrape_category_archive(
    category_slug: str = "news/bangladesh/crime-justice",
    max_pages: int = 2,
    rate_limit_s: float = 1.0,
) -> int:
    """
    Scrape listing pages from The Daily Star archive to populate older news.
    """
    logger.info("Crawling archive: %s (pages=1..%d)", category_slug, max_pages)
    dataset = load_dataset()
    existing_urls = {r.get("url") for r in dataset if r.get("url")}
    added = 0

    base_url = f"https://www.thedailystar.net/{category_slug}"

    for page in range(max_pages):
        url = f"{base_url}?page={page}" if page > 0 else base_url
        logger.info("Fetching archive index page %d: %s", page + 1, url)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12)
            if resp.status_code != 200:
                continue
            # Extract links to news stories
            links = set(re.findall(r'href=["\'](/news/[^"\']+)["\']', resp.text))
            for rel in links:
                full_url = urljoin("https://www.thedailystar.net", rel)
                # Skip index or listing URLs
                if full_url in existing_urls or rel.endswith(category_slug):
                    continue
                
                stub = Article(url=full_url, category=category_slug.split("/")[-1])
                try:
                    art = fetch_article(stub, rate_limit_s=rate_limit_s)
                    save_article_stub(art)
                    if art.body and len(art.body) > 100:
                        dataset.append(art.to_dict())
                        existing_urls.add(full_url)
                        added += 1
                        logger.info("  [%d] Added: %s", added, art.title[:65])
                except Exception as e:
                    logger.debug("Failed %s: %s", full_url, e)

        except Exception as exc:
            logger.error("Failed page %s: %s", url, exc)

    if added:
        save_dataset(dataset)
        logger.info("Archive scrape complete: %d new articles added (Total: %d)", added, len(dataset))
    return added


def run_daemon(interval_seconds: int = 3600, limit_per_cycle: int = 25) -> None:
    """
    Continuous background loop polling every `interval_seconds`.
    """
    logger.info(
        "Starting Daily Star periodic scraper daemon (Interval: %ds / %.1f hours)",
        interval_seconds, interval_seconds / 3600
    )
    cycle = 1
    while True:
        try:
            logger.info("--- Scraper Loop #%d [%s] ---", cycle, datetime.now().isoformat())
            scrape_cycle(limit_new=limit_per_cycle)
        except KeyboardInterrupt:
            logger.info("Scraper daemon stopped by user.")
            break
        except Exception as exc:
            logger.error("Error in scrape cycle #%d: %s", cycle, exc, exc_info=True)

        logger.info("Sleeping for %d seconds until next poll...", interval_seconds)
        time.sleep(interval_seconds)
        cycle += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Daily Star periodic news scraper")
    parser.add_argument("--once", action="store_true", help="Run a single scrape cycle and exit")
    parser.add_argument("--interval", type=int, default=3600, help="Daemon sleep interval in seconds (default: 3600s)")
    parser.add_argument("--bulk", action="store_true", help="Crawl historical archives instead of RSS only")
    parser.add_argument("--pages", type=int, default=2, help="Number of archive pages to crawl in --bulk mode")
    parser.add_argument("--limit", type=int, default=25, help="Max new articles to crawl per cycle")

    parser.add_argument("--category", type=str, default=None, help="Specific section slug to crawl (e.g., news/crime-justice)")

    args = parser.parse_args()

    if args.bulk:
        categories = [args.category] if args.category else [
            "news/crime-justice",
            "news/bangladesh/crime-justice",
            "news/bangladesh/politics",
        ]
        for cat in categories:
            scrape_category_archive(category_slug=cat, max_pages=args.pages)
    elif args.once:
        scrape_cycle(limit_new=args.limit)
    else:
        run_daemon(interval_seconds=args.interval, limit_per_cycle=args.limit)
