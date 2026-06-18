"""
Unit tests for confidence_scorer.py
"""

import pytest
from backend.analytics.confidence_scorer import calculate_confidence_score


def test_weights_sum_to_one():
    """Weights should sum to 1.0"""
    domain_score = {"grade": "good", "data_quality_flags": [], "competition_component": 15}
    financial = {"break_even_month": 12, "year_1_net": 30000}
    risk = {}
    profile = {"revenue_model": "subscription", "legal_form": "GmbH"}

    result = calculate_confidence_score(domain_score, financial, risk, profile)

    weights = [d["weight"] for d in result["drivers"]]
    assert sum(weights) == pytest.approx(1.0, abs=0.01)


def test_tier_high_boundary():
    """Score >= 75 should yield 'high' tier"""
    domain_score = {"grade": "excellent", "data_quality_flags": [], "competition_component": 20}
    financial = {"break_even_month": 3, "year_1_net": 50000}
    risk = {}
    profile = {"revenue_model": "subscription", "legal_form": "Einzelunternehmen"}

    result = calculate_confidence_score(domain_score, financial, risk, profile)

    assert result["confidence_tier"] == "high"
    assert result["confidence_band_pct"] == 15


def test_tier_medium_boundary():
    """Score >= 50 and < 75 should yield 'medium' tier"""
    domain_score = {"grade": "moderate", "data_quality_flags": [], "competition_component": 12}
    financial = {"break_even_month": 12, "year_1_net": 20000}
    risk = {}
    profile = {"revenue_model": "hourly", "legal_form": "GmbH"}

    result = calculate_confidence_score(domain_score, financial, risk, profile)

    assert result["confidence_tier"] == "medium"
    assert result["confidence_band_pct"] == 25


def test_tier_low_boundary():
    """Score < 50 should yield 'low' tier"""
    domain_score = {"grade": "saturated", "data_quality_flags": ["default1", "default2"], "competition_component": 2}
    financial = {"break_even_month": 30, "year_1_net": 5000}
    risk = {}
    profile = {"revenue_model": "commission", "legal_form": "AG"}

    result = calculate_confidence_score(domain_score, financial, risk, profile)

    assert result["confidence_tier"] == "low"
    assert result["confidence_band_pct"] == 40


def test_excellent_grade_higher_than_saturated():
    """Excellent domain should have higher score than saturated"""
    profile = {"revenue_model": "subscription", "legal_form": "GmbH"}
    financial = {"break_even_month": 12, "year_1_net": 30000}
    risk = {}

    excellent_score = calculate_confidence_score(
        {"grade": "excellent", "data_quality_flags": [], "competition_component": 20},
        financial, risk, profile
    )

    saturated_score = calculate_confidence_score(
        {"grade": "saturated", "data_quality_flags": [], "competition_component": 5},
        financial, risk, profile
    )

    assert excellent_score["confidence_score"] > saturated_score["confidence_score"]


def test_short_breakeven_higher_score():
    """Faster break-even should result in higher confidence score"""
    domain_score = {"grade": "good", "data_quality_flags": [], "competition_component": 15}
    risk = {}
    profile = {"revenue_model": "subscription", "legal_form": "GmbH"}

    fast_breakeven = calculate_confidence_score(
        domain_score, {"break_even_month": 3, "year_1_net": 30000}, risk, profile
    )

    slow_breakeven = calculate_confidence_score(
        domain_score, {"break_even_month": 24, "year_1_net": 30000}, risk, profile
    )

    assert fast_breakeven["confidence_score"] > slow_breakeven["confidence_score"]


def test_legal_form_impact():
    """Einzelunternehmen should have higher regulatory clarity than AG"""
    domain_score = {"grade": "good", "data_quality_flags": [], "competition_component": 15}
    financial = {"break_even_month": 12, "year_1_net": 30000}
    risk = {}

    einzelunternehmen = calculate_confidence_score(
        domain_score, financial, risk, {"revenue_model": "hourly", "legal_form": "Einzelunternehmen"}
    )

    ag = calculate_confidence_score(
        domain_score, financial, risk, {"revenue_model": "hourly", "legal_form": "AG"}
    )

    # Einzelunternehmen should have higher score due to better regulatory clarity
    assert einzelunternehmen["confidence_score"] > ag["confidence_score"]


def test_all_warnings_are_strings():
    """All warnings should be strings"""
    domain_score = {"grade": "saturated", "data_quality_flags": ["trend_default", "count_default"], "competition_component": 5}
    financial = {"break_even_month": 30, "year_1_net": 5000}
    risk = {}
    profile = {"revenue_model": "hourly", "legal_form": "AG"}

    result = calculate_confidence_score(domain_score, financial, risk, profile)

    assert all(isinstance(w, str) for w in result["warnings"])


def test_returns_required_keys():
    """Result should contain all required keys"""
    domain_score = {"grade": "good", "data_quality_flags": [], "competition_component": 15}
    financial = {"break_even_month": 12, "year_1_net": 30000}
    risk = {}
    profile = {"revenue_model": "subscription", "legal_form": "GmbH"}

    result = calculate_confidence_score(domain_score, financial, risk, profile)

    assert "confidence_score" in result
    assert "confidence_tier" in result
    assert "confidence_band_pct" in result
    assert "drivers" in result
    assert "warnings" in result


def test_confidence_score_0_to_100():
    """Confidence score should be between 0 and 100"""
    domain_score = {"grade": "moderate", "data_quality_flags": [], "competition_component": 12}
    financial = {"break_even_month": 12, "year_1_net": 30000}
    risk = {}
    profile = {"revenue_model": "subscription", "legal_form": "GmbH"}

    result = calculate_confidence_score(domain_score, financial, risk, profile)

    assert 0 <= result["confidence_score"] <= 100


def test_drivers_have_required_structure():
    """Each driver should have factor, score, weight"""
    domain_score = {"grade": "good", "data_quality_flags": [], "competition_component": 15}
    financial = {"break_even_month": 12, "year_1_net": 30000}
    risk = {}
    profile = {"revenue_model": "subscription", "legal_form": "GmbH"}

    result = calculate_confidence_score(domain_score, financial, risk, profile)

    for driver in result["drivers"]:
        assert "factor" in driver
        assert "score" in driver
        assert "weight" in driver
        assert 0 <= driver["score"] <= 100
        assert 0 <= driver["weight"] <= 1


def test_data_quality_flags_reduce_score():
    """More data quality flags should result in lower score"""
    domain_score_clean = {"grade": "good", "data_quality_flags": [], "competition_component": 15}
    domain_score_dirty = {"grade": "good", "data_quality_flags": ["trend_default", "count_default"], "competition_component": 15}
    financial = {"break_even_month": 12, "year_1_net": 30000}
    risk = {}
    profile = {"revenue_model": "subscription", "legal_form": "GmbH"}

    clean = calculate_confidence_score(domain_score_clean, financial, risk, profile)
    dirty = calculate_confidence_score(domain_score_dirty, financial, risk, profile)

    assert clean["confidence_score"] > dirty["confidence_score"]


def test_long_runway_generates_warning():
    """Break-even > 18 months should generate warning"""
    domain_score = {"grade": "good", "data_quality_flags": [], "competition_component": 15}
    financial = {"break_even_month": 24, "year_1_net": 30000}
    risk = {}
    profile = {"revenue_model": "subscription", "legal_form": "GmbH"}

    result = calculate_confidence_score(domain_score, financial, risk, profile)

    assert any("runway" in w.lower() for w in result["warnings"])


def test_empty_profile_handled():
    """Empty profile should not crash"""
    domain_score = {"grade": "good", "data_quality_flags": [], "competition_component": 15}
    financial = {"break_even_month": 12, "year_1_net": 30000}
    risk = {}
    profile = {}

    result = calculate_confidence_score(domain_score, financial, risk, profile)

    assert "confidence_score" in result
    assert result["confidence_score"] >= 0


def test_missing_financial_data():
    """Missing financial data should use defaults"""
    domain_score = {"grade": "good", "data_quality_flags": [], "competition_component": 15}
    financial = {}
    risk = {}
    profile = {"revenue_model": "subscription", "legal_form": "GmbH"}

    result = calculate_confidence_score(domain_score, financial, risk, profile)

    assert "confidence_score" in result
    assert result["confidence_score"] >= 0
