"""
tests/test_cameo_classifier.py
Unit tests for CAMEO event classification, BD extensions, and dataclass properties.
"""
import unittest
from nlp.cameo_classifier import ClassificationResult, CAMEOClassifier, classify_event
from nlp.event_triggers import TriggerSpan


class TestCameoClassifier(unittest.TestCase):
    def test_classification_result_properties(self):
        # Regression test for Issue #2 (dataclass properties instead of monkey-patching)
        res = ClassificationResult(
            cameo_code="182",
            cameo_label="Physical assault",
            confidence=0.85,
            method="rule",
            bd_code="BD-PV-01",
        )
        self.assertEqual(res.code, "182")
        self.assertEqual(res.label, "Physical assault")
        self.assertTrue(res.is_violence)
        self.assertEqual(res.bd_code, "BD-PV-01")

        # Test non-violent CAMEO code (root < 13 e.g. "020" Appeal)
        res_non_violence = ClassificationResult(
            cameo_code="020",
            cameo_label="Appeal",
            confidence=0.9,
            method="rule",
        )
        self.assertFalse(res_non_violence.is_violence)

        # Test violent CAMEO code (root 14 Protest/Clash)
        res_protest = ClassificationResult(
            cameo_code="145",
            cameo_label="Violent protest",
            confidence=0.9,
            method="rule",
        )
        self.assertTrue(res_protest.is_violence)

    def test_rule_based_classifier(self):
        classifier = CAMEOClassifier()
        text = "Supporters of rival groups clashed in the street, throwing stones and bricks."
        result = classifier.classify(text, mode="rule_only")
        self.assertIsNotNone(result)
        self.assertIsInstance(result.code, str)
        self.assertTrue(result.is_violence)

    def test_trigger_mapping(self):
        trigger = TriggerSpan(
            text="clash",
            lemma="clash",
            start=0,
            end=5,
            cameo_code="145",
            kind="verb",
        )
        result = classify_event(trigger, "A violent clash broke out between students.", use_model=False)
        self.assertIsNotNone(result.cameo_code)
        self.assertTrue(result.is_violence)


if __name__ == "__main__":
    unittest.main()
