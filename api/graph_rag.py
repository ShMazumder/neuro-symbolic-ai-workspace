"""
api/graph_rag.py
Task 4.6 — Graph-RAG: LLM grounded in BlazeGraph for analyst Q&A.

Architecture:
  User question
      │
      ▼
  Keyword / entity extraction (spaCy)
      │
      ▼
  SPARQL query generation (template-based → LLM fallback)
      │
      ▼
  BlazeGraph query → result triples
      │
      ▼
  Context assembly (triples → markdown snippets)
      │
      ▼
  LLM generation (Gemini / OpenAI) with grounded context
      │
      ▼
  Cited answer + source article URLs

The LLM only generates text; all facts come from the KG.

Dependencies:
    pip install spacy requests google-generativeai
    python -m spacy download en_core_web_sm
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

# ── SPARQL template library ───────────────────────────────────────────────────

# Templates keyed by intent; {placeholders} filled from extracted entities
SPARQL_TEMPLATES = {
    "hotspots": """
PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (COUNT(?evt) AS ?count)
WHERE {{
  ?evt a cameo:ViolenceEvent ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
  {date_filter}
}}
GROUP BY ?district
ORDER BY DESC(?count)
LIMIT 10
""",
    "actor_network": """
PREFIX cameo: <http://example.org/cameo/>
SELECT ?actor ?actorName ?type (COUNT(?evt) AS ?events)
WHERE {{
  ?evt a cameo:ViolenceEvent ;
       cameo:actor ?actor .
  ?actor cameo:actorName ?actorName ;
         cameo:actorType ?type .
  {actor_filter}
}}
GROUP BY ?actor ?actorName ?type
ORDER BY DESC(?events)
LIMIT 20
""",
    "district_events": """
PREFIX cameo: <http://example.org/cameo/>
PREFIX prov:  <http://www.w3.org/ns/prov#>
SELECT ?evt ?code ?date ?actorName ?articleUrl
WHERE {{
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district "{district}" .
  OPTIONAL {{
    ?evt cameo:actor ?actor .
    ?actor cameo:actorName ?actorName .
  }}
  OPTIONAL {{
    ?evt prov:wasDerivedFrom ?src .
    ?src cameo:articleUrl ?articleUrl .
  }}
}}
ORDER BY DESC(?date)
LIMIT 20
""",
    "cameo_trend": """
PREFIX cameo: <http://example.org/cameo/>
SELECT ?month (COUNT(?evt) AS ?count)
WHERE {{
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date .
  FILTER (?code >= {min_code} && ?code <= {max_code})
  BIND(SUBSTR(STR(?date), 1, 7) AS ?month)
}}
GROUP BY ?month
ORDER BY ?month
""",
    "escalation_check": """
PREFIX cameo: <http://example.org/cameo/>
SELECT ?district (MAX(?code) AS ?maxCode) (COUNT(?evt) AS ?events)
WHERE {{
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district ?district .
  FILTER (?date >= "{since_date}")
}}
GROUP BY ?district
HAVING (?maxCode >= 18)
ORDER BY DESC(?maxCode)
""",
}


# ── Entity extraction ─────────────────────────────────────────────────────────

BD_DISTRICTS = {
    "dhaka", "chittagong", "sylhet", "rajshahi", "khulna",
    "barisal", "rangpur", "mymensingh", "gazipur", "narayanganj",
    "cox's bazar", "cox bazar", "comilla", "bogura", "jessore",
}

INTENT_KEYWORDS = {
    "hotspots":       ["hotspot", "most violent", "top district", "where", "location"],
    "actor_network":  ["actor", "who", "party", "force", "group", "perpetrator"],
    "district_events": ["event", "incident", "what happened", "attacks"],
    "cameo_trend":    ["trend", "over time", "monthly", "increase", "decrease"],
    "escalation_check": ["escalat", "worsen", "surge", "spike", "forecast"],
}


def _extract_entities(question: str) -> dict:
    """Extract districts, date references, CAMEO code ranges from the question."""
    q_lower = question.lower()
    entities: dict = {}

    # Districts
    for d in BD_DISTRICTS:
        if d in q_lower:
            entities["district"] = d.title()
            break

    # Date patterns
    m = re.search(r"(since|after|from)\s+(\d{4}-\d{2}-\d{2}|\w+ \d{4})", q_lower)
    if m:
        entities["since_date"] = m.group(2)

    # CAMEO range
    if "killing" in q_lower or "death" in q_lower:
        entities["min_code"] = 19
        entities["max_code"] = 20
    elif "assault" in q_lower or "attack" in q_lower:
        entities["min_code"] = 17
        entities["max_code"] = 20
    else:
        entities["min_code"] = 13
        entities["max_code"] = 20

    return entities


def _classify_intent(question: str) -> str:
    """Simple keyword-based intent classifier."""
    q_lower = question.lower()
    best_intent, best_score = "hotspots", 0

    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in q_lower)
        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent


def _build_sparql(intent: str, entities: dict) -> str:
    """Fill template with extracted entities."""
    template = SPARQL_TEMPLATES.get(intent, SPARQL_TEMPLATES["hotspots"])

    fills = {
        "date_filter": (
            f'FILTER (?date >= "{entities["since_date"]}")' if "since_date" in entities else ""
        ),
        "actor_filter": (
            f'?actor cameo:actorName "{entities.get("actor_name", "")}" .' 
            if "actor_name" in entities else ""
        ),
        "district": entities.get("district", "Dhaka"),
        "since_date": entities.get("since_date", "2024-01-01"),
        "min_code": entities.get("min_code", 13),
        "max_code": entities.get("max_code", 20),
    }

    try:
        return template.format(**fills)
    except KeyError:
        return SPARQL_TEMPLATES["hotspots"].format(date_filter="")


# ── BlazeGraph query runner ───────────────────────────────────────────────────

def _run_sparql(query: str, endpoint: str = SPARQL_ENDPOINT) -> list[dict]:
    """Execute a SPARQL SELECT query and return rows as flat dicts."""
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
        logger.error("SPARQL query failed: %s", exc)
        return []


# ── Context assembler ─────────────────────────────────────────────────────────

def _assemble_context(rows: list[dict], intent: str) -> str:
    """Convert SPARQL result rows into a markdown context block for the LLM."""
    if not rows:
        return "No relevant events found in the knowledge graph for this query."

    lines = [f"## Knowledge Graph Results ({intent})\n"]

    if intent == "hotspots":
        lines.append("| District | Event Count |")
        lines.append("|---|---|")
        for r in rows[:10]:
            lines.append(f"| {r.get('district', '?')} | {r.get('count', '?')} |")

    elif intent == "district_events":
        lines.append("| Date | CAMEO Code | Actor | Source Article |")
        lines.append("|---|---|---|---|")
        for r in rows[:15]:
            url = r.get("articleUrl", "")
            url_md = f"[link]({url})" if url else "—"
            lines.append(
                f"| {r.get('date','?')[:10]} | {r.get('code','?')} | "
                f"{r.get('actorName','?')} | {url_md} |"
            )

    elif intent == "cameo_trend":
        lines.append("| Month | Event Count |")
        lines.append("|---|---|")
        for r in rows:
            lines.append(f"| {r.get('month', '?')} | {r.get('count', '?')} |")

    elif intent == "escalation_check":
        lines.append("| District | Max CAMEO Code | Recent Events |")
        lines.append("|---|---|---|")
        for r in rows[:10]:
            lines.append(
                f"| {r.get('district','?')} | {r.get('maxCode','?')} | "
                f"{r.get('events','?')} |"
            )

    elif intent == "actor_network":
        lines.append("| Actor | Type | Event Count |")
        lines.append("|---|---|---|")
        for r in rows[:15]:
            lines.append(
                f"| {r.get('actorName','?')} | {r.get('type','?')} | {r.get('events','?')} |"
            )

    else:
        for r in rows[:10]:
            lines.append(str(r))

    return "\n".join(lines)


# ── LLM generation ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert conflict analyst specialising in Bangladeshi violence events.
You answer questions ONLY using the provided knowledge graph context.
You MUST cite specific events, districts, actors, and source articles from the context.
If the context does not contain enough information, say so clearly — do NOT hallucinate.
Always be concise, factual, and mention data limitations."""


def _generate_with_llm(question: str, context: str, sparql_query: str) -> str:
    """
    Generate a grounded answer using Google Gemini (primary) or fallback to rule-based.

    Requires: GOOGLE_API_KEY environment variable.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")

    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")

            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"**Question:** {question}\n\n"
                f"**SPARQL query executed:**\n```sparql\n{sparql_query.strip()}\n```\n\n"
                f"{context}\n\n"
                f"**Answer (cite specific rows from the table above):**"
            )
            response = model.generate_content(prompt)
            return response.text

        except Exception as exc:
            logger.warning("Gemini API failed: %s — falling back to rule-based.", exc)

    # Rule-based fallback: summarise the context directly
    return (
        f"Based on the knowledge graph:\n\n{context}\n\n"
        f"*(LLM unavailable — showing raw KG results. "
        f"Set GOOGLE_API_KEY for narrative answers.)*"
    )


# ── Main Q&A interface ────────────────────────────────────────────────────────

@dataclass
class RAGResponse:
    question:     str
    intent:       str
    sparql_query: str
    num_results:  int
    context:      str
    answer:       str
    source_urls:  list[str] = field(default_factory=list)


def ask(
    question: str,
    endpoint: str = SPARQL_ENDPOINT,
) -> RAGResponse:
    """
    Main Graph-RAG entry point.

    question: Natural language question from the analyst.
    Returns:  RAGResponse with grounded answer and citation.
    """
    logger.info("Graph-RAG question: %s", question)

    # 1. Intent + entity extraction
    intent   = _classify_intent(question)
    entities = _extract_entities(question)
    logger.info("Intent: %s | Entities: %s", intent, entities)

    # 2. SPARQL query generation
    query = _build_sparql(intent, entities)
    logger.info("Generated SPARQL:\n%s", query)

    # 3. BlazeGraph query
    rows = _run_sparql(query, endpoint)
    logger.info("SPARQL returned %d rows.", len(rows))

    # 4. Context assembly
    context = _assemble_context(rows, intent)

    # 5. LLM answer generation
    answer = _generate_with_llm(question, context, query)

    # 6. Source URL extraction
    source_urls = list({r["articleUrl"] for r in rows if r.get("articleUrl")})

    return RAGResponse(
        question=question,
        intent=intent,
        sparql_query=query,
        num_results=len(rows),
        context=context,
        answer=answer,
        source_urls=source_urls[:10],
    )


# ── FastAPI endpoint ──────────────────────────────────────────────────────────

def create_app():
    """Create a FastAPI app exposing the Graph-RAG endpoint."""
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
    except ImportError:
        raise ImportError("Run: pip install fastapi uvicorn")

    app = FastAPI(
        title="Violence KG Graph-RAG API",
        description="Ask natural language questions about Bangladesh violence events grounded in BlazeGraph.",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class QuestionRequest(BaseModel):
        question: str
        endpoint: str = SPARQL_ENDPOINT

    class AnswerResponse(BaseModel):
        question:     str
        intent:       str
        sparql_query: str
        num_results:  int
        answer:       str
        source_urls:  list[str]

    @app.post("/ask", response_model=AnswerResponse)
    def ask_endpoint(req: QuestionRequest):
        resp = ask(req.question, req.endpoint)
        return AnswerResponse(
            question=resp.question,
            intent=resp.intent,
            sparql_query=resp.sparql_query,
            num_results=resp.num_results,
            answer=resp.answer,
            source_urls=resp.source_urls,
        )

    @app.get("/health")
    def health():
        return {"status": "ok", "endpoint": SPARQL_ENDPOINT}

    return app


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")

    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Which districts have the most violence events?"
    resp = ask(q)
    print(f"\n{'='*60}")
    print(f"Q: {resp.question}")
    print(f"Intent: {resp.intent}  |  Results: {resp.num_results}")
    print(f"{'='*60}")
    print(resp.answer)
    if resp.source_urls:
        print(f"\nSources: {resp.source_urls[:3]}")
