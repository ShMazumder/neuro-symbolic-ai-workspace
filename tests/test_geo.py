"""
tests/test_geo.py
Unit tests for nlp/geo.py (Geospatial extraction and normalization for Bangladesh).
"""

import pytest
from nlp.geo import (
    BD_DISTRICTS,
    LOCATION_ALIASES,
    GeoResult,
    normalize_location,
    extract_locations,
    extract_districts,
)


class TestGeoExtraction:
    def test_gazetteer_contains_major_districts(self):
        assert "dhaka" in BD_DISTRICTS
        assert "chittagong" in BD_DISTRICTS
        assert "sylhet" in BD_DISTRICTS
        assert "rajshahi" in BD_DISTRICTS
        assert BD_DISTRICTS["dhaka"]["division"] == "Dhaka"

    def test_normalize_exact_district(self):
        res = normalize_location("Dhaka")
        assert res.district == "Dhaka"
        assert res.division == "Dhaka"
        assert res.confidence == 0.9
        assert res.method == "gazetteer"
        assert res.latitude is not None
        assert res.longitude is not None

    def test_normalize_with_suffix(self):
        res = normalize_location("Sylhet district")
        assert res.district == "Sylhet"
        assert res.division == "Sylhet"
        assert res.confidence == 0.9

    def test_normalize_aliases(self):
        # Cumilla -> Comilla
        res_cumilla = normalize_location("Cumilla")
        assert res_cumilla.district == "Comilla"

        # Bogra -> Bogura
        res_bogra = normalize_location("Bogra")
        assert res_bogra.district == "Bogura"

        # Dhaka city -> Dhaka
        res_dhaka_city = normalize_location("Dhaka city")
        assert res_dhaka_city.district == "Dhaka"

    def test_normalize_unknown_location(self):
        res = normalize_location("Atlantis Undersea")
        assert res.district is None
        assert res.confidence == 0.0
        assert res.method == "failed"

    def test_extract_locations_regex_fallback(self):
        text = "Violent clashes broke out between students and police in Chittagong and Rajshahi yesterday."
        results = extract_locations(text)
        districts = [r.district for r in results if r.district]
        assert "Chittagong" in districts
        assert "Rajshahi" in districts

    def test_extract_districts_helper(self):
        text = "Protesters marched through Barisal and then moved towards Khulna district."
        districts = extract_districts(text)
        assert "Barisal" in districts
        assert "Khulna" in districts
