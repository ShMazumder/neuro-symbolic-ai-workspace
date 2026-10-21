"""
knowledge_graph/ingest.py
Task 3.2 — BlazeGraph bulk ingest via REST API.

Supports:
  - Single Turtle/N-Triples string POST
  - Batch file ingest with chunking
  - SPARQL UPDATE (INSERT DATA)
  - Named graph (context) support
  - Retry logic with exponential back-off
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

import requests
from rdflib import Graph

logger = logging.getLogger(__name__)

# ── Default config ────────────────────────────────────────────────────────────

SPARQL_ENDPOINT   = "http://localhost:9999/blazegraph/sparql"
STATUS_ENDPOINT   = "http://localhost:9999/blazegraph/status"
NAMESPACE_ENDPOINT = "http://localhost:9999/blazegraph/namespace"

DEFAULT_NAMESPACE = "kb"
CHUNK_SIZE        = 500        # triples per POST
MAX_RETRIES       = 3
BACKOFF_BASE      = 2.0        # seconds


# ── Connectivity ──────────────────────────────────────────────────────────────

def is_alive(endpoint: str = STATUS_ENDPOINT, timeout: int = 5) -> bool:
    """Return True if BlazeGraph is reachable."""
    try:
        r = requests.get(endpoint, timeout=timeout)
        return r.status_code == 200
    except requests.RequestException:
        return False


def wait_for_blazegraph(
    endpoint: str = STATUS_ENDPOINT,
    max_wait: int = 60,
    poll_interval: int = 3,
) -> bool:
    """Poll until BlazeGraph is ready or timeout. Returns True on success."""
    logger.info("Waiting for BlazeGraph at %s…", endpoint)
    start = time.time()
    while time.time() - start < max_wait:
        if is_alive(endpoint):
            logger.info("BlazeGraph is ready.")
            return True
        time.sleep(poll_interval)
    logger.error("BlazeGraph did not become ready within %ds.", max_wait)
    return False


# ── Core POST ingest ──────────────────────────────────────────────────────────

def post_turtle(
    content: str,
    endpoint: str = SPARQL_ENDPOINT,
    context_uri: Optional[str] = None,
    content_type: str = "application/x-turtle",
) -> bool:
    """
    POST RDF content to BlazeGraph.

    Args:
        content:      Turtle or N-Triples string.
        endpoint:     SPARQL endpoint URL.
        context_uri:  Named graph URI (optional).
        content_type: MIME type of content.

    Returns:
        True on success.
    """
    params = {}
    if context_uri:
        params["context-uri"] = context_uri

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(
                endpoint,
                params=params,
                data=content.encode("utf-8"),
                headers={"Content-Type": content_type},
                timeout=120,
            )
            if r.status_code in (200, 204):
                return True
            logger.warning(
                "Attempt %d: HTTP %d — %s",
                attempt, r.status_code, r.text[:200],
            )
        except requests.RequestException as exc:
            logger.warning("Attempt %d: Request error — %s", attempt, exc)

        if attempt < MAX_RETRIES:
            sleep = BACKOFF_BASE ** attempt
            logger.info("Retrying in %.1fs…", sleep)
            time.sleep(sleep)

    logger.error("All %d retries exhausted.", MAX_RETRIES)
    return False


def post_graph(
    g: Graph,
    endpoint: str = SPARQL_ENDPOINT,
    context_uri: Optional[str] = None,
    fmt: str = "nt",
) -> bool:
    """
    Serialize and POST an rdflib Graph to BlazeGraph.

    Uses N-Triples (faster than Turtle for large graphs).
    """
    content = g.serialize(format=fmt)
    mime = "application/n-triples" if fmt == "nt" else "application/x-turtle"
    logger.info("Ingesting graph (%d triples)…", len(g))
    ok = post_turtle(content, endpoint=endpoint,
                     context_uri=context_uri, content_type=mime)
    if ok:
        logger.info("✓ Ingested %d triples.", len(g))
    return ok


# ── Chunked ingest ────────────────────────────────────────────────────────────

def post_graph_chunked(
    g: Graph,
    endpoint: str = SPARQL_ENDPOINT,
    chunk_size: int = CHUNK_SIZE,
    context_uri: Optional[str] = None,
) -> tuple[int, int]:
    """
    Ingest a large graph in N-Triple chunks.

    Returns:
        (success_count, fail_count) chunk counts.
    """
    nt_lines = g.serialize(format="nt").strip().splitlines()
    total_chunks = (len(nt_lines) + chunk_size - 1) // chunk_size
    success = fail = 0

    for i in range(0, len(nt_lines), chunk_size):
        chunk = "\n".join(nt_lines[i: i + chunk_size])
        chunk_num = i // chunk_size + 1
        logger.info("Chunk %d/%d (%d triples)…", chunk_num, total_chunks, len(nt_lines[i:i+chunk_size]))
        ok = post_turtle(
            chunk,
            endpoint=endpoint,
            context_uri=context_uri,
            content_type="application/n-triples",
        )
        if ok:
            success += 1
        else:
            fail += 1

    logger.info("Chunked ingest complete. %d/%d chunks succeeded.", success, total_chunks)
    return success, fail


# ── File-based ingest ─────────────────────────────────────────────────────────

def ingest_file(
    path: Path,
    endpoint: str = SPARQL_ENDPOINT,
    context_uri: Optional[str] = None,
) -> bool:
    """
    Load a Turtle/N-Triples file and POST to BlazeGraph.
    """
    suffix = path.suffix.lower()
    if suffix in (".ttl", ".turtle"):
        content_type = "application/x-turtle"
    elif suffix in (".nt", ".ntriples"):
        content_type = "application/n-triples"
    elif suffix in (".rdf", ".xml"):
        content_type = "application/rdf+xml"
    else:
        logger.warning("Unknown file extension %s — assuming Turtle.", suffix)
        content_type = "application/x-turtle"

    content = path.read_text(encoding="utf-8")
    logger.info("Ingesting %s (%d bytes)…", path.name, len(content))
    return post_turtle(content, endpoint=endpoint,
                       context_uri=context_uri, content_type=content_type)


def ingest_directory(
    directory: Path,
    endpoint: str = SPARQL_ENDPOINT,
    patterns: list[str] = ("*.ttl", "*.nt"),
) -> tuple[int, int]:
    """
    Ingest all RDF files in a directory.

    Returns:
        (success_count, fail_count)
    """
    files = []
    for pattern in patterns:
        files.extend(directory.glob(pattern))
    files = sorted(set(files))

    success = fail = 0
    for f in files:
        ok = ingest_file(f, endpoint=endpoint)
        if ok:
            success += 1
        else:
            fail += 1

    logger.info("Directory ingest: %d ok, %d failed.", success, fail)
    return success, fail


# ── SPARQL UPDATE helper ──────────────────────────────────────────────────────

def sparql_update(
    query: str,
    endpoint: str = SPARQL_ENDPOINT,
) -> bool:
    """Execute a SPARQL UPDATE query."""
    try:
        r = requests.post(
            endpoint,
            data={"update": query},
            timeout=60,
        )
        if r.status_code in (200, 204):
            return True
        logger.error("SPARQL UPDATE failed: HTTP %d — %s", r.status_code, r.text[:200])
        return False
    except requests.RequestException as exc:
        logger.error("SPARQL UPDATE error: %s", exc)
        return False


def sparql_query(
    query: str,
    endpoint: str = SPARQL_ENDPOINT,
    fmt: str = "application/sparql-results+json",
) -> Optional[dict]:
    """Execute a SPARQL SELECT query and return parsed JSON."""
    try:
        r = requests.post(
            endpoint,
            data={"query": query},
            headers={"Accept": fmt},
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()
        logger.error("SPARQL query failed: HTTP %d", r.status_code)
        return None
    except requests.RequestException as exc:
        logger.error("SPARQL query error: %s", exc)
        return None


# ── Triple count ──────────────────────────────────────────────────────────────

def get_triple_count(endpoint: str = SPARQL_ENDPOINT) -> Optional[int]:
    """Return total triple count from BlazeGraph."""
    result = sparql_query("SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }", endpoint)
    if result:
        try:
            return int(result["results"]["bindings"][0]["n"]["value"])
        except (KeyError, IndexError, ValueError):
            pass
    return None


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s")

    if not is_alive():
        print("BlazeGraph not running. Start: docker-compose -f docker/docker-compose.yml up -d")
        sys.exit(1)

    processed_dir = Path("data/processed")
    ttl_files = list(processed_dir.glob("*.ttl"))

    if not ttl_files:
        print(f"No .ttl files found in {processed_dir}. Run rdf_generator first.")
        sys.exit(1)

    ok, fail = ingest_directory(processed_dir)
    count = get_triple_count()
    print(f"Ingest complete. {ok} files ok, {fail} failed. Total triples: {count}")
