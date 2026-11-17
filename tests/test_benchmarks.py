"""
tests/test_benchmarks.py
Unit tests verifying unbiased matching in ACLED and GDELT benchmarks.
"""

import unittest
from evaluation.benchmark_acled import align_with_acled, compute_acled_metrics
from evaluation.benchmark_gdelt import align_events, compute_metrics


class TestBenchmarkAlignments(unittest.TestCase):
    def test_acled_unbiased_alignment_and_location_tiers(self):
        # System event in Dhaka, predicting CAMEO 18 (Assault)
        system_events = [
            {
                "event_id": "s1",
                "date": {"normalized": "2024-10-15"},
                "district": "Dhaka",
                "cameo_code": "182",
                "actors": [{"name": "Police"}],
            }
        ]
        # Two ACLED candidates in the date window:
        # Candidate 1: 0 days away, Dhaka district, ACLED event type 'Protests' (CAMEO 14)
        # Candidate 2: 5 days away, Dhaka district, ACLED event type 'Violence against civilians' (CAMEO 18)
        # Candidate 3: 0 days away, Gazipur (Dhaka division, not Dhaka district)
        acled_events = [
            {
                "event_date": "2024-10-15",
                "admin1": "Dhaka Division",
                "admin2": "Dhaka",
                "event_type": "Protests",
                "sub_event_type": "Peaceful protest",
                "actor1": "Police",
                "source": "Newspaper A",
            },
            {
                "event_date": "2024-10-20",
                "admin1": "Dhaka Division",
                "admin2": "Dhaka",
                "event_type": "Violence against civilians",
                "sub_event_type": "Attack",
                "actor1": "Unknown",
                "source": "Newspaper B",
            },
        ]

        # Prior to the fix, type_penalty would have picked Candidate 2 because CAMEO 18 == scode 18!
        # With unbiased matching, Candidate 1 MUST be picked because temporal distance is 0 days vs 5 days!
        alignments = align_with_acled(system_events, acled_events, date_window_days=7)
        self.assertEqual(len(alignments), 1)
        align = alignments[0]

        # Unbiased candidate selection picks Candidate 1 (Protests, code 14)
        self.assertEqual(align["acled_code"], 14)
        self.assertFalse(align["code_match"])  # scode 18 != acled 14
        self.assertTrue(align["exact_district_match"])
        self.assertTrue(align["division_match"])

        metrics = compute_acled_metrics(alignments)
        self.assertEqual(metrics["total_system_events"], 1)
        self.assertEqual(metrics["matched_with_acled"], 1)
        self.assertEqual(metrics["exact_district_accuracy"], 1.0)
        self.assertEqual(metrics["cameo_code_accuracy"], 0.0)

    def test_gdelt_alignment_modes(self):
        system_events = [
            {
                "event_id": "s1",
                "date": "2024-10-10",
                "district": "Chittagong",
                "cameo_code": "193",  # Fight
                "source_url": "https://www.thedailystar.net/news/clash-123?ref=rss",
                "actors": [{"name": "Activists"}],
            }
        ]
        gdelt_events = [
            {
                "date": "2024-10-10",
                "location": "Chittagong",
                "cameo_code": "145",
                "actor1": "Activists",
                "source_url": "http://thedailystar.net/news/clash-123/",
            },
            {
                "date": "2024-10-12",
                "location": "Chittagong",
                "cameo_code": "190",
                "actor1": "Army",
                "source_url": "http://other-outlet.com/news/army-456",
            },
        ]

        # Mode A: URL matching should find the first candidate via normalized URL
        aligns_url = align_events(system_events, gdelt_events, date_window_days=3, mode="url")
        self.assertEqual(len(aligns_url), 1)
        self.assertEqual(aligns_url[0]["gdelt_code"], 14)
        self.assertFalse(aligns_url[0]["match"])  # 19 != 14

        # Mode B: Spatiotemporal matching with dt=0 should pick candidate 1 (dt=0 vs dt=2)
        aligns_st = align_events(system_events, gdelt_events, date_window_days=3, mode="spatiotemporal")
        self.assertEqual(len(aligns_st), 1)
        self.assertEqual(aligns_st[0]["gdelt_code"], 14)
