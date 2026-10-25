"""
neurosymbolic/forecasting.py
Task 4.4 — Escalation forecasting: predict CAMEO code escalation from event sequences.

Approach:
  - Temporal event sequences per district are encoded as CAMEO code trajectories.
  - A BiLSTM (neural) classifies whether the next event represents *escalation*
    (jump to a higher CAMEO code category).
  - A symbolic post-filter enforces domain constraints: escalation can only
    occur if specific precondition codes are present in the window.

CAMEO escalation ladder (simplified, Bangladesh context):
  13 → 14 → 15 → 16 → 17 → 18 → 19 → 20
  (Threaten) → (Protest) → (Exhibit Force) → (Reduce Relations) →
  (Coerce) → (Assault) → (Fight) → (Mass Violence)

Dependencies:
    pip install torch
"""

from __future__ import annotations

import json
import logging
import pickle
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)

PROCESSED_DIR  = Path("data/processed")
MODELS_DIR     = Path("models/forecasting")
KG_EXPORT_DIR  = Path("data/kg_export")

# ── Symbolic escalation rules ─────────────────────────────────────────────────

# CAMEO codes that must appear in a window to allow escalation prediction
ESCALATION_PRECONDITIONS: dict[int, list[int]] = {
    18: [17, 16],  # Assault requires prior Coerce or Exhibit Force
    19: [17, 18],  # Fight requires prior Assault or Coerce
    20: [18, 19],  # Mass Violence requires prior Fight or Assault
}

CAMEO_CODE_TO_IDX: dict[int, int] = {c: i for i, c in enumerate(range(13, 21))}
IDX_TO_CAMEO_CODE: dict[int, int] = {v: k for k, v in CAMEO_CODE_TO_IDX.items()}
NUM_CODES = len(CAMEO_CODE_TO_IDX)  # 8


@dataclass
class EscalationForecast:
    district:       str
    window_codes:   list[int]       # last N CAMEO codes
    predicted_code: int             # most likely next CAMEO code
    escalation:     bool            # True if predicted > max(window_codes)
    confidence:     float
    symbolic_valid: bool            # passes symbolic precondition check
    explanation:    str


# ── Neural model: BiLSTM sequence encoder ────────────────────────────────────

class EscalationLSTM(nn.Module):
    """
    BiLSTM that takes a sequence of CAMEO code embeddings and predicts
    the next CAMEO code distribution.

    Architecture:
      Embedding(8, embed_dim) → BiLSTM(hidden_dim) → Linear(8)
    """

    def __init__(
        self,
        num_codes: int = NUM_CODES,
        embed_dim: int = 16,
        hidden_dim: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.embed = nn.Embedding(num_codes + 1, embed_dim, padding_idx=num_codes)
        self.lstm  = nn.LSTM(
            embed_dim, hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
        )
        self.drop = nn.Dropout(dropout)
        self.fc   = nn.Linear(hidden_dim * 2, num_codes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: [B, T] integer code indices
        returns: [B, num_codes] log-probabilities
        """
        emb = self.embed(x)                      # [B, T, embed_dim]
        out, _ = self.lstm(emb)                  # [B, T, hidden*2]
        last = out[:, -1, :]                     # last time step
        logits = self.fc(self.drop(last))        # [B, num_codes]
        return F.log_softmax(logits, dim=-1)


# ── Symbolic post-filter ──────────────────────────────────────────────────────

def _symbolic_validate(window_codes: list[int], predicted_code: int) -> tuple[bool, str]:
    """
    Check whether the symbolic precondition rule allows the predicted escalation.

    Returns (valid: bool, reason: str).
    """
    if predicted_code not in ESCALATION_PRECONDITIONS:
        return True, "No symbolic constraint for this code."

    required = ESCALATION_PRECONDITIONS[predicted_code]
    present  = [c for c in required if c in window_codes]
    if present:
        return True, f"Precondition met: codes {present} found in window."
    else:
        return False, (
            f"Symbolic violation: code {predicted_code} requires one of "
            f"{required} in window, but window contains {window_codes}."
        )


# ── Sequence builder from KGGraph ─────────────────────────────────────────────

def build_district_sequences(kg_path: Path = KG_EXPORT_DIR / "kg_graph.pkl") -> dict[str, list[int]]:
    """
    Extract per-district ordered CAMEO code sequences from the KGGraph.

    Returns: {district_name → [cameo_code_int, …]} sorted by event date.
    """
    with open(kg_path, "rb") as f:
        kg = pickle.load(f)

    district_events: dict[str, list[tuple[str, int]]] = {}

    for uri, ntype in kg.node_types.items():
        if ntype != "event":
            continue
        feat = kg.node_features.get(uri, {})
        district = feat.get("district", "UNKNOWN")
        date_str  = feat.get("date", "")
        code_str  = feat.get("code", "")
        try:
            code = int(float(code_str))
            if code >= 100:
                code = code // 10
        except (ValueError, TypeError):
            continue
        if code < 13 or code > 20:
            continue
        district_events.setdefault(district, []).append((date_str or "", code))

    # Sort by date, strip to code sequence
    sequences = {}
    for district, events in district_events.items():
        events.sort(key=lambda x: x[0])
        sequences[district] = [c for _, c in events]

    logger.info("Built sequences for %d districts.", len(sequences))
    return sequences


def _codes_to_tensor(codes: list[int], window: int = 8) -> torch.Tensor:
    """Convert a CAMEO code list to a padded tensor of index sequences."""
    # Convert codes to 0-indexed (13→0, …, 20→7)
    indices = [CAMEO_CODE_TO_IDX.get(c, 0) for c in codes]
    # Pad/truncate to window
    pad_val = NUM_CODES  # padding index
    if len(indices) < window:
        indices = [pad_val] * (window - len(indices)) + indices
    else:
        indices = indices[-window:]
    return torch.tensor([indices], dtype=torch.long)  # [1, window]


# ── Forecasting interface ─────────────────────────────────────────────────────

def forecast_district(
    district: str,
    code_sequence: list[int],
    model: EscalationLSTM,
    window: int = 4,
) -> EscalationForecast:
    """
    Run neuro-symbolic forecasting for a single district.

    1. Neural model predicts next CAMEO code distribution.
    2. Symbolic rules validate the top prediction.
    3. Returns an EscalationForecast with full explanation.
    """
    model.eval()
    window_codes = code_sequence[-window:] if len(code_sequence) >= window else code_sequence
    x = _codes_to_tensor(window_codes, window)

    with torch.no_grad():
        log_probs = model(x)  # [1, num_codes]
    probs = log_probs.exp().squeeze(0)  # [num_codes]

    pred_idx  = probs.argmax().item()
    pred_code = IDX_TO_CAMEO_CODE[pred_idx]
    confidence = probs[pred_idx].item()

    escalation = pred_code > (max(window_codes) if window_codes else 13)
    sym_valid, sym_reason = _symbolic_validate(window_codes, pred_code)

    return EscalationForecast(
        district=district,
        window_codes=window_codes,
        predicted_code=pred_code,
        escalation=escalation,
        confidence=round(confidence, 4),
        symbolic_valid=sym_valid,
        explanation=(
            f"Neural model predicts CAMEO {pred_code} (conf={confidence:.2%}). "
            f"Escalation={'YES' if escalation else 'NO'}. "
            f"Symbolic check: {sym_reason}"
        ),
    )


# ── Training ──────────────────────────────────────────────────────────────────

def train_forecasting_model(
    kg_path: Path = KG_EXPORT_DIR / "kg_graph.pkl",
    window: int = 4,
    epochs: int = 150,
    lr: float = 1e-3,
    out_dir: Path = MODELS_DIR,
) -> EscalationLSTM:
    """
    Train the EscalationLSTM on district code sequences.

    Task: given window of N codes, predict the N+1th code (next-step prediction).
    """
    sequences = build_district_sequences(kg_path)

    # Build training pairs
    X_list, y_list = [], []
    for codes in sequences.values():
        if len(codes) < window + 1:
            continue
        for i in range(len(codes) - window):
            x_codes = codes[i: i + window]
            y_code  = codes[i + window]
            y_idx   = CAMEO_CODE_TO_IDX.get(y_code, 0)
            X_list.append([CAMEO_CODE_TO_IDX.get(c, 0) for c in x_codes])
            y_list.append(y_idx)

    if not X_list:
        logger.warning("No training sequences found. Using synthetic data.")
        # Synthetic escalation sequences for bootstrap training
        for start in range(13, 20):
            seq = list(range(start, min(start + window + 1, 21)))
            while len(seq) < window + 1:
                seq.append(seq[-1])
            X_list.append([CAMEO_CODE_TO_IDX.get(c, 0) for c in seq[:window]])
            y_list.append(CAMEO_CODE_TO_IDX.get(seq[window], 0))

    X = torch.tensor(X_list, dtype=torch.long)
    y = torch.tensor(y_list, dtype=torch.long)

    model = EscalationLSTM()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        log_probs = model(X)
        loss = F.nll_loss(log_probs, y)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 30 == 0:
            preds = log_probs.argmax(dim=1)
            acc = (preds == y).float().mean()
            logger.info("Epoch %3d | loss=%.4f | acc=%.4f", epoch + 1, loss.item(), acc.item())

    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_dir / "escalation_lstm.pt")
    logger.info("Forecasting model saved to %s", out_dir)
    return model


def run_all_forecasts(
    kg_path: Path = KG_EXPORT_DIR / "kg_graph.pkl",
    model_path: Optional[Path] = None,
    window: int = 4,
    out_path: Path = Path("data/processed/escalation_forecasts.json"),
) -> list[EscalationForecast]:
    """Load trained model, run forecasts for all districts, save JSON."""
    model = EscalationLSTM()
    if model_path and model_path.exists():
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        logger.info("Loaded model from %s", model_path)
    else:
        logger.warning("No model found at %s. Training first…", model_path)
        model = train_forecasting_model(kg_path)

    sequences = build_district_sequences(kg_path)
    forecasts = []
    for district, codes in sequences.items():
        if not codes:
            continue
        fc = forecast_district(district, codes, model, window)
        forecasts.append(fc)

    # Save
    out_path.parent.mkdir(parents=True, exist_ok=True)
    records = [
        {
            "district":       f.district,
            "window_codes":   f.window_codes,
            "predicted_code": f.predicted_code,
            "escalation":     f.escalation,
            "confidence":     f.confidence,
            "symbolic_valid": f.symbolic_valid,
            "explanation":    f.explanation,
        }
        for f in forecasts
    ]
    out_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    logger.info("Forecasts saved: %d districts → %s", len(forecasts), out_path)
    return forecasts


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s")
    model = train_forecasting_model()
    forecasts = run_all_forecasts(model_path=MODELS_DIR / "escalation_lstm.pt")
    escalating = [f for f in forecasts if f.escalation and f.symbolic_valid]
    print(f"\nDistricts with validated escalation signals: {len(escalating)}")
    for f in sorted(escalating, key=lambda x: -x.confidence)[:10]:
        print(f"  {f.district:30s}  CAMEO→{f.predicted_code}  conf={f.confidence:.2%}")
