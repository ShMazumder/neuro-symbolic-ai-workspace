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


if __name__ == "__main__":
    records = load_corpus()
    train, test = get_stratified_splits()
    print(f"Loaded {len(records)} events. Train: {len(train)}, Test: {len(test)}")
