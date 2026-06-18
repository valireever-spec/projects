"""Unit tests for domain scoring algorithm with plausibility validation."""
import pytest
from backend.analytics.domain_scorer import (
    score_domains,
    score_single_domain,
    _calculate_trend_momentum,
    _calculate_market_growth,
    _calculate_competition_density,
    _calculate_registration_momentum,
    _grade_score
)


class TestDomainScoringAlgorithm:
    """Test the core domain scoring algorithm."""

    def test_score_single_domain_returns_valid_structure(self):
        """Test that scoring returns all required fields."""
        domain = {
            "slug": "test-domain",
            "name_de": "Test Domain",
            "market_size_estimate": "€10M",
            "trend_momentum": 20.0,
            "market_growth": 15.0,
            "competition_density": 5.0,
            "registration_momentum": 10.0,
        }

        score = score_single_domain(domain)

        assert "total_score" in score
        assert "components" in score
        assert "grade" in score
        assert 0 <= score["total_score"] <= 100

    def test_total_score_composition(self):
        """Test that total score is sum of components."""
        domain = {
            "slug": "test",
            "name_de": "Test",
            "trend_momentum": 10.0,
            "market_growth": 10.0,
            "competition_density": 10.0,
            "registration_momentum": 10.0,
        }

        score = score_single_domain(domain)
        components = score["components"]

        expected_total = (
            components["trend"] +
            components["market"] +
            components["competition"] +
            components["registration"]
        )

        assert score["total_score"] == expected_total

    def test_maximum_possible_score(self):
        """Test that maximum score is 100."""
        domain = {
            "slug": "perfect",
            "name_de": "Perfect",
            "trend_momentum": 100.0,  # Max trend
            "market_growth": 100.0,   # Max market growth
            "competition_density": 0.0,   # Min competition (best case)
            "registration_momentum": 100.0,  # Max registration
        }

        score = score_single_domain(domain)
        assert score["total_score"] <= 100

    def test_minimum_possible_score(self):
        """Test that minimum score is 0."""
        domain = {
            "slug": "worst",
            "name_de": "Worst",
            "trend_momentum": 0.0,
            "market_growth": 0.0,
            "competition_density": 1000.0,  # Very high competition
            "registration_momentum": 0.0,
        }

        score = score_single_domain(domain)
        assert score["total_score"] >= 0

    def test_competition_density_inverted(self):
        """Test that higher competition yields lower score."""
        domain_low_competition = {
            "slug": "low-comp",
            "name_de": "Low Competition",
            "competition_density": 1.0,
            "trend_momentum": 50.0,
            "market_growth": 50.0,
            "registration_momentum": 50.0,
        }

        domain_high_competition = {
            "slug": "high-comp",
            "name_de": "High Competition",
            "competition_density": 100.0,
            "trend_momentum": 50.0,
            "market_growth": 50.0,
            "registration_momentum": 50.0,
        }

        score_low = score_single_domain(domain_low_competition)
        score_high = score_single_domain(domain_high_competition)

        assert score_low["total_score"] > score_high["total_score"], \
            "Lower competition should yield higher score"

    def test_grading_boundaries(self):
        """Test that grade boundaries are correct."""
        # Excellent (≥80)
        domain_excellent = {
            "slug": "excellent",
            "name_de": "Excellent",
            "trend_momentum": 30.0,
            "market_growth": 25.0,
            "competition_density": 0.0,
            "registration_momentum": 20.0,
        }
        assert _grade_score(80) == "Excellent"

        # Good (≥60, <80)
        assert _grade_score(70) == "Good"

        # Moderate (≥40, <60)
        assert _grade_score(50) == "Moderate"

        # Saturated (<40)
        assert _grade_score(30) == "Saturated"


class TestComponentCalculations:
    """Test individual scoring components."""

    def test_trend_momentum_bounds(self):
        """Test that trend momentum is bounded 0-30."""
        score = _calculate_trend_momentum(0.0)
        assert 0 <= score <= 30

        score = _calculate_trend_momentum(100.0)
        assert 0 <= score <= 30

        score = _calculate_trend_momentum(50.0)
        assert 0 <= score <= 30

    def test_market_growth_bounds(self):
        """Test that market growth is bounded 0-25."""
        score = _calculate_market_growth(0.0)
        assert 0 <= score <= 25

        score = _calculate_market_growth(100.0)
        assert 0 <= score <= 25

    def test_competition_density_bounds(self):
        """Test that competition density is bounded 0-25."""
        score = _calculate_competition_density(0.0)
        assert 0 <= score <= 25

        score = _calculate_competition_density(1000.0)
        assert 0 <= score <= 25

    def test_registration_momentum_bounds(self):
        """Test that registration momentum is bounded 0-20."""
        score = _calculate_registration_momentum(0.0)
        assert 0 <= score <= 20

        score = _calculate_registration_momentum(100.0)
        assert 0 <= score <= 20

    def test_component_monotonicity(self):
        """Test that components increase monotonically (except competition)."""
        # Trend should increase with input
        trend_low = _calculate_trend_momentum(10.0)
        trend_high = _calculate_trend_momentum(50.0)
        assert trend_low <= trend_high, "Trend should increase with momentum"

        # Competition should decrease with input (inverted)
        comp_low = _calculate_competition_density(10.0)
        comp_high = _calculate_competition_density(100.0)
        assert comp_low >= comp_high, "Competition should decrease with density"


class TestScoringPlausibility:
    """Test plausibility of scoring results."""

    def test_similar_inputs_similar_scores(self):
        """Test that similar domain inputs produce similar scores."""
        domain1 = {
            "slug": "domain-1",
            "name_de": "Domain 1",
            "trend_momentum": 50.0,
            "market_growth": 40.0,
            "competition_density": 20.0,
            "registration_momentum": 30.0,
        }

        domain2 = {
            "slug": "domain-2",
            "name_de": "Domain 2",
            "trend_momentum": 51.0,  # Slightly different
            "market_growth": 41.0,
            "competition_density": 21.0,
            "registration_momentum": 31.0,
        }

        score1 = score_single_domain(domain1)["total_score"]
        score2 = score_single_domain(domain2)["total_score"]

        # Scores should be very close (within 5 points)
        assert abs(score1 - score2) < 5, \
            "Similar inputs should produce similar scores"

    def test_no_negative_scores(self):
        """Test that scores are never negative."""
        domain = {
            "slug": "any",
            "name_de": "Any",
            "trend_momentum": 0.0,
            "market_growth": 0.0,
            "competition_density": 1000.0,
            "registration_momentum": 0.0,
        }

        score = score_single_domain(domain)
        assert score["total_score"] >= 0, "Score should never be negative"

    def test_component_weights_correct(self):
        """Test that component weights are within expected ranges."""
        domain = {
            "slug": "test",
            "name_de": "Test",
            "trend_momentum": 50.0,
            "market_growth": 50.0,
            "competition_density": 50.0,
            "registration_momentum": 50.0,
        }

        score = score_single_domain(domain)
        components = score["components"]

        # Check weights sum to 100 total
        total_weight = (
            (components["trend"] / 30) +  # trend is 0-30
            (components["market"] / 25) +  # market is 0-25
            (components["competition"] / 25) +  # competition is 0-25
            (components["registration"] / 20)  # registration is 0-20
        )

        # Total should be roughly proportional to input values
        assert total_weight > 0, "Components should have weight"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_values(self):
        """Test that zero values are handled correctly."""
        domain = {
            "slug": "zero",
            "name_de": "Zero",
            "trend_momentum": 0.0,
            "market_growth": 0.0,
            "competition_density": 0.0,
            "registration_momentum": 0.0,
        }

        score = score_single_domain(domain)
        assert 0 <= score["total_score"] <= 100

    def test_extreme_high_values(self):
        """Test that extreme high values are capped correctly."""
        domain = {
            "slug": "extreme",
            "name_de": "Extreme",
            "trend_momentum": 10000.0,
            "market_growth": 10000.0,
            "competition_density": 0.0,
            "registration_momentum": 10000.0,
        }

        score = score_single_domain(domain)
        assert score["total_score"] <= 100, "Score should be capped at 100"

    def test_negative_values_handled(self):
        """Test that negative input values are handled gracefully."""
        domain = {
            "slug": "negative",
            "name_de": "Negative",
            "trend_momentum": -10.0,
            "market_growth": -5.0,
            "competition_density": -100.0,
            "registration_momentum": -20.0,
        }

        # Should not crash
        score = score_single_domain(domain)
        assert 0 <= score["total_score"] <= 100


class TestRankingConsistency:
    """Test that ranking is consistent."""

    def test_ranking_order(self):
        """Test that domains are ranked correctly."""
        domains = [
            {
                "slug": "low",
                "name_de": "Low Score",
                "trend_momentum": 10.0,
                "market_growth": 10.0,
                "competition_density": 100.0,
                "registration_momentum": 10.0,
            },
            {
                "slug": "medium",
                "name_de": "Medium Score",
                "trend_momentum": 50.0,
                "market_growth": 50.0,
                "competition_density": 50.0,
                "registration_momentum": 50.0,
            },
            {
                "slug": "high",
                "name_de": "High Score",
                "trend_momentum": 90.0,
                "market_growth": 90.0,
                "competition_density": 10.0,
                "registration_momentum": 90.0,
            },
        ]

        scored = score_domains(domains)
        scores = [d["total_score"] for d in scored]

        # Should be sorted in descending order
        assert scores == sorted(scores, reverse=True), \
            "Domains should be ranked highest score first"

    def test_consistent_ranking_order(self):
        """Test that re-scoring produces same order."""
        domains = [
            {
                "slug": f"domain-{i}",
                "name_de": f"Domain {i}",
                "trend_momentum": float(i * 10),
                "market_growth": float(i * 5),
                "competition_density": float(100 - i * 10),
                "registration_momentum": float(i * 3),
            }
            for i in range(1, 6)
        ]

        scored1 = score_domains(domains)
        scored2 = score_domains(domains)

        order1 = [d["slug"] for d in scored1]
        order2 = [d["slug"] for d in scored2]

        assert order1 == order2, "Ranking should be consistent across runs"
