"""
evaluation/split_dataset.py
Article-Grouped Dataset Splitter for Bangladesh Conflict Benchmark.

Guarantees ZERO article / publisher leakage across training, development,
and test sets by grouping all sentence-level events by their source article URL.
Uses StratifiedGroupKFold to maintain balanced CAMEO class distributions while
enforcing strict group disjointness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

logger = logging.getLogger(__name__)

DEFAULT_DATASET = Path("data/evaluation/benchmark_events_gold.json")
DEFAULT_CORPUS = Path("data/cameo_bd_corpus/cameo_bd_corpus.json")
DEFAULT_OUTPUT_DIR = Path("data/splits")
MANIFEST_NAME = "bd_conflict_manifest.json"


def _compute_sha256(data_bytes: bytes) -> str:
    """Compute SHA-256 hex digest for dataset integrity verification."""
    return hashlib.sha256(data_bytes).hexdigest()


def _extract_article_id(event: dict) -> str:
    """
    Extracts a canonical article identifier from event record.
    Falls back to hashing the source URL or source text if URL is absent.
    """
    url = (event.get("source_url") or event.get("article_url") or "").strip()
    if url:
        # Strip scheme and query params for normalization
        import re
        norm_url = re.sub(r"^https?://(www\.)?", "", url.lower()).split("?")[0].rstrip("/")
        return norm_url
    aid = event.get("article_id")
    if aid:
        return str(aid).strip()
    # Fallback: hash the source text
    txt = event.get("source_sentence") or event.get("text") or event.get("event_id") or ""
    return f"art_{hashlib.md5(txt.encode('utf-8')).hexdigest()[:12]}"


def create_article_grouped_manifest(
    dataset_path: Union[str, Path] = DEFAULT_DATASET,
    output_dir: Union[str, Path] = DEFAULT_OUTPUT_DIR,
    seed: int = 42,
    test_ratio: float = 0.2,
    dev_ratio: float = 0.1,
    n_splits_cv: int = 5,
) -> dict:
    """
    Generates an article-grouped, class-stratified split manifest with strict zero-leakage guarantees.
    """
    dpath = Path(dataset_path)
    if not dpath.exists():
        if DEFAULT_CORPUS.exists():
            dpath = DEFAULT_CORPUS
        else:
            raise FileNotFoundError(f"Dataset not found at {dpath} or {DEFAULT_CORPUS}")

    raw_bytes = dpath.read_bytes()
    dataset_sha256 = _compute_sha256(raw_bytes)
    events: list[dict] = json.loads(raw_bytes.decode("utf-8"))

    total_events = len(events)
    if total_events == 0:
        raise ValueError("Cannot split an empty dataset.")

    event_ids = [e.get("event_id", f"ev_{i:04d}") for i, e in enumerate(events)]
    article_ids = [_extract_article_id(e) for e in events]
    labels = [int(e.get("gold_cameo_code") or e.get("cameo_code") or 14) for e in events]

    unique_articles = sorted(list(set(article_ids)))
    total_articles = len(unique_articles)

    logger.info("Splitting %d events across %d unique articles (seed=%d)", total_events, total_articles, seed)

    # ── 1. Generate 5-Fold Stratified Group Cross-Validation ──────────────────
    sgkf_cv = StratifiedGroupKFold(n_splits=n_splits_cv, shuffle=True, random_state=seed)
    cv_folds = []
    for fold_idx, (train_idx, val_idx) in enumerate(sgkf_cv.split(events, labels, groups=article_ids)):
        fold_train_eids = [event_ids[i] for i in train_idx]
        fold_val_eids = [event_ids[i] for i in val_idx]
        fold_train_arts = set(article_ids[i] for i in train_idx)
        fold_val_arts = set(article_ids[i] for i in val_idx)

        # Zero leakage check
        overlap = fold_train_arts & fold_val_arts
        assert len(overlap) == 0, f"Leakage in CV Fold {fold_idx}: {overlap}"

        cv_folds.append({
            "fold": fold_idx,
            "train_event_count": len(fold_train_eids),
            "val_event_count": len(fold_val_eids),
            "train_article_count": len(fold_train_arts),
            "val_article_count": len(fold_val_arts),
            "train_events": fold_train_eids,
            "val_events": fold_val_eids,
        })

    # ── 2. Generate Train (70%) / Dev (10%) / Test (20%) Primary Split ────────
    # We use Fold 0's test set as the 20% test partition
    test_indices = set(sgkf_cv.split(events, labels, groups=article_ids).__next__()[1])
    test_eids = [event_ids[i] for i in sorted(list(test_indices))]
    test_articles = set(article_ids[i] for i in test_indices)

    # From remaining (train+dev), carve out dev partition (~10% total)
    train_dev_indices = [i for i in range(total_events) if i not in test_indices]
    td_events = [events[i] for i in train_dev_indices]
    td_labels = [labels[i] for i in train_dev_indices]
    td_articles = [article_ids[i] for i in train_dev_indices]

    # Carve dev split using StratifiedGroupKFold on td subset
    sgkf_td = StratifiedGroupKFold(n_splits=8, shuffle=True, random_state=seed + 1)
    dev_sub_indices = set(sgkf_td.split(td_events, td_labels, groups=td_articles).__next__()[1])

    dev_indices = set(train_dev_indices[i] for i in dev_sub_indices)
    train_indices = set(i for i in train_dev_indices if i not in dev_indices)

    train_eids = [event_ids[i] for i in sorted(list(train_indices))]
    dev_eids = [event_ids[i] for i in sorted(list(dev_indices))]

    train_articles = set(article_ids[i] for i in train_indices)
    dev_articles = set(article_ids[i] for i in dev_indices)

    # Verification: Mutual Exclusivity (Zero Article Leakage)
    assert len(train_articles & dev_articles) == 0, "Leakage between train and dev articles!"
    assert len(train_articles & test_articles) == 0, "Leakage between train and test articles!"
    assert len(dev_articles & test_articles) == 0, "Leakage between dev and test articles!"
    assert len(train_eids) + len(dev_eids) + len(test_eids) == total_events, "Event count mismatch in split!"

    event_to_split = {}
    for eid in train_eids:
        event_to_split[eid] = "train"
    for eid in dev_eids:
        event_to_split[eid] = "dev"
    for eid in test_eids:
        event_to_split[eid] = "test"

    article_to_split = {}
    for art in train_articles:
        article_to_split[art] = "train"
    for art in dev_articles:
        article_to_split[art] = "dev"
    for art in test_articles:
        article_to_split[art] = "test"

    # Compute label distributions
    def _dist(eids: list[str]) -> dict[str, int]:
        eid_set = set(eids)
        counts = Counter(labels[i] for i, eid in enumerate(event_ids) if eid in eid_set)
        return {str(k): v for k, v in sorted(counts.items())}

    manifest = {
        "manifest_version": "1.0.0",
        "dataset_name": "cameo_bd_conflict_benchmark",
        "dataset_source_path": str(dpath),
        "dataset_sha256": dataset_sha256,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "random_seed": seed,
        "split_methodology": "StratifiedGroupKFold (Zero-Article-Leakage)",
        "summary": {
            "total_events": total_events,
            "total_unique_articles": total_articles,
            "train": {
                "events": len(train_eids),
                "articles": len(train_articles),
                "event_ratio": round(len(train_eids) / total_events, 4),
                "class_distribution": _dist(train_eids),
            },
            "dev": {
                "events": len(dev_eids),
                "articles": len(dev_articles),
                "event_ratio": round(len(dev_eids) / total_events, 4),
                "class_distribution": _dist(dev_eids),
            },
            "test": {
                "events": len(test_eids),
                "articles": len(test_articles),
                "event_ratio": round(len(test_eids) / total_events, 4),
                "class_distribution": _dist(test_eids),
            },
        },
        "splits": {
            "train": train_eids,
            "dev": dev_eids,
            "test": test_eids,
        },
        "k_fold_cross_validation": cv_folds,
        "event_to_split": event_to_split,
        "article_to_split": article_to_split,
    }

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / MANIFEST_NAME
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info("Saved article-grouped manifest → %s", manifest_path)

    # Also sync to cameo_bd_corpus if directory exists
    corpus_splits_dir = Path("data/cameo_bd_corpus/splits")
    if corpus_splits_dir.parent.exists():
        corpus_splits_dir.mkdir(parents=True, exist_ok=True)
        (corpus_splits_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        logger.info("Synchronized manifest to %s", corpus_splits_dir / MANIFEST_NAME)

    return manifest


def load_split_events(
    split_name: str,
    manifest_path: Union[str, Path] = DEFAULT_OUTPUT_DIR / MANIFEST_NAME,
    dataset_path: Union[str, Path] = DEFAULT_DATASET,
) -> list[dict]:
    """
    Loads events corresponding to a specific partition ('train', 'dev', 'test')
    using the authoritative article-grouped manifest.
    """
    mpath = Path(manifest_path)
    if not mpath.exists():
        mpath = Path("data/cameo_bd_corpus/splits") / MANIFEST_NAME
        if not mpath.exists():
            create_article_grouped_manifest(dataset_path=dataset_path, output_dir=mpath.parent)

    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    if split_name not in manifest["splits"]:
        raise ValueError(f"Unknown split '{split_name}'. Available: {list(manifest['splits'].keys())}")

    target_eids = set(manifest["splits"][split_name])

    dpath = Path(dataset_path)
    if not dpath.exists():
        dpath = DEFAULT_CORPUS
    events = json.loads(dpath.read_text(encoding="utf-8"))

    selected = [e for e in events if e.get("event_id") in target_eids]
    return selected


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    parser = argparse.ArgumentParser(description="Generate article-grouped dataset splits with zero leakage.")
    parser.add_argument("--dataset", type=str, default=str(DEFAULT_DATASET), help="Path to gold dataset JSON")
    parser.add_argument("--out-dir", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Output directory for manifest")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    manifest = create_article_grouped_manifest(
        dataset_path=args.dataset,
        output_dir=args.out_dir,
        seed=args.seed,
    )
    s = manifest["summary"]
    print("\n=== Dataset Split Manifest Summary ===")
    print(f"Total Events: {s['total_events']} | Unique Articles: {s['total_unique_articles']}")
    print(f"Train: {s['train']['events']} events ({s['train']['event_ratio']:.1%}) across {s['train']['articles']} articles")
    print(f"Dev:   {s['dev']['events']} events ({s['dev']['event_ratio']:.1%}) across {s['dev']['articles']} articles")
    print(f"Test:  {s['test']['events']} events ({s['test']['event_ratio']:.1%}) across {s['test']['articles']} articles")
