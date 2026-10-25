"""
api/nl2sparql.py
Task 4.7 — NL2SPARQL: natural language → SPARQL via LLM + schema grounding.

Two-stage approach:
  Stage 1 — Schema grounding:
    Loads the CAMEO ontology class/property inventory from BlazeGraph.
    Injects it as a compact schema description into the LLM prompt.

  Stage 2 — LLM generation + validation:
    Calls Gemini (primary) or a rule-based fallback to produce SPARQL.
    Validates the generated query: syntax check, forbidden clause check,
    and dry-run against BlazeGraph with LIMIT 0.

  Stage 3 — Safe execution:
    Runs the validated query with a hard row-limit cap (≤500).
    Returns results + the query for downstream use.

Dependencies:
    pip install google-generativeai requests
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SPARQL_ENDPOINT = "http://localhost:9999/blazegraph/sparql"
MAX_ROWS        = 500   # hard safety cap on result size

# ── Schema inventory ──────────────────────────────────────────────────────────

# Compact schema description injected into LLM prompts.
# Reflects the event_schema.ttl / cameo_base.ttl ontology.
SCHEMA_DESCRIPTION = """
## CAMEO Knowledge Graph Schema (BlazeGraph)

### Prefixes
PREFIX cameo: <http://example.org/cameo/>
PREFIX event: <http://example.org/event/>
PREFIX prov:  <http://www.w3.org/ns/prov#>
PREFIX owl:   <http://www.w3.org/2002/07/owl#>
PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>

### Classes
- cameo:ViolenceEvent    — an extracted violence event
- cameo:Actor            — a named entity (person, org, party, force)
- cameo:Location         — a geographic entity (district, division)
- cameo:Source           — a news article (provenance node)

### Properties on cameo:ViolenceEvent
- cameo:code            xsd:integer    (13–20, CAMEO violence codes)
- cameo:bdExtensionCode xsd:string     (BD-specific extension code, optional)
- cameo:confidence      xsd:decimal    (0.0–1.0)
- cameo:date            xsd:date       (YYYY-MM-DD)
- cameo:actor           → cameo:Actor
- cameo:target          → cameo:Actor  (victim)
- cameo:location        → cameo:Location
- prov:wasDerivedFrom   → cameo:Source

### Properties on cameo:Actor
- cameo:actorName       xsd:string
- cameo:actorType       xsd:string  (SECURITY_FORCE | POLITICAL_PARTY | ARMED_GROUP | CIVILIAN | GOVERNMENT)

### Properties on cameo:Location
- cameo:district        xsd:string
- cameo:division        xsd:string
- cameo:latitude        xsd:decimal
- cameo:longitude       xsd:decimal

### Properties on cameo:Source
- cameo:articleUrl      xsd:anyURI
- cameo:sentenceIdx     xsd:integer
- cameo:sentenceText    xsd:string

### CAMEO Code Meanings (violence range 13–20)
13=Threaten, 14=Protest, 15=Exhibit Force, 16=Reduce Relations,
17=Coerce, 18=Assault, 19=Fight/Armed Battle, 20=Mass Violence/Bombing

### Common Bangladesh Districts
Dhaka, Chittagong, Sylhet, Rajshahi, Khulna, Barisal, Rangpur, Mymensingh,
Gazipur, Narayanganj, Comilla, Bogura, Cox's Bazar, Jessore
"""

NL2SPARQL_SYSTEM_PROMPT = f"""You are an expert SPARQL query generator for a Bangladesh violence event knowledge graph.
Given a natural language question, generate a valid SPARQL SELECT query using ONLY the schema below.

RULES:
1. Always add PREFIX declarations (use the prefixes from the schema).
2. NEVER use INSERT, DELETE, DROP, UPDATE, or CLEAR.
3. Always add LIMIT (max 500) unless counting.
4. Use OPTIONAL for fields that may not exist on all triples.
5. Use FILTER for numeric comparisons, string comparisons, date ranges.
6. For date comparisons, use xsd:date("YYYY-MM-DD") or string prefix: FILTER(STR(?date) >= "2024-01").
7. Return ONLY the SPARQL query, no explanation, no markdown fences.

{SCHEMA_DESCRIPTION}
"""


# ── Output dataclass ──────────────────────────────────────────────────────────

@dataclass
class NL2SPARQLResult:
    question:       str
    sparql_query:   str
    valid:          bool
    validation_errors: list[str] = field(default_factory=list)
    rows:           list[dict]   = field(default_factory=list)
    num_rows:       int = 0
    source_urls:    list[str]    = field(default_factory=list)
    method:         str = "llm"  # "llm" | "fallback"

    def to_dict(self) -> dict:
        return {
            "question":          self.question,
            "sparql_query":      self.sparql_query,
            "valid":             self.valid,
            "validation_errors": self.validation_errors,
            "num_rows":          self.num_rows,
            "rows":              self.rows[:20],   # truncate for display
            "source_urls":       self.source_urls,
            "method":            self.method,
        }


# ── SPARQL validator ──────────────────────────────────────────────────────────

_FORBIDDEN_CLAUSES = re.compile(
    r"\b(INSERT|DELETE|DROP|UPDATE|CLEAR|LOAD|CREATE)\b",
    re.IGNORECASE,
)

_SELECT_RE = re.compile(r"\bSELECT\b", re.IGNORECASE)


def validate_sparql(query: str) -> list[str]:
    """
    Syntax-level validation of a generated SPARQL query.

    Returns a list of error strings (empty if valid).
    """
    errors: list[str] = []

    if not _SELECT_RE.search(query):
        errors.append("Query must be a SELECT query.")

    m = _FORBIDDEN_CLAUSES.search(query)
    if m:
        errors.append(f"Forbidden clause detected: {m.group(0)}. Only SELECT is allowed.")

    # Check balanced braces
    opens  = query.count("{")
    closes = query.count("}")
    if opens != closes:
        errors.append(f"Unbalanced braces: {{ {opens} vs }} {closes}.")

    # Check PREFIX declarations
    if "PREFIX cameo:" not in query:
        errors.append("Missing PREFIX cameo: declaration.")

    return errors


def _dry_run(query: str, endpoint: str) -> Optional[str]:
    """
    Execute the query with LIMIT 0 to check for server-side errors.

    Returns an error string, or None if successful.
    """
    # Inject LIMIT 0 for dry run (strip existing LIMIT first)
    dry_query = re.sub(r"\bLIMIT\s+\d+", "", query, flags=re.IGNORECASE).strip()
    dry_query += "\nLIMIT 0"

    try:
        from knowledge_graph.ingest import sparql_query
        result = sparql_query(dry_query, endpoint)
        if result is None:
            return "BlazeGraph returned null response."
        return None  # OK
    except Exception as exc:
        return str(exc)


# ── LLM query generator ────────────────────────────────────────────────────────

def _generate_with_gemini(question: str) -> Optional[str]:
    """Call Gemini to generate a SPARQL query. Returns raw query string or None."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = f"{NL2SPARQL_SYSTEM_PROMPT}\n\nQuestion: {question}\n\nSPARQL:"
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown fences if present
        raw = re.sub(r"```sparql\s*", "", raw)
        raw = re.sub(r"```\s*", "", raw)
        return raw.strip()

    except Exception as exc:
        logger.warning("Gemini NL2SPARQL failed: %s", exc)
        return None


# ── Rule-based fallback ────────────────────────────────────────────────────────

_FALLBACK_TEMPLATES: list[tuple[re.Pattern, str]] = [
    (
        re.compile(r"hotspot|most violent|top district|where.*most", re.I),
        """PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
GROUP BY ?district
ORDER BY DESC(?count)
LIMIT 15""",
    ),
    (
        re.compile(r"actor|who|party|force|group", re.I),
        """PREFIX cameo: <http://example.org/cameo/>
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
    ),
    (
        re.compile(r"trend|over time|monthly|month", re.I),
        """PREFIX cameo: <http://example.org/cameo/>
SELECT ?month (COUNT(?evt) AS ?count)
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date .
  BIND(SUBSTR(STR(?date), 1, 7) AS ?month)
}
GROUP BY ?month
ORDER BY ?month""",
    ),
    (
        re.compile(r"kill|death|fatal|mass violence", re.I),
        """PREFIX cameo: <http://example.org/cameo/>
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT ?evt ?date ?district ?articleUrl
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
  FILTER (?code >= 19)
  OPTIONAL {
    ?evt prov:wasDerivedFrom ?src .
    ?src cameo:articleUrl ?articleUrl .
  }
}
ORDER BY DESC(?date)
LIMIT 30""",
    ),
    (
        re.compile(r"source|article|news|url", re.I),
        """PREFIX cameo: <http://example.org/cameo/>
PREFIX prov:  <http://www.w3.org/ns/prov#>
SELECT ?evt ?date ?code ?articleUrl ?sentenceText
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:date ?date ;
       cameo:code ?code ;
       prov:wasDerivedFrom ?src .
  ?src cameo:articleUrl ?articleUrl .
  OPTIONAL { ?src cameo:sentenceText ?sentenceText }
}
ORDER BY DESC(?date)
LIMIT 20""",
    ),
]


KNOWN_DISTRICTS = [
    "Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Barisal", "Rangpur",
    "Mymensingh", "Gazipur", "Narayanganj", "Pabna", "Bogura", "Cox's Bazar",
    "Rangamati", "Jessore", "Comilla"
]

def _fallback_query(question: str) -> Optional[str]:
    """Match question against fallback templates with entity slot filling."""
    q_lower = question.lower()

    # 1. District-specific queries
    for dist in KNOWN_DISTRICTS:
        if dist.lower() in q_lower:
            if "how many" in q_lower or "count" in q_lower:
                return f"""PREFIX cameo: <http://example.org/cameo/>
SELECT (COUNT(?evt) AS ?count)
WHERE {{
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district "{dist}" .
}}"""
            if "source" in q_lower or "provenance" in q_lower or "article" in q_lower:
                return f"""PREFIX cameo: <http://example.org/cameo/>
PREFIX prov:  <http://www.w3.org/ns/prov#>
SELECT ?evt ?articleUrl ?sentenceText
WHERE {{
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc ;
       prov:wasDerivedFrom ?src .
  ?loc cameo:district "{dist}" .
  ?src cameo:articleUrl ?articleUrl ;
       cameo:sentenceText ?sentenceText .
}}"""
            return f"""PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date
WHERE {{
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district "{dist}" .
}}"""

    # 2. Actor-specific queries
    for actor in ["Awami League", "BNP", "Chhatra League", "Police", "RAB"]:
        if actor.lower() in q_lower:
            return f"""PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date
WHERE {{
  ?evt a cameo:ViolenceEvent ;
       cameo:actor ?actor ;
       cameo:code ?code ;
       cameo:date ?date .
  ?actor cameo:actorName ?name .
  FILTER (REGEX(?name, "{actor}", "i"))
}}"""

    # 3. CAMEO Code-specific queries
    if "assault" in q_lower or "18" in q_lower:
        return """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code 18 ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}"""
    if "battle" in q_lower or "clash" in q_lower or "19" in q_lower:
        return """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code 19 ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}"""
    if "bomb" in q_lower or "explosion" in q_lower or "mass violence" in q_lower or "20" in q_lower:
        return """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code 20 ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}"""
    if "protest" in q_lower or "demonstrat" in q_lower or "14" in q_lower:
        return """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code 14 ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}"""
    if "curfew" in q_lower or "arrest" in q_lower or "coerce" in q_lower or "17" in q_lower:
        return """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code 17 ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}"""

    # 4. Pattern template matching
    for pattern, template in _FALLBACK_TEMPLATES:
        if pattern.search(question):
            return template

    # Generic fallback: recent events
    return """PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
}
ORDER BY DESC(?date)
LIMIT 20"""


# ── Execution ─────────────────────────────────────────────────────────────────

def _enforce_limit(query: str, max_rows: int = MAX_ROWS) -> str:
    """Ensure the query has a LIMIT no greater than max_rows."""
    m = re.search(r"\bLIMIT\s+(\d+)", query, re.IGNORECASE)
    if m:
        existing = int(m.group(1))
        if existing > max_rows:
            query = re.sub(r"\bLIMIT\s+\d+", f"LIMIT {max_rows}", query, flags=re.IGNORECASE)
    else:
        # COUNT queries should not have LIMIT
        if "COUNT" not in query.upper():
            query += f"\nLIMIT {max_rows}"
    return query


def _execute(query: str, endpoint: str) -> list[dict]:
    """Run the query and return flat result rows."""
    try:
        from knowledge_graph.ingest import sparql_query
        result = sparql_query(query, endpoint)
        if not result:
            return []
        return [
            {k: v.get("value", "") for k, v in row.items()}
            for row in result.get("results", {}).get("bindings", [])
        ]
    except Exception as exc:
        logger.error("Query execution failed: %s", exc)
        return []


# ── Main entry point ──────────────────────────────────────────────────────────

def nl2sparql(
    question: str,
    endpoint: str = SPARQL_ENDPOINT,
    dry_run: bool = True,
) -> NL2SPARQLResult:
    """
    Convert a natural language question to SPARQL and execute it.

    Stages:
      1. Try LLM (Gemini) generation.
      2. If LLM unavailable or query invalid → rule-based fallback.
      3. Validate (syntax + optionally dry-run against BlazeGraph).
      4. Execute with row-limit cap.
      5. Return NL2SPARQLResult with full audit trail.
    """
    logger.info("NL2SPARQL question: %s", question)
    method = "llm"

    # Stage 1: LLM generation
    query = _generate_with_gemini(question)
    if not query:
        query = _fallback_query(question) or ""
        method = "fallback"

    # Stage 2: Syntax validation
    errors = validate_sparql(query)

    if errors:
        logger.warning("LLM query invalid (%s) → falling back.", errors)
        query  = _fallback_query(question) or query
        method = "fallback"
        errors = validate_sparql(query)

    # Stage 3: Dry run
    if dry_run and not errors:
        err = _dry_run(query, endpoint)
        if err:
            errors.append(f"BlazeGraph dry-run error: {err}")
            query  = _fallback_query(question) or query
            method = "fallback"
            errors = validate_sparql(query)

    valid = len(errors) == 0

    # Stage 4: Execute (with limit cap)
    rows: list[dict] = []
    if valid:
        safe_query = _enforce_limit(query, MAX_ROWS)
        rows = _execute(safe_query, endpoint)
    else:
        safe_query = query

    source_urls = list({r.get("articleUrl", "") for r in rows if r.get("articleUrl")})

    logger.info(
        "NL2SPARQL complete: method=%s valid=%s rows=%d errors=%s",
        method, valid, len(rows), errors,
    )

    return NL2SPARQLResult(
        question=question,
        sparql_query=safe_query,
        valid=valid,
        validation_errors=errors,
        rows=rows,
        num_rows=len(rows),
        source_urls=source_urls,
        method=method,
    )


# ── FastAPI endpoint ──────────────────────────────────────────────────────────

def create_app():
    """Attach NL2SPARQL endpoint to a FastAPI app."""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
    except ImportError:
        raise ImportError("Run: pip install fastapi uvicorn")

    app = FastAPI(
        title="Violence KG NL2SPARQL API",
        description="Convert natural language questions to SPARQL and query BlazeGraph.",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class QueryRequest(BaseModel):
        question: str
        endpoint: str = SPARQL_ENDPOINT

    class QueryResponse(BaseModel):
        question:          str
        sparql_query:      str
        valid:             bool
        validation_errors: list[str]
        num_rows:          int
        rows:              list[dict]
        source_urls:       list[str]
        method:            str

    @app.post("/query", response_model=QueryResponse)
    def query_endpoint(req: QueryRequest):
        result = nl2sparql(req.question, req.endpoint)
        return QueryResponse(
            question=result.question,
            sparql_query=result.sparql_query,
            valid=result.valid,
            validation_errors=result.validation_errors,
            num_rows=result.num_rows,
            rows=result.rows[:50],
            source_urls=result.source_urls,
            method=result.method,
        )

    @app.get("/schema")
    def get_schema():
        return {"schema": SCHEMA_DESCRIPTION}

    @app.get("/health")
    def health():
        return {"status": "ok", "endpoint": SPARQL_ENDPOINT}

    return app


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")

    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        "Show me the top 10 districts by violence event count"

    result = nl2sparql(question)
    print(f"\nQuestion: {result.question}")
    print(f"Method: {result.method}  |  Valid: {result.valid}  |  Rows: {result.num_rows}")
    if result.validation_errors:
        print(f"Errors: {result.validation_errors}")
    print(f"\nGenerated SPARQL:\n{result.sparql_query}")
    if result.rows:
        print(f"\nFirst 5 rows:")
        for row in result.rows[:5]:
            print(f"  {row}")
