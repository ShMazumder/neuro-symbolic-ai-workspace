"""
research/hier-nesy-bd/train_and_eval_hierarchy.py
Paper 2: hier-nesy-bd (Hierarchical Neuro-Symbolic Event Extraction)

Benchmarks 3 conditions via 5-Fold Stratified Cross-Validation:
  Condition 1: Flat Multiclass Neural Baseline (Standard CE over 8 roots)
  Condition 2: 4-Tier Hierarchical Model (Pure Multi-task CE)
  Condition 3: 4-Tier Hierarchical Model + Soft Constraint Loss (Full Neuro-Symbolic)

Evaluates:
  - 8-class macro accuracy & macro F1 (tackling the 22.0% plateau)
  - Binary violence accuracy & F1
  - Description Logic ontological violation rate
  - Hierarchical consistency violation rate
"""

import json
import logging
import random
from pathlib import Path
from typing import NamedTuple

import numpy as np
import torch
import torch.nn as nn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold

from nlp.hier_nesy.hierarchical_classifier import (
    HierarchicalEventClassifier,
    CAMEO_ROOT_CODES,
    ROOT_CODE_TO_IDX,
    IDX_TO_ROOT_CODE,
    VIOLENT_ROOT_CODES,
)
from nlp.hier_nesy.soft_constraint_loss import (
    SoftConstraintLoss,
    ILLEGAL_TRANSITIONS_MAP,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BENCHMARK_PATH = Path("data/annotations/gold_benchmark_events.json")
RESULTS_DIR = Path("research/hier-nesy-bd/results")
INPUT_DIM = 384
HIDDEN_DIM = 256
NUM_ROOT_CLASSES = 8
EPOCHS = 35
BATCH_SIZE = 32
LR = 1e-3
SEED = 42


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


# ── Flat Multiclass Baseline Architecture ────────────────────────────────────

class FlatMulticlassClassifier(nn.Module):
    """Flat 8-class neural baseline with identical parameter budget."""

    def __init__(self, input_dim: int = 384, hidden_dim: int = 256, dropout: float = 0.2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LayerNorm(hidden_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, NUM_ROOT_CLASSES),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ── Evaluation Metrics Helper ────────────────────────────────────────────────

class FoldMetrics(NamedTuple):
    root_acc: float
    root_f1: float
    violence_acc: float
    violence_f1: float
    ontological_violation_rate: float
    hierarchical_violation_rate: float


def evaluate_flat_model(
    model: nn.Module,
    X_test: torch.Tensor,
    y_root: np.ndarray,
    prev_roots: np.ndarray,
) -> FoldMetrics:
    model.eval()
    with torch.no_grad():
        logits = model(X_test)
        probs = torch.softmax(logits, dim=-1)
        preds = torch.argmax(probs, dim=-1).cpu().numpy()

    root_acc = accuracy_score(y_root, preds)
    root_f1 = f1_score(y_root, preds, average="macro", zero_division=0)

    # Derived violence binary: violent if root in {14, 17, 18, 19, 20}
    violent_indices = {ROOT_CODE_TO_IDX[c] for c in VIOLENT_ROOT_CODES if c in ROOT_CODE_TO_IDX}
    y_viol = np.array([1 if y in violent_indices else 0 for y in y_root])
    pred_viol = np.array([1 if p in violent_indices else 0 for p in preds])

    viol_acc = accuracy_score(y_viol, pred_viol)
    viol_f1 = f1_score(y_viol, pred_viol, average="binary", zero_division=0)

    # Ontological illegal transition rate
    violations = 0
    for p_root, pred_idx in zip(prev_roots, preds):
        pred_code = IDX_TO_ROOT_CODE[pred_idx]
        if pred_code in ILLEGAL_TRANSITIONS_MAP.get(p_root, set()):
            violations += 1
    onto_viol_rate = violations / max(1, len(preds))

    return FoldMetrics(
        root_acc=root_acc,
        root_f1=root_f1,
        violence_acc=viol_acc,
        violence_f1=viol_f1,
        ontological_violation_rate=onto_viol_rate,
        hierarchical_violation_rate=0.0,  # Flat has no hierarchical heads
    )


def evaluate_hierarchical_model(
    model: HierarchicalEventClassifier,
    X_test: torch.Tensor,
    y_root: np.ndarray,
    y_viol: np.ndarray,
    prev_roots: np.ndarray,
) -> FoldMetrics:
    model.eval()
    with torch.no_grad():
        out = model(X_test)
        prob_root = out.prob_root
        prob_v = out.prob_violence
        pred_roots = torch.argmax(prob_root, dim=-1).cpu().numpy()
        pred_viols = torch.argmax(prob_v, dim=-1).cpu().numpy()

    root_acc = accuracy_score(y_root, pred_roots)
    root_f1 = f1_score(y_root, pred_roots, average="macro", zero_division=0)
    viol_acc = accuracy_score(y_viol, pred_viols)
    viol_f1 = f1_score(y_viol, pred_viols, average="binary", zero_division=0)

    # Ontological illegal transition rate
    violations = 0
    for p_root, pred_idx in zip(prev_roots, pred_roots):
        pred_code = IDX_TO_ROOT_CODE[pred_idx]
        if pred_code in ILLEGAL_TRANSITIONS_MAP.get(p_root, set()):
            violations += 1
    onto_viol_rate = violations / max(1, len(pred_roots))

    # Hierarchical violation: sum of violent root probs > P(violence) + 0.05
    violent_indices = [ROOT_CODE_TO_IDX[c] for c in VIOLENT_ROOT_CODES if c in ROOT_CODE_TO_IDX]
    p_sum_viol = torch.sum(prob_root[:, violent_indices], dim=-1).cpu().numpy()
    p_v = prob_v[:, 1].cpu().numpy()
    hier_violations = np.sum(p_sum_viol > (p_v + 0.05))
    hier_viol_rate = hier_violations / max(1, len(pred_roots))

    return FoldMetrics(
        root_acc=root_acc,
        root_f1=root_f1,
        violence_acc=viol_acc,
        violence_f1=viol_f1,
        ontological_violation_rate=onto_viol_rate,
        hierarchical_violation_rate=float(hier_viol_rate),
    )


# ── Training Loops ────────────────────────────────────────────────────────────

def train_flat_fold(
    X_train: torch.Tensor,
    y_root_train: torch.Tensor,
    X_test: torch.Tensor,
    y_root_test: np.ndarray,
    prev_roots_test: np.ndarray,
) -> FoldMetrics:
    model = FlatMulticlassClassifier(input_dim=INPUT_DIM, hidden_dim=HIDDEN_DIM, dropout=0.2)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    loss_fn = nn.CrossEntropyLoss()

    dataset = torch.utils.data.TensorDataset(X_train, y_root_train)
    loader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    for epoch in range(EPOCHS):
        model.train()
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = loss_fn(logits, batch_y)
            loss.backward()
            optimizer.step()

    return evaluate_flat_model(model, X_test, y_root_test, prev_roots_test)


def train_hierarchical_fold(
    X_train: torch.Tensor,
    y_root_train: torch.Tensor,
    y_viol_train: torch.Tensor,
    prev_train: torch.Tensor,
    X_test: torch.Tensor,
    y_root_test: np.ndarray,
    y_viol_test: np.ndarray,
    prev_roots_test: np.ndarray,
    lambda_hier: float = 0.5,
    lambda_logic: float = 0.3,
) -> FoldMetrics:
    model = HierarchicalEventClassifier(input_dim=INPUT_DIM, hidden_dim=HIDDEN_DIM, dropout=0.2)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    loss_fn = SoftConstraintLoss(
        weight_event=1.0,
        weight_violence=1.0,
        weight_root=1.5,
        weight_subcode=0.0,
        weight_context=0.0,
        lambda_hier=lambda_hier,
        lambda_logic=lambda_logic,
    )

    y_event_train = torch.ones_like(y_viol_train)
    dataset = torch.utils.data.TensorDataset(X_train, y_event_train, y_viol_train, y_root_train, prev_train)
    loader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    for epoch in range(EPOCHS):
        model.train()
        for bx, bev, bv, br, bprev in loader:
            optimizer.zero_grad()
            out = model(bx)
            loss_dict = loss_fn(
                output=out,
                target_event=bev,
                target_violence=bv,
                target_root=br,
                prev_root_codes=bprev,
            )
            loss_dict["loss"].backward()
            optimizer.step()

    return evaluate_hierarchical_model(model, X_test, y_root_test, y_viol_test, prev_roots_test)


# ── Main 5-Fold Benchmark Runner ──────────────────────────────────────────────

def main():
    set_seed(SEED)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if not BENCHMARK_PATH.exists():
        raise FileNotFoundError(f"Benchmark events file not found at {BENCHMARK_PATH}")

    data = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    logger.info("Loaded %d gold benchmark events from %s", len(data), BENCHMARK_PATH)

    sentences = [ev.get("source_sentence", "") for ev in data]
    gold_codes = [ev.get("gold_cameo_code", 14) for ev in data]
    prev_codes = [ev.get("prev_code", 14) for ev in data]

    # Map to indices
    root_indices = np.array([ROOT_CODE_TO_IDX.get(c, 1) for c in gold_codes])
    violent_indices_set = {ROOT_CODE_TO_IDX[c] for c in VIOLENT_ROOT_CODES if c in ROOT_CODE_TO_IDX}
    violence_binary = np.array([1 if idx in violent_indices_set else 0 for idx in root_indices])
    prev_roots = np.array(prev_codes)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    results_flat: list[FoldMetrics] = []
    results_hier_ce: list[FoldMetrics] = []
    results_hier_nesy: list[FoldMetrics] = []

    for fold, (train_idx, test_idx) in enumerate(skf.split(sentences, root_indices)):
        logger.info("Executing Fold %d / 5...", fold + 1)

        train_texts = [sentences[i] for i in train_idx]
        test_texts = [sentences[i] for i in test_idx]

        # Feature representation: TF-IDF dense vectors (d=384)
        vectorizer = TfidfVectorizer(max_features=INPUT_DIM, ngram_range=(1, 2), sublinear_tf=True)
        X_tr = vectorizer.fit_transform(train_texts).toarray()
        X_te = vectorizer.transform(test_texts).toarray()

        # If vocabulary < INPUT_DIM, pad with zeros
        if X_tr.shape[1] < INPUT_DIM:
            pad_tr = np.zeros((X_tr.shape[0], INPUT_DIM - X_tr.shape[1]), dtype=np.float32)
            pad_te = np.zeros((X_te.shape[0], INPUT_DIM - X_te.shape[1]), dtype=np.float32)
            X_tr = np.hstack([X_tr, pad_tr])
            X_te = np.hstack([X_te, pad_te])

        X_train_t = torch.tensor(X_tr, dtype=torch.float32)
        X_test_t = torch.tensor(X_te, dtype=torch.float32)

        y_root_tr_t = torch.tensor(root_indices[train_idx], dtype=torch.long)
        y_viol_tr_t = torch.tensor(violence_binary[train_idx], dtype=torch.long)
        prev_tr_t = torch.tensor(prev_roots[train_idx], dtype=torch.long)

        y_root_te = root_indices[test_idx]
        y_viol_te = violence_binary[test_idx]
        prev_te = prev_roots[test_idx]

        # 1. Flat Multiclass Baseline
        m_flat = train_flat_fold(X_train_t, y_root_tr_t, X_test_t, y_root_te, prev_te)
        results_flat.append(m_flat)

        # 2. 4-Tier Hierarchical Model (CE Only)
        m_hier_ce = train_hierarchical_fold(
            X_train_t, y_root_tr_t, y_viol_tr_t, prev_tr_t,
            X_test_t, y_root_te, y_viol_te, prev_te,
            lambda_hier=0.0, lambda_logic=0.0,
        )
        results_hier_ce.append(m_hier_ce)

        # 3. 4-Tier Hierarchical Model + Soft Constraint Loss (Full Neuro-Symbolic)
        m_hier_nesy = train_hierarchical_fold(
            X_train_t, y_root_tr_t, y_viol_tr_t, prev_tr_t,
            X_test_t, y_root_te, y_viol_te, prev_te,
            lambda_hier=0.5, lambda_logic=0.3,
        )
        results_hier_nesy.append(m_hier_nesy)

    def agg(metrics_list: list[FoldMetrics]) -> dict:
        return {
            "root_acc_mean": round(float(np.mean([m.root_acc for m in metrics_list])), 4),
            "root_acc_std":  round(float(np.std([m.root_acc for m in metrics_list])), 4),
            "root_f1_mean":  round(float(np.mean([m.root_f1 for m in metrics_list])), 4),
            "root_f1_std":   round(float(np.std([m.root_f1 for m in metrics_list])), 4),
            "viol_acc_mean": round(float(np.mean([m.violence_acc for m in metrics_list])), 4),
            "viol_acc_std":  round(float(np.std([m.violence_acc for m in metrics_list])), 4),
            "viol_f1_mean":  round(float(np.mean([m.violence_f1 for m in metrics_list])), 4),
            "viol_f1_std":   round(float(np.std([m.violence_f1 for m in metrics_list])), 4),
            "onto_viol_mean": round(float(np.mean([m.ontological_violation_rate for m in metrics_list])), 4),
            "onto_viol_std":  round(float(np.std([m.ontological_violation_rate for m in metrics_list])), 4),
            "hier_viol_mean": round(float(np.mean([m.hierarchical_violation_rate for m in metrics_list])), 4),
            "hier_viol_std":  round(float(np.std([m.hierarchical_violation_rate for m in metrics_list])), 4),
        }

    summary = {
        "dataset_size": len(data),
        "cv_folds": 5,
        "epochs_per_fold": EPOCHS,
        "conditions": {
            "flat_multiclass_baseline": agg(results_flat),
            "hierarchical_ce_only":     agg(results_hier_ce),
            "hierarchical_soft_nesy":   agg(results_hier_nesy),
        },
    }

    out_file = RESULTS_DIR / "hierarchy_benchmark_results.json"
    out_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.info("Saved 5-fold benchmark results to %s", out_file)

    # Print summary comparison table
    f_agg = summary["conditions"]["flat_multiclass_baseline"]
    h_agg = summary["conditions"]["hierarchical_ce_only"]
    n_agg = summary["conditions"]["hierarchical_soft_nesy"]

    print("\n" + "=" * 80)
    print("5-FOLD STRATIFIED BENCHMARK: BREAKING THE 22.0% ROOT ACCURACY PLATEAU")
    print("=" * 80)
    print(f"| Model Condition | 8-Class Root Acc | 8-Class Root F1 | Violence BinAcc | Violence F1 | Onto Violation Rate | Hier Violation Rate |")
    print(f"|---|---|---|---|---|---|---|")
    print(f"| 1. Flat Multiclass Baseline (CE) | {f_agg['root_acc_mean']*100:.1f} ± {f_agg['root_acc_std']*100:.1f}% | {f_agg['root_f1_mean']:.3f} | {f_agg['viol_acc_mean']*100:.1f}% | {f_agg['viol_f1_mean']:.3f} | {f_agg['onto_viol_mean']*100:.1f}% | N/A |")
    print(f"| 2. 4-Tier Hierarchical (CE) | {h_agg['root_acc_mean']*100:.1f} ± {h_agg['root_acc_std']*100:.1f}% | {h_agg['root_f1_mean']:.3f} | {h_agg['viol_acc_mean']*100:.1f}% | {h_agg['viol_f1_mean']:.3f} | {h_agg['onto_viol_mean']*100:.1f}% | {h_agg['hier_viol_mean']*100:.1f}% |")
    print(f"| 3. 4-Tier Hierarchical + Soft Loss (NeSy) | {n_agg['root_acc_mean']*100:.1f} ± {n_agg['root_acc_std']*100:.1f}% | {n_agg['root_f1_mean']:.3f} | {n_agg['viol_acc_mean']*100:.1f}% | {n_agg['viol_f1_mean']:.3f} | {n_agg['onto_viol_mean']*100:.1f}% | {n_agg['hier_viol_mean']*100:.1f}% |")
    print("=" * 80)


if __name__ == "__main__":
    main()
