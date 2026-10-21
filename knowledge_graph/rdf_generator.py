"""
knowledge_graph/rdf_generator.py
Task 3.1 — Convert EventRecord JSON → RDF Turtle/N-Triples.

Generates fully provenance-linked RDF triples conforming to the
ontology defined in ontology/event_schema.ttl.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union
from urllib.parse import quote

from rdflib import (
    Graph, Namespace, URIRef, Literal, BNode,
    RDF, RDFS, OWL, XSD
)
from rdflib.namespace import PROV

logger = logging.getLogger(__name__)

# ── Namespaces ────────────────────────────────────────────────────────────────

CAMEO    = Namespace("http://example.org/cameo/")
CAMEO_BD = Namespace("http://example.org/cameo/bd/")
EVENT    = Namespace("http://example.org/event/")
ACTOR    = Namespace("http://example.org/actor/")
GEO      = Namespace("http://example.org/geo/")
ARTICLE  = Namespace("http://example.org/article/")

ALL_NAMESPACES = {
    "cameo":    CAMEO,
    "cameo-bd": CAMEO_BD,
    "event":    EVENT,
    "actor":    ACTOR,
    "geo":      GEO,
    "article":  ARTICLE,
    "prov":     PROV,
    "owl":      OWL,
    "xsd":      XSD,
}


# ── URI helpers ───────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    """Create a safe URI slug from arbitrary text."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "_", text).strip("_")
    return quote(text, safe="_")


def _event_uri(event_id: str) -> URIRef:
    return EVENT[event_id]


def _actor_uri(name: str) -> URIRef:
    return ACTOR[_slug(name)]


def _geo_uri(raw: str, district: Optional[str] = None) -> URIRef:
    key = district or raw
    return GEO[_slug(key)]


def _article_uri(url: str) -> URIRef:
    digest = hashlib.md5(url.encode()).hexdigest()[:16]
    return ARTICLE[digest]


def _cameo_class_uri(code: str) -> URIRef:
    """Map CAMEO code to ontology class URI."""
    if re.match(r"^[A-Z]{2}\d{2}$", code):
        return CAMEO_BD[code]
    return CAMEO[f"Code{code}"]


# ── Core triple generator ─────────────────────────────────────────────────────

def event_to_graph(event: dict, g: Optional[Graph] = None) -> Graph:
    """
    Convert a single EventRecord dict to RDF triples.

    Adds:
      - Event node with all properties
      - Actor nodes (perpetrators + victims)
      - Location node
      - Article provenance node
      - PROV derivation triples

    Args:
        event: EventRecord.to_dict() output.
        g:     Existing Graph to add to (creates new if None).

    Returns:
        Graph with new triples appended.
    """
    if g is None:
        g = _new_graph()

    evt_uri = _event_uri(event["event_id"])

    # ── Event type ─────────────────────────────────────────────────────────────
    cameo_cls = _cameo_class_uri(event["cameo_code"])
    g.add((evt_uri, RDF.type, cameo_cls))
    g.add((evt_uri, RDF.type, CAMEO.ViolenceEvent))

    # ── Core properties ────────────────────────────────────────────────────────
    g.add((evt_uri, EVENT.eventId,       Literal(event["event_id"])))
    g.add((evt_uri, CAMEO.code,          Literal(event["cameo_code"])))
    g.add((evt_uri, CAMEO.label,         Literal(event["cameo_label"], lang="en")))
    g.add((evt_uri, CAMEO.trigger,       Literal(event["trigger"])))
    g.add((evt_uri, CAMEO.confidence,    Literal(event["confidence"], datatype=XSD.float)))
    g.add((evt_uri, CAMEO.sourceSentence, Literal(event["source_sentence"])))
    g.add((evt_uri, CAMEO.sourceUrl,     URIRef(event["source_url"])))

    if event.get("bd_code"):
        g.add((evt_uri, EVENT.bdExtensionCode, Literal(event["bd_code"])))

    if event.get("article_title"):
        g.add((evt_uri, EVENT.articleTitle, Literal(event["article_title"])))

    # ── Sentence offset ────────────────────────────────────────────────────────
    offsets = event.get("sentence_offset", [-1, -1])
    if offsets and offsets[0] >= 0:
        g.add((evt_uri, EVENT.sentenceOffset,
               Literal(json.dumps(offsets), datatype=XSD.string)))

    # ── Date ──────────────────────────────────────────────────────────────────
    date_rec = event.get("date", {})
    norm_date = str(date_rec.get("normalized", ""))
    if norm_date:
        if re.match(r"^\d{4}-\d{2}-\d{2}", norm_date):
            g.add((evt_uri, CAMEO.date, Literal(norm_date[:10], datatype=XSD.date)))
        else:
            g.add((evt_uri, CAMEO.date, Literal(norm_date)))
    if date_rec.get("raw"):
        g.add((evt_uri, EVENT["date_raw"], Literal(date_rec["raw"])))

    if event.get("article_published"):
        try:
            g.add((evt_uri, EVENT.articlePublishedDate,
                   Literal(event["article_published"][:10], datatype=XSD.date)))
        except Exception:
            pass

    # ── Counts ────────────────────────────────────────────────────────────────
    for field_name, prop in [
        ("victim_count",   EVENT.victimCount),
        ("injured_count",  EVENT.injuredCount),
    ]:
        val = event.get(field_name)
        if val is not None:
            g.add((evt_uri, prop, Literal(int(val), datatype=XSD.integer)))

    # ── Location ──────────────────────────────────────────────────────────────
    loc = event.get("location", {})
    loc_raw = loc.get("raw", "")
    if loc_raw:
        loc_uri = _geo_uri(loc_raw, loc.get("district"))
        g.add((evt_uri, CAMEO.location, loc_uri))
        g.add((loc_uri, RDF.type, CAMEO.Location))
        g.add((loc_uri, CAMEO.rawLocation, Literal(loc_raw)))
        if loc.get("district"):
            g.add((loc_uri, CAMEO.district, Literal(loc["district"])))
        if loc.get("division"):
            g.add((loc_uri, CAMEO.division, Literal(loc["division"])))
        coords = loc.get("coordinates")
        if coords and len(coords) == 2 and coords[0] is not None:
            g.add((loc_uri, CAMEO.latitude,  Literal(coords[0], datatype=XSD.double)))
            g.add((loc_uri, CAMEO.longitude, Literal(coords[1], datatype=XSD.double)))

    # ── Actors ────────────────────────────────────────────────────────────────
    for actor in event.get("actors", []):
        name = actor.get("name", "").strip()
        if not name:
            continue
        canonical = actor.get("canonical") or name
        actor_uri = _actor_uri(canonical)

        g.add((actor_uri, RDF.type, CAMEO.Actor))
        g.add((actor_uri, CAMEO.actorName, Literal(canonical)))
        g.add((actor_uri, CAMEO.actorType, Literal(actor.get("type", "UNKNOWN"))))

        role = actor.get("role", "unknown")
        if role == "perpetrator":
            g.add((evt_uri, CAMEO.actor, actor_uri))
        elif role == "target":
            g.add((evt_uri, CAMEO.target, actor_uri))

    # ── Provenance (PROV-O) ───────────────────────────────────────────────────
    art_uri = _article_uri(event["source_url"])
    g.add((art_uri, RDF.type, PROV.Entity))
    g.add((art_uri, RDFS.label, Literal(event.get("article_title", ""), lang="en")))
    g.add((art_uri, URIRef("http://schema.org/url"), URIRef(event["source_url"])))

    g.add((evt_uri, PROV.wasDerivedFrom, art_uri))
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    g.add((evt_uri, PROV.generatedAtTime,
           Literal(now_str, datatype=XSD.dateTime)))
    g.add((evt_uri, EVENT.extractionModel,
           Literal(event.get("extraction_method", "pipeline-v1"))))

    return g


def events_to_graph(events: list[dict]) -> Graph:
    """Convert a list of EventRecord dicts to a single RDF Graph."""
    g = _new_graph()
    for event in events:
        try:
            event_to_graph(event, g)
        except Exception as exc:
            logger.error("Failed to convert event %s: %s",
                         event.get("event_id", "?"), exc)
    logger.info("Generated %d triples from %d events.", len(g), len(events))
    return g


def _new_graph() -> Graph:
    """Create a new Graph with all namespace bindings."""
    g = Graph()
    for prefix, ns in ALL_NAMESPACES.items():
        g.bind(prefix, ns)
    return g


# ── Serialisation helpers ─────────────────────────────────────────────────────

def graph_to_turtle(g: Graph) -> str:
    """Serialize graph to Turtle string."""
    return g.serialize(format="turtle")


def graph_to_ntriples(g: Graph) -> str:
    """Serialize graph to N-Triples string (fastest for bulk ingest)."""
    return g.serialize(format="nt")


def save_graph(
    g: Graph,
    path: Path,
    fmt: str = "turtle",
) -> None:
    """Serialize and save graph to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(path), format=fmt)
    logger.info("Saved graph (%d triples) to %s [%s]", len(g), path, fmt)


def event_to_triples(event: dict) -> list[tuple[str, str, str]]:
    """Convert an event dictionary into a list of (subject, predicate, object) string triples."""
    ev = dict(event)
    ev.setdefault("cameo_label", "ViolenceEvent")
    ev.setdefault("trigger", "violence")
    ev.setdefault("confidence", 0.8)
    ev.setdefault("source_sentence", "")
    ev.setdefault("source_url", "http://example.org/article/1")
    g = event_to_graph(ev)
    return [(str(s), str(p), str(o)) for s, p, o in g]



# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s")

    if len(sys.argv) < 2:
        print("Usage: python -m knowledge_graph.rdf_generator <events.json>")
        sys.exit(1)

    events_file = Path(sys.argv[1])
    events = json.loads(events_file.read_text(encoding="utf-8"))
    if isinstance(events, dict):
        events = [events]

    g = events_to_graph(events)
    out = events_file.with_suffix(".ttl")
    save_graph(g, out, fmt="turtle")
    print(f"Saved {len(g)} triples → {out}")
