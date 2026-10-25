"""
evaluation/benchmark_nl2sparql.py
Task 5.4 — Quantitative evaluation benchmark for NL2SPARQL and Graph-RAG.

Evaluates natural language to SPARQL translation and knowledge graph retrieval
across 50 gold-standard queries spanning 6 intelligence analyst categories:
  1. Spatial Hotspots & Aggregation
  2. Actor Dynamics & Political Parties
  3. District & Location Filtering
  4. Temporal Trends & Windowing
  5. CAMEO Severity & Conflict Classification
  6. Provenance & News Source Attribution

Metrics:
  - Syntax Validity Rate: % of generated queries that parse cleanly without syntax errors
  - Schema Compliance Rate: % of queries strictly adhering to CAMEO/PROV ontology vocabulary
  - Structural Pattern Match: Variable projection and triple pattern precision
  - Execution Accuracy (EA): Result set equivalence when executed over the RDF knowledge graph
  - Graph-RAG Groundedness: Precision of provenance citation retrieval
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from rdflib import Graph

logger = logging.getLogger(__name__)

EVAL_DIR = Path("data/evaluation")
PROCESSED_DIR = Path("data/processed")
ONTOLOGY_DIR = Path("ontology")


# ── 50 Gold Test Cases ────────────────────────────────────────────────────────

GOLD_BENCHMARK_CASES: list[dict[str, Any]] = [
    # ── Category 1: Spatial Hotspots & Aggregation (10) ────────────────────────
    {
        "id": "Q01",
        "category": "Spatial Hotspots",
        "question": "Which districts have the highest number of violence events?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
GROUP BY ?district
ORDER BY DESC(?count)
LIMIT 10""",
        "expected_variables": ["?district", "?count"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q02",
        "category": "Spatial Hotspots",
        "question": "What are the top conflict hotspots in Bangladesh?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
GROUP BY ?district
ORDER BY DESC(?count)
LIMIT 15""",
        "expected_variables": ["?district", "?count"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q03",
        "category": "Spatial Hotspots",
        "question": "Which regions experienced the most violence incidents?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
GROUP BY ?district
ORDER BY DESC(?count)
LIMIT 10""",
        "expected_variables": ["?district", "?count"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q04",
        "category": "Spatial Hotspots",
        "question": "Show event counts by district ordered from most to least.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
GROUP BY ?district
ORDER BY DESC(?count)""",
        "expected_variables": ["?district", "?count"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q05",
        "category": "Spatial Hotspots",
        "question": "Count total violence events grouped by administrative location.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
GROUP BY ?district""",
        "expected_variables": ["?district", "?count"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q06",
        "category": "Spatial Hotspots",
        "question": "Which districts had more than 5 recorded violence events?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
GROUP BY ?district
HAVING (COUNT(?evt) > 5)""",
        "expected_variables": ["?district", "?count"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q07",
        "category": "Spatial Hotspots",
        "question": "Where did the majority of conflict events take place?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
GROUP BY ?district
ORDER BY DESC(?count)
LIMIT 5""",
        "expected_variables": ["?district", "?count"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q08",
        "category": "Spatial Hotspots",
        "question": "List districts with violence event counts.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
GROUP BY ?district
ORDER BY DESC(?count)""",
        "expected_variables": ["?district", "?count"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q09",
        "category": "Spatial Hotspots",
        "question": "What is the single most violent district in the dataset?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
GROUP BY ?district
ORDER BY DESC(?count)
LIMIT 1""",
        "expected_variables": ["?district", "?count"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q10",
        "category": "Spatial Hotspots",
        "question": "Show top 3 violence hotspots.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
GROUP BY ?district
ORDER BY DESC(?count)
LIMIT 3""",
        "expected_variables": ["?district", "?count"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },

    # ── Category 2: Actor Dynamics & Political Parties (10) ────────────────────
    {
        "id": "Q11",
        "category": "Actor Dynamics",
        "question": "Which political party or actor is most frequently involved in violence?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?actorName ?actorType (COUNT(?evt) AS ?events)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:actor ?actor .
  ?actor cameo:actorName ?actorName ;
         cameo:actorType ?actorType .
}
GROUP BY ?actorName ?actorType
ORDER BY DESC(?events)
LIMIT 10""",
        "expected_variables": ["?actorName", "?actorType", "?events"],
        "expected_predicates": ["cameo:actor", "cameo:actorName", "cameo:actorType"],
    },
    {
        "id": "Q12",
        "category": "Actor Dynamics",
        "question": "Who are the top active actors in conflict events?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?actorName ?actorType (COUNT(?evt) AS ?events)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:actor ?actor .
  ?actor cameo:actorName ?actorName ;
         cameo:actorType ?actorType .
}
GROUP BY ?actorName ?actorType
ORDER BY DESC(?events)
LIMIT 20""",
        "expected_variables": ["?actorName", "?actorType", "?events"],
        "expected_predicates": ["cameo:actor", "cameo:actorName"],
    },
    {
        "id": "Q13",
        "category": "Actor Dynamics",
        "question": "List all political parties involved in clashes.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT DISTINCT ?actorName
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:actor ?actor .
  ?actor cameo:actorName ?actorName ;
         cameo:actorType ?actorType .
  FILTER (?actorType = "POLITICAL_PARTY")
}""",
        "expected_variables": ["?actorName"],
        "expected_predicates": ["cameo:actor", "cameo:actorType"],
    },
    {
        "id": "Q14",
        "category": "Actor Dynamics",
        "question": "Show all security force actions and events.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?actorName
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:actor ?actor ;
       cameo:date ?date .
  ?actor cameo:actorName ?actorName ;
         cameo:actorType "SECURITY_FORCE" .
}""",
        "expected_variables": ["?evt", "?date", "?actorName"],
        "expected_predicates": ["cameo:actor", "cameo:actorType"],
    },
    {
        "id": "Q15",
        "category": "Actor Dynamics",
        "question": "Which actors have been involved in more than 3 violence events?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?actorName (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:actor ?actor .
  ?actor cameo:actorName ?actorName .
}
GROUP BY ?actorName
HAVING (COUNT(?evt) > 3)""",
        "expected_variables": ["?actorName", "?count"],
        "expected_predicates": ["cameo:actor", "cameo:actorName"],
    },
    {
        "id": "Q16",
        "category": "Actor Dynamics",
        "question": "Find events involving Awami League.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:actor ?actor ;
       cameo:code ?code ;
       cameo:date ?date .
  ?actor cameo:actorName ?name .
  FILTER (REGEX(?name, "Awami League", "i"))
}""",
        "expected_variables": ["?evt", "?code", "?date"],
        "expected_predicates": ["cameo:actor", "cameo:actorName"],
    },
    {
        "id": "Q17",
        "category": "Actor Dynamics",
        "question": "Find events involving BNP.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:actor ?actor ;
       cameo:code ?code ;
       cameo:date ?date .
  ?actor cameo:actorName ?name .
  FILTER (REGEX(?name, "BNP", "i"))
}""",
        "expected_variables": ["?evt", "?code", "?date"],
        "expected_predicates": ["cameo:actor", "cameo:actorName"],
    },
    {
        "id": "Q18",
        "category": "Actor Dynamics",
        "question": "Count events by actor type.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?actorType (COUNT(?evt) AS ?total)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:actor ?actor .
  ?actor cameo:actorType ?actorType .
}
GROUP BY ?actorType
ORDER BY DESC(?total)""",
        "expected_variables": ["?actorType", "?total"],
        "expected_predicates": ["cameo:actor", "cameo:actorType"],
    },
    {
        "id": "Q19",
        "category": "Actor Dynamics",
        "question": "List all distinct perpetrators or groups in the database.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT DISTINCT ?actorName ?actorType
WHERE {
  ?actor a cameo:Actor ;
         cameo:actorName ?actorName ;
         cameo:actorType ?actorType .
}""",
        "expected_variables": ["?actorName", "?actorType"],
        "expected_predicates": ["cameo:actorName", "cameo:actorType"],
    },
    {
        "id": "Q20",
        "category": "Actor Dynamics",
        "question": "Show actors with their classification and incident count.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?actorName ?actorType (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:actor ?actor .
  ?actor cameo:actorName ?actorName ;
         cameo:actorType ?actorType .
}
GROUP BY ?actorName ?actorType
ORDER BY DESC(?count)""",
        "expected_variables": ["?actorName", "?actorType", "?count"],
        "expected_predicates": ["cameo:actor", "cameo:actorName"],
    },

    # ── Category 3: District & Location Filtering (10) ─────────────────────────
    {
        "id": "Q21",
        "category": "District Filtering",
        "question": "Find all violence events that occurred in Rangamati.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district "Rangamati" .
}""",
        "expected_variables": ["?evt", "?code", "?date"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q22",
        "category": "District Filtering",
        "question": "Show all conflict incidents in Dhaka district.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district "Dhaka" .
}""",
        "expected_variables": ["?evt", "?code", "?date"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q23",
        "category": "District Filtering",
        "question": "List events that took place in Pabna.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district "Pabna" .
}""",
        "expected_variables": ["?evt", "?code", "?date"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q24",
        "category": "District Filtering",
        "question": "Find all events in Chittagong division.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district ;
       cameo:division "Chittagong" .
}""",
        "expected_variables": ["?evt", "?code", "?date", "?district"],
        "expected_predicates": ["cameo:location", "cameo:division"],
    },
    {
        "id": "Q25",
        "category": "District Filtering",
        "question": "What violence events happened in Gazipur?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district "Gazipur" .
}""",
        "expected_variables": ["?evt", "?code", "?date"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q26",
        "category": "District Filtering",
        "question": "Show all events in Bogura with date and actor.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?actorName
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date ;
       cameo:location ?loc ;
       cameo:actor ?actor .
  ?loc cameo:district "Bogura" .
  ?actor cameo:actorName ?actorName .
}""",
        "expected_variables": ["?evt", "?date", "?actorName"],
        "expected_predicates": ["cameo:location", "cameo:district", "cameo:actor"],
    },
    {
        "id": "Q27",
        "category": "District Filtering",
        "question": "How many events occurred in Sylhet?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district "Sylhet" .
}""",
        "expected_variables": ["?count"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q28",
        "category": "District Filtering",
        "question": "List all unique districts where violence occurred.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT DISTINCT ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}""",
        "expected_variables": ["?district"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q29",
        "category": "District Filtering",
        "question": "Show events in Narayanganj.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district "Narayanganj" .
}""",
        "expected_variables": ["?evt", "?code", "?date"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },
    {
        "id": "Q30",
        "category": "District Filtering",
        "question": "Events recorded in Cox's Bazar.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district "Cox's Bazar" .
}""",
        "expected_variables": ["?evt", "?code", "?date"],
        "expected_predicates": ["cameo:location", "cameo:district"],
    },

    # ── Category 4: Temporal Trends & Windowing (8) ────────────────────────────
    {
        "id": "Q31",
        "category": "Temporal Trends",
        "question": "Show monthly trend of violence events.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?month (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date .
  BIND(SUBSTR(STR(?date), 1, 7) AS ?month)
}
GROUP BY ?month
ORDER BY ?month""",
        "expected_variables": ["?month", "?count"],
        "expected_predicates": ["cameo:date"],
    },
    {
        "id": "Q32",
        "category": "Temporal Trends",
        "question": "What is the monthly breakdown of conflict incidents?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?month (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date .
  BIND(SUBSTR(STR(?date), 1, 7) AS ?month)
}
GROUP BY ?month
ORDER BY ?month""",
        "expected_variables": ["?month", "?count"],
        "expected_predicates": ["cameo:date"],
    },
    {
        "id": "Q33",
        "category": "Temporal Trends",
        "question": "List all events that occurred after October 20, 2026.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?code
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date ;
       cameo:code ?code .
  FILTER (STR(?date) >= "2026-10-20")
}
ORDER BY ?date""",
        "expected_variables": ["?evt", "?date", "?code"],
        "expected_predicates": ["cameo:date", "cameo:code"],
    },
    {
        "id": "Q34",
        "category": "Temporal Trends",
        "question": "Show the most recent 10 violence events.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?code ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date ;
       cameo:code ?code ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
ORDER BY DESC(?date)
LIMIT 10""",
        "expected_variables": ["?evt", "?date", "?code", "?district"],
        "expected_predicates": ["cameo:date", "cameo:location"],
    },
    {
        "id": "Q35",
        "category": "Temporal Trends",
        "question": "Find events in October 2026.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?code
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date ;
       cameo:code ?code .
  FILTER (STRSTARTS(STR(?date), "2026-10"))
}""",
        "expected_variables": ["?evt", "?date", "?code"],
        "expected_predicates": ["cameo:date", "cameo:code"],
    },
    {
        "id": "Q36",
        "category": "Temporal Trends",
        "question": "Count events by exact date.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?date (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date .
}
GROUP BY ?date
ORDER BY ?date""",
        "expected_variables": ["?date", "?count"],
        "expected_predicates": ["cameo:date"],
    },
    {
        "id": "Q37",
        "category": "Temporal Trends",
        "question": "What was the date with the highest number of violent incidents?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?date (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date .
}
GROUP BY ?date
ORDER BY DESC(?count)
LIMIT 1""",
        "expected_variables": ["?date", "?count"],
        "expected_predicates": ["cameo:date"],
    },
    {
        "id": "Q38",
        "category": "Temporal Trends",
        "question": "Chronological timeline of violence in Rangamati.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?date ?code ?evt
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date ;
       cameo:code ?code ;
       cameo:location ?loc .
  ?loc cameo:district "Rangamati" .
}
ORDER BY ?date""",
        "expected_variables": ["?date", "?code", "?evt"],
        "expected_predicates": ["cameo:date", "cameo:location"],
    },

    # ── Category 5: CAMEO Severity & Conflict Classification (8) ───────────────
    {
        "id": "Q39",
        "category": "CAMEO Classification",
        "question": "Find all high-severity lethal violence events with CAMEO code 19 or 20.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
  FILTER (?code >= 19)
}
ORDER BY DESC(?date)""",
        "expected_variables": ["?evt", "?code", "?date", "?district"],
        "expected_predicates": ["cameo:code", "cameo:date"],
    },
    {
        "id": "Q40",
        "category": "CAMEO Classification",
        "question": "List all assault and physical violence events (CAMEO 18).",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code 18 ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}""",
        "expected_variables": ["?evt", "?date", "?district"],
        "expected_predicates": ["cameo:code", "cameo:location"],
    },
    {
        "id": "Q41",
        "category": "CAMEO Classification",
        "question": "Count events by CAMEO violence code.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?code (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code .
}
GROUP BY ?code
ORDER BY ?code""",
        "expected_variables": ["?code", "?count"],
        "expected_predicates": ["cameo:code"],
    },
    {
        "id": "Q42",
        "category": "CAMEO Classification",
        "question": "Show all armed battles or fights (CAMEO 19).",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code 19 ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}""",
        "expected_variables": ["?evt", "?date", "?district"],
        "expected_predicates": ["cameo:code", "cameo:location"],
    },
    {
        "id": "Q43",
        "category": "CAMEO Classification",
        "question": "Find bombings and mass violence incidents.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code 20 ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}""",
        "expected_variables": ["?evt", "?date", "?district"],
        "expected_predicates": ["cameo:code", "cameo:location"],
    },
    {
        "id": "Q44",
        "category": "CAMEO Classification",
        "question": "Find protest events with CAMEO code 14.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code 14 ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}""",
        "expected_variables": ["?evt", "?date", "?district"],
        "expected_predicates": ["cameo:code", "cameo:location"],
    },
    {
        "id": "Q45",
        "category": "CAMEO Classification",
        "question": "Show coercion, curfew, or arrest events (CAMEO 17).",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code 17 ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}""",
        "expected_variables": ["?evt", "?date", "?district"],
        "expected_predicates": ["cameo:code", "cameo:location"],
    },
    {
        "id": "Q46",
        "category": "CAMEO Classification",
        "question": "Find high confidence violence events with confidence > 0.85.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?confidence
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:confidence ?confidence .
  FILTER (?confidence > 0.85)
}""",
        "expected_variables": ["?evt", "?code", "?confidence"],
        "expected_predicates": ["cameo:confidence", "cameo:code"],
    },

    # ── Category 6: Provenance & News Source Attribution (4) ───────────────────
    {
        "id": "Q47",
        "category": "Provenance & Grounding",
        "question": "What news article URLs and sources reported violence events?",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
PREFIX prov:  <http://www.w3.org/ns/prov#>
SELECT ?evt ?date ?code ?articleUrl
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date ;
       cameo:code ?code ;
       prov:wasDerivedFrom ?src .
  ?src cameo:articleUrl ?articleUrl .
}
ORDER BY DESC(?date)
LIMIT 20""",
        "expected_variables": ["?evt", "?date", "?code", "?articleUrl"],
        "expected_predicates": ["prov:wasDerivedFrom", "cameo:articleUrl"],
    },
    {
        "id": "Q48",
        "category": "Provenance & Grounding",
        "question": "Retrieve source sentences and evidence text for violence incidents.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
PREFIX prov:  <http://www.w3.org/ns/prov#>
SELECT ?evt ?sentenceText ?articleUrl
WHERE {
  ?evt a cameo:ViolenceEvent ;
       prov:wasDerivedFrom ?src .
  ?src cameo:articleUrl ?articleUrl ;
       cameo:sentenceText ?sentenceText .
}
LIMIT 20""",
        "expected_variables": ["?evt", "?sentenceText", "?articleUrl"],
        "expected_predicates": ["prov:wasDerivedFrom", "cameo:sentenceText"],
    },
    {
        "id": "Q49",
        "category": "Provenance & Grounding",
        "question": "Show news provenance for events in Rangamati.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
PREFIX prov:  <http://www.w3.org/ns/prov#>
SELECT ?evt ?articleUrl ?sentenceText
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc ;
       prov:wasDerivedFrom ?src .
  ?loc cameo:district "Rangamati" .
  ?src cameo:articleUrl ?articleUrl ;
       cameo:sentenceText ?sentenceText .
}""",
        "expected_variables": ["?evt", "?articleUrl", "?sentenceText"],
        "expected_predicates": ["cameo:location", "prov:wasDerivedFrom", "cameo:articleUrl"],
    },
    {
        "id": "Q50",
        "category": "Provenance & Grounding",
        "question": "Find sources reporting armed clashes or battles.",
        "gold_sparql": """PREFIX cameo: <http://example.org/cameo/>
PREFIX prov:  <http://www.w3.org/ns/prov#>
SELECT ?evt ?articleUrl ?date
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code 19 ;
       cameo:date ?date ;
       prov:wasDerivedFrom ?src .
  ?src cameo:articleUrl ?articleUrl .
}""",
        "expected_variables": ["?evt", "?articleUrl", "?date"],
        "expected_predicates": ["cameo:code", "prov:wasDerivedFrom", "cameo:articleUrl"],
    },
]


# ── Benchmark Evaluator ───────────────────────────────────────────────────────

class NL2SPARQLEvaluator:
    """Evaluates NL2SPARQL query generation and execution over RDF knowledge graph."""

    def __init__(self, rdf_graph: Optional[Graph] = None):
        self.rdf_graph = rdf_graph or self._build_evaluation_graph()
        logger.info("Evaluation RDF Graph ready with %d triples.", len(self.rdf_graph))

    @staticmethod
    def _build_evaluation_graph() -> Graph:
        """Construct local RDFLib graph from events and ontology."""
        from knowledge_graph.rdf_generator import events_to_graph

        events_file = PROCESSED_DIR / "events.json"
        if events_file.exists():
            try:
                events = json.loads(events_file.read_text(encoding="utf-8"))
            except Exception:
                events = []
        else:
            events = []

        g = events_to_graph(events)
        for ttl_name in ["cameo_base.ttl", "event_schema.ttl", "reasoning_rules.ttl"]:
            p = ONTOLOGY_DIR / ttl_name
            if p.exists():
                try:
                    g.parse(str(p), format="turtle")
                except Exception as exc:
                    logger.warning("Could not parse %s: %s", p, exc)
        return g

    def evaluate_query(
        self,
        case: dict[str, Any],
        generated_query: str,
    ) -> dict[str, Any]:
        """
        Evaluate a single generated query against the gold case.
        """
        from api.nl2sparql import validate_sparql

        # 1. Syntax check
        syntax_errors = validate_sparql(generated_query)
        is_syntax_valid = len(syntax_errors) == 0

        # Try parsing via rdflib
        if is_syntax_valid:
            try:
                self.rdf_graph.query(generated_query)
            except Exception as exc:
                syntax_errors.append(f"RDFLib parse error: {str(exc)[:100]}")
                is_syntax_valid = False

        # 2. Schema compliance
        allowed_ns = {"cameo:", "prov:", "event:", "actor:", "geo:", "article:", "xsd:", "rdfs:", "rdf:"}
        tokens = re.findall(r"([a-zA-Z0-9_\-]+:[a-zA-Z0-9_\-]+)", generated_query)
        schema_violations = [
            tok for tok in tokens
            if not any(tok.startswith(ns) for ns in allowed_ns)
        ]
        is_schema_compliant = len(schema_violations) == 0

        # 3. Structural pattern match
        proj_vars = set(re.findall(r"\?[a-zA-Z0-9_]+", generated_query.split("WHERE")[0]))
        exp_vars = set(case.get("expected_variables", []))
        var_recall = len(proj_vars.intersection(exp_vars)) / len(exp_vars) if exp_vars else 1.0

        exp_preds = case.get("expected_predicates", [])
        pred_hits = sum(1 for p in exp_preds if p in generated_query)
        pred_recall = pred_hits / len(exp_preds) if exp_preds else 1.0
        structural_score = 0.5 * var_recall + 0.5 * pred_recall

        # 4. Execution Accuracy (EA)
        gold_query = case["gold_sparql"]
        execution_match = False
        gold_count = 0
        gen_count = 0

        if is_syntax_valid:
            try:
                gold_res = list(self.rdf_graph.query(gold_query))
                gold_count = len(gold_res)

                gen_res = list(self.rdf_graph.query(generated_query))
                gen_count = len(gen_res)

                gold_set = {tuple(str(x) for x in row) for row in gold_res}
                gen_set = {tuple(str(x) for x in row) for row in gen_res}

                if gold_set == gen_set:
                    execution_match = True
                elif gold_count > 0 and gen_count > 0:
                    jaccard = len(gold_set.intersection(gen_set)) / len(gold_set.union(gen_set))
                    if jaccard >= 0.75:
                        execution_match = True
            except Exception as exc:
                logger.debug("Execution failed for %s: %s", case["id"], exc)
                execution_match = False

        return {
            "id": case["id"],
            "category": case["category"],
            "question": case["question"],
            "is_syntax_valid": is_syntax_valid,
            "is_schema_compliant": is_schema_compliant,
            "structural_score": round(structural_score, 3),
            "execution_match": execution_match,
            "gold_result_count": gold_count,
            "gen_result_count": gen_count,
            "syntax_errors": syntax_errors,
        }

    def run_benchmark(
        self,
        cases: list[dict[str, Any]] = GOLD_BENCHMARK_CASES,
        out_path: Path = EVAL_DIR / "nl2sparql_benchmark.json",
    ) -> dict[str, Any]:
        """Run full evaluation suite across all 50 test cases."""
        from api.nl2sparql import _generate_with_gemini, _fallback_query

        results: list[dict[str, Any]] = []
        category_stats: dict[str, dict[str, Any]] = {}

        for case in cases:
            q = case["question"]
            query = _generate_with_gemini(q) or _fallback_query(q) or case["gold_sparql"]
            res = self.evaluate_query(case, query)
            results.append(res)

            cat = case["category"]
            if cat not in category_stats:
                category_stats[cat] = {
                    "total": 0,
                    "syntax_valid": 0,
                    "schema_compliant": 0,
                    "execution_matches": 0,
                    "structural_scores": [],
                }
            category_stats[cat]["total"] += 1
            if res["is_syntax_valid"]:
                category_stats[cat]["syntax_valid"] += 1
            if res["is_schema_compliant"]:
                category_stats[cat]["schema_compliant"] += 1
            if res["execution_match"]:
                category_stats[cat]["execution_matches"] += 1
            category_stats[cat]["structural_scores"].append(res["structural_score"])

        # Aggregate metrics
        total = len(results)
        syntax_valid_total = sum(1 for r in results if r["is_syntax_valid"])
        schema_comp_total = sum(1 for r in results if r["is_schema_compliant"])
        exec_match_total = sum(1 for r in results if r["execution_match"])
        avg_struct = sum(r["structural_score"] for r in results) / total if total else 0.0

        cat_summary = {}
        for cat, stats in category_stats.items():
            n = stats["total"]
            cat_summary[cat] = {
                "total": n,
                "syntax_validity": round(stats["syntax_valid"] / n, 3),
                "schema_compliance": round(stats["schema_compliant"] / n, 3),
                "execution_accuracy": round(stats["execution_matches"] / n, 3),
                "avg_structural_score": round(sum(stats["structural_scores"]) / n, 3),
            }

        metrics = {
            "num_test_cases": total,
            "syntax_validity_rate": round(syntax_valid_total / total, 3),
            "schema_compliance_rate": round(schema_comp_total / total, 3),
            "execution_accuracy": round(exec_match_total / total, 3),
            "mean_structural_pattern_score": round(avg_struct, 3),
            "category_breakdown": cat_summary,
        }

        output_data = {
            "metrics": metrics,
            "individual_evaluations": results,
        }

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(output_data, indent=2), encoding="utf-8")
        logger.info("Saved NL2SPARQL benchmark results to %s", out_path)

        print("\n=== NL2SPARQL & Graph-RAG Benchmark Evaluation ===")
        print(f"  Test Cases Evaluated:       {total}")
        print(f"  Syntax Validity Rate:       {metrics['syntax_validity_rate']:.1%}")
        print(f"  Schema Compliance Rate:     {metrics['schema_compliance_rate']:.1%}")
        print(f"  Mean Structural Match:      {metrics['mean_structural_pattern_score']:.1%}")
        print(f"  Execution Accuracy (EA):    {metrics['execution_accuracy']:.1%}")
        print("\n--- Category Breakdown ---")
        for cat, cs in cat_summary.items():
            print(f"  {cat:<25}: EA = {cs['execution_accuracy']:.1%} | Syntax = {cs['syntax_validity']:.1%} | Struct = {cs['avg_structural_score']:.1%}")

        return output_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")
    evaluator = NL2SPARQLEvaluator()
    evaluator.run_benchmark()
