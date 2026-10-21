"""
neurosymbolic/explain.py
Task 4.8 — Explainability module: trace predictions to source triples + articles.

Provides human-readable explanations for:
  1. GNN event pattern predictions → which graph neighbourhood triggered it
  2. Escalation forecasts → which prior events caused the prediction
  3. Anomaly alerts → which events form the statistical spike

Each explanation is grounded in:
  - Source triples (subject, predicate, object) from the KG
  - Source article URLs and sentence offsets (PROV-O provenance)
  - Symbolic rules that were activated or violated

Dependencies:
    pip install torch torch_geometric
"""

from __future__ import annotations

import json
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import torch

logger = logging.getLogger(__name__)

KG_EXPORT_DIR  = Path("data/kg_export")
PROCESSED_DIR  = Path("data/processed")
SPARQL_ENDPOINT = "http://localhost:9999/blazegraph/sparql"

# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class Evidence:
    triple:       tuple[str, str, str]   # (subject_uri, predicate, object_uri)
    article_url:  Optional[str] = None
    sentence_idx: Optional[int] = None
    sentence_text: Optional[str] = None
    confidence:   float = 1.0


@dataclass
class Explanation:
    prediction_type: str          # "gnn_pattern" | "escalation" | "anomaly"
    target:          str          # node URI, district name, or alert ID
    label:           str          # human-readable predicted class / alert
    confidence:      float
    supporting_evidence: list[Evidence] = field(default_factory=list)
    contradicting_evidence: list[Evidence] = field(default_factory=list)
    symbolic_rules_fired:  list[str] = field(default_factory=list)
    symbolic_rules_blocked: list[str] = field(default_factory=list)
    narrative:       str = ""

    def to_dict(self) -> dict:
        return {
            "prediction_type": self.prediction_type,
            "target":          self.target,
            "label":           self.label,
            "confidence":      self.confidence,
            "supporting_evidence": [
                {
                    "triple": list(e.triple),
                    "article_url": e.article_url,
                    "sentence_idx": e.sentence_idx,
                    "sentence_text": e.sentence_text,
                    "confidence": e.confidence,
                }
                for e in self.supporting_evidence
            ],
            "contradicting_evidence": [
                {
                    "triple": list(e.triple),
                    "article_url": e.article_url,
                    "sentence_idx": e.sentence_idx,
                    "sentence_text": e.sentence_text,
                    "confidence": e.confidence,
                }
                for e in self.contradicting_evidence
            ],
            "symbolic_rules_fired":   self.symbolic_rules_fired,
            "symbolic_rules_blocked": self.symbolic_rules_blocked,
            "narrative":              self.narrative,
        }


# ── Provenance retrieval ───────────────────────────────────────────────────────

_Q_PROVENANCE = """
PREFIX cameo: <http://example.org/cameo/>
PREFIX prov:  <http://www.w3.org/ns/prov#>
SELECT ?evt ?articleUrl ?sentenceIdx ?sentenceText ?confidence
WHERE {{
  VALUES ?evt {{ <{uri}> }}
  OPTIONAL {{ ?evt prov:wasDerivedFrom ?src .
               ?src cameo:articleUrl   ?articleUrl ;
                    cameo:sentenceIdx  ?sentenceIdx .
               OPTIONAL {{ ?src cameo:sentenceText ?sentenceText }}
            }}
  OPTIONAL {{ ?evt cameo:confidence ?confidence }}
}}
"""

_Q_NEIGHBOURS = """
PREFIX cameo: <http://example.org/cameo/>
SELECT ?rel ?obj ?objType
WHERE {{
  VALUES ?evt {{ <{uri}> }}
  {{
    ?evt cameo:actor    ?obj . BIND("actor"    AS ?rel) BIND("actor"    AS ?objType)
  }} UNION {{
    ?evt cameo:target   ?obj . BIND("target"   AS ?rel) BIND("actor"    AS ?objType)
  }} UNION {{
    ?evt cameo:location ?obj . BIND("location" AS ?rel) BIND("location" AS ?objType)
  }}
}}
"""


def _fetch_provenance(uri: str, endpoint: str = SPARQL_ENDPOINT) -> list[Evidence]:
    """Query BlazeGraph for provenance of a single event URI."""
    try:
        from knowledge_graph.ingest import sparql_query
        result = sparql_query(_Q_PROVENANCE.format(uri=uri), endpoint)
        rows = result.get("results", {}).get("bindings", []) if result else []
        evidences = []
        for row in rows:
            ev = Evidence(
                triple=(uri, "prov:wasDerivedFrom", row.get("articleUrl", {}).get("value", "")),
                article_url=row.get("articleUrl", {}).get("value"),
                sentence_idx=(
                    int(row["sentenceIdx"]["value"]) if "sentenceIdx" in row else None
                ),
                sentence_text=row.get("sentenceText", {}).get("value"),
                confidence=float(row["confidence"]["value"]) if "confidence" in row else 1.0,
            )
            evidences.append(ev)
        return evidences
    except Exception as exc:
        logger.warning("Provenance fetch failed for %s: %s", uri, exc)
        return []


def _fetch_neighbours(uri: str, endpoint: str = SPARQL_ENDPOINT) -> list[Evidence]:
    """Fetch 1-hop neighbourhood triples for a node URI."""
    try:
        from knowledge_graph.ingest import sparql_query
        result = sparql_query(_Q_NEIGHBOURS.format(uri=uri), endpoint)
        rows = result.get("results", {}).get("bindings", []) if result else []
        return [
            Evidence(
                triple=(uri, row["rel"]["value"], row["obj"]["value"]),
            )
            for row in rows
        ]
    except Exception as exc:
        logger.warning("Neighbour fetch failed for %s: %s", uri, exc)
        return []


# ── GNN prediction explainer ──────────────────────────────────────────────────

def explain_gnn_prediction(
    node_uri: str,
    logits: torch.Tensor,         # [num_classes] raw logits for this node
    kg_path: Path = KG_EXPORT_DIR / "kg_graph.pkl",
    endpoint: str = SPARQL_ENDPOINT,
    top_k_neighbours: int = 5,
) -> Explanation:
    """
    Explain a GNN escalation-pattern prediction for a single event node.

    1. Extracts confidence from logits.
    2. Fetches 1-hop neighbours from KG (the graph context used by R-GCN).
    3. Fetches provenance (source article, sentence).
    4. Identifies symbolic rules that apply.
    5. Composes a natural-language narrative.
    """
    probs  = torch.softmax(logits, dim=0)
    pred   = probs.argmax().item()
    conf   = probs[pred].item()
    label  = "HIGH_VIOLENCE_PATTERN" if pred == 1 else "NORMAL_PATTERN"

    # Graph evidence: 1-hop neighbourhood
    neighbour_evidence = _fetch_neighbours(node_uri, endpoint)[:top_k_neighbours]
    prov_evidence = _fetch_provenance(node_uri, endpoint)

    # Load KG features for this node
    symbolic_rules = []
    try:
        with open(kg_path, "rb") as f:
            kg = pickle.load(f)
        feat = kg.node_features.get(node_uri, {})
        code = feat.get("code", "?")
        district = feat.get("district", "?")
        date = feat.get("date", "?")

        # Symbolic rule: CAMEO ≥ 17 → always flag
        try:
            if int(float(str(code))) >= 17:
                symbolic_rules.append(f"Rule: CAMEO code {code} ≥ 17 → classified HIGH_VIOLENCE by definition.")
        except (ValueError, TypeError):
            pass
    except Exception:
        feat, code, district, date = {}, "?", "?", "?"

    narrative = (
        f"Event <{node_uri}> was classified as **{label}** "
        f"(confidence={conf:.1%}) by the R-GCN model. "
        f"CAMEO code: {code}. Location: {district}. Date: {date}. "
        f"The model's decision was influenced by {len(neighbour_evidence)} "
        f"neighbouring graph nodes (actors, targets, locations). "
    )
    if prov_evidence:
        urls = list({e.article_url for e in prov_evidence if e.article_url})
        narrative += f"This event was extracted from: {', '.join(urls[:2])}."
    if symbolic_rules:
        narrative += " " + symbolic_rules[0]

    return Explanation(
        prediction_type="gnn_pattern",
        target=node_uri,
        label=label,
        confidence=round(conf, 4),
        supporting_evidence=neighbour_evidence + prov_evidence,
        symbolic_rules_fired=symbolic_rules,
        narrative=narrative,
    )


# ── Escalation forecast explainer ─────────────────────────────────────────────

def explain_escalation_forecast(
    district: str,
    window_codes: list[int],
    predicted_code: int,
    confidence: float,
    symbolic_valid: bool,
    symbolic_reason: str,
    endpoint: str = SPARQL_ENDPOINT,
) -> Explanation:
    """
    Explain an escalation forecast for a district.

    Fetches the most recent events from BlazeGraph for that district
    to provide concrete source triples.
    """
    _Q_DISTRICT_EVENTS = f"""
PREFIX cameo: <http://example.org/cameo/>
SELECT ?evt ?code ?date ?articleUrl
WHERE {{
  ?evt a cameo:ViolenceEvent ;
       cameo:code ?code ;
       cameo:date ?date ;
       cameo:location ?loc .
  ?loc cameo:district "{district}" .
  OPTIONAL {{
    ?evt <http://www.w3.org/ns/prov#wasDerivedFrom> ?src .
    ?src cameo:articleUrl ?articleUrl .
  }}
}}
ORDER BY DESC(?date)
LIMIT 10
"""
    evidences: list[Evidence] = []
    try:
        from knowledge_graph.ingest import sparql_query
        result = sparql_query(_Q_DISTRICT_EVENTS, endpoint)
        rows = result.get("results", {}).get("bindings", []) if result else []
        for row in rows:
            evidences.append(Evidence(
                triple=(
                    row.get("evt", {}).get("value", ""),
                    "cameo:code",
                    row.get("code", {}).get("value", ""),
                ),
                article_url=row.get("articleUrl", {}).get("value"),
                confidence=1.0,
            ))
    except Exception as exc:
        logger.warning("District event fetch failed: %s", exc)

    escalation = predicted_code > (max(window_codes) if window_codes else 13)
    label = f"ESCALATION→CAMEO_{predicted_code}" if escalation else f"STABLE_CAMEO_{predicted_code}"

    rules_fired  = [symbolic_reason] if symbolic_valid else []
    rules_blocked = [] if symbolic_valid else [symbolic_reason]

    narrative = (
        f"For **{district}**, the BiLSTM model analysed the last {len(window_codes)} "
        f"events (CAMEO codes: {window_codes}) and predicts the next event will be "
        f"**CAMEO {predicted_code}** (confidence={confidence:.1%}). "
        f"{'⚠️ ESCALATION DETECTED. ' if escalation else '✅ No escalation. '}"
        f"Symbolic validation: {symbolic_reason}"
    )

    return Explanation(
        prediction_type="escalation",
        target=district,
        label=label,
        confidence=confidence,
        supporting_evidence=evidences,
        symbolic_rules_fired=rules_fired,
        symbolic_rules_blocked=rules_blocked,
        narrative=narrative,
    )


# ── Anomaly alert explainer ───────────────────────────────────────────────────

def explain_anomaly_alert(
    alert_type: str,
    dimension: str,
    z_score: float,
    recent_count: int,
    baseline_avg: float,
    window_days: int,
    reference_date: str,
    endpoint: str = SPARQL_ENDPOINT,
) -> Explanation:
    """
    Explain a violence anomaly alert (spike vs baseline).
    """
    severity = (
        "CRITICAL" if z_score >= 4 else
        "HIGH" if z_score >= 3 else
        "MEDIUM" if z_score >= 2 else "LOW"
    )

    narrative = (
        f"**{severity} ANOMALY** detected in *{dimension}* ({alert_type}). "
        f"In the last {window_days} days ({reference_date}), there were "
        f"**{recent_count} events** vs a baseline average of "
        f"**{baseline_avg:.1f}** (Z-score={z_score:.2f}). "
        f"This is a {z_score:.1f}σ deviation — statistically {'very ' if z_score >= 3 else ''}unusual."
    )

    return Explanation(
        prediction_type="anomaly",
        target=dimension,
        label=f"ANOMALY_{severity}",
        confidence=min(1.0, (z_score - 2) / 4 + 0.5) if z_score >= 2 else 0.3,
        symbolic_rules_fired=[
            f"Rule: Z-score {z_score:.2f} ≥ threshold 2.0 → alert raised."
        ],
        narrative=narrative,
    )


# ── Batch explainer ───────────────────────────────────────────────────────────

def explain_batch_gnn(
    node_uris: list[str],
    logits: torch.Tensor,        # [N, num_classes]
    kg_path: Path = KG_EXPORT_DIR / "kg_graph.pkl",
    endpoint: str = SPARQL_ENDPOINT,
    out_path: Path = PROCESSED_DIR / "explanations_gnn.json",
) -> list[Explanation]:
    """Explain GNN predictions for a list of nodes and save to JSON."""
    explanations = []
    for i, uri in enumerate(node_uris):
        exp = explain_gnn_prediction(uri, logits[i], kg_path, endpoint)
        explanations.append(exp)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps([e.to_dict() for e in explanations], indent=2),
        encoding="utf-8",
    )
    logger.info("GNN explanations saved: %d → %s", len(explanations), out_path)
    return explanations


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")

    # Demo: explain a synthetic anomaly alert
    exp = explain_anomaly_alert(
        alert_type="district_spike",
        dimension="Dhaka",
        z_score=3.7,
        recent_count=42,
        baseline_avg=11.3,
        window_days=7,
        reference_date="2026-10-21",
    )
    print(exp.narrative)
    print(json.dumps(exp.to_dict(), indent=2))
