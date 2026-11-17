"""
tests/test_dataset_splits.py
Unit tests verifying article-grouped dataset splits and zero-leakage guarantees.
"""

import unittest
from pathlib import Path
from evaluation.split_dataset import (
    create_article_grouped_manifest,
    load_split_events,
    _extract_article_id,
)
from data.cameo_bd_corpus.loader import load_corpus, get_article_grouped_splits


class TestDatasetSplits(unittest.TestCase):
    def test_extract_article_id(self):
        e1 = {"source_url": "https://www.thedailystar.net/news/bangladesh/clash-1?ref=rss"}
        e2 = {"source_url": "http://thedailystar.net/news/bangladesh/clash-1"}
        # Both URLs should normalize to the same article identifier
        self.assertEqual(_extract_article_id(e1), _extract_article_id(e2))

        e3 = {"article_id": "art_999"}
        self.assertEqual(_extract_article_id(e3), "art_999")

    def test_article_grouped_zero_leakage(self):
        # Generate manifest to test directory
        test_out_dir = Path("data/splits")
        manifest = create_article_grouped_manifest(
            output_dir=test_out_dir,
            seed=42,
        )

        self.assertIn("summary", manifest)
        self.assertIn("splits", manifest)
        self.assertIn("k_fold_cross_validation", manifest)

        splits = manifest["splits"]
        train_eids = set(splits["train"])
        dev_eids = set(splits["dev"])
        test_eids = set(splits["test"])

        # Disjoint events
        self.assertEqual(len(train_eids & dev_eids), 0)
        self.assertEqual(len(train_eids & test_eids), 0)
        self.assertEqual(len(dev_eids & test_eids), 0)

        # Completeness
        total_events = manifest["summary"]["total_events"]
        self.assertEqual(len(train_eids) + len(dev_eids) + len(test_eids), total_events)

        # Disjoint articles
        art_map = manifest["article_to_split"]
        train_arts = {art for art, sp in art_map.items() if sp == "train"}
        dev_arts = {art for art, sp in art_map.items() if sp == "dev"}
        test_arts = {art for art, sp in art_map.items() if sp == "test"}

        self.assertEqual(len(train_arts & dev_arts), 0, "Train and Dev share articles!")
        self.assertEqual(len(train_arts & test_arts), 0, "Train and Test share articles!")
        self.assertEqual(len(dev_arts & test_arts), 0, "Dev and Test share articles!")

    def test_corpus_loader_grouped_splits(self):
        train, dev, test = get_article_grouped_splits()
        self.assertEqual(len(train) + len(dev) + len(test), 300)

        # Verify no shared articles via loader
        train_arts = {_extract_article_id(e) for e in train}
        dev_arts = {_extract_article_id(e) for e in dev}
        test_arts = {_extract_article_id(e) for e in test}

        self.assertEqual(len(train_arts & dev_arts), 0)
        self.assertEqual(len(train_arts & test_arts), 0)
        self.assertEqual(len(dev_arts & test_arts), 0)
