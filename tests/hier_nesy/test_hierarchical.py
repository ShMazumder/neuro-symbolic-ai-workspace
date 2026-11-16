"""
tests/hier_nesy/test_hierarchical.py
Unit and integration tests for Paper 2 ('hier-nesy-bd'):
  1. 4-tier coarse-to-fine hierarchical classifier
  2. Differentiable soft constraint loss (hierarchical + ALC logic penalties)
  3. Hungarian 1-to-1 bipartite ACLED matching across temporal thresholds
"""

import unittest
import torch
import numpy as np

from nlp.hier_nesy.hierarchical_classifier import (
    HierarchicalEventClassifier,
    HierarchicalOutput,
    HierarchicalPrediction,
    CAMEO_ROOT_CODES,
    BD_SUBCODES,
    CONTEXT_TAGS,
)
from nlp.hier_nesy.soft_constraint_loss import (
    SoftConstraintLoss,
    build_illegal_transition_tensor,
)
from evaluation.hier_nesy.benchmark_acled_bipartite import (
    BipartiteACLEDMatcher,
    haversine_km,
    parse_date,
    to_cameo_root,
    run_bipartite_acled_benchmark,
)


class TestHierarchicalClassifier(unittest.TestCase):
    def setUp(self):
        self.input_dim = 64
        self.hidden_dim = 32
        self.batch_size = 4
        self.model = HierarchicalEventClassifier(
            input_dim=self.input_dim,
            hidden_dim=self.hidden_dim,
            dropout=0.1,
        )

    def test_forward_shapes(self):
        x = torch.randn(self.batch_size, self.input_dim)
        out = self.model(x)

        self.assertIsInstance(out, HierarchicalOutput)
        self.assertEqual(out.logits_event.shape, (self.batch_size, 2))
        self.assertEqual(out.logits_violence.shape, (self.batch_size, 2))
        self.assertEqual(out.logits_root.shape, (self.batch_size, 8))
        self.assertEqual(out.logits_subcode.shape, (self.batch_size, 22))
        self.assertEqual(out.logits_context.shape, (self.batch_size, 9))

        # Check probability bounds
        self.assertTrue(torch.all(out.prob_event >= 0.0) and torch.all(out.prob_event <= 1.0))
        self.assertTrue(torch.all(out.prob_violence >= 0.0) and torch.all(out.prob_violence <= 1.0))
        self.assertTrue(torch.all(out.prob_root >= 0.0) and torch.all(out.prob_root <= 1.0))
        self.assertTrue(torch.all(out.prob_subcode >= 0.0) and torch.all(out.prob_subcode <= 1.0))
        self.assertTrue(torch.all(out.prob_context >= 0.0) and torch.all(out.prob_context <= 1.0))

    def test_predict_single(self):
        emb = torch.randn(self.input_dim)
        pred = self.model.predict_single(emb, context_threshold=0.3)

        self.assertIsInstance(pred, HierarchicalPrediction)
        self.assertIsInstance(pred.is_event, bool)
        self.assertIsInstance(pred.is_violence, bool)
        self.assertIn(pred.cameo_root_code, CAMEO_ROOT_CODES)
        self.assertIsInstance(pred.cameo_root_name, str)
        if pred.bd_subcode is not None:
            self.assertIn(pred.bd_subcode, BD_SUBCODES)
        for tag in pred.context_tags:
            self.assertIn(tag, CONTEXT_TAGS)


class TestSoftConstraintLoss(unittest.TestCase):
    def setUp(self):
        self.loss_fn = SoftConstraintLoss(
            lambda_hier=0.5,
            lambda_logic=0.3,
        )
        self.input_dim = 64
        self.model = HierarchicalEventClassifier(
            input_dim=self.input_dim,
            hidden_dim=32,
        )

    def test_loss_backward_pass(self):
        batch_size = 4
        x = torch.randn(batch_size, self.input_dim)
        out = self.model(x)

        target_event = torch.tensor([1, 1, 0, 1], dtype=torch.long)
        target_violence = torch.tensor([1, 0, 0, 1], dtype=torch.long)
        target_root = torch.tensor([5, 1, 0, 6], dtype=torch.long)  # indices in 0..7
        target_subcode = torch.tensor([1, 0, 0, 5], dtype=torch.long)  # indices in 0..21
        target_context = torch.zeros(batch_size, 9)
        target_context[0, 1] = 1.0  # HARTAL
        prev_root_codes = torch.tensor([14, 13, 13, 18], dtype=torch.long)

        loss_dict = self.loss_fn(
            output=out,
            target_event=target_event,
            target_violence=target_violence,
            target_root=target_root,
            target_subcode=target_subcode,
            target_context=target_context,
            prev_root_codes=prev_root_codes,
        )

        total_loss = loss_dict["loss"]
        self.assertGreater(total_loss.item(), 0.0)
        self.assertGreaterEqual(loss_dict["loss_hier"].item(), 0.0)
        self.assertGreaterEqual(loss_dict["loss_logic"].item(), 0.0)

        # Verify gradient backpropagation through the 4-tier model
        total_loss.backward()
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                self.assertIsNotNone(param.grad, f"Parameter {name} has no gradient.")

    def test_logic_penalty_illegal_transition(self):
        """13 (Threaten) -> 20 (Mass Violence) is illegal in ALC and must incur positive penalty."""
        # Fake logits where root predicts 20 with high probability (index 7 = code 20)
        logits_root = torch.tensor([[-5.0, -5.0, -5.0, -5.0, -5.0, -5.0, -5.0, 5.0]])
        prob_root = torch.softmax(logits_root, dim=-1)

        prev_code_illegal = torch.tensor([13], dtype=torch.long)
        pen_illegal = self.loss_fn.compute_logic_penalty(prob_root, prev_code_illegal)
        self.assertGreater(pen_illegal.item(), 0.8)

        # 13 (Threaten) -> 14 (Protest) is legal and must incur near-zero penalty (< 1e-3 tail prob)
        logits_legal = torch.tensor([[-5.0, 5.0, -5.0, -5.0, -5.0, -5.0, -5.0, -5.0]])
        prob_legal = torch.softmax(logits_legal, dim=-1)
        pen_legal = self.loss_fn.compute_logic_penalty(prob_legal, prev_code_illegal)
        self.assertLess(pen_legal.item(), 1e-3)

    def test_hierarchical_penalty_violation(self):
        """P(violence) > P(event) must incur positive hierarchical violation penalty."""
        out = HierarchicalOutput(
            logits_event=torch.tensor([[-5.0, -5.0]]),       # P(event=1) ~ 0.5
            logits_violence=torch.tensor([[-10.0, 10.0]]),   # P(violence=1) ~ 1.0
            logits_root=torch.zeros(1, 8),
            logits_subcode=torch.zeros(1, 22),
            logits_context=torch.zeros(1, 9),
        )
        pen = self.loss_fn.compute_hierarchical_penalty(out)
        self.assertGreater(pen.item(), 0.0)


class TestBipartiteACLEDMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = BipartiteACLEDMatcher(max_spatial_km=50.0)

    def test_haversine_distance(self):
        # Distance between Dhaka (23.8103, 90.4125) and Chittagong (22.3569, 91.7832) ~ 205-225 km
        d = haversine_km(23.8103, 90.4125, 22.3569, 91.7832)
        self.assertGreater(d, 200.0)
        self.assertLess(d, 250.0)

        # Same point should be 0.0 km
        d_self = haversine_km(23.8103, 90.4125, 23.8103, 90.4125)
        self.assertAlmostEqual(d_self, 0.0, places=4)

    def test_date_and_cameo_normalization(self):
        d1 = parse_date("2024-10-15")
        self.assertEqual(str(d1), "2024-10-15")
        d2 = parse_date({"normalized": "2024-10-20"})
        self.assertEqual(str(d2), "2024-10-20")

        self.assertEqual(to_cameo_root("182"), 18)
        self.assertEqual(to_cameo_root(145), 14)
        self.assertEqual(to_cameo_root("Violence against civilians"), 18)
        self.assertEqual(to_cameo_root("Protests"), 14)

    def test_bipartite_matching_kuhn_munkres(self):
        # 3 predicted events and 3 ACLED events
        predicted = [
            {
                "event_id": "p1",
                "date": "2024-10-10",
                "location": {"district": "dhaka", "lat": 23.81, "lon": 90.41},
                "cameo_code": "182",
            },
            {
                "event_id": "p2",
                "date": "2024-10-12",
                "location": {"district": "chittagong", "lat": 22.35, "lon": 91.78},
                "cameo_code": "145",
            },
            {
                "event_id": "p3",
                "date": "2024-10-25",  # Way out of temporal range for early events
                "location": {"district": "sylhet", "lat": 24.89, "lon": 91.86},
                "cameo_code": "193",
            },
        ]
        acled = [
            {
                "event_id_cnty": "a1",
                "event_date": "2024-10-11",  # 1 day from p1
                "admin2": "dhaka",
                "latitude": 23.82,
                "longitude": 90.42,
                "event_type": "Violence against civilians",
            },
            {
                "event_id_cnty": "a2",
                "event_date": "2024-10-13",  # 1 day from p2
                "admin2": "chittagong",
                "latitude": 22.36,
                "longitude": 91.79,
                "event_type": "Protests",
            },
            {
                "event_id_cnty": "a3",
                "event_date": "2024-10-10",
                "admin2": "rajshahi",  # Different district & >150km away
                "latitude": 24.36,
                "longitude": 88.60,
                "event_type": "Battles",
            },
        ]

        # In a tau=3 day window, p1 should match a1, p2 should match a2, p3 should match none
        b_pairs = self.matcher.match_bipartite(predicted, acled, tau_days=3)
        self.assertEqual(len(b_pairs), 2)

        # 1-to-1 constraint check: each pred and acled appears at most once
        pred_matched = [p.pred_id for p in b_pairs]
        acled_matched = [p.acled_id for p in b_pairs]
        self.assertEqual(len(pred_matched), len(set(pred_matched)))
        self.assertEqual(len(acled_matched), len(set(acled_matched)))
        self.assertIn("p1", pred_matched)
        self.assertIn("p2", pred_matched)
        self.assertIn("a1", acled_matched)
        self.assertIn("a2", acled_matched)

    def test_run_bipartite_acled_benchmark(self):
        predicted = [
            {"event_id": "p1", "date": "2024-10-10", "district": "dhaka", "cameo_code": "182"},
            {"event_id": "p2", "date": "2024-10-12", "district": "dhaka", "cameo_code": "145"},
        ]
        acled = [
            {"event_id": "a1", "date": "2024-10-11", "admin2": "dhaka", "event_type": "Violence against civilians"},
        ]

        curve = run_bipartite_acled_benchmark(predicted, acled, windows=(1, 3, 7))
        self.assertEqual(len(curve), 3)
        for res in curve:
            self.assertGreaterEqual(res.bipartite_precision, 0.0)
            self.assertLessEqual(res.bipartite_precision, 1.0)
            self.assertGreaterEqual(res.bipartite_concordance, 0.0)


if __name__ == "__main__":
    unittest.main()
