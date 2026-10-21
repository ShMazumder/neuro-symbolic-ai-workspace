"""
neurosymbolic/hybrid.py
Task 4.9 — Hybrid inference: symbolic constraints filter neural predictions.

This module is the integration layer of the neuro-symbolic system.
It combines:
  1. Neural outputs (GNN event patterns, LSTM escalation probabilities)
  2. Symbolic rules (OWL/CAMEO ontology constraints, domain rules)

into final decisions that are both statistically grounded and logically valid.

Symbolic constraint categories
───────────────────────────────
  A. Ontological constraints  — CAMEO code taxonomy rules
  B. Temporal constraints     — events must follow time ordering
  C. Geographic constraints   — BD administrative hierarchy
  D. Actor-event constraints  — actor types allowed for each CAMEO code
  E. Confidence thresholds    — neural predictions below τ are suppressed

Dependencies:
    pip install torch
"""

from __future__ import annotations

import json
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import torch
import torch.nn.functional as F

logger = logging.getLogger(__name__)

KG_EXPORT_DIR = Path("data/kg_export")
PROCESSED_DIR = Path("data/processed")

# ── Symbolic rule definitions ─────────────────────────────────────────────────

# A. CAMEO code taxonomy — valid escalation transitions
#    Key: from_code, Value: allowed next codes (can go to any of these or stay)
VALID_TRANSITIONS: dict[int, set[int]] = {
    13: {13, 14, 15, 16, 17},           # Threaten → up to Coerce
    14: {13, 14, 15, 16, 17},           # Protest
    15: {14, 15, 16, 17, 18},           # Exhibit Force
    16: {15, 16, 17, 18},               # Reduce Relations
    17: {16, 17, 18, 19},               # Coerce
    18: {17, 18, 19, 20},               # Assault
    19: {18, 19, 20},                   # Fight
    20: {19, 20},                       # Mass Violence — no downward jump unless ceasefire
}

# B. Actor-event type constraints
#    Key: CAMEO code, Value: set of allowed perpetrator actor types
ACTOR_CODE_CONSTRAINTS: dict[int, set[str]] = {
    18: {"SECURITY_FORCE", "ARMED_GROUP", "POLITICAL_PARTY"},
    19: {"SECURITY_FORCE", "ARMED_GROUP"},
    20: {"SECURITY_FORCE", "ARMED_GROUP"},
}

# C. Minimum confidence threshold for neural predictions
NEURAL_CONFIDENCE_THRESHOLD = 0.35

# D. Geographic hierarchy — valid division→district relationships (sample)
BD_GEO_HIERARCHY: dict[str, set[str]] = {
    "Dhaka":      {"Dhaka", "Gazipur", "Narayanganj", "Narsingdi", "Manikganj"},
    "Chittagong": {"Chittagong", "Cox's Bazar", "Rangamati", "Bandarban", "Khagrachari"},
    "Rajshahi":   {"Rajshahi", "Bogura", "Naogaon", "Natore", "Chapainawabganj"},
    "Khulna":     {"Khulna", "Jessore", "Satkhira", "Bagerhat", "Narail"},
    "Sylhet":     {"Sylhet", "Habiganj", "Moulvibazar", "Sunamganj"},
    "Barisal":    {"Barisal", "Bhola", "Patuakhali", "Jhalokati", "Pirojpur"},
    "Rangpur":    {"Rangpur", "Dinajpur", "Gaibandha", "Kurigram", "Lalmonirhat"},
    "Mymensingh": {"Mymensingh", "Jamalpur", "Netrokona", "Sherpur"},
}


# ── Constraint violation record ───────────────────────────────────────────────

@dataclass
class ConstraintViolation:
    rule_id:   str
    rule_type: str   # "ontological" | "temporal" | "geographic" | "actor" | "confidence"
    description: str
    severity:  str   # "hard" (reject) | "soft" (penalise)


@dataclass
class HybridDecision:
    """
    Final decision from the hybrid neuro-symbolic inference engine.
    """
    event_uri:      str
    neural_code:    int          # raw neural prediction
    final_code:     int          # after symbolic filtering
    neural_conf:    float
    final_conf:     float
    accepted:       bool         # False if hard-rejected
    violations:     list[ConstraintViolation] = field(default_factory=list)
    corrections:    list[str]    = field(default_factory=list)
    explanation:    str = ""

    def to_dict(self) -> dict:
        return {
            "event_uri":   self.event_uri,
            "neural_code": self.neural_code,
            "final_code":  self.final_code,
            "neural_conf": self.neural_conf,
            "final_conf":  self.final_conf,
            "accepted":    self.accepted,
            "violations":  [
                {"rule_id": v.rule_id, "type": v.rule_type,
                 "description": v.description, "severity": v.severity}
                for v in self.violations
            ],
            "corrections":  self.corrections,
            "explanation":  self.explanation,
        }


# ── Constraint checkers ────────────────────────────────────────────────────────

def _check_confidence(
    neural_code: int,
    conf: float,
) -> Optional[ConstraintViolation]:
    if conf < NEURAL_CONFIDENCE_THRESHOLD:
        return ConstraintViolation(
            rule_id="C-CONF-01",
            rule_type="confidence",
            description=(
                f"Neural confidence {conf:.2%} below threshold "
                f"{NEURAL_CONFIDENCE_THRESHOLD:.2%} for code {neural_code}."
            ),
            severity="soft",
        )
    return None


def _check_ontological_transition(
    prev_code: Optional[int],
    neural_code: int,
) -> Optional[ConstraintViolation]:
    if prev_code is None:
        return None
    allowed = VALID_TRANSITIONS.get(prev_code, set(range(13, 21)))
    if neural_code not in allowed:
        return ConstraintViolation(
            rule_id="C-ONTO-01",
            rule_type="ontological",
            description=(
                f"CAMEO transition {prev_code}→{neural_code} is not in valid "
                f"transition set {sorted(allowed)}."
            ),
            severity="hard",
        )
    return None


def _check_actor_constraint(
    neural_code: int,
    actor_type: Optional[str],
) -> Optional[ConstraintViolation]:
    if neural_code not in ACTOR_CODE_CONSTRAINTS:
        return None
    allowed = ACTOR_CODE_CONSTRAINTS[neural_code]
    if actor_type and actor_type not in allowed:
        return ConstraintViolation(
            rule_id="C-ACTOR-01",
            rule_type="actor",
            description=(
                f"Actor type '{actor_type}' is not permitted for CAMEO code {neural_code}. "
                f"Allowed: {sorted(allowed)}."
            ),
            severity="soft",
        )
    return None


def _check_geographic(
    division: Optional[str],
    district: Optional[str],
) -> Optional[ConstraintViolation]:
    if not division or not district:
        return None
    allowed = BD_GEO_HIERARCHY.get(division, set())
    if allowed and district not in allowed:
        return ConstraintViolation(
            rule_id="C-GEO-01",
            rule_type="geographic",
            description=(
                f"District '{district}' does not belong to division '{division}' "
                f"in Bangladesh administrative hierarchy."
            ),
            severity="soft",
        )
    return None


# ── Hybrid inference engine ────────────────────────────────────────────────────

class HybridInferenceEngine:
    """
    Core neuro-symbolic inference engine.

    Workflow per event:
      1. Accept neural CAMEO code prediction + confidence.
      2. Run symbolic constraint checkers.
      3. Hard violations → reject + fallback to last valid code.
      4. Soft violations → penalise confidence, accept with warning.
      5. Return HybridDecision with full audit trail.
    """

    def __init__(self, confidence_threshold: float = NEURAL_CONFIDENCE_THRESHOLD):
        self.conf_threshold = confidence_threshold

    def infer(
        self,
        event_uri: str,
        neural_logits: torch.Tensor,    # [num_codes] raw logits
        prev_code: Optional[int] = None,
        actor_type: Optional[str] = None,
        division: Optional[str] = None,
        district: Optional[str] = None,
    ) -> HybridDecision:
        """
        Run hybrid inference for a single event node.

        Returns a HybridDecision with the final accepted CAMEO code.
        """
        from neurosymbolic.forecasting import IDX_TO_CAMEO_CODE, NUM_CODES

        probs = torch.softmax(neural_logits[:NUM_CODES], dim=0)
        top_idx  = probs.argmax().item()
        neural_code = IDX_TO_CAMEO_CODE.get(top_idx, 17)
        neural_conf = probs[top_idx].item()

        # Run all constraints
        violations: list[ConstraintViolation] = []
        corrections: list[str] = []

        v = _check_confidence(neural_code, neural_conf)
        if v: violations.append(v)

        v = _check_ontological_transition(prev_code, neural_code)
        if v: violations.append(v)

        v = _check_actor_constraint(neural_code, actor_type)
        if v: violations.append(v)

        v = _check_geographic(division, district)
        if v: violations.append(v)

        # Determine final decision
        hard_violations = [v for v in violations if v.severity == "hard"]
        soft_violations = [v for v in violations if v.severity == "soft"]

        if hard_violations:
            # Fallback: use previous code or nearest valid transition
            final_code = prev_code if prev_code else 17
            allowed = VALID_TRANSITIONS.get(prev_code or 17, {17})
            # Pick nearest valid code to neural prediction
            final_code = min(allowed, key=lambda c: abs(c - neural_code))
            final_conf = neural_conf * 0.5  # penalised
            accepted = False
            corrections.append(
                f"Hard violation {hard_violations[0].rule_id}: "
                f"reverted from CAMEO {neural_code} to CAMEO {final_code}."
            )
        else:
            final_code = neural_code
            # Penalise for soft violations
            penalty = 0.05 * len(soft_violations)
            final_conf = max(0.0, neural_conf - penalty)
            accepted = final_conf >= self.conf_threshold
            if soft_violations:
                corrections.append(
                    f"{len(soft_violations)} soft violation(s) — confidence penalised by "
                    f"{penalty:.0%}."
                )

        narrative = (
            f"Event <{event_uri}>: neural prediction CAMEO {neural_code} "
            f"(conf={neural_conf:.1%}) → final CAMEO {final_code} "
            f"(conf={final_conf:.1%}). "
            f"{'ACCEPTED' if accepted else 'REJECTED'}. "
            f"{len(violations)} constraint(s) checked "
            f"({len(hard_violations)} hard, {len(soft_violations)} soft)."
        )

        return HybridDecision(
            event_uri=event_uri,
            neural_code=neural_code,
            final_code=final_code,
            neural_conf=round(neural_conf, 4),
            final_conf=round(final_conf, 4),
            accepted=accepted,
            violations=violations,
            corrections=corrections,
            explanation=narrative,
        )


# ── Batch runner ──────────────────────────────────────────────────────────────

def run_hybrid_inference_batch(
    kg_path: Path = KG_EXPORT_DIR / "kg_graph.pkl",
    gnn_model_path: Optional[Path] = Path("models/gnn/event_pattern_gnn.pt"),
    out_path: Path = PROCESSED_DIR / "hybrid_decisions.json",
) -> list[HybridDecision]:
    """
    Run hybrid inference over all event nodes in the KG.

    Loads the trained GNN, runs forward pass, applies symbolic constraints,
    and saves decisions to JSON.
    """
    from neurosymbolic.gnn_model import EventPatternGNN, build_node_features
    from neurosymbolic.forecasting import CAMEO_CODE_TO_IDX, NUM_CODES

    with open(kg_path, "rb") as f:
        kg = pickle.load(f)

    CAMEO_CODES  = [str(c) for c in range(13, 21)]
    ACTOR_TYPES  = ["SECURITY_FORCE", "POLITICAL_PARTY", "ARMED_GROUP", "CIVILIAN", "GOVERNMENT"]

    x = build_node_features(kg, CAMEO_CODES, ACTOR_TYPES)
    edge_srcs  = [kg.node_index[s] for s, _, _ in kg.edges if s in kg.node_index]
    edge_dsts  = [kg.node_index[d] for _, _, d in kg.edges if d in kg.node_index]
    edge_types = [kg.rel_index.get(r, 0) for _, r, _ in kg.edges]
    edge_index = torch.tensor([edge_srcs, edge_dsts], dtype=torch.long)
    edge_type  = torch.tensor(edge_types, dtype=torch.long)

    model = EventPatternGNN(
        in_dim=x.size(1),
        hidden_dim=64,
        out_dim=2,
        num_relations=kg.num_relations or 1,
    )
    if gnn_model_path and gnn_model_path.exists():
        model.load_state_dict(torch.load(gnn_model_path, map_location="cpu"))
        logger.info("Loaded GNN from %s", gnn_model_path)

    model.eval()
    with torch.no_grad():
        logits = model(x, edge_index, edge_type)   # [N, 2] — binary

    # Expand to NUM_CODES logits using code features (approximation)
    # For a full production system, the GNN head would output NUM_CODES logits.
    # Here we synthesise code logits from binary + node code feature.
    engine = HybridInferenceEngine()
    decisions: list[HybridDecision] = []

    idx_to_uri = {v: k for k, v in kg.node_index.items()}

    for uri, node_idx in kg.node_index.items():
        if kg.node_types.get(uri) != "event":
            continue
        feat      = kg.node_features.get(uri, {})
        code_str  = feat.get("code", "17")
        actor     = feat.get("actor_type")
        district  = feat.get("district")

        # Synthesise per-code logits from binary escalation logit
        esc_logit = logits[node_idx, 1].item()
        code_logits = torch.zeros(NUM_CODES)
        try:
            base_code = int(float(code_str))
            base_idx  = max(0, min(base_code - 13, NUM_CODES - 1))
        except (ValueError, TypeError):
            base_idx = 4  # default to code 17
        code_logits[base_idx] = 2.0 + esc_logit  # boost predicted code

        decision = engine.infer(
            event_uri=uri,
            neural_logits=code_logits,
            actor_type=actor,
            district=district,
        )
        decisions.append(decision)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps([d.to_dict() for d in decisions], indent=2),
        encoding="utf-8",
    )
    logger.info(
        "Hybrid inference complete: %d decisions → %s  "
        "(accepted=%d, rejected=%d)",
        len(decisions), out_path,
        sum(1 for d in decisions if d.accepted),
        sum(1 for d in decisions if not d.accepted),
    )
    return decisions


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")

    # Demo: single-event inference with synthetic logits
    engine = HybridInferenceEngine()
    fake_logits = torch.tensor([0.1, 0.2, 0.5, 0.8, 3.2, 0.3, 0.1, 0.0])  # peaks at code 17
    decision = engine.infer(
        event_uri="http://example.org/event/demo_001",
        neural_logits=fake_logits,
        prev_code=16,
        actor_type="SECURITY_FORCE",
        district="Dhaka",
        division="Dhaka",
    )
    print(decision.explanation)
    print(json.dumps(decision.to_dict(), indent=2))
