"""
knowledge_graph/graph_stats.py
Task 3.7 — Graph statistics report.

Queries BlazeGraph and produces a structured statistics report covering:
  - Total triples, events, actors, locations
  - CAMEO code distribution
  - Temporal coverage
  - Top districts and top actors
  - Data quality metrics (confidence distribution, missing fields)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from knowledge_graph.ingest import sparql_query, get_triple_count, is_alive, SPARQL_ENDPOINT

logger = logging.getLogger(__name__)


# ── Queries ───────────────────────────────────────────────────────────────────

_Q_EVENT_COUNT = """
PREFIX cameo: <http://example.org/cameo/>
SELECT (COUNT(DISTINCT ?e) AS ?n)
WHERE { ?e a cameo:ViolenceEvent }
"""

_Q_ACTOR_COUNT = """
PREFIX cameo: <http://example.org/cameo/>
SELECT (COUNT(DISTINCT ?a) AS ?n)
WHERE { ?a a cameo:Actor }
"""

_Q_LOCATION_COUNT = """
PREFIX cameo: <http://example.org/cameo/>
SELECT (COUNT(DISTINCT ?l) AS ?n)
WHERE { ?l a cameo:Location }
"""

_Q_ARTICLE_COUNT = """
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT (COUNT(DISTINCT ?a) AS ?n)
WHERE { ?a a prov:Entity }
"""

_Q_CAMEO_DIST = """
PREFIX cameo: <http://example.org/cameo/>
SELECT ?code ?label (COUNT(DISTINCT ?e) AS ?count)
WHERE {
  ?e a cameo:ViolenceEvent ;
     cameo:code  ?code ;
     cameo:label ?label .
}
GROUP BY ?code ?label
ORDER BY DESC(?count)
LIMIT 20
"""

_Q_TOP_DISTRICTS = """
PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(DISTINCT ?e) AS ?count)
WHERE {
  ?e a cameo:ViolenceEvent ;
     cameo:location ?l .
  ?l cameo:district ?district .
}
GROUP BY ?district
ORDER BY DESC(?count)
LIMIT 10
"""

_Q_TOP_ACTORS = """
PREFIX cameo: <http://example.org/cameo/>
SELECT ?name ?type (COUNT(DISTINCT ?e) AS ?count)
WHERE {
  { ?e cameo:actor ?a } UNION { ?e cameo:target ?a }
  ?a cameo:actorName ?name ;
     cameo:actorType ?type .
  ?e a cameo:ViolenceEvent .
}
GROUP BY ?name ?type
ORDER BY DESC(?count)
LIMIT 15
"""

_Q_TEMPORAL_RANGE = """
PREFIX cameo: <http://example.org/cameo/>
SELECT (MIN(?d) AS ?earliest) (MAX(?d) AS ?latest)
WHERE {
  ?e a cameo:ViolenceEvent ;
     cameo:date ?d .
}
"""

_Q_MONTHLY_TREND = """
PREFIX cameo: <http://example.org/cameo/>
SELECT ?month (COUNT(DISTINCT ?e) AS ?count)
WHERE {
  ?e a cameo:ViolenceEvent ;
     cameo:date ?d .
  BIND(SUBSTR(STR(?d), 1, 7) AS ?month)
}
GROUP BY ?month
ORDER BY ?month
"""

_Q_CONF_BUCKETS = """
PREFIX cameo: <http://example.org/cameo/>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
SELECT
  (COUNT(DISTINCT ?e) AS ?total)
  (SUM(IF(?conf >= 0.8,  1, 0)) AS ?high)
  (SUM(IF(?conf >= 0.6 && ?conf < 0.8, 1, 0)) AS ?medium)
  (SUM(IF(?conf < 0.6,  1, 0)) AS ?low)
WHERE {
  ?e a cameo:ViolenceEvent ;
     cameo:confidence ?conf .
}
"""

_Q_BD_CODES = """
PREFIX event:    <http://example.org/event/>
PREFIX cameo:    <http://example.org/cameo/>
SELECT ?bdCode (COUNT(DISTINCT ?e) AS ?count)
WHERE {
  ?e a cameo:ViolenceEvent ;
     event:bdExtensionCode ?bdCode .
}
GROUP BY ?bdCode
ORDER BY DESC(?count)
"""


# ── Stats collector ───────────────────────────────────────────────────────────

def _scalar(result: Optional[dict], var: str = "n") -> Optional[int]:
    """Extract a single integer scalar from a SPARQL result."""
    if not result:
        return None
    try:
        return int(result["results"]["bindings"][0][var]["value"])
    except (KeyError, IndexError, ValueError):
        return None


def _rows(result: Optional[dict]) -> list[dict]:
    """Extract rows from a SPARQL result as list of {var: value} dicts."""
    if not result:
        return []
    return [
        {k: v["value"] for k, v in row.items()}
        for row in result.get("results", {}).get("bindings", [])
    ]


def collect_stats(endpoint: str = SPARQL_ENDPOINT) -> dict:
    """
    Run all statistics queries against BlazeGraph and return a structured dict.
    """
    stats: dict = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endpoint": endpoint,
    }

    # ── Counts ────────────────────────────────────────────────────────────────
    stats["total_triples"]   = get_triple_count(endpoint)
    stats["total_events"]    = _scalar(sparql_query(_Q_EVENT_COUNT,    endpoint))
    stats["total_actors"]    = _scalar(sparql_query(_Q_ACTOR_COUNT,    endpoint))
    stats["total_locations"] = _scalar(sparql_query(_Q_LOCATION_COUNT, endpoint))
    stats["total_articles"]  = _scalar(sparql_query(_Q_ARTICLE_COUNT,  endpoint))

    # ── CAMEO distribution ────────────────────────────────────────────────────
    stats["cameo_distribution"] = _rows(sparql_query(_Q_CAMEO_DIST, endpoint))

    # ── BD extension code distribution ────────────────────────────────────────
    stats["bd_code_distribution"] = _rows(sparql_query(_Q_BD_CODES, endpoint))

    # ── Top districts ─────────────────────────────────────────────────────────
    stats["top_districts"] = _rows(sparql_query(_Q_TOP_DISTRICTS, endpoint))

    # ── Top actors ────────────────────────────────────────────────────────────
    stats["top_actors"] = _rows(sparql_query(_Q_TOP_ACTORS, endpoint))

    # ── Temporal range ────────────────────────────────────────────────────────
    tr = _rows(sparql_query(_Q_TEMPORAL_RANGE, endpoint))
    if tr:
        stats["temporal_range"] = {
            "earliest": tr[0].get("earliest"),
            "latest":   tr[0].get("latest"),
        }

    # ── Monthly trend ─────────────────────────────────────────────────────────
    stats["monthly_trend"] = _rows(sparql_query(_Q_MONTHLY_TREND, endpoint))

    # ── Confidence distribution ───────────────────────────────────────────────
    conf = _rows(sparql_query(_Q_CONF_BUCKETS, endpoint))
    if conf:
        stats["confidence_distribution"] = conf[0]

    return stats


def print_report(stats: dict) -> None:
    """Pretty-print a stats report to stdout."""
    print("=" * 60)
    print("  KNOWLEDGE GRAPH STATISTICS REPORT")
    print(f"  Generated: {stats.get('generated_at', 'N/A')}")
    print("=" * 60)
    print(f"  Total triples:   {stats.get('total_triples', '?'):>10}")
    print(f"  Events:          {stats.get('total_events',  '?'):>10}")
    print(f"  Actors:          {stats.get('total_actors',  '?'):>10}")
    print(f"  Locations:       {stats.get('total_locations','?'):>10}")
    print(f"  Source articles: {stats.get('total_articles','?'):>10}")

    tr = stats.get("temporal_range", {})
    if tr:
        print(f"\n  Date range: {tr.get('earliest','?')} → {tr.get('latest','?')}")

    print("\n  TOP CAMEO CODES:")
    for row in stats.get("cameo_distribution", [])[:10]:
        print(f"    {row.get('code','?'):>5}  {row.get('label','?'):<40}  {row.get('count','?'):>6}")

    print("\n  BD EXTENSION CODES:")
    for row in stats.get("bd_code_distribution", []):
        print(f"    {row.get('bdCode','?'):<8}  {row.get('count','?'):>6}")

    print("\n  TOP DISTRICTS:")
    for row in stats.get("top_districts", []):
        print(f"    {row.get('district','?'):<20}  {row.get('count','?'):>6}")

    print("\n  TOP ACTORS:")
    for row in stats.get("top_actors", []):
        print(f"    {row.get('name','?'):<30} [{row.get('type','?')}]  {row.get('count','?'):>5}")

    conf = stats.get("confidence_distribution", {})
    if conf:
        print(f"\n  CONFIDENCE: high={conf.get('high','?')}  "
              f"medium={conf.get('medium','?')}  low={conf.get('low','?')}")
    print("=" * 60)


def save_stats(stats: dict, path: Path) -> None:
    """Save stats as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Stats saved to %s", path)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s")

    if not is_alive():
        print("BlazeGraph not running.")
        sys.exit(1)

    stats = collect_stats()
    print_report(stats)
    save_stats(stats, Path("data/graph_stats.json"))
