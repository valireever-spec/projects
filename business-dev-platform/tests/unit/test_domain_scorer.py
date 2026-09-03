"""Unit tests for the domain scoring algorithm with plausibility validation.

Validates the *shipping* API: score_domains(domain_data, trend_data,
sector_stats, registrations) -> sorted list[DomainScore], plus the pure
component helpers it delegates to.
"""
import pytest
from backend.analytics.domain_scorer import (
    score_domains,
    _grade_score,
    _calculate_market_growth,
    _calculate_competition_score,
    _calculate_registration_momentum,
)


def _domains(*slugs):
    """Minimal domain_data records keyed by slug, each with its own nace code."""
    return [{"slug": s, "name_de": s, "name_en": s, "nace_r2_code": s} for s in slugs]


def _reg(latest, previous):
    """A two-point registration history (previous, latest)."""
    return [{"registrations": previous}, {"registrations": latest}]


class TestCompositeScoring:
    """Test the end-to-end scoring via the public API."""

    def test_returns_all_fields_and_bounded(self):
        scored = score_domains(_domains("a"), {"a": 50}, {"a": {}}, {})
        s = scored[0]
        assert 0 <= s.composite_score <= 100
        assert s.grade in {"Excellent", "Good", "Moderate", "Saturated"}
        assert s.trend_momentum + s.market_growth + s.competition_density + \
            s.registration_momentum == pytest.approx(s.composite_score, abs=0.3)

    def test_trend_momentum_scales_0_to_30(self):
        # trend interest 100 -> full 30; interest 0 -> 0.
        full = score_domains(_domains("a"), {"a": 100}, {"a": {}}, {})[0]
        none = score_domains(_domains("a"), {"a": 0}, {"a": {}}, {})[0]
        assert full.trend_momentum == pytest.approx(30)
        assert none.trend_momentum == pytest.approx(0)

    def test_maximum_and_minimum_bounded(self):
        best = score_domains(
            _domains("best"),
            {"best": 100},
            {"best": {"growth_rate": 0.20, "enterprise_count": 10}},
            {"best": _reg(200, 100)},
        )[0]
        worst = score_domains(
            _domains("worst"),
            {"worst": 0},
            {"worst": {"growth_rate": -0.1, "enterprise_count": 5_000_000}},
            {"worst": _reg(50, 100)},
        )[0]
        assert 0 <= worst.composite_score <= best.composite_score <= 100


class TestGrading:
    def test_grade_boundaries(self):
        assert _grade_score(80) == "Excellent"
        assert _grade_score(79.9) == "Good"
        assert _grade_score(60) == "Good"
        assert _grade_score(50) == "Moderate"
        assert _grade_score(40) == "Moderate"
        assert _grade_score(39.9) == "Saturated"
        assert _grade_score(0) == "Saturated"


class TestMarketGrowthComponent:
    def test_bounds(self):
        assert 0 <= _calculate_market_growth({"x": {"growth_rate": 0.0}}, "x") <= 25
        assert 0 <= _calculate_market_growth({"x": {"growth_rate": 1.0}}, "x") <= 25

    def test_caps_at_12_percent(self):
        assert _calculate_market_growth({"x": {"growth_rate": 0.12}}, "x") == 25
        assert _calculate_market_growth({"x": {"growth_rate": 0.50}}, "x") == 25

    def test_monotonic_in_growth(self):
        low = _calculate_market_growth({"x": {"growth_rate": 0.03}}, "x")
        high = _calculate_market_growth({"x": {"growth_rate": 0.09}}, "x")
        assert low < high


class TestCompetitionComponent:
    """Competition is inverted: more enterprises -> lower score."""

    def test_bounds(self):
        assert 0 <= _calculate_competition_score({"x": {"enterprise_count": 10}}, "x") <= 25
        assert 0 <= _calculate_competition_score({"x": {"enterprise_count": 5_000_000}}, "x") <= 25

    def test_inverted(self):
        low_comp = _calculate_competition_score({"x": {"enterprise_count": 100}}, "x")
        high_comp = _calculate_competition_score({"x": {"enterprise_count": 5_000_000}}, "x")
        assert low_comp > high_comp

    def test_1000x_bug_is_fixed(self):
        # 5000 enterprises across 83M people is ~0.06 per 1000 residents = very
        # low competition. Before the fix this returned 0 (saturated); it should
        # now score near the top of the 0-25 range.
        score = _calculate_competition_score({"x": {"enterprise_count": 5000}}, "x")
        assert score >= 20


class TestRegistrationComponent:
    def test_bounds(self):
        assert 0 <= _calculate_registration_momentum({"x": _reg(100, 100)}, "x") <= 20
        assert 0 <= _calculate_registration_momentum({"x": _reg(300, 100)}, "x") <= 20

    def test_default_when_no_history(self):
        assert _calculate_registration_momentum({}, "x") == 10

    def test_growth_beats_decline(self):
        growth = _calculate_registration_momentum({"x": _reg(130, 100)}, "x")
        decline = _calculate_registration_momentum({"x": _reg(80, 100)}, "x")
        assert growth > decline


class TestRankingConsistency:
    def test_sorted_descending(self):
        domain_data = _domains("low", "high")
        trend = {"low": 5, "high": 95}
        sector = {
            "low": {"growth_rate": 0.0, "enterprise_count": 5_000_000},
            "high": {"growth_rate": 0.15, "enterprise_count": 50},
        }
        scored = score_domains(domain_data, trend, sector, {})
        scores = [d.composite_score for d in scored]
        assert scores == sorted(scores, reverse=True)
        assert scored[0].slug == "high"

    def test_consistent_across_runs(self):
        domain_data = _domains(*[f"d{i}" for i in range(5)])
        trend = {f"d{i}": i * 20 for i in range(5)}
        a = score_domains(domain_data, trend, {}, {})
        b = score_domains(domain_data, trend, {}, {})
        assert [d.slug for d in a] == [d.slug for d in b]


class TestEdgeCases:
    def test_missing_trend_uses_default(self):
        # No trend entry for the slug -> default interest of 20 -> non-zero, bounded.
        s = score_domains(_domains("a"), {}, {}, {})[0]
        assert 0 <= s.composite_score <= 100
        assert s.trend_momentum == pytest.approx(6)  # (20/100)*30

    def test_empty_domain_list(self):
        assert score_domains([], {}, {}, {}) == []
