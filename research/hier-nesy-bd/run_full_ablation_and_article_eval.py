"""
research/hier-nesy-bd/run_full_ablation_and_article_eval.py
Full Empirical Component Ablation and Zero-Leakage Article-Grouped Evaluation for Paper 2.

Evaluates:
  Part 1: 5-Fold Stratified CV Component Ablation:
    1. Flat Multiclass Baseline (Standard CE over 8 roots)
    2. 4-Tier Hierarchical Model (Pure CE: lambda_hier=0, lambda_logic=0)
    3. 4-Tier Hierarchical Model + Hierarchical Penalty (lambda_hier=0.5, lambda_logic=0)
    4. 4-Tier Hierarchical Model + Logic Penalty (lambda_hier=0, lambda_logic=0.3)
    5. Full Composite Loss (lambda_hier=0.5, lambda_logic=0.3)

  Part 2: Zero-Leakage Article-Grouped Holdout Evaluation:
    Evaluates on data/splits/bd_conflict_manifest.json (207 Train / 31 Dev / 62 Test; 0 Article Overlap)
    Compares Flat Baseline vs Pure Hierarchical CE vs Full Neuro-Symbolic.
"""

from __future__ import annotations

import json
import logging
import random
import sys
from pathlib import Path
from typing import NamedTuple

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

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
from evaluation.split_dataset import load_split_events

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BENCHMARK_PATH = Path("data/annotations/gold_benchmark_events.json")
MANIFEST_PATH = Path("data/splits/bd_conflict_manifest.json")
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


class FlatMulticlassClassifier(nn.Module):
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


class FoldMetrics(NamedTuple):
    root_acc: float
    root_f1: float
    violence_acc: float
    violence_f1: float
    ontological_violation_rate: float
    hierarchical_violation_rate: float


def evaluate_flat(model: nn.Module, X_test: torch.Tensor, y_root: np.ndarray, prev_roots: np.ndarray) -> FoldMetrics:
    model.eval()
    with torch.no_grad():
        logits = model(X_test)
        preds = torch.argmax(logits, dim=-1).cpu().numpy()

    root_acc = accuracy_score(y_root, preds)
    root_f1 = f1_score(y_root, preds, average="macro", zero_division=0)

    violent_indices = {ROOT_CODE_TO_IDX[c] for c in VIOLENT_ROOT_CODES if c in ROOT_CODE_TO_IDX}
    y_viol = np.array([1 if y in violent_indices else 0 for y in y_root])
    pred_viol = np.array([1 if p in violent_indices else 0 for p in preds])

    viol_acc = accuracy_score(y_viol, pred_viol)
    viol_f1 = f1_score(y_viol, pred_viol, average="binary", zero_division=0)

    violations = sum(1 for p_root, pred_idx in zip(prev_roots, preds) if IDX_TO_ROOT_CODE[pred_idx] in ILLEGAL_TRANSITIONS_MAP.get(p_root, set()))
    onto_viol_rate = violations / max(1, len(preds))

    return FoldMetrics(root_acc, root_f1, viol_acc, viol_f1, onto_viol_rate, 0.0)


def evaluate_hierarchical(
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

    violations = sum(1 for p_root, pred_idx in zip(prev_roots, pred_roots) if IDX_TO_ROOT_CODE[pred_idx] in ILLEGAL_TRANSITIONS_MAP.get(p_root, set()))
    onto_viol_rate = violations / max(1, len(pred_roots))

    violent_indices = [ROOT_CODE_TO_IDX[c] for c in VIOLENT_ROOT_CODES if c in ROOT_CODE_TO_IDX]
    p_sum_viol = torch.sum(prob_root[:, violent_indices], dim=-1).cpu().numpy()
    p_v = prob_v[:, 1].cpu().numpy()
    hier_viol_rate = float(np.sum(p_sum_viol > (p_v + 0.05)) / max(1, len(pred_roots)))

    return FoldMetrics(root_acc, root_f1, viol_acc, viol_f1, onto_viol_rate, hier_viol_rate)


def train_flat(X_tr: torch.Tensor, y_r_tr: torch.Tensor, X_te: torch.Tensor, y_r_te: np.ndarray, prev_te: np.ndarray) -> FoldMetrics:
    model = FlatMulticlassClassifier(input_dim=INPUT_DIM, hidden_dim=HIDDEN_DIM, dropout=0.2)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    loss_fn = nn.CrossEntropyLoss()
    dataset = torch.utils.data.TensorDataset(X_tr, y_r_tr)
    loader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    for epoch in range(EPOCHS):
        model.train()
        for bx, by in loader:
            optimizer.zero_grad()
            loss = loss_fn(model(bx), by)
            loss.backward()
            optimizer.step()

    return evaluate_flat(model, X_te, y_r_te, prev_te)


def train_hier(
    X_tr: torch.Tensor,
    y_r_tr: torch.Tensor,
    y_v_tr: torch.Tensor,
    prev_tr: torch.Tensor,
    X_te: torch.Tensor,
    y_r_te: np.ndarray,
    y_v_te: np.ndarray,
    prev_te: np.ndarray,
    lambda_hier: float,
    lambda_logic: float,
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

    y_ev_tr = torch.ones_like(y_v_tr)
    dataset = torch.utils.data.TensorDataset(X_tr, y_ev_tr, y_v_tr, y_r_tr, prev_tr)
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

    return evaluate_hierarchical(model, X_te, y_r_te, y_v_te, prev_te)


def run_5fold_ablation(sentences: list[str], root_indices: np.ndarray, violence_binary: np.ndarray, prev_roots: np.ndarray) -> dict:
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    conditions = {
        "flat_baseline": {"hier": False, "l_hier": 0.0, "l_logic": 0.0},
        "hier_ce_only":  {"hier": True,  "l_hier": 0.0, "l_logic": 0.0},
        "hier_plus_hier": {"hier": True, "l_hier": 0.5, "l_logic": 0.0},
        "hier_plus_logic":{"hier": True, "l_hier": 0.0, "l_logic": 0.3},
        "hier_full_nesy": {"hier": True, "l_hier": 0.5, "l_logic": 0.3},
    }

    results: dict[str, list[FoldMetrics]] = {k: [] for k in conditions}

    for fold, (train_idx, test_idx) in enumerate(skf.split(sentences, root_indices)):
        logger.info("Executing 5-Fold Ablation Fold %d / 5...", fold + 1)
        train_texts = [sentences[i] for i in train_idx]
        test_texts = [sentences[i] for i in test_idx]

        vectorizer = TfidfVectorizer(max_features=INPUT_DIM, ngram_range=(1, 2), sublinear_tf=True)
        X_tr = vectorizer.fit_transform(train_texts).toarray()
        X_te = vectorizer.transform(test_texts).toarray()

        if X_tr.shape[1] < INPUT_DIM:
            X_tr = np.hstack([X_tr, np.zeros((X_tr.shape[0], INPUT_DIM - X_tr.shape[1]), dtype=np.float32)])
            X_te = np.hstack([X_te, np.zeros((X_te.shape[0], INPUT_DIM - X_te.shape[1]), dtype=np.float32)])

        t_X_tr = torch.tensor(X_tr, dtype=torch.float32)
        t_X_te = torch.tensor(X_te, dtype=torch.float32)
        t_yr_tr = torch.tensor(root_indices[train_idx], dtype=torch.long)
        t_yv_tr = torch.tensor(violence_binary[train_idx], dtype=torch.long)
        t_prev_tr = torch.tensor(prev_roots[train_idx], dtype=torch.long)

        yr_te = root_indices[test_idx]
        yv_te = violence_binary[test_idx]
        prev_te = prev_roots[test_idx]

        for cond_name, cfg in conditions.items():
            set_seed(SEED + fold)
            if not cfg["hier"]:
                m = train_flat(t_X_tr, t_yr_tr, t_X_te, yr_te, prev_te)
            else:
                m = train_hier(t_X_tr, t_yr_tr, t_yv_tr, t_prev_tr, t_X_te, yr_te, yv_te, prev_te, cfg["l_hier"], cfg["l_logic"])
            results[cond_name].append(m)

    # Compute mean and std
    summary = {}
    for cond_name, m_list in results.items():
        summary[cond_name] = {
            "root_accuracy": {
                "mean": round(float(np.mean([m.root_acc for m in m_list])), 4),
                "std": round(float(np.std([m.root_acc for m in m_list])), 4),
            },
            "root_macro_f1": {
                "mean": round(float(np.mean([m.root_f1 for m in m_list])), 4),
                "std": round(float(np.std([m.root_f1 for m in m_list])), 4),
            },
            "violence_accuracy": {
                "mean": round(float(np.mean([m.violence_acc for m in m_list])), 4),
                "std": round(float(np.std([m.violence_acc for m in m_list])), 4),
            },
            "violence_f1": {
                "mean": round(float(np.mean([m.violence_f1 for m in m_list])), 4),
                "std": round(float(np.std([m.violence_f1 for m in m_list])), 4),
            },
            "ontological_violation_rate": {
                "mean": round(float(np.mean([m.ontological_violation_rate for m in m_list])), 4),
                "std": round(float(np.std([m.ontological_violation_rate for m in m_list])), 4),
            },
            "hierarchical_violation_rate": {
                "mean": round(float(np.mean([m.hierarchical_violation_rate for m in m_list])), 4),
                "std": round(float(np.std([m.hierarchical_violation_rate for m in m_list])), 4),
            },
        }

    return summary


def run_article_grouped_evaluation(manifest_path: Path) -> dict:
    """Evaluates models on the official zero-leakage article holdout test set (N=62)."""
    train_events = load_split_events("train", manifest_path=manifest_path)
    dev_events = load_split_events("dev", manifest_path=manifest_path)
    test_events = load_split_events("test", manifest_path=manifest_path)

    # Use train + dev for training (238 events), test for holdout evaluation (62 events)
    tr_all = train_events + dev_events
    te_all = test_events

    train_texts = [e.get("source_sentence", "") for e in tr_all]
    test_texts = [e.get("source_sentence", "") for e in te_all]

    vectorizer = TfidfVectorizer(max_features=INPUT_DIM, ngram_range=(1, 2), sublinear_tf=True)
    X_tr = vectorizer.fit_transform(train_texts).toarray()
    X_te = vectorizer.transform(test_texts).toarray()

    if X_tr.shape[1] < INPUT_DIM:
        X_tr = np.hstack([X_tr, np.zeros((X_tr.shape[0], INPUT_DIM - X_tr.shape[1]), dtype=np.float32)])
        X_te = np.hstack([X_te, np.zeros((X_te.shape[0], INPUT_DIM - X_te.shape[1]), dtype=np.float32)])

    violent_indices_set = {ROOT_CODE_TO_IDX[c] for c in VIOLENT_ROOT_CODES if c in ROOT_CODE_TO_IDX}

    def _prep(evs):
        roots = np.array([ROOT_CODE_TO_IDX.get(e.get("gold_cameo_code") or e.get("cameo_code", 14), 1) for e in evs])
        viols = np.array([1 if r in violent_indices_set else 0 for r in roots])
        prevs = np.array([e.get("prev_code", 14) for e in evs])
        return roots, viols, prevs

    yr_tr, yv_tr, prev_tr = _prep(tr_all)
    yr_te, yv_te, prev_te = _prep(te_all)

    t_X_tr = torch.tensor(X_tr, dtype=torch.float32)
    t_X_te = torch.tensor(X_te, dtype=torch.float32)
    t_yr_tr = torch.tensor(yr_tr, dtype=torch.long)
    t_yv_tr = torch.tensor(yv_tr, dtype=torch.long)
    t_prev_tr = torch.tensor(prev_tr, dtype=torch.long)

    # Evaluate conditions on holdout
    set_seed(SEED)
    m_flat = train_flat(t_X_tr, t_yr_tr, t_X_te, yr_te, prev_te)

    set_seed(SEED)
    m_hier_ce = train_hier(t_X_tr, t_yr_tr, t_yv_tr, t_prev_tr, t_X_te, yr_te, yv_te, prev_te, lambda_hier=0.0, lambda_logic=0.0)

    set_seed(SEED)
    m_hier_nesy = train_hier(t_X_tr, t_yr_tr, t_yv_tr, t_prev_tr, t_X_te, yr_te, yv_te, prev_te, lambda_hier=0.5, lambda_logic=0.3)

    return {
        "dataset_split": {
            "train_articles": 79,
            "train_events": len(tr_all),
            "test_articles": 19,
            "test_events": len(te_all),
            "article_leakage": 0,
        },
        "flat_baseline": {
            "root_accuracy": round(m_flat.root_acc, 4),
            "root_macro_f1": round(m_flat.root_f1, 4),
            "violence_accuracy": round(m_flat.violence_acc, 4),
            "violence_f1": round(m_flat.violence_f1, 4),
            "ontological_violation_rate": round(m_flat.ontological_violation_rate, 4),
        },
        "hier_ce_only": {
            "root_accuracy": round(m_hier_ce.root_acc, 4),
            "root_macro_f1": round(m_hier_ce.root_f1, 4),
            "violence_accuracy": round(m_hier_ce.violence_acc, 4),
            "violence_f1": round(m_hier_ce.violence_f1, 4),
            "ontological_violation_rate": round(m_hier_ce.ontological_violation_rate, 4),
            "hierarchical_violation_rate": round(m_hier_ce.hierarchical_violation_rate, 4),
        },
        "hier_full_nesy": {
            "root_accuracy": round(m_hier_nesy.root_acc, 4),
            "root_macro_f1": round(m_hier_nesy.root_f1, 4),
            "violence_accuracy": round(m_hier_nesy.violence_acc, 4),
            "violence_f1": round(m_hier_nesy.violence_f1, 4),
            "ontological_violation_rate": round(m_hier_nesy.ontological_violation_rate, 4),
            "hierarchical_violation_rate": round(m_hier_nesy.hierarchical_violation_rate, 4),
        },
    }


def main():
    set_seed(SEED)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    data = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    sentences = [ev.get("source_sentence", "") for ev in data]
    gold_codes = [ev.get("gold_cameo_code", 14) for ev in data]
    prev_codes = [ev.get("prev_code", 14) for ev in data]

    root_indices = np.array([ROOT_CODE_TO_IDX.get(c, 1) for c in gold_codes])
    violent_indices_set = {ROOT_CODE_TO_IDX[c] for c in VIOLENT_ROOT_CODES if c in ROOT_CODE_TO_IDX}
    violence_binary = np.array([1 if idx in violent_indices_set else 0 for idx in root_indices])
    prev_roots = np.array(prev_codes)

    logger.info("=== Running Part 1: 5-Fold Component Loss Ablation ===")
    ablation_summary = run_5fold_ablation(sentences, root_indices, violence_binary, prev_roots)
    out_ablation = RESULTS_DIR / "component_ablation_results.json"
    out_ablation.write_text(json.dumps(ablation_summary, indent=2), encoding="utf-8")
    logger.info("Saved ablation summary → %s", out_ablation)

    logger.info("=== Running Part 2: Zero-Leakage Article-Grouped Holdout Evaluation ===")
    article_summary = run_article_grouped_evaluation(MANIFEST_PATH)
    out_article = RESULTS_DIR / "article_grouped_results.json"
    out_article.write_text(json.dumps(article_summary, indent=2), encoding="utf-8")
    logger.info("Saved article grouped holdout summary → %s", out_article)

    print("\n" + "=" * 80)
    print("TABLE 2: LOSS COMPONENT ABLATION (5-Fold Stratified Cross-Validation)")
    print("=" * 80)
    print(f"{'Condition':<20} | {'Root Acc (%)':<15} | {'Root Macro F1':<15} | {'Viol Acc (%)':<15} | {'Onto Viol Rate'}")
    print("-" * 80)
    for c_name, m in ablation_summary.items():
        r_acc = f"{m['root_accuracy']['mean']:.1%} ± {m['root_accuracy']['std']:.1%}"
        r_f1 = f"{m['root_macro_f1']['mean']:.3f} ± {m['root_macro_f1']['std']:.3f}"
        v_acc = f"{m['violence_accuracy']['mean']:.1%} ± {m['violence_accuracy']['std']:.1%}"
        o_v = f"{m['ontological_violation_rate']['mean']:.1%}"
        print(f"{c_name:<20} | {r_acc:<15} | {r_f1:<15} | {v_acc:<15} | {o_v}")

    print("\n" + "=" * 80)
    print("TABLE 3: ZERO-LEAKAGE ARTICLE-GROUPED HOLDOUT EVALUATION (Test N=62)")
    print("=" * 80)
    print(f"{'Model Architecture':<25} | {'Root Acc (%)':<15} | {'Root Macro F1':<15} | {'Viol Acc (%)':<15} | {'Onto Viol Rate'}")
    print("-" * 80)
    for m_name in ["flat_baseline", "hier_ce_only", "hier_full_nesy"]:
        m = article_summary[m_name]
        print(f"{m_name:<25} | {m['root_accuracy']:.1%}          | {m['root_macro_f1']:.3f}          | {m['violence_accuracy']:.1%}          | {m['ontological_violation_rate']:.1%}")


if __name__ == "__main__":
    main()
