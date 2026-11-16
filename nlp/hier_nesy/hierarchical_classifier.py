"""
nlp/hier_nesy/hierarchical_classifier.py
Paper 2: hier-nesy-bd (Hierarchical Neuro-Symbolic Event Extraction)

Implements a 4-tier coarse-to-fine hierarchical neural classifier:
  Level 1: Event Identification (Binary: Non-event [0] vs Event [1])
  Level 2: Violence Binary (Binary: Non-violent [0] vs Violent [1])
  Level 3: CAMEO Root Category (8-class: 13=Threaten to 20=Mass Violence)
  Level 4: BD Context-Action Subcode (21 subclasses + 1 NONE = 22 classes)
  Decoupled Context Head: Localized conflict context tags (9 categories)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)

# ── Hierarchical Taxonomy Constants ──────────────────────────────────────────

# Level 3: 8 CAMEO Root Categories (13 to 20)
CAMEO_ROOT_CODES: list[int] = [13, 14, 15, 16, 17, 18, 19, 20]
CAMEO_ROOT_LABELS: dict[int, str] = {
    13: "Threaten",
    14: "Protest",
    15: "Exhibit Force",
    16: "Reduce Relations",
    17: "Coerce",
    18: "Assault",
    19: "Fight",
    20: "Use Unconventional Mass Violence",
}
VIOLENT_ROOT_CODES: set[int] = {14, 17, 18, 19, 20}
ROOT_CODE_TO_IDX: dict[int, int] = {c: i for i, c in enumerate(CAMEO_ROOT_CODES)}
IDX_TO_ROOT_CODE: dict[int, int] = {i: c for i, c in enumerate(CAMEO_ROOT_CODES)}

# Level 4: 21 BD Ontology Extension Subcodes (+ NONE at index 0)
BD_SUBCODES: list[str] = [
    "NONE",
    "PV01", "PV02", "PV03", "PV04",  # Political Violence
    "SV01", "SV02", "SV03", "SV04",  # State / Custodial Violence
    "CV01", "CV02", "CV03",          # Communal / Ethnic Violence
    "GV01", "GV02", "GV03", "GV04",  # Gender-Based / Domestic Violence
    "LV01", "LV02", "LV03",          # Labor / RMG Unrest
    "OC01", "OC02", "OC03",          # Organized Crime & Mob Justice
]
BD_SUBCODE_TO_IDX: dict[str, int] = {s: i for i, s in enumerate(BD_SUBCODES)}
IDX_TO_BD_SUBCODE: dict[int, str] = {i: s for i, s in enumerate(BD_SUBCODES)}

# Mapping each BD subcode to its primary CAMEO root category
BD_SUBCODE_TO_PARENT_ROOT: dict[str, int] = {
    "PV01": 14,  # Hartal violence -> Protest / Riot
    "PV02": 19,  # Political clash -> Fight / Clashes
    "PV03": 14,  # Election violence -> Protest / Riot / Clashes
    "PV04": 14,  # Student violence -> Protest / Clashes
    "SV01": 18,  # Extrajudicial killing -> Assault / Killing
    "SV02": 18,  # Enforced disappearance -> Assault / Abduction
    "SV03": 18,  # Custodial torture -> Assault
    "SV04": 17,  # Excessive force -> Coerce
    "CV01": 18,  # Religious communal violence -> Assault
    "CV02": 18,  # Land communal violence -> Assault
    "CV03": 18,  # Ethnic violence -> Assault
    "GV01": 18,  # Acid attack -> Assault
    "GV02": 18,  # Domestic violence fatality -> Assault
    "GV03": 18,  # Sexual assault -> Assault
    "GV04": 18,  # Dowry violence -> Assault
    "LV01": 14,  # Garment worker unrest -> Protest
    "LV02": 17,  # Industrial disaster / safety -> Coerce / Repression
    "LV03": 17,  # Labor rights suppression -> Coerce
    "OC01": 18,  # Drug-related killing -> Assault
    "OC02": 17,  # Extortion violence -> Coerce / Assault
    "OC03": 18,  # Mob justice / lynching -> Assault
}

# Decoupled Context Tags (Context vs Action separation)
CONTEXT_TAGS: list[str] = [
    "ELECTION",
    "HARTAL",
    "STUDENT_POLITICS",
    "LABOR_RMG",
    "LAND_DISPUTE",
    "COMMUNAL_RELIGIOUS",
    "STATE_SECURITY",
    "ORGANIZED_CRIME",
    "DOMESTIC_GENDER",
]
CONTEXT_TAG_TO_IDX: dict[str, int] = {t: i for i, t in enumerate(CONTEXT_TAGS)}

ACTION_CODES: list[str] = [
    "THREATEN",
    "PROTEST",
    "MOBILIZE",
    "SANCTION",
    "ARREST_DETAIN",
    "PHYSICAL_ASSAULT",
    "ARMED_CLASH",
    "EXPLOSIVE_BOMBING",
]


# ── Output Data Structures ───────────────────────────────────────────────────

@dataclass
class HierarchicalOutput:
    logits_event:    torch.Tensor   # [B, 2] Level 1: Event Identification
    logits_violence: torch.Tensor   # [B, 2] Level 2: Violence Binary
    logits_root:     torch.Tensor   # [B, 8] Level 3: CAMEO Root Categories
    logits_subcode:  torch.Tensor   # [B, 22] Level 4: BD Subcodes (including NONE)
    logits_context:  torch.Tensor   # [B, 9] Decoupled Context Tags

    @property
    def prob_event(self) -> torch.Tensor:
        return F.softmax(self.logits_event, dim=-1)

    @property
    def prob_violence(self) -> torch.Tensor:
        return F.softmax(self.logits_violence, dim=-1)

    @property
    def prob_root(self) -> torch.Tensor:
        return F.softmax(self.logits_root, dim=-1)

    @property
    def prob_subcode(self) -> torch.Tensor:
        return F.softmax(self.logits_subcode, dim=-1)

    @property
    def prob_context(self) -> torch.Tensor:
        return torch.sigmoid(self.logits_context)


@dataclass
class HierarchicalPrediction:
    is_event:        bool
    event_conf:      float
    is_violence:     bool
    violence_conf:   float
    cameo_root_code: int
    cameo_root_name: str
    cameo_root_conf: float
    bd_subcode:      Optional[str]
    bd_subcode_conf: float
    context_tags:    list[str]

    def to_dict(self) -> dict:
        return {
            "is_event":        self.is_event,
            "event_conf":      round(self.event_conf, 4),
            "is_violence":     self.is_violence,
            "violence_conf":   round(self.violence_conf, 4),
            "cameo_root_code": self.cameo_root_code,
            "cameo_root_name": self.cameo_root_name,
            "cameo_root_conf": round(self.cameo_root_conf, 4),
            "bd_subcode":      self.bd_subcode,
            "bd_subcode_conf": round(self.bd_subcode_conf, 4),
            "context_tags":    self.context_tags,
        }


# ── Hierarchical Classifier Architecture ─────────────────────────────────────

class HierarchicalEventClassifier(nn.Module):
    """
    Coarse-to-fine Hierarchical Neural Classifier.
    Information flows progressively from general event identification down to specific BD subcode.
    """

    def __init__(
        self,
        input_dim: int = 384,
        hidden_dim: int = 256,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim

        # Shared representation backbone
        self.backbone = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )

        # Tier 1: Event Identification Head (2 classes)
        self.head_event = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Linear(hidden_dim // 2, 2),
        )

        # Tier 2: Violence Binary Head (conditioned on backbone + Tier 1 logits)
        self.tier2_proj = nn.Linear(hidden_dim + 2, hidden_dim // 2)
        self.head_violence = nn.Sequential(
            nn.LayerNorm(hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, 2),
        )

        # Tier 3: CAMEO Root Category Head (8 classes; conditioned on Tier 2 hidden + Tier 2 logits)
        self.tier3_proj = nn.Linear((hidden_dim // 2) + 2, hidden_dim // 2)
        self.head_root = nn.Sequential(
            nn.LayerNorm(hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, len(CAMEO_ROOT_CODES)),
        )

        # Tier 4: BD Subcode Head (22 classes; conditioned on Tier 3 hidden + Tier 3 logits)
        self.tier4_proj = nn.Linear((hidden_dim // 2) + len(CAMEO_ROOT_CODES), hidden_dim // 2)
        self.head_subcode = nn.Sequential(
            nn.LayerNorm(hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, len(BD_SUBCODES)),
        )

        # Decoupled Context Tag Head (9 multi-label context tags)
        self.head_context = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, len(CONTEXT_TAGS)),
        )

    def forward(self, x: torch.Tensor) -> HierarchicalOutput:
        """
        Forward pass with coarse-to-fine conditioning.
        Args:
            x: Input embeddings of shape [BatchSize, input_dim]
        Returns:
            HierarchicalOutput containing logits across all 4 tiers + context head.
        """
        h = self.backbone(x)  # [B, hidden_dim]

        # Tier 1: Event Identification
        logits_event = self.head_event(h)  # [B, 2]

        # Tier 2: Condition on Tier 1
        h2_in = torch.cat([h, logits_event], dim=-1)
        h2 = self.tier2_proj(h2_in)
        logits_violence = self.head_violence(h2)  # [B, 2]

        # Tier 3: Condition on Tier 2
        h3_in = torch.cat([h2, logits_violence], dim=-1)
        h3 = self.tier3_proj(h3_in)
        logits_root = self.head_root(h3)  # [B, 8]

        # Tier 4: Condition on Tier 3
        h4_in = torch.cat([h3, logits_root], dim=-1)
        h4 = self.tier4_proj(h4_in)
        logits_subcode = self.head_subcode(h4)  # [B, 22]

        # Decoupled Context Tags
        logits_context = self.head_context(h)  # [B, 9]

        return HierarchicalOutput(
            logits_event=logits_event,
            logits_violence=logits_violence,
            logits_root=logits_root,
            logits_subcode=logits_subcode,
            logits_context=logits_context,
        )

    @torch.no_grad()
    def predict_single(
        self,
        embedding: torch.Tensor,
        context_threshold: float = 0.5,
    ) -> HierarchicalPrediction:
        """
        Predicts hierarchical labels for a single instance.
        """
        self.eval()
        if embedding.dim() == 1:
            embedding = embedding.unsqueeze(0)

        out = self.forward(embedding)

        # Probabilities
        prob_event = out.prob_event[0]
        prob_violence = out.prob_violence[0]
        prob_root = out.prob_root[0]
        prob_subcode = out.prob_subcode[0]
        prob_context = out.prob_context[0]

        is_event = bool(torch.argmax(prob_event).item() == 1)
        event_conf = prob_event[1 if is_event else 0].item()

        is_violence = bool(torch.argmax(prob_violence).item() == 1)
        violence_conf = prob_violence[1 if is_violence else 0].item()

        root_idx = torch.argmax(prob_root).item()
        root_code = IDX_TO_ROOT_CODE[root_idx]
        root_name = CAMEO_ROOT_LABELS.get(root_code, "Unknown")
        root_conf = prob_root[root_idx].item()

        subcode_idx = torch.argmax(prob_subcode).item()
        subcode_label = IDX_TO_BD_SUBCODE[subcode_idx]
        bd_subcode = None if subcode_label == "NONE" else subcode_label
        subcode_conf = prob_subcode[subcode_idx].item()

        # Context tags
        active_tags = [
            CONTEXT_TAGS[i]
            for i, p in enumerate(prob_context)
            if p.item() >= context_threshold
        ]

        return HierarchicalPrediction(
            is_event=is_event,
            event_conf=event_conf,
            is_violence=is_violence,
            violence_conf=violence_conf,
            cameo_root_code=root_code,
            cameo_root_name=root_name,
            cameo_root_conf=root_conf,
            bd_subcode=bd_subcode,
            bd_subcode_conf=subcode_conf,
            context_tags=active_tags,
        )
