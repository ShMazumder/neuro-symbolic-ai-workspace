"""
nlp/hier_nesy/soft_constraint_loss.py
Paper 2: hier-nesy-bd (Hierarchical Neuro-Symbolic Event Extraction)

Implements differentiable Soft Constraint Loss:
    L = L_CE + lambda_hier * L_hier + lambda_logic * L_logic

1. L_CE: Multi-task cross-entropy across all 4 tiers + context head.
2. L_hier: Hierarchical conditional probability consistency penalties:
   - P(violence) <= P(event)
   - sum_{c in ViolentRoots} P(root=c) <= P(violence)
   - P(subcode=s) <= P(root=parent(s))
3. L_logic: Ontological transition penalty gating illegal transitions (8x8 CAMEO matrix).
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from .hierarchical_classifier import (
    HierarchicalOutput,
    CAMEO_ROOT_CODES,
    ROOT_CODE_TO_IDX,
    VIOLENT_ROOT_CODES,
    BD_SUBCODES,
    BD_SUBCODE_TO_IDX,
    BD_SUBCODE_TO_PARENT_ROOT,
)

# ── 8x8 Ontological Illegal Transition Matrix ─────────────────────────────────
# 1 = Illegal transition (violates ALC ontology), 0 = Valid transition
# Verified by knowledge_graph/dl_reasoner_check.py
ILLEGAL_TRANSITIONS_MAP: dict[int, set[int]] = {
    13: {18, 19, 20},
    14: {18, 19, 20},
    15: {13, 19, 20},
    16: {13, 14, 19, 20},
    17: {13, 14, 15, 20},
    18: {13, 14, 15, 16},
    19: {13, 14, 15, 16, 17},
    20: {13, 14, 15, 16, 17, 18},
}


def build_illegal_transition_tensor() -> torch.Tensor:
    """Builds an [8, 8] binary tensor of illegal transitions."""
    mat = torch.zeros(len(CAMEO_ROOT_CODES), len(CAMEO_ROOT_CODES), dtype=torch.float32)
    for from_code, illegals in ILLEGAL_TRANSITIONS_MAP.items():
        from_idx = ROOT_CODE_TO_IDX[from_code]
        for to_code in illegals:
            if to_code in ROOT_CODE_TO_IDX:
                to_idx = ROOT_CODE_TO_IDX[to_code]
                mat[from_idx, to_idx] = 1.0
    return mat


class SoftConstraintLoss(nn.Module):
    """
    Differentiable neuro-symbolic multi-task loss with hierarchical consistency
    and Description Logic transition constraints.
    """

    def __init__(
        self,
        weight_event: float = 1.0,
        weight_violence: float = 1.0,
        weight_root: float = 1.5,
        weight_subcode: float = 1.2,
        weight_context: float = 0.5,
        lambda_hier: float = 0.5,
        lambda_logic: float = 0.3,
    ):
        super().__init__()
        self.w_event = weight_event
        self.w_violence = weight_violence
        self.w_root = weight_root
        self.w_subcode = weight_subcode
        self.w_ctx = weight_context
        self.lambda_hier = lambda_hier
        self.lambda_logic = lambda_logic

        # Loss functions
        self.ce = nn.CrossEntropyLoss(reduction="mean")
        self.bce = nn.BCEWithLogitsLoss(reduction="mean")

        # Register ontological matrix buffer (non-trainable)
        self.register_buffer("illegal_matrix", build_illegal_transition_tensor())

        # Precompute violent root indices
        violent_indices = [ROOT_CODE_TO_IDX[c] for c in VIOLENT_ROOT_CODES if c in ROOT_CODE_TO_IDX]
        self.register_buffer("violent_root_indices", torch.tensor(violent_indices, dtype=torch.long))

        # Precompute subcode to root index mapping
        subcode_parents = []
        for s in BD_SUBCODES:
            if s == "NONE" or s not in BD_SUBCODE_TO_PARENT_ROOT:
                subcode_parents.append(-1)
            else:
                p_code = BD_SUBCODE_TO_PARENT_ROOT[s]
                subcode_parents.append(ROOT_CODE_TO_IDX.get(p_code, -1))
        self.register_buffer("subcode_parent_indices", torch.tensor(subcode_parents, dtype=torch.long))

    def compute_hierarchical_penalty(self, out: HierarchicalOutput) -> torch.Tensor:
        """
        Computes conditional hierarchical probability violation penalty:
          L_hier = L_ev_viol + L_viol_root + L_root_subcode
        """
        prob_ev = out.prob_event        # [B, 2], index 1 = is_event
        prob_v = out.prob_violence      # [B, 2], index 1 = is_violence
        prob_root = out.prob_root       # [B, 8]
        prob_sub = out.prob_subcode     # [B, 22]

        p_event = prob_ev[:, 1]
        p_violence = prob_v[:, 1]

        # 1. P(violence) should not exceed P(event)
        # Violation: ReLU(P(violence) - P(event))
        pen_ev_viol = torch.mean(F.relu(p_violence - p_event) ** 2)

        # 2. Sum of violent root probabilities should not exceed P(violence)
        p_violent_roots = torch.sum(prob_root[:, self.violent_root_indices], dim=-1)  # [B]
        pen_viol_root = torch.mean(F.relu(p_violent_roots - p_violence) ** 2)

        # 3. For each subcode s, P(subcode=s) should not exceed P(root=parent(s))
        pen_sub_list = []
        for s_idx, p_idx in enumerate(self.subcode_parent_indices):
            if p_idx >= 0:
                p_sub = prob_sub[:, s_idx]       # [B]
                p_parent = prob_root[:, p_idx]   # [B]
                pen_sub_list.append(F.relu(p_sub - p_parent) ** 2)

        if pen_sub_list:
            pen_root_sub = torch.mean(torch.stack(pen_sub_list, dim=-1))
        else:
            pen_root_sub = torch.tensor(0.0, device=prob_ev.device)

        return pen_ev_viol + pen_viol_root + pen_root_sub

    def compute_logic_penalty(
        self,
        prob_root: torch.Tensor,
        prev_root_codes: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Computes ontological illegal transition penalty:
          L_logic = sum_j M_illegal[prev_code, j] * P(root = j)
        """
        if prev_root_codes is None:
            return torch.tensor(0.0, device=prob_root.device)

        batch_size = prob_root.size(0)
        penalties = []
        for b in range(batch_size):
            p_code = prev_root_codes[b].item()
            if p_code in ROOT_CODE_TO_IDX:
                p_idx = ROOT_CODE_TO_IDX[p_code]
                illegal_mask = self.illegal_matrix[p_idx]  # [8]
                penalty = torch.sum(illegal_mask * prob_root[b])
                penalties.append(penalty)
            else:
                penalties.append(torch.tensor(0.0, device=prob_root.device))

        return torch.mean(torch.stack(penalties))

    def forward(
        self,
        output: HierarchicalOutput,
        target_event: Optional[torch.Tensor] = None,
        target_violence: Optional[torch.Tensor] = None,
        target_root: Optional[torch.Tensor] = None,
        target_subcode: Optional[torch.Tensor] = None,
        target_context: Optional[torch.Tensor] = None,
        prev_root_codes: Optional[torch.Tensor] = None,
    ) -> dict[str, torch.Tensor]:
        """
        Calculates the complete loss decomposed into its constituent terms.
        """
        device = output.logits_event.device

        # 1. Multi-Task Cross-Entropy
        loss_event = (
            self.ce(output.logits_event, target_event)
            if target_event is not None
            else torch.tensor(0.0, device=device)
        )
        loss_violence = (
            self.ce(output.logits_violence, target_violence)
            if target_violence is not None
            else torch.tensor(0.0, device=device)
        )
        loss_root = (
            self.ce(output.logits_root, target_root)
            if target_root is not None
            else torch.tensor(0.0, device=device)
        )
        loss_subcode = (
            self.ce(output.logits_subcode, target_subcode)
            if target_subcode is not None
            else torch.tensor(0.0, device=device)
        )
        loss_context = (
            self.bce(output.logits_context, target_context)
            if target_context is not None
            else torch.tensor(0.0, device=device)
        )

        l_ce = (
            self.w_event * loss_event
            + self.w_violence * loss_violence
            + self.w_root * loss_root
            + self.w_subcode * loss_subcode
            + self.w_ctx * loss_context
        )

        # 2. Hierarchical Consistency Loss
        l_hier = self.compute_hierarchical_penalty(output)

        # 3. Description Logic Transition Penalty
        l_logic = self.compute_logic_penalty(output.prob_root, prev_root_codes)

        # Total Loss
        total_loss = l_ce + self.lambda_hier * l_hier + self.lambda_logic * l_logic

        return {
            "loss": total_loss,
            "loss_ce": l_ce,
            "loss_event": loss_event,
            "loss_violence": loss_violence,
            "loss_root": loss_root,
            "loss_subcode": loss_subcode,
            "loss_context": loss_context,
            "loss_hier": l_hier,
            "loss_logic": l_logic,
        }
