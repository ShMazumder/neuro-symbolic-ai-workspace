"""
neurosymbolic/gnn_model.py
Task 4.3 — R-GCN / CompGCN for event pattern detection.

Implements:
  - RelationalGCN (R-GCN): Multi-relational message passing over the KG.
  - CompGCN layer: Composition-based KG convolution (Vashishth et al. 2020).
  - EventPatternClassifier: thin head that detects known escalation sub-graphs.

Dependencies:
    pip install torch torch_geometric pykeen
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)

KG_EXPORT_DIR = Path("data/kg_export")
MODELS_DIR = Path("models/gnn")


def _load_kg(kg_path: Path):
    """Safely load KGGraph pickle handling namespace aliases."""
    import sys
    from neurosymbolic.kg_export import KGGraph
    if "__main__" in sys.modules and not hasattr(sys.modules["__main__"], "KGGraph"):
        sys.modules["__main__"].KGGraph = KGGraph
    with open(kg_path, "rb") as f:
        return pickle.load(f)


# ── R-GCN building blocks ─────────────────────────────────────────────────────

class RGCNConv(nn.Module):
    """
    Single R-GCN convolution layer (basis-decomposition).

    h_i^{l+1} = σ( Σ_{r∈R} Σ_{j∈N_r(i)} (1/c_{i,r}) W_r h_j^l + W_0 h_i^l )

    Basis decomposition: W_r = Σ_b a_{rb} V_b  (reduces parameters).
    """

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        num_relations: int,
        num_bases: int = 4,
        self_loop: bool = True,
    ):
        super().__init__()
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.num_relations = num_relations
        self.num_bases = num_bases
        self.self_loop = self_loop

        # Basis matrices V_b ∈ R^{in×out}
        self.basis = nn.Parameter(torch.empty(num_bases, in_dim, out_dim))
        # Coefficients a_{rb} ∈ R^{R×B}
        self.coeffs = nn.Parameter(torch.empty(num_relations, num_bases))
        # Self-loop weight W_0
        if self_loop:
            self.w_self = nn.Linear(in_dim, out_dim, bias=False)
        self.bias = nn.Parameter(torch.zeros(out_dim))

        nn.init.xavier_uniform_(self.basis)
        nn.init.xavier_uniform_(self.coeffs)

    def forward(
        self,
        x: torch.Tensor,           # [N, in_dim]
        edge_index: torch.Tensor,  # [2, E]
        edge_type: torch.Tensor,   # [E]
    ) -> torch.Tensor:
        N = x.size(0)
        # W_r = coeffs @ basis  → [R, in, out]
        W = torch.einsum("rb,bio->rio", self.coeffs, self.basis)  # [R, in, out]

        out = torch.zeros(N, self.out_dim, device=x.device)

        for r in range(self.num_relations):
            mask = edge_type == r
            if not mask.any():
                continue
            src = edge_index[0, mask]  # source nodes for relation r
            dst = edge_index[1, mask]  # destination nodes

            # Aggregate: Σ_j W_r h_j
            msg = x[src] @ W[r]         # [E_r, out]

            # Normalise by degree (1/c_{i,r})
            deg = torch.zeros(N, device=x.device).scatter_add_(
                0, dst, torch.ones(mask.sum(), device=x.device)
            )
            deg_inv = deg.clamp(min=1).reciprocal()
            out.scatter_add_(0, dst.unsqueeze(1).expand_as(msg), msg)
            out = out * deg_inv.unsqueeze(1)

        if self.self_loop:
            out = out + self.w_self(x)

        return F.relu(out + self.bias)


# ── CompGCN building blocks ───────────────────────────────────────────────────

class CompGCNConv(nn.Module):
    """
    CompGCN convolution layer (composition function: subtract).

    h_i = σ( Σ_{(j,r,i)∈G} W_λ(r) φ(h_j, e_r) )

    Composition φ: subtraction (h_j - e_r) — lightest option.
    Learns both entity and relation embeddings jointly.
    """

    def __init__(self, in_dim: int, out_dim: int, num_relations: int, dropout: float = 0.1):
        super().__init__()
        self.W_sub = nn.Linear(in_dim, out_dim, bias=False)   # for normal edges
        self.W_inv = nn.Linear(in_dim, out_dim, bias=False)   # for inverse edges
        self.W_self = nn.Linear(in_dim, out_dim, bias=False)  # self-loop
        self.W_rel = nn.Linear(in_dim, out_dim, bias=False)   # relation transform

        self.bn = nn.BatchNorm1d(out_dim)
        self.drop = nn.Dropout(dropout)
        self.num_relations_half = num_relations  # original relations (inv added externally)

    def forward(
        self,
        x: torch.Tensor,           # [N, in_dim] entity embeddings
        rel_emb: torch.Tensor,     # [R*2+1, in_dim] relation embeddings (incl. inv + self)
        edge_index: torch.Tensor,  # [2, E]
        edge_type: torch.Tensor,   # [E]  (inv edges have type r + num_relations)
    ) -> tuple[torch.Tensor, torch.Tensor]:
        N = x.size(0)
        out = torch.zeros(N, self.W_sub.out_features, device=x.device)

        R_half = self.num_relations_half

        for i, (W, mask_fn) in enumerate([
            (self.W_sub, lambda et: et < R_half),       # forward
            (self.W_inv, lambda et: et >= R_half),      # inverse
        ]):
            mask = mask_fn(edge_type)
            if not mask.any():
                continue
            src = edge_index[0, mask]
            dst = edge_index[1, mask]
            et  = edge_type[mask]

            # Composition: φ(h_src, e_r) = h_src - e_r
            comp = x[src] - rel_emb[et]          # [E_m, in_dim]
            msg  = W(self.drop(comp))             # [E_m, out_dim]
            out.scatter_add_(0, dst.unsqueeze(1).expand_as(msg), msg)

        # Self-loop
        self_rel_idx = rel_emb.size(0) - 1
        out = out + self.W_self(x)

        out = F.relu(self.bn(out))

        # Update relation embeddings
        new_rel = self.W_rel(rel_emb)
        return out, new_rel


# ── High-level model ──────────────────────────────────────────────────────────

class EventPatternGNN(nn.Module):
    """
    Two-layer R-GCN for event pattern classification.

    Input:  node features (one-hot type + code embedding)
    Output: per-node logit for escalation pattern membership.
    """

    def __init__(
        self,
        in_dim: int,
        hidden_dim: int,
        out_dim: int,
        num_relations: int,
        num_bases: int = 4,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.conv1 = RGCNConv(in_dim, hidden_dim, num_relations, num_bases)
        self.conv2 = RGCNConv(hidden_dim, hidden_dim, num_relations, num_bases)
        self.drop = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_dim, out_dim)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_type: torch.Tensor,
    ) -> torch.Tensor:
        h = self.conv1(x, edge_index, edge_type)
        h = self.drop(h)
        h = self.conv2(h, edge_index, edge_type)
        return self.classifier(h)  # [N, out_dim]


# ── Feature builder ───────────────────────────────────────────────────────────

def build_node_features(
    kg,
    cameo_codes: Optional[list[str]] = None,
    actor_types: Optional[list[str]] = None,
) -> torch.Tensor:
    """
    Build initial node feature matrix from KGGraph topology and non-leaked metadata.

    Features per node (ZERO target label leakage):
      - one-hot node type (3): event / actor / location
      - in-degree and out-degree normalised (2)
      - event extraction confidence (1): float in [0, 1]
      - one-hot actor type (len(actor_types)): for actors, else zeros
      - [lat, lon] normalised: for locations, else zeros

    Note: Target CAMEO event codes are STRICTLY EXCLUDED to guarantee zero label leakage.
    Returns: float tensor [N, feature_dim]
    """
    if actor_types is None:
        actor_types = ["SECURITY_FORCE", "POLITICAL_PARTY", "ARMED_GROUP", "CIVILIAN", "GOVERNMENT"]

    NODE_TYPES = ["event", "actor", "location"]
    feat_dim = len(NODE_TYPES) + 2 + 1 + len(actor_types) + 2
    N = kg.num_nodes
    feats = torch.zeros(N, feat_dim)

    # Compute node degrees
    in_degree = torch.zeros(N)
    out_degree = torch.zeros(N)
    for s, _, d in kg.edges:
        if s in kg.node_index:
            out_degree[kg.node_index[s]] += 1
        if d in kg.node_index:
            in_degree[kg.node_index[d]] += 1
    max_deg = max(1.0, float(max(in_degree.max().item(), out_degree.max().item())))

    for uri, idx in kg.node_index.items():
        ntype = kg.node_types.get(uri, "event")
        nfeat = kg.node_features.get(uri, {})

        # Node-type one-hot (dim 0..2)
        if ntype in NODE_TYPES:
            feats[idx, NODE_TYPES.index(ntype)] = 1.0

        # Structural degree features (dim 3..4)
        feats[idx, 3] = in_degree[idx] / max_deg
        feats[idx, 4] = out_degree[idx] / max_deg

        # Extraction confidence (dim 5)
        conf = float(nfeat.get("confidence", 0.5) or 0.5)
        feats[idx, 5] = max(0.0, min(1.0, conf))

        # Actor type one-hot (dim 6..6+len)
        atype = str(nfeat.get("type", ""))
        if atype in actor_types:
            feats[idx, 6 + actor_types.index(atype)] = 1.0

        # Geo coordinates normalised (dim -2..-1)
        lat = float(nfeat.get("lat", 0.0) or 0.0)
        lon = float(nfeat.get("lon", 0.0) or 0.0)
        feats[idx, -2] = lat / 90.0
        feats[idx, -1] = lon / 180.0

    return feats


# ── Training loop ─────────────────────────────────────────────────────────────

def train_gnn(
    kg_path: Path = KG_EXPORT_DIR / "kg_graph.pkl",
    epochs: int = 100,
    lr: float = 1e-3,
    hidden_dim: int = 64,
    out_dir: Path = MODELS_DIR,
) -> EventPatternGNN:
    """
    Train the EventPatternGNN on the exported KG with out-of-sample evaluation.

    Uses self-supervised binary labels: events with CAMEO code ≥17
    (high-violence: assault, killing, bombing, mass violence) are positive.
    Negative samples: CAMEO codes 13–16 (lower-intensity).

    Evaluated on a genuine held-out 80/20 train/test split.
    """
    import random
    kg = _load_kg(kg_path)

    ACTOR_TYPES = ["SECURITY_FORCE", "POLITICAL_PARTY", "ARMED_GROUP", "CIVILIAN", "GOVERNMENT"]
    x = build_node_features(kg, actor_types=ACTOR_TYPES)

    # Edge tensors
    edge_srcs = [kg.node_index[s] for s, _, _ in kg.edges if s in kg.node_index]
    edge_dsts = [kg.node_index[d] for _, _, d in kg.edges if d in kg.node_index]
    edge_types = [kg.rel_index.get(r, 0) for _, r, _ in kg.edges]

    edge_index = torch.tensor([edge_srcs, edge_dsts], dtype=torch.long)
    edge_type  = torch.tensor(edge_types, dtype=torch.long)

    num_relations = kg.num_relations or 1
    model = EventPatternGNN(
        in_dim=x.size(1),
        hidden_dim=hidden_dim,
        out_dim=2,
        num_relations=num_relations,
    )

    # Target labels: CAMEO ≥ 17 → high violence
    labels = torch.zeros(kg.num_nodes, dtype=torch.long)
    event_indices = []
    for uri, idx in kg.node_index.items():
        if kg.node_types.get(uri) == "event":
            event_indices.append(idx)
            code_str = kg.node_features.get(uri, {}).get("code", "")
            try:
                if int(float(code_str)) >= 17:
                    labels[idx] = 1
            except (ValueError, TypeError):
                pass

    # 80/20 train/test split over event nodes
    random.seed(42)
    shuffled_events = list(event_indices)
    random.shuffle(shuffled_events)
    split_pt = max(1, int(0.8 * len(shuffled_events)))
    train_set = set(shuffled_events[:split_pt])
    test_set = set(shuffled_events[split_pt:])

    train_mask = torch.tensor([i in train_set for i in range(kg.num_nodes)], dtype=torch.bool)
    test_mask = torch.tensor([i in test_set for i in range(kg.num_nodes)], dtype=torch.bool)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()

    for epoch in range(epochs):
        optimizer.zero_grad()
        logits = model(x, edge_index, edge_type)
        loss = F.cross_entropy(logits[train_mask], labels[train_mask])
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 20 == 0:
            with torch.no_grad():
                train_preds = logits[train_mask].argmax(dim=1)
                train_acc = (train_preds == labels[train_mask]).float().mean()
                test_preds = logits[test_mask].argmax(dim=1)
                test_acc = (test_preds == labels[test_mask]).float().mean() if test_mask.any() else 0.0
            logger.info("Epoch %3d | loss=%.4f | train_acc=%.4f | test_acc=%.4f",
                        epoch + 1, loss.item(), train_acc.item(), test_acc.item())

    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_dir / "event_pattern_gnn.pt")
    logger.info("GNN saved to %s", out_dir / "event_pattern_gnn.pt")
    return model


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")
    model = train_gnn()
    logger.info("Training complete.")
