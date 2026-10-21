"""
tests/test_scraper.py
Unit tests for Daily Star article schema, serialization, and RSS feed metadata.
"""
import unittest
from scraper.schema import Article


class TestScraperSchema(unittest.TestCase):
    def test_article_serialization(self):
        article = Article(
            url="https://www.thedailystar.net/news/bangladesh/crime-justice/news/clash-dhaka-385000",
            title="Clash in Dhaka leaves 5 injured",
            body="A clash broke out between two factions in Dhaka yesterday, leaving five people injured.",
            category="crime-justice",
            tags=["clash", "dhaka", "crime"],
            published_date="2025-03-15T12:00:00+06:00",
            source="thedailystar.net",
        )
        data = article.to_dict()
        self.assertEqual(data["title"], "Clash in Dhaka leaves 5 injured")
        self.assertEqual(data["category"], "crime-justice")
        self.assertIn("clash", data["tags"])

        json_str = article.to_json()
        restored = Article.from_json(json_str)
        self.assertEqual(restored.url, article.url)
        self.assertEqual(restored.title, article.title)
        self.assertEqual(restored.body, article.body)

    def test_article_default_id(self):
        a1 = Article()
        a2 = Article()
        self.assertTrue(a1.id)
        self.assertTrue(a2.id)
        self.assertNotEqual(a1.id, a2.id)


if __name__ == "__main__":
    unittest.main()
