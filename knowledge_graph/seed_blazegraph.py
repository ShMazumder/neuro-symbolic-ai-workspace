#!/usr/bin/env python3
"""
knowledge_graph/seed_blazegraph.py
Task 1.9 — Seed BlazeGraph with CAMEO ontologies + sample triples.

Usage:
    python -m knowledge_graph.seed_blazegraph [--endpoint URL] [--dry-run]
"""

import argparse
import logging
import sys
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

BLAZEGRAPH_ENDPOINT = "http://localhost:9999/blazegraph/sparql"
ONTOLOGY_DIR = Path("ontology")

TTL_FILES = [
    ONTOLOGY_DIR / "cameo_base.ttl",
    ONTOLOGY_DIR / "cameo_bd_extension.ttl",
    ONTOLOGY_DIR / "event_schema.ttl",
]


def blazegraph_status(endpoint: str) -> bool:
    """Return True if BlazeGraph is reachable."""
    status_url = endpoint.replace("/sparql", "/status")
    try:
        resp = requests.get(status_url, timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def ingest_turtle(endpoint: str, ttl_path: Path, dry_run: bool = False) -> bool:
    """
    POST a Turtle file to BlazeGraph via the SPARQL update endpoint.

    Returns True on success.
    """
    if not ttl_path.exists():
        logger.error("File not found: %s", ttl_path)
        return False

    content = ttl_path.read_text(encoding="utf-8")
    logger.info("Ingesting %s (%d bytes)…", ttl_path.name, len(content))

    if dry_run:
        logger.info("[DRY RUN] Would POST %s to %s", ttl_path.name, endpoint)
        return True

    try:
        resp = requests.post(
            endpoint,
            data=content.encode("utf-8"),
            headers={"Content-Type": "application/x-turtle"},
            timeout=60,
        )
        if resp.status_code in (200, 204):
            logger.info("✓  %s ingested successfully.", ttl_path.name)
            return True
        else:
            logger.error("✗  %s failed: HTTP %d — %s", ttl_path.name, resp.status_code, resp.text[:200])
            return False
    except requests.RequestException as exc:
        logger.error("✗  %s failed: %s", ttl_path.name, exc)
        return False


def sparql_smoke_test(endpoint: str) -> bool:
    """Run a simple SPARQL query to verify triples were loaded."""
    query = """
    SELECT (COUNT(*) AS ?triples)
    WHERE { ?s ?p ?o }
    """
    try:
        resp = requests.post(
            endpoint,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            count = data["results"]["bindings"][0]["triples"]["value"]
            logger.info("✓  SPARQL smoke test passed — %s triples in store.", count)
            return True
        else:
            logger.error("✗  SPARQL smoke test failed: HTTP %d", resp.status_code)
            return False
    except Exception as exc:
        logger.error("✗  SPARQL smoke test error: %s", exc)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed BlazeGraph with CAMEO ontologies.")
    parser.add_argument("--endpoint", default=BLAZEGRAPH_ENDPOINT, help="BlazeGraph SPARQL endpoint URL")
    parser.add_argument("--dry-run", action="store_true", help="Parse files but do not POST to BlazeGraph")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
    )

    # 1. Check connectivity
    if not args.dry_run:
        logger.info("Checking BlazeGraph at %s…", args.endpoint)
        if not blazegraph_status(args.endpoint):
            logger.error(
                "BlazeGraph not reachable at %s. "
                "Start it with: docker-compose -f docker/docker-compose.yml up -d",
                args.endpoint,
            )
            return 1
        logger.info("✓  BlazeGraph is up.")

    # 2. Ingest each TTL file
    success = True
    for ttl in TTL_FILES:
        if not ingest_turtle(args.endpoint, ttl, dry_run=args.dry_run):
            success = False

    # 3. Smoke test
    if not args.dry_run and success:
        sparql_smoke_test(args.endpoint)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
