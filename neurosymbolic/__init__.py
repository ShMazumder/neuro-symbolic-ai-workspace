"""
neurosymbolic — Neuro-Symbolic Reasoning Package

Modules:
    kg_export   (4.1) — Export BlazeGraph KG to PyTorch Geometric / DGL format
    embeddings  (4.2) — KG embeddings: TransE, ComplEx, RotatE via PyKEEN
    gnn_model   (4.3) — R-GCN / CompGCN for event pattern detection
    forecasting (4.4) — BiLSTM escalation forecasting + symbolic post-filter
    anomaly     (4.5) — Rule-based anomaly detection (violence spikes vs baseline)
    explain     (4.8) — Explainability: trace predictions → source triples + articles
    hybrid      (4.9) — Hybrid inference: symbolic constraints filter neural predictions
"""

from .kg_export   import export_kg, save_export, KGGraph, to_pytorch_geometric
from .embeddings  import train_embedding, load_embedding, predict_link
from .gnn_model   import EventPatternGNN, train_gnn, build_node_features
from .forecasting import (
    EscalationLSTM, train_forecasting_model,
    forecast_district, run_all_forecasts,
    build_district_sequences,
)
from .anomaly     import ViolenceBaseline, detect_anomalies, AnomalyAlert
from .explain     import (
    explain_gnn_prediction, explain_escalation_forecast,
    explain_anomaly_alert, Explanation, Evidence,
)
from .hybrid      import (
    HybridInferenceEngine, HybridDecision,
    run_hybrid_inference_batch, ConstraintViolation,
)

__all__ = [
    # 4.1
    "export_kg", "save_export", "KGGraph", "to_pytorch_geometric",
    # 4.2
    "train_embedding", "load_embedding", "predict_link",
    # 4.3
    "EventPatternGNN", "train_gnn", "build_node_features",
    # 4.4
    "EscalationLSTM", "train_forecasting_model",
    "forecast_district", "run_all_forecasts", "build_district_sequences",
    # 4.5
    "ViolenceBaseline", "detect_anomalies", "AnomalyAlert",
    # 4.8
    "explain_gnn_prediction", "explain_escalation_forecast",
    "explain_anomaly_alert", "Explanation", "Evidence",
    # 4.9
    "HybridInferenceEngine", "HybridDecision",
    "run_hybrid_inference_batch", "ConstraintViolation",
]
