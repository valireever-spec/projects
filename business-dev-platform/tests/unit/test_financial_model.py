"""Unit tests for the financial projection model with validation.

Validates the *shipping* API: build_projections(**kwargs) plus the internal
helpers _calculate_break_even and _build_36_month_projections.
"""
import pytest
from backend.analytics.financial_model import (
    build_projections,
    _calculate_break_even,
    _build_36_month_projections,
)


def _project(monthly_revenue, fixed=5000, var_ratio=0.3, startup=0, months=36):
    """Run the raw 36-month engine and return a flat month list."""
    proj = _build_36_month_projections(
        monthly_revenue, fixed, var_ratio, {}, {"total": startup}
    )
    flat = proj["year_1"] + proj["year_2"] + proj["year_3"]
    return flat[:months]


def _build(monthly_revenue, **overrides):
    params = dict(
        domain_slug="test-domain",
        revenue_model="subscription",
        monthly_revenue_estimate=monthly_revenue,
        city="Berlin",
        legal_form="GmbH",
    )
    params.update(overrides)
    return build_projections(**params)


class TestStructure:
    def test_returns_required_fields(self):
        result = _build(8000)
        for key in (
            "startup_costs", "monthly_fixed_costs", "break_even_month",
            "key_metrics", "scenarios", "months_1_12", "months_13_24", "months_25_36",
        ):
            assert key in result

    def test_three_years_of_twelve_months(self):
        result = _build(3000)
        assert len(result["months_1_12"]) == 12
        assert len(result["months_13_24"]) == 12
        assert len(result["months_25_36"]) == 12


class TestBreakEven:
    def test_revenue_needed_is_fixed_over_contribution_margin(self):
        data = _calculate_break_even(5000, 0.5, 20000)
        assert data["monthly_revenue_needed"] == pytest.approx(5000 / (1 - 0.5))

    def test_zero_contribution_margin_handled(self):
        data = _calculate_break_even(5000, 1.0, 20000)  # cm_ratio == 0
        assert data["achievable"] is False  # does not crash / divide by zero

    def test_revenue_needed_increases_with_fixed_costs(self):
        low = _calculate_break_even(3000, 0.4, 20000)["monthly_revenue_needed"]
        high = _calculate_break_even(6000, 0.4, 20000)["monthly_revenue_needed"]
        assert high > low

    def test_revenue_needed_decreases_with_higher_margin(self):
        thin = _calculate_break_even(5000, 0.7, 20000)["monthly_revenue_needed"]  # margin 0.3
        fat = _calculate_break_even(5000, 0.4, 20000)["monthly_revenue_needed"]   # margin 0.6
        assert thin > fat


class TestRevenueRampUp:
    def test_ramp_curve_first_five_months(self):
        months = _project(10000)
        for i, pct in enumerate([0.30, 0.50, 0.70, 0.90, 1.0]):
            assert months[i]["revenue"] == pytest.approx(10000 * pct, abs=1)

    def test_full_revenue_from_month_six(self):
        months = _project(10000)
        for m in months[5:]:
            assert m["revenue"] == pytest.approx(10000, abs=1)

    def test_year1_total_matches_ramp(self):
        rev = 5000
        months = _project(rev, months=12)
        expected = rev * (0.30 + 0.50 + 0.70 + 0.90 + 1.0 + 1.0 * 7)
        assert sum(m["revenue"] for m in months) == pytest.approx(expected, rel=0.01)


class TestCashFlowAndTax:
    def test_cumulative_cf_monotonic_when_profitable(self):
        months = _project(10000, fixed=3000, var_ratio=0.3)
        prev = months[0]["cumulative_cf"]
        for m in months[1:]:
            if m["net_income"] >= 0:
                assert m["cumulative_cf"] >= prev
            prev = m["cumulative_cf"]

    def test_no_tax_in_year_one(self):
        months = _project(10000, fixed=3000, var_ratio=0.3)
        assert all(m["tax"] == 0 for m in months[:12])

    def test_25pct_tax_from_month_13(self):
        months = _project(10000, fixed=3000, var_ratio=0.3)
        for m in months[12:24]:
            if m["ebitda"] > 0:
                assert m["tax"] == pytest.approx(m["ebitda"] * 0.25, abs=1)


class TestScenarios:
    def test_ordering_conservative_base_optimistic(self):
        scen = _build(6000)["scenarios"]
        assert (
            scen["conservative"]["year_1_revenue"]
            <= scen["base"]["year_1_revenue"]
            <= scen["optimistic"]["year_1_revenue"]
        )

    def test_multipliers(self):
        scen = _build(4000)["scenarios"]
        assert scen["conservative"]["multiplier"] == 0.6
        assert scen["optimistic"]["multiplier"] == 1.5


class TestEdgeCases:
    def test_zero_revenue(self):
        result = _build(0)
        assert result["months_1_12"][0]["revenue"] == 0

    def test_very_high_startup_costs_structure_valid(self):
        result = _build(10000, startup_capital=500_000)
        assert len(result["months_1_12"]) == 12
        assert result["break_even_month"] > 0

    def test_high_revenue_breaks_even_fast(self):
        # 30k/month against ~8k fixed at 75% margin clears the bar by the ramp's
        # 50%-revenue month.
        result = _build(30000)
        assert result["break_even_month"] <= 3


class TestPlausibility:
    def test_strong_revenue_business_is_profitable(self):
        result = _build(20000)
        assert result["key_metrics"]["year_1"]["net_income"] > 0

    def test_break_even_within_bounds(self):
        result = _build(12000)
        assert 0 < result["break_even_month"] <= 36

    def test_year3_revenue_at_least_year1(self):
        result = _build(4000)
        y1 = result["key_metrics"]["year_1"]["total_revenue"]
        y3 = result["key_metrics"]["year_3"]["total_revenue"]
        assert y3 >= y1
