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
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

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

    if BeautifulSoup is not None:
        soup = BeautifulSoup(resp.text, "html.parser")
        article.body = _extract_body(soup)
        article.author = article.author or _extract_author(soup)
        article.published_date = article.published_date or _extract_published_date(soup)
    else:
        # Regex fallback when bs4 is not available
        paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", resp.text, re.DOTALL | re.IGNORECASE)
        clean_paras = []
        for p in paragraphs:
            text = re.sub(r"<[^>]+>", "", p)
            text = _clean_text(text)
            if len(text) > 30 and not any(skip in text.lower() for skip in ["advertisement", "all rights reserved", "subscribe"]):
                clean_paras.append(text)
        article.body = "\n\n".join(clean_paras)
        
        author_m = re.search(r'name=["\']author["\']\s+content=["\'](.*?)["\']', resp.text, re.IGNORECASE)
        if author_m:
            article.author = article.author or author_m.group(1).strip()
            
        date_m = re.search(r'property=["\'](?:article|og:article):published_time["\']\s+content=["\'](.*?)["\']', resp.text, re.IGNORECASE)
        if date_m:
            article.published_date = article.published_date or date_m.group(1).strip()

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


# ── Archive Crawler (Task 1.1) ────────────────────────────────────────────────

ARCHIVE_CATEGORIES = [
    "news/crime-justice",
    "news/bangladesh",
    "news/bangladesh/politics",
    "news/city",
]


def crawl_archive(
    categories: list[str] = ARCHIVE_CATEGORIES,
    max_pages_per_category: int = 10,
    max_articles_total: int = 500,
    rate_limit_s: float = 0.5,
    save_raw: bool = True,
) -> list[Article]:
    """
    Paginate through Daily Star archive sections and extract articles.

    Args:
        categories: Category path suffixes to crawl.
        max_pages_per_category: Maximum pages to paginate per category.
        max_articles_total: Global limit on articles to scrape.
        rate_limit_s: Sleep between requests.
        save_raw: Whether to persist article JSONs to data/raw/.
    """
    import hashlib
    import json
    from pathlib import Path

    raw_dir = Path("data/raw")
    seen_file = Path("data/.seen_urls.json")

    seen: set[str] = set()
    if seen_file.exists():
        try:
            seen = set(json.loads(seen_file.read_text(encoding="utf-8")))
        except Exception:
            seen = set()

    crawled: list[Article] = []

    for cat in categories:
        if len(crawled) >= max_articles_total:
            break
        logger.info("--- Starting archive category: %s ---", cat)

        for page in range(0, max_pages_per_category):
            if len(crawled) >= max_articles_total:
                break

            url = f"https://www.thedailystar.net/{cat}?page={page}"
            logger.info("Fetching index page %d: %s", page, url)

            try:
                resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                if resp.status_code != 200:
                    logger.warning("Index page %s returned HTTP %d", url, resp.status_code)
                    break
            except Exception as e:
                logger.error("Failed to fetch index %s: %s", url, e)
                break

            soup = BeautifulSoup(resp.text, "html.parser") if BeautifulSoup else None
            page_links = []

            if soup:
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if re.search(r"/(news/|crime-justice/|bangladesh/)", href) and re.search(r"-\d+$", href):
                        full = href if href.startswith("http") else "https://www.thedailystar.net" + href
                        if full not in seen and full not in page_links:
                            title = _clean_text(a.get_text()) or ""
                            page_links.append((full, title))

            logger.info("Found %d new article links on page %d", len(page_links), page)
            if not page_links:
                continue

            for art_url, art_title in page_links:
                if len(crawled) >= max_articles_total:
                    break
                stub = Article(
                    url=art_url,
                    title=art_title,
                    category=cat,
                    source="thedailystar.net",
                )
                try:
                    full_art = fetch_article(stub, rate_limit_s=rate_limit_s)
                    if full_art.body and len(full_art.body) > 100:
                        crawled.append(full_art)
                        seen.add(art_url)

                        if save_raw:
                            date_str = (full_art.published_date or full_art.scraped_at)[:10]
                            slug = hashlib.md5(art_url.encode()).hexdigest()[:12]
                            target_path = raw_dir / date_str / f"{slug}.json"
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            target_path.write_text(full_art.to_json(), encoding="utf-8")

                        logger.info("Crawled [%d/%d]: %s", len(crawled), max_articles_total, full_art.title[:60])
                except Exception as e:
                    logger.warning("Error fetching %s: %s", art_url, e)

            # Checkpoint seen file after every index page
            seen_file.parent.mkdir(parents=True, exist_ok=True)
            seen_file.write_text(json.dumps(sorted(seen), indent=2), encoding="utf-8")
            time.sleep(rate_limit_s)

    logger.info("Archive crawling complete. Total new articles: %d", len(crawled))
    return crawled


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    import json
    import sys
    from pathlib import Path

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )

    parser = argparse.ArgumentParser(description="Daily Star Article Crawler")
    parser.add_argument("--archive", action="store_true", help="Crawl archive sections")
    parser.add_argument("--max-pages", type=int, default=5, help="Max pages per category")
    parser.add_argument("--max-articles", type=int, default=100, help="Max total articles")
    parser.add_argument("--rate-limit", type=float, default=0.3, help="Rate limit delay in seconds")
    parser.add_argument("stub", nargs="?", help="Optional article stub JSON path")

    args = parser.parse_args()

    if args.archive:
        crawl_archive(
            max_pages_per_category=args.max_pages,
            max_articles_total=args.max_articles,
            rate_limit_s=args.rate_limit,
        )
    elif args.stub:
        stub_path = Path(args.stub)
        article = Article.from_json(stub_path.read_text(encoding="utf-8"))
        article = fetch_article(article)
        out_path = stub_path.with_stem(stub_path.stem + "_full")
        out_path.write_text(article.to_json(), encoding="utf-8")
        print(f"Saved to {out_path}")
        print(f"Body preview:\n{article.body[:500]}")
    else:
        parser.print_help()
