"""
tests/test_neurosymbolic.py
Unit tests for hybrid neuro-symbolic inference and constraint enforcement.
"""
import unittest
import torch
from neurosymbolic.hybrid import (
    HybridInferenceEngine,
    VALID_TRANSITIONS,
    BD_GEO_HIERARCHY,
    _check_ontological_transition,
    _check_geographic,
)


class TestNeurosymbolic(unittest.TestCase):
    def test_geographic_constraint(self):
        # District matches division
        v_ok = _check_geographic("Dhaka", "Dhaka")
        self.assertIsNone(v_ok)

        v_ok_sub = _check_geographic("Dhaka", "Gazipur")
        self.assertIsNone(v_ok_sub)

        # District does not match division
        v_bad = _check_geographic("Sylhet", "Gazipur")
        self.assertIsNotNone(v_bad)
        self.assertEqual(v_bad.rule_type, "geographic")

    def test_ontological_transition(self):
        # Valid: 14 (Protest) -> 17 (Coerce)
        v_valid = _check_ontological_transition(14, 17)
        self.assertIsNone(v_valid)

        # Invalid jump: 13 (Threaten) -> 20 (Mass Violence)
        v_invalid = _check_ontological_transition(13, 20)
        self.assertIsNotNone(v_invalid)
        self.assertEqual(v_invalid.severity, "hard")

    def test_hybrid_engine_inference(self):
        engine = HybridInferenceEngine()
        logits = torch.randn(8)
        decision = engine.infer(
            event_uri="http://example.org/event/test_001",
            neural_logits=logits,
            division="Dhaka",
            district="Dhaka",
        )
        self.assertIsNotNone(decision)
        self.assertTrue(hasattr(decision, "accepted"))
        self.assertTrue(hasattr(decision, "final_code"))
        d_dict = decision.to_dict()
        self.assertIn("event_uri", d_dict)
        self.assertIn("final_code", d_dict)


if __name__ == "__main__":
    unittest.main()
