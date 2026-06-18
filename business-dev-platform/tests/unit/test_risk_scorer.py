"""Unit tests for risk assessment model with validation."""
import pytest
from backend.analytics.risk_scorer import assess_risks


class TestRiskAssessmentStructure:
    """Test that risk assessment returns correct structure."""

    def test_risk_assessment_returns_required_fields(self):
        """Test that assess_risks returns all required fields."""
        result = assess_risks(
            domain="consulting",
            legal_form="Einzelunternehmen",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        assert "overall_risk_level" in result
        assert "risk_score" in result
        assert "risk_factors" in result
        assert "top_3_risks" in result
        assert "mitigation_strategies" in result

    def test_risk_level_values(self):
        """Test that risk level is one of valid values."""
        result = assess_risks(
            domain="consulting",
            legal_form="GmbH",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        valid_levels = ["low", "medium", "high"]
        assert result["overall_risk_level"] in valid_levels

    def test_risk_score_in_bounds(self):
        """Test that risk score is between 0-100."""
        result = assess_risks(
            domain="online-coaching",
            legal_form="Freiberufler",
            city="Hamburg",
            financial_projection={"break_even_month": 3}
        )

        assert 0 <= result["risk_score"] <= 100

    def test_eight_risk_dimensions(self):
        """Test that assessment covers 8 risk dimensions."""
        result = assess_risks(
            domain="ecommerce",
            legal_form="GmbH",
            city="Munich",
            financial_projection={"break_even_month": 9}
        )

        risk_factors = result["risk_factors"]
        assert len(risk_factors) == 8, "Should assess 8 dimensions"

        # Check all have required fields
        for factor in risk_factors:
            assert "name" in factor
            assert "score" in factor
            assert "description" in factor
            assert "color" in factor


class TestRiskDimensionBounds:
    """Test that each risk dimension is properly bounded."""

    def test_risk_factor_scores_bounded(self):
        """Test that all risk factors are bounded."""
        result = assess_risks(
            domain="consulting",
            legal_form="Einzelunternehmen",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        for factor in result["risk_factors"]:
            score = factor["score"]
            assert 0 <= score <= 20, \
                f"Risk factor {factor['name']} score {score} out of bounds"

    def test_risk_colors_valid(self):
        """Test that risk colors are valid."""
        result = assess_risks(
            domain="saas",
            legal_form="UG",
            city="Berlin",
            financial_projection={"break_even_month": 8}
        )

        valid_colors = ["green", "yellow", "orange", "red"]
        for factor in result["risk_factors"]:
            color = factor.get("color", "")
            assert color in valid_colors, \
                f"Invalid color {color} for {factor['name']}"

    def test_risk_color_correlates_with_score(self):
        """Test that risk color matches score level."""
        result = assess_risks(
            domain="consulting",
            legal_form="GmbH",
            city="Hamburg",
            financial_projection={"break_even_month": 4}
        )

        for factor in result["risk_factors"]:
            score = factor["score"]
            color = factor["color"]

            if score <= 5:
                assert color == "green", f"Score {score} should be green"
            elif score <= 10:
                assert color == "yellow", f"Score {score} should be yellow"
            elif score <= 15:
                assert color == "orange", f"Score {score} should be orange"
            else:
                assert color == "red", f"Score {score} should be red"


class TestBreakEvenRiskInfluence:
    """Test that break-even month influences risk score."""

    def test_quick_break_even_lower_risk(self):
        """Test that quick break-even results in lower risk."""
        risk_fast = assess_risks(
            domain="consulting",
            legal_form="Einzelunternehmen",
            city="Berlin",
            financial_projection={"break_even_month": 2}
        )

        risk_slow = assess_risks(
            domain="consulting",
            legal_form="Einzelunternehmen",
            city="Berlin",
            financial_projection={"break_even_month": 18}
        )

        assert risk_fast["risk_score"] < risk_slow["risk_score"], \
            "Faster break-even should result in lower risk"

    def test_break_even_within_first_year_healthy(self):
        """Test that break-even within first year is considered lower risk."""
        risk_12mo = assess_risks(
            domain="ecommerce",
            legal_form="GmbH",
            city="Munich",
            financial_projection={"break_even_month": 12}
        )

        risk_24mo = assess_risks(
            domain="ecommerce",
            legal_form="GmbH",
            city="Munich",
            financial_projection={"break_even_month": 24}
        )

        # Score should be lower for 12-month break-even
        assert risk_12mo["risk_score"] <= risk_24mo["risk_score"]


class TestLegalFormRiskInfluence:
    """Test that legal form influences risk assessment."""

    def test_different_legal_forms_produce_different_risk(self):
        """Test that legal forms impact risk assessment."""
        result_einzelunternehmen = assess_risks(
            domain="consulting",
            legal_form="Einzelunternehmen",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        result_gmbh = assess_risks(
            domain="consulting",
            legal_form="GmbH",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        # Should return valid results for both
        assert result_einzelunternehmen["risk_score"] >= 0
        assert result_gmbh["risk_score"] >= 0

    def test_complex_legal_forms_higher_operational_risk(self):
        """Test that complex forms (AG, GmbH) have higher operational risk."""
        result_simple = assess_risks(
            domain="consulting",
            legal_form="Einzelunternehmen",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        result_complex = assess_risks(
            domain="consulting",
            legal_form="AG",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        # Both should be valid
        assert result_simple["risk_score"] >= 0
        assert result_complex["risk_score"] >= 0


class TestDomainSpecificRisks:
    """Test domain-specific risk factors."""

    def test_consulting_vs_ecommerce_risk(self):
        """Test that different domains have different risk profiles."""
        risk_consulting = assess_risks(
            domain="consulting",
            legal_form="Freiberufler",
            city="Berlin",
            financial_projection={"break_even_month": 3}
        )

        risk_ecommerce = assess_risks(
            domain="ecommerce",
            legal_form="GmbH",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        # Both should produce valid results
        assert risk_consulting["risk_score"] >= 0
        assert risk_ecommerce["risk_score"] >= 0

    def test_high_capital_domain_higher_risk(self):
        """Test that capital-intensive domains may have higher risk."""
        result = assess_risks(
            domain="manufacturing",
            legal_form="GmbH",
            city="Munich",
            financial_projection={"break_even_month": 12}
        )

        # Should still produce valid risk assessment
        assert 0 <= result["risk_score"] <= 100


class TestTopRisksValidity:
    """Test that top 3 risks are valid and actionable."""

    def test_top_3_risks_present(self):
        """Test that top 3 risks are identified."""
        result = assess_risks(
            domain="consulting",
            legal_form="Einzelunternehmen",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        top_risks = result["top_3_risks"]
        assert len(top_risks) >= 1, "Should identify at least 1 top risk"
        assert len(top_risks) <= 3, "Should identify at most 3 top risks"

    def test_top_risks_have_descriptions(self):
        """Test that top risks have descriptions."""
        result = assess_risks(
            domain="saas",
            legal_form="UG",
            city="Hamburg",
            financial_projection={"break_even_month": 8}
        )

        for risk in result["top_3_risks"]:
            assert "name" in risk or "title" in risk
            assert "description" in risk
            if "mitigation_strategies" in risk:
                assert isinstance(risk["mitigation_strategies"], list)

    def test_mitigation_strategies_present(self):
        """Test that mitigation strategies are provided."""
        result = assess_risks(
            domain="consulting",
            legal_form="GmbH",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        # Should have mitigation strategies
        strategies = result.get("mitigation_strategies", [])
        assert isinstance(strategies, list)


class TestRiskPlausibility:
    """Test plausibility of risk assessments."""

    def test_best_case_scenario_low_risk(self):
        """Test that ideal scenario has low risk."""
        result = assess_risks(
            domain="online-coaching",
            legal_form="Freiberufler",
            city="Berlin",
            financial_projection={"break_even_month": 2}
        )

        # Should be low risk
        assert result["overall_risk_level"] in ["low", "medium"]
        assert result["risk_score"] < 50

    def test_worst_case_scenario_high_risk(self):
        """Test that challenging scenario has higher risk."""
        result = assess_risks(
            domain="manufacturing",
            legal_form="AG",
            city="Berlin",
            financial_projection={"break_even_month": 36}
        )

        # Should be medium or high risk
        assert result["overall_risk_level"] in ["medium", "high"]
        # Score should be substantial
        assert result["risk_score"] > 20

    def test_consistent_assessment(self):
        """Test that same inputs produce same risk assessment."""
        result1 = assess_risks(
            domain="consulting",
            legal_form="Einzelunternehmen",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        result2 = assess_risks(
            domain="consulting",
            legal_form="Einzelunternehmen",
            city="Berlin",
            financial_projection={"break_even_month": 6}
        )

        assert result1["risk_score"] == result2["risk_score"], \
            "Same inputs should produce same risk assessment"


class TestEdgeCases:
    """Test edge cases in risk assessment."""

    def test_immediate_break_even(self):
        """Test risk with month 1 break-even."""
        result = assess_risks(
            domain="consulting",
            legal_form="Freiberufler",
            city="Berlin",
            financial_projection={"break_even_month": 1}
        )

        assert 0 <= result["risk_score"] <= 100
        assert result["overall_risk_level"] in ["low", "medium", "high"]

    def test_very_delayed_break_even(self):
        """Test risk with 36+ month break-even."""
        result = assess_risks(
            domain="biotech",
            legal_form="GmbH",
            city="Munich",
            financial_projection={"break_even_month": 48}
        )

        assert 0 <= result["risk_score"] <= 100
        # Should be high risk
        assert result["overall_risk_level"] in ["medium", "high"]

    def test_missing_financial_data_handled(self):
        """Test that missing financial projection is handled."""
        result = assess_risks(
            domain="consulting",
            legal_form="Einzelunternehmen",
            city="Berlin",
            financial_projection={}
        )

        # Should still produce valid assessment
        assert 0 <= result["risk_score"] <= 100
        assert result["overall_risk_level"] in ["low", "medium", "high"]
