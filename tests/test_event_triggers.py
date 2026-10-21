"""
tests/test_event_triggers.py
Unit tests for violence trigger verb and noun phrase detection.
"""
import unittest
from nlp.event_triggers import detect_triggers, extract_triggers, TRIGGER_VERBS, TRIGGER_NOUNS


class TestEventTriggers(unittest.TestCase):
    def test_verb_trigger_detection(self):
        text = "Armed men attacked the checkpoint and killed two security guards."
        triggers = detect_triggers(text)
        self.assertGreater(len(triggers), 0)
        lemmas = [t.lemma for t in triggers]
        self.assertTrue("attack" in lemmas or "kill" in lemmas)

    def test_noun_phrase_trigger(self):
        text = "An arson attack destroyed three vehicles during the protest."
        triggers = detect_triggers(text)
        self.assertGreater(len(triggers), 0)
        matched_noun = any(t.kind == "noun" for t in triggers)
        self.assertTrue(matched_noun)

    def test_extract_triggers_alias(self):
        text = "Protesters clashed with police."
        t1 = detect_triggers(text)
        t2 = extract_triggers(text)
        self.assertEqual(len(t1), len(t2))


if __name__ == "__main__":
    unittest.main()
