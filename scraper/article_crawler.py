"""
scraper/article_crawler.py
Task 1.2 — Fetch full article body from a Daily Star article URL.
"""

import logging
import re
import time
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from scraper.schema import Article

logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; NeuroSymbolicResearchBot/1.0; "
        "+https://github.com/ShMazumder/neuro-symbolic-ai-workspace)"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
REQUEST_TIMEOUT = 15   # seconds
RATE_LIMIT_S    = 2.0  # seconds between requests (respect robots.txt spirit)
MAX_RETRIES     = 3


# ── Extraction helpers ─────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Normalise whitespace and remove zero-width chars."""
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_body(soup: BeautifulSoup) -> str:
    """
    Extract article body text from The Daily Star HTML.

    The Daily Star uses:
      <div class="field-items"> or <div class="d-body"> for body content.
    """
    # Primary selector (most common)
    container = soup.find("div", class_="d-body")

    # Fallback selectors
    if not container:
        container = soup.find("div", class_="field-items")
    if not container:
        container = soup.find("article")
    if not container:
        container = soup.find("div", id="content")

    if not container:
        logger.warning("Could not find article body container.")
        return ""

    # Remove scripts, ads, related articles
    for tag in container.find_all(["script", "style", "figure", "aside", "nav"]):
        tag.decompose()
    for tag in container.find_all(class_=re.compile(r"(ad|related|share|social|tag)", re.I)):
        tag.decompose()

    paragraphs = [_clean_text(p.get_text()) for p in container.find_all("p")]
    return "\n\n".join(p for p in paragraphs if p)


def _extract_author(soup: BeautifulSoup) -> Optional[str]:
    """Extract byline / author name."""
    byline = soup.find(class_=re.compile(r"(author|byline|reporter)", re.I))
    if byline:
        return _clean_text(byline.get_text())
    meta = soup.find("meta", attrs={"name": "author"})
    if meta:
        return meta.get("content", "").strip() or None
    return None


def _extract_published_date(soup: BeautifulSoup) -> Optional[str]:
    """Extract canonical published date from meta tags."""
    for attr in ("article:published_time", "og:article:published_time"):
        meta = soup.find("meta", property=attr)
        if meta and meta.get("content"):
            return meta["content"].strip()
    meta = soup.find("meta", attrs={"name": "publish-date"})
    if meta and meta.get("content"):
        return meta["content"].strip()
    return None


# ── Core crawler ───────────────────────────────────────────────────────────────

def fetch_article(article: Article, rate_limit_s: float = RATE_LIMIT_S) -> Article:
    """
    Fetch and populate the body of a Daily Star article stub.

    Args:
        article: Article stub (url must be set).
        rate_limit_s: Wait time in seconds after the request.

    Returns:
        Updated Article with body, author, and confirmed published_date.
    """
    if not article.url:
        raise ValueError("Article URL is empty.")

    parsed = urlparse(article.url)
    if parsed.netloc not in ("www.thedailystar.net", "thedailystar.net"):
        raise ValueError(f"Unexpected domain: {parsed.netloc}")

    last_exc: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                article.url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            resp.raise_for_status()
            break
        except requests.RequestException as exc:
            logger.warning("Attempt %d/%d failed for %s: %s", attempt, MAX_RETRIES, article.url, exc)
            last_exc = exc
            time.sleep(rate_limit_s * attempt)
    else:
        logger.error("All retries exhausted for %s", article.url)
        raise last_exc  # type: ignore[misc]

    soup = BeautifulSoup(resp.text, "html.parser")

    # Enrich article fields
    article.body = _extract_body(soup)
    article.author = article.author or _extract_author(soup)
    article.published_date = article.published_date or _extract_published_date(soup)

    # Store raw HTML for debugging (optional — comment out to save disk)
    # article.raw_html = resp.text

    logger.debug("Fetched %d chars body from %s", len(article.body), article.url)
    time.sleep(rate_limit_s)
    return article


def crawl_articles(
    articles: list[Article],
    rate_limit_s: float = RATE_LIMIT_S,
) -> list[Article]:
    """
    Sequentially crawl a list of article stubs.

    Args:
        articles: List of Article stubs with urls set.
        rate_limit_s: Seconds to wait between requests.

    Returns:
        List of fully populated Article objects (failed ones have empty body).
    """
    results: list[Article] = []
    for i, article in enumerate(articles, 1):
        logger.info("[%d/%d] Crawling %s", i, len(articles), article.url[:80])
        try:
            results.append(fetch_article(article, rate_limit_s))
        except Exception as exc:
            logger.error("Failed to crawl %s: %s", article.url, exc)
            results.append(article)   # Return stub unchanged on failure
    return results


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )

    if len(sys.argv) < 2:
        print("Usage: python -m scraper.article_crawler <article_stub.json>")
        sys.exit(1)

    stub_path = Path(sys.argv[1])
    article = Article.from_json(stub_path.read_text(encoding="utf-8"))
    article = fetch_article(article)

    out_path = stub_path.with_stem(stub_path.stem + "_full")
    out_path.write_text(article.to_json(), encoding="utf-8")
    print(f"Saved to {out_path}")
    print(f"Body preview:\n{article.body[:500]}")
