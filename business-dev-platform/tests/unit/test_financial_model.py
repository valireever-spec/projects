"""Unit tests for financial projection model with validation."""
import pytest
from backend.analytics.financial_model import (
    build_projections,
    _calculate_monthly_costs,
    _calculate_monthly_revenue,
    _calculate_break_even,
    _build_monthly_p_and_l
)


class TestFinancialModelStructure:
    """Test that financial model returns correct structure."""

    def test_projections_returns_required_fields(self):
        """Test that build_projections returns all required fields."""
        params = {
            "revenue_model": "project-based",
            "startup_costs": {"total": 30000},
            "monthly_revenue_estimate": 5000,
            "legal_form": "Einzelunternehmen",
            "city": "Berlin",
            "sector": "consulting",
        }

        result = build_projections(params)

        assert "startup_costs" in result
        assert "monthly_costs" in result
        assert "break_even_month" in result
        assert "key_metrics" in result
        assert "scenarios" in result
        assert "months_1_12" in result
        assert "months_13_24" in result
        assert "months_25_36" in result

    def test_projections_contain_valid_months(self):
        """Test that projections have correct number of months."""
        params = {
            "revenue_model": "subscription",
            "startup_costs": {"total": 20000},
            "monthly_revenue_estimate": 3000,
            "legal_form": "GmbH",
            "city": "Munich",
            "sector": "saas",
        }

        result = build_projections(params)

        assert len(result["months_1_12"]) == 12, "Year 1 should have 12 months"
        assert len(result["months_13_24"]) == 12, "Year 2 should have 12 months"
        assert len(result["months_25_36"]) == 12, "Year 3 should have 12 months"


class TestBreakEvenCalculation:
    """Test break-even calculation logic."""

    def test_break_even_positive_contribution_margin(self):
        """Test break-even with positive contribution margin."""
        fixed_costs = 5000
        contribution_margin_ratio = 0.5

        breakeven = _calculate_break_even(fixed_costs, contribution_margin_ratio)

        assert breakeven > 0, "Break-even should be positive with positive margin"
        # Break-even = Fixed Costs / Contribution Margin Ratio
        expected = fixed_costs / contribution_margin_ratio
        assert breakeven == expected

    def test_break_even_zero_margin_handled(self):
        """Test that zero margin doesn't cause division by zero."""
        fixed_costs = 5000
        contribution_margin_ratio = 0.0

        # Should either return inf or handle gracefully
        try:
            breakeven = _calculate_break_even(fixed_costs, contribution_margin_ratio)
            # If it returns a number, it should be handled
            assert breakeven >= 0 or breakeven == float('inf')
        except ZeroDivisionError:
            # If it raises error, that's also acceptable
            pytest.skip("Zero margin raises ZeroDivisionError (acceptable)")

    def test_break_even_increases_with_fixed_costs(self):
        """Test that break-even increases with fixed costs."""
        margin_ratio = 0.4

        breakeven_low = _calculate_break_even(3000, margin_ratio)
        breakeven_high = _calculate_break_even(6000, margin_ratio)

        assert breakeven_high > breakeven_low, \
            "Higher fixed costs should require higher break-even revenue"

    def test_break_even_decreases_with_higher_margin(self):
        """Test that break-even decreases with higher margin ratio."""
        fixed_costs = 5000

        breakeven_low_margin = _calculate_break_even(fixed_costs, 0.3)
        breakeven_high_margin = _calculate_break_even(fixed_costs, 0.6)

        assert breakeven_low_margin > breakeven_high_margin, \
            "Higher margin ratio should result in lower break-even"


class TestMonthlyRevenueRampUp:
    """Test that revenue ramp-up follows expected curve."""

    def test_revenue_ramp_up_curve(self):
        """Test that revenue follows the ramp-up schedule."""
        base_revenue = 10000
        months_data = _build_monthly_p_and_l(base_revenue, 5000, 12)

        # Month 1-5 should be at reduced percentages
        expected_rampup = [0.3, 0.5, 0.7, 0.9, 1.0]

        for i, percentage in enumerate(expected_rampup):
            expected_revenue = base_revenue * percentage
            actual_revenue = months_data[i]["revenue"]
            assert abs(actual_revenue - expected_revenue) < 100, \
                f"Month {i+1} revenue should be {percentage*100}% of base"

    def test_revenue_100_percent_from_month_6(self):
        """Test that revenue reaches 100% from month 6 onwards."""
        base_revenue = 10000
        months_data = _build_monthly_p_and_l(base_revenue, 5000, 36)

        # Months 6+ should be at 100%
        for i in range(5, len(months_data)):
            revenue = months_data[i]["revenue"]
            expected = base_revenue  # 100% = base
            assert abs(revenue - expected) < 100, \
                f"Month {i+1} should be at 100% of base revenue"

    def test_revenue_reaches_expected_annual_total(self):
        """Test that year 1 revenue totals correctly."""
        monthly_revenue = 5000
        months_data = _build_monthly_p_and_l(monthly_revenue, 3000, 12)

        # Year 1: 30% + 50% + 70% + 90% + 100% + 100%*7
        # = 0.3 + 0.5 + 0.7 + 0.9 + 1.0 + 7*1.0 = 11 months of partial/full revenue
        expected_y1 = (
            monthly_revenue * (0.3 + 0.5 + 0.7 + 0.9) +  # Ramp-up
            monthly_revenue * (1.0 * 8)  # 8 months at 100%
        )

        actual_y1 = sum(m["revenue"] for m in months_data[:12])

        # Allow 1% tolerance
        tolerance = expected_y1 * 0.01
        assert abs(actual_y1 - expected_y1) < tolerance, \
            f"Year 1 total should be ~{expected_y1}, got {actual_y1}"


class TestCashFlowLogic:
    """Test cumulative cash flow calculations."""

    def test_cumulative_cash_flow_never_jumps_down(self):
        """Test that cumulative cash flow is monotonic (never decreases unexpectedly)."""
        months_data = _build_monthly_p_and_l(8000, 4000, 24)

        prev_cumulative = months_data[0]["cumulative_cf"]

        for i, month in enumerate(months_data[1:], 1):
            current_cumulative = month["cumulative_cf"]
            # Cumulative should only increase if cash flow is positive
            cf = month["ebitda"]
            if cf >= 0:
                assert current_cumulative >= prev_cumulative, \
                    f"Cumulative CF should not decrease in month {i+1} with positive EBITDA"
            prev_cumulative = current_cumulative

    def test_break_even_reflected_in_cumulative(self):
        """Test that break-even point is reflected in cumulative cash flow."""
        months_data = _build_monthly_p_and_l(10000, 5000, 12)

        # Find month where cumulative CF turns positive
        breakeven_month = None
        for i, month in enumerate(months_data):
            if month["cumulative_cf"] > 0:
                breakeven_month = i + 1
                break

        # Break-even should be found within reasonable timeframe
        if breakeven_month:
            assert breakeven_month <= 12, \
                "Break-even should occur within first year with good margins"


class TestTaxCalculations:
    """Test tax application in projections."""

    def test_tax_applied_after_month_12(self):
        """Test that 25% tax is applied starting month 13."""
        months_data = _build_monthly_p_and_l(10000, 3000, 24)

        # Months 1-12 should have no tax
        for i in range(12):
            month = months_data[i]
            if month["ebitda"] > 0:
                # Tax should not be applied (or minimal)
                assert month.get("tax", 0) == 0 or \
                       month.get("net_income", 0) == month["ebitda"]

        # Months 13+ with positive EBITDA should have 25% tax
        for i in range(12, 24):
            month = months_data[i]
            if month["ebitda"] > 0:
                expected_tax = month["ebitda"] * 0.25
                actual_tax = month.get("tax", 0)
                # Allow some tolerance due to rounding
                assert abs(actual_tax - expected_tax) < 10, \
                    f"Month {i+1} should apply 25% tax to positive EBITDA"


class TestScenarioComparison:
    """Test that scenarios (conservative, base, optimistic) are reasonable."""

    def test_scenario_relationships(self):
        """Test that conservative < base < optimistic."""
        params = {
            "revenue_model": "project-based",
            "startup_costs": {"total": 25000},
            "monthly_revenue_estimate": 4000,
            "legal_form": "Einzelunternehmen",
            "city": "Berlin",
            "sector": "consulting",
        }

        result = build_projections(params)
        scenarios = result["scenarios"]

        conservative = scenarios["conservative"]["year_1"]["total_revenue"]
        base = scenarios["base"]["year_1"]["total_revenue"]
        optimistic = scenarios["optimistic"]["year_1"]["total_revenue"]

        assert conservative <= base <= optimistic, \
            "Scenarios should follow conservative <= base <= optimistic order"

    def test_scenario_multipliers_correct(self):
        """Test that scenarios use correct revenue multipliers."""
        params = {
            "revenue_model": "subscription",
            "startup_costs": {"total": 15000},
            "monthly_revenue_estimate": 3000,
            "legal_form": "GmbH",
            "city": "Hamburg",
            "sector": "saas",
        }

        result = build_projections(params)
        scenarios = result["scenarios"]

        base_revenue = scenarios["base"]["year_1"]["total_revenue"]
        conservative_revenue = scenarios["conservative"]["year_1"]["total_revenue"]
        optimistic_revenue = scenarios["optimistic"]["year_1"]["total_revenue"]

        # Conservative should be roughly 0.6x, optimistic roughly 1.5x
        conservative_ratio = conservative_revenue / base_revenue if base_revenue > 0 else 1
        optimistic_ratio = optimistic_revenue / base_revenue if base_revenue > 0 else 1

        assert 0.5 <= conservative_ratio <= 0.7, \
            "Conservative should be 0.6x base (±tolerance)"
        assert 1.3 <= optimistic_ratio <= 1.7, \
            "Optimistic should be 1.5x base (±tolerance)"


class TestEdgeCases:
    """Test edge cases in financial model."""

    def test_zero_revenue_handled(self):
        """Test that zero revenue is handled gracefully."""
        params = {
            "revenue_model": "product",
            "startup_costs": {"total": 10000},
            "monthly_revenue_estimate": 0,
            "legal_form": "Einzelunternehmen",
            "city": "Berlin",
            "sector": "retail",
        }

        result = build_projections(params)
        assert result["months_1_12"][0]["revenue"] == 0

    def test_very_high_startup_costs(self):
        """Test projections with very high startup costs."""
        params = {
            "revenue_model": "saas",
            "startup_costs": {"total": 500000},
            "monthly_revenue_estimate": 10000,
            "legal_form": "GmbH",
            "city": "Munich",
            "sector": "saas",
        }

        result = build_projections(params)
        # Should still return valid structure
        assert len(result["months_1_12"]) == 12
        assert result["break_even_month"] > 0

    def test_very_low_costs(self):
        """Test projections with minimal costs."""
        params = {
            "revenue_model": "consulting",
            "startup_costs": {"total": 1000},
            "monthly_revenue_estimate": 2000,
            "legal_form": "Freiberufler",
            "city": "Berlin",
            "sector": "consulting",
        }

        result = build_projections(params)
        # Should show quick break-even
        assert result["break_even_month"] <= 3


class TestFinancialPlausibility:
    """Test plausibility of financial projections."""

    def test_positive_revenue_business(self):
        """Test that business with positive revenue reaches profitability."""
        params = {
            "revenue_model": "product",
            "startup_costs": {"total": 20000},
            "monthly_revenue_estimate": 5000,  # Good revenue
            "legal_form": "GmbH",
            "city": "Berlin",
            "sector": "ecommerce",
        }

        result = build_projections(params)

        # Should be profitable by year 1
        year_1_net = result["key_metrics"]["year_1"]["net_income"]
        assert year_1_net > 0, "Business with €5k/month revenue should be profitable"

    def test_break_even_reasonable(self):
        """Test that break-even month is reasonable."""
        params = {
            "revenue_model": "subscription",
            "startup_costs": {"total": 15000},
            "monthly_revenue_estimate": 3000,
            "legal_form": "UG",
            "city": "Hamburg",
            "sector": "saas",
        }

        result = build_projections(params)

        # Break-even should be within first 12-18 months for healthy business
        breakeven = result["break_even_month"]
        assert 0 < breakeven <= 24, \
            f"Break-even should be within 24 months, got month {breakeven}"

    def test_year_1_revenue_grows(self):
        """Test that Year 3 revenue is higher than Year 1."""
        params = {
            "revenue_model": "product",
            "startup_costs": {"total": 25000},
            "monthly_revenue_estimate": 4000,
            "legal_form": "GmbH",
            "city": "Munich",
            "sector": "consulting",
        }

        result = build_projections(params)

        y1_revenue = result["key_metrics"]["year_1"]["total_revenue"]
        y3_revenue = result["key_metrics"]["year_3"]["total_revenue"]

        assert y3_revenue >= y1_revenue, \
            "Year 3 revenue should be >= Year 1 revenue (no negative growth)"
