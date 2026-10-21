"""
tests/test_relevance_filter.py
Unit tests for relevance filter and violence keyword detection.
"""
import unittest
from nlp.relevance_filter import is_violence_related, Verdict, VIOLENCE_PATTERNS


class TestRelevanceFilter(unittest.TestCase):
    def test_violence_matching(self):
        title = "Clash leaves three killed in Sylhet"
        body = "Three people were killed and twenty injured in a violent clash between two factions."
        result = is_violence_related(title, body)
        self.assertEqual(result.verdict, Verdict.VIOLENCE)
        self.assertGreater(result.confidence, 0.5)

    def test_dowry_violence_pattern(self):
        # Specific regression test for Issue #5 (dowry typo fix)
        text = "Police arrested the husband in connection with a brutal dowry killing case in Sylhet."
        matched = any(p.search(text) for p in VIOLENCE_PATTERNS)
        self.assertTrue(matched, "Dowry violence pattern must match 'dowry killing'")
        result = is_violence_related("Dowry killing incident", text)
        self.assertEqual(result.verdict, Verdict.VIOLENCE)

    def test_non_violence_filtering(self):
        title = "Central bank announces new interest rate policy"
        body = "The central bank announced a new monetary policy to curb inflation and promote trade growth."
        result = is_violence_related(title, body)
        self.assertEqual(result.verdict, Verdict.NOT_VIOLENCE)
        self.assertGreater(result.confidence, 0.5)


if __name__ == "__main__":
    unittest.main()
