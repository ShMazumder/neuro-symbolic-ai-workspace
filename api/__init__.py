"""
api — Violence KG API Package

Modules:
    graph_rag  (4.6) — Graph-RAG: LLM grounded in BlazeGraph for analyst Q&A
    nl2sparql  (4.7) — NL2SPARQL: natural language → SPARQL via LLM + schema grounding

Usage:
    # Graph-RAG
    from api.graph_rag import ask
    response = ask("Which districts have the most violence events?")
    print(response.answer)

    # NL2SPARQL
    from api.nl2sparql import nl2sparql
    result = nl2sparql("Show me all assault events in Dhaka after 2025-01-01")
    print(result.sparql_query)
    print(result.rows[:5])

    # FastAPI servers
    from api.graph_rag import create_app as graph_rag_app
    from api.nl2sparql import create_app as nl2sparql_app
    # Run with: uvicorn api.graph_rag:app --port 8001
    #           uvicorn api.nl2sparql:app --port 8002
"""

from .graph_rag import ask, RAGResponse
from .nl2sparql import nl2sparql, NL2SPARQLResult

__all__ = ["ask", "RAGResponse", "nl2sparql", "NL2SPARQLResult"]
