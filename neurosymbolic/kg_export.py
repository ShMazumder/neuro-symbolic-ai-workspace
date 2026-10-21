"""
neurosymbolic/kg_export.py
Task 4.1 — Export BlazeGraph knowledge graph to PyTorch Geometric format.

Converts RDF triples into edge-indexed heterogeneous graph tensors
suitable for R-GCN, CompGCN, and TransE/ComplEx/RotatE training.
"""

from __future__ import annotations

import json
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SPARQL_ENDPOINT = "http://localhost:9999/blazegraph/sparql"

# ── SPARQL queries for graph export ──────────────────────────────────────────

_Q_EVENTS = """
PREFIX cameo: <http://example.org/cameo/>
PREFIX event: <http://example.org/event/>
SELECT DISTINCT ?evt ?code ?bdCode ?confidence ?date ?district
WHERE {
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code .
  OPTIONAL { ?evt event:bdExtensionCode ?bdCode }
  OPTIONAL { ?evt cameo:confidence ?confidence }
  OPTIONAL { ?evt cameo:date ?date }
  OPTIONAL {
    ?evt cameo:location ?loc .
    ?loc cameo:district ?district
  }
}
"""

_Q_ACTORS = """
PREFIX cameo: <http://example.org/cameo/>
SELECT DISTINCT ?actor ?name ?type
WHERE {
  ?actor a cameo:Actor ;
         cameo:actorName ?name ;
         cameo:actorType ?type .
}
"""

_Q_LOCATIONS = """
PREFIX cameo: <http://example.org/cameo/>
SELECT DISTINCT ?loc ?district ?division ?lat ?lon
WHERE {
  ?loc a cameo:Location ;
       cameo:district ?district .
  OPTIONAL { ?loc cameo:division ?division }
  OPTIONAL { ?loc cameo:latitude  ?lat }
  OPTIONAL { ?loc cameo:longitude ?lon }
}
"""

_Q_EDGES = """
PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?rel ?obj
WHERE {
  {
    ?evt cameo:actor    ?obj . BIND("actor" AS ?rel)
  } UNION {
    ?evt cameo:target   ?obj . BIND("target" AS ?rel)
  } UNION {
    ?evt cameo:location ?obj . BIND("location" AS ?rel)
  }
}
"""

_Q_SAME_AS = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?a ?b WHERE { ?a owl:sameAs ?b }
"""


@dataclass
class KGGraph:
    """
    Exported knowledge graph in tensor-ready format.

    node_index: {uri → int}  — unified node ID space
    node_types: {uri → str}  — "event" | "actor" | "location"
    node_features: {uri → dict}  — feature dicts per node
    edges: list of (src_uri, rel_type, dst_uri)
    rel_types: {rel_str → int}  — relation type index
    """
    node_index:    dict = field(default_factory=dict)
    node_types:    dict = field(default_factory=dict)
    node_features: dict = field(default_factory=dict)
    edges:         list = field(default_factory=list)
    rel_index:     dict = field(default_factory=dict)

    @property
    def num_nodes(self) -> int:
        return len(self.node_index)

    @property
    def num_edges(self) -> int:
        return len(self.edges)

    @property
    def num_relations(self) -> int:
        return len(self.rel_index)


def _rows(result: Optional[dict]) -> list[dict]:
    if not result:
        return []
    return [
        {k: v.get("value", "") for k, v in row.items()}
        for row in result.get("results", {}).get("bindings", [])
    ]


def export_kg(endpoint: str = SPARQL_ENDPOINT) -> KGGraph:
    """
    Query BlazeGraph and build a KGGraph object.

    Returns a KGGraph with all nodes indexed and edges as triples.
    """
    from knowledge_graph.ingest import sparql_query

    kg = KGGraph()
    node_counter = [0]

    def _add_node(uri: str, ntype: str, features: dict = {}) -> int:
        if uri not in kg.node_index:
            kg.node_index[uri] = node_counter[0]
            kg.node_types[uri] = ntype
            kg.node_features[uri] = features
            node_counter[0] += 1
        return kg.node_index[uri]

    rel_counter = [0]
    def _rel_id(rel: str) -> int:
        if rel not in kg.rel_index:
            kg.rel_index[rel] = rel_counter[0]
            rel_counter[0] += 1
        return kg.rel_index[rel]

    logger.info("Exporting events…")
    for row in _rows(sparql_query(_Q_EVENTS, endpoint)):
        uri = row["evt"]
        _add_node(uri, "event", {
            "code":       row.get("code", ""),
            "bd_code":    row.get("bdCode", ""),
            "confidence": float(row.get("confidence", 0.5)),
            "date":       row.get("date", ""),
            "district":   row.get("district", ""),
        })

    logger.info("Exporting actors…")
    for row in _rows(sparql_query(_Q_ACTORS, endpoint)):
        uri = row["actor"]
        _add_node(uri, "actor", {
            "name": row.get("name", ""),
            "type": row.get("type", ""),
        })

    logger.info("Exporting locations…")
    for row in _rows(sparql_query(_Q_LOCATIONS, endpoint)):
        uri = row["loc"]
        lat = float(row["lat"]) if row.get("lat") else 0.0
        lon = float(row["lon"]) if row.get("lon") else 0.0
        _add_node(uri, "location", {
            "district": row.get("district", ""),
            "division": row.get("division", ""),
            "lat": lat,
            "lon": lon,
        })

    logger.info("Exporting edges…")
    for row in _rows(sparql_query(_Q_EDGES, endpoint)):
        src, rel, dst = row["evt"], row["rel"], row["obj"]
        if src in kg.node_index and dst in kg.node_index:
            kg.edges.append((src, rel, dst))
            _rel_id(rel)

    # Inverse edges for undirected GNN variants
    for src, rel, dst in list(kg.edges):
        inv_rel = f"{rel}_inv"
        kg.edges.append((dst, inv_rel, src))
        _rel_id(inv_rel)

    logger.info(
        "KG export complete: %d nodes, %d edges, %d relation types.",
        kg.num_nodes, kg.num_edges, kg.num_relations,
    )
    return kg


def to_pytorch_geometric(kg: KGGraph) -> dict:
    """
    Convert KGGraph to PyTorch Geometric HeteroData-compatible dict.

    Returns a dict that can be loaded with:
        from torch_geometric.data import HeteroData
        data = HeteroData(**exported_dict)

    Also returns edge_index tensors for homogeneous R-GCN training.
    """
    try:
        import torch
    except ImportError:
        raise ImportError("PyTorch not installed. Run: pip install torch")

    # Build edge_index: shape [2, num_edges]
    edge_srcs = [kg.node_index[s] for s, _, _ in kg.edges if s in kg.node_index]
    edge_dsts = [kg.node_index[d] for _, _, d in kg.edges if d in kg.node_index]
    edge_types = [kg.rel_index.get(r, 0) for _, r, _ in kg.edges]

    result = {
        "num_nodes":    kg.num_nodes,
        "num_edges":    kg.num_edges,
        "num_relations": kg.num_relations,
        "node_index":   kg.node_index,
        "node_types":   kg.node_types,
        "node_features": kg.node_features,
        "rel_index":    kg.rel_index,
        "edge_index":   torch.tensor([edge_srcs, edge_dsts], dtype=torch.long),
        "edge_type":    torch.tensor(edge_types, dtype=torch.long),
    }
    return result


def save_export(kg: KGGraph, out_dir: Path = Path("data/kg_export")) -> None:
    """Save KGGraph and PyG tensors to disk."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # Raw KG as JSON (for inspection)
    meta = {
        "num_nodes": kg.num_nodes,
        "num_edges": kg.num_edges,
        "num_relations": kg.num_relations,
        "node_types_summary": {
            t: sum(1 for v in kg.node_types.values() if v == t)
            for t in set(kg.node_types.values())
        },
        "rel_index": kg.rel_index,
    }
    (out_dir / "kg_meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )

    # Pickle full KGGraph
    with open(out_dir / "kg_graph.pkl", "wb") as f:
        pickle.dump(kg, f)

    logger.info("KG export saved to %s", out_dir)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-8s %(message)s")

    kg = export_kg()
    save_export(kg)
    print(f"Nodes: {kg.num_nodes}  Edges: {kg.num_edges}  Relations: {kg.num_relations}")
