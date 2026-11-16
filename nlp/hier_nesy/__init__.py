"""
nlp/hier_nesy — Hierarchical Neuro-Symbolic Event Extraction & Classification.
Part of the 'hier-nesy-bd' (Paper 2) research initiative.
"""

from .hierarchical_classifier import (
    HierarchicalEventClassifier,
    HierarchicalOutput,
    CAMEO_ROOT_CODES,
    BD_SUBCODES,
    BD_SUBCODE_TO_PARENT_ROOT,
    CONTEXT_TAGS,
    ACTION_CODES,
)
from .soft_constraint_loss import SoftConstraintLoss

__all__ = [
    "HierarchicalEventClassifier",
    "HierarchicalOutput",
    "CAMEO_ROOT_CODES",
    "BD_SUBCODES",
    "BD_SUBCODE_TO_PARENT_ROOT",
    "CONTEXT_TAGS",
    "ACTION_CODES",
    "SoftConstraintLoss",
]
