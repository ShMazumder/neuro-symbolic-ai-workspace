"""
tests/test_rdf_generator.py
Unit tests for knowledge_graph/rdf_generator.py (RDF N-Triples and Turtle generation).
"""

import pytest
from rdflib import Graph, URIRef, RDF, Literal
from knowledge_graph.rdf_generator import (
    _slug,
    _actor_uri,
    _cameo_class_uri,
    _article_uri,
    event_to_graph,
    events_to_graph,
    graph_to_turtle,
    graph_to_ntriples,
    CAMEO,
    CAMEO_BD,
    EVENT,
    ACTOR,
    GEO,
    ARTICLE,
)


class TestRdfGenerator:
    def test_slug_generation(self):
        assert _slug("Dhaka City Police") == "dhaka_city_police"
        assert _slug("Cox's Bazar!") == "coxs_bazar"
        assert _slug("  Student League -- General  ") == "student_league_general"

    def test_actor_uri(self):
        uri = _actor_uri("Police Officers")
        assert uri == URIRef("http://example.org/actor/police_officers")

    def test_cameo_class_uri_standard(self):
        uri = _cameo_class_uri("180")
        assert uri == CAMEO["Code180"]

    def test_cameo_class_uri_bd_extension(self):
        uri = _cameo_class_uri("BD01")
        assert uri == CAMEO_BD["BD01"]

    def test_article_uri_deterministic(self):
        url = "https://www.thedailystar.net/news/bangladesh/crime-justice/article-12345"
        uri1 = _article_uri(url)
        uri2 = _article_uri(url)
        assert uri1 == uri2
        assert str(uri1).startswith("http://example.org/article/")

    def test_event_to_graph_conversion(self):
        sample_event = {
            "event_id": "EVT_TEST_001",
            "cameo_code": "180",
            "cameo_label": "Assault",
            "confidence": 0.88,
            "trigger": "clashed with",
            "source_sentence": "Police and protesters clashed in Dhaka.",
            "source_url": "https://www.thedailystar.net/test-news",
            "article_title": "Police and protesters clash in Dhaka",
            "location": {
                "raw": "Dhaka",
                "district": "Dhaka",
                "division": "Dhaka",
                "latitude": 23.8103,
                "longitude": 90.4125,
            },
            "perpetrators": [{"name": "Protesters", "role": "perpetrator"}],
            "victims": [{"name": "Police", "role": "target"}],
            "actors": [
                {"name": "Protesters", "role": "perpetrator", "type": "PROTESTER"},
                {"name": "Police", "role": "target", "type": "POLICE"}
            ],
            "temporal": {"date": "2026-10-20"},
        }

        g = event_to_graph(sample_event)
        assert isinstance(g, Graph)
        assert len(g) > 5

        # Check Event node exists
        event_node = EVENT["EVT_TEST_001"]
        assert (event_node, RDF.type, CAMEO["Code180"]) in g

        # Check confidence literal
        confidences = list(g.objects(event_node, CAMEO["confidence"]))
        assert len(confidences) == 1
        assert float(confidences[0]) == pytest.approx(0.88)

        # Check serialization
        ttl = graph_to_turtle(g)
        assert "Code180" in ttl
        nt = graph_to_ntriples(g)
        assert "EVT_TEST_001" in nt

    def test_events_to_graph(self):
        events = [
            {
                "event_id": f"EVT_TEST_{i}",
                "cameo_code": "140",
                "cameo_label": "Protest",
                "confidence": 0.75,
                "trigger": "demonstration",
                "source_sentence": f"Protesters held a demonstration {i}.",
                "source_url": f"https://www.thedailystar.net/test-{i}",
                "article_title": f"Rally {i}",
                "location": {"raw": "Sylhet", "district": "Sylhet"},
                "actors": [],
            }
            for i in range(3)
        ]

        g = events_to_graph(events)
        assert isinstance(g, Graph)
        for i in range(3):
            assert (EVENT[f"EVT_TEST_{i}"], RDF.type, CAMEO["Code140"]) in g
