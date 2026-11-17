"""
data/cameo_bd_corpus/loader.py
Resource loader for the CAMEO-BD conflict benchmark dataset.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Union

CORPUS_PATH = Path(__file__).parent / "cameo_bd_corpus.json"


def load_corpus(path: Optional[Union[str, Path]] = None) -> list[dict]:
    """Loads the 300 double-annotated conflict event benchmark records."""
    target_path = Path(path) if path else CORPUS_PATH
    if not target_path.exists():
        raise FileNotFoundError(f"Corpus not found at {target_path}")
    return json.loads(target_path.read_text(encoding="utf-8"))


def get_stratified_splits(
    test_size: float = 0.2,
    seed: int = 42,
    path: Optional[Union[str, Path]] = None,
) -> tuple[list[dict], list[dict]]:
    """Returns stratified (train, test) splits partitioned by gold CAMEO code."""
    from sklearn.model_selection import StratifiedShuffleSplit

    records = load_corpus(path)
    codes = [r.get("gold_cameo_code", 14) for r in records]

    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_idx, test_idx = next(sss.split(records, codes))

    train_data = [records[i] for i in train_idx]
    test_data = [records[i] for i in test_idx]

    return train_data, test_data


def get_article_grouped_splits(
    manifest_path: Optional[Union[str, Path]] = None,
    corpus_path: Optional[Union[str, Path]] = None,
) -> tuple[list[dict], list[dict], list[dict]]:
    """
    Returns article-grouped (train, dev, test) splits with zero article leakage.
    Grounded by the versioned split manifest.
    """
    mpath = Path(manifest_path) if manifest_path else Path(__file__).parent / "splits" / "bd_conflict_manifest.json"
    if not mpath.exists():
        # Fallback to evaluation/split_dataset.py
        from evaluation.split_dataset import create_article_grouped_manifest
        create_article_grouped_manifest(dataset_path=corpus_path or CORPUS_PATH, output_dir=mpath.parent)

    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    records = load_corpus(corpus_path)
    rec_by_id = {r.get("event_id"): r for r in records}

    train_data = [rec_by_id[eid] for eid in manifest["splits"]["train"] if eid in rec_by_id]
    dev_data = [rec_by_id[eid] for eid in manifest["splits"]["dev"] if eid in rec_by_id]
    test_data = [rec_by_id[eid] for eid in manifest["splits"]["test"] if eid in rec_by_id]

    return train_data, dev_data, test_data


if __name__ == "__main__":
    records = load_corpus()
    train, test = get_stratified_splits()
    print(f"Loaded {len(records)} events. Stratified: Train: {len(train)}, Test: {len(test)}")
    tr_grp, dev_grp, te_grp = get_article_grouped_splits()
    print(f"Article-grouped (zero leakage): Train: {len(tr_grp)}, Dev: {len(dev_grp)}, Test: {len(te_grp)}")
