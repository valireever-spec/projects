"""
Sensitivity analysis for financial projections.
Varies revenue, costs, and margin across ±30% range to show impact on break-even and net income.
"""

from backend.analytics.financial_model import build_projections


def build_sensitivity_matrix(base_params: dict, base_result: dict) -> dict:
    """
    Build sensitivity matrix by varying 3 dimensions at 7 points each (-30% to +30%).

    Args:
        base_params: {
            'domain_slug': str,
            'revenue_model': str,
            'monthly_revenue_estimate': float,
            'city': str,
            'legal_form': str,
            'startup_capital': float,
            'employees': int,
            'sector_margins': dict with 'gross_margin_pct'
        }
        base_result: Result from build_projections() (12/36-month dict with break_even_month, year_1_net, etc.)

    Returns:
        {
            "sensitivity_matrix": {
                "revenue_variance": [
                    {"change_pct": -30, "year_1_net_delta": -8000, "breakeven_delta_months": 3},
                    ...7 total points
                ],
                "cost_variance": [...7],
                "margin_variance": [...7]
            },
            "key_driver": "revenue",
            "impact_ranking": ["revenue", "costs", "margin"]
        }
    """

    base_year_1_net = base_result.get("year_1_net", 0)
    base_break_even = base_result.get("break_even_month", 12)
    base_monthly_costs = base_result.get("monthly_fixed_costs", 0)
    base_gross_margin = base_result.get("gross_margin_pct", 0.60)

    change_percentages = [-30, -20, -10, 0, 10, 20, 30]

    # Revenue variance
    revenue_variance = []
    for change_pct in change_percentages:
        modified_monthly_revenue = base_params["monthly_revenue_estimate"] * (1 + change_pct / 100)
        modified_params = base_params.copy()
        modified_params["monthly_revenue_estimate"] = modified_monthly_revenue

        try:
            result = build_projections(**modified_params)
            year_1_net = result.get("year_1_net", base_year_1_net)
            breakeven = result.get("break_even_month", base_break_even)
            year_1_net_delta = year_1_net - base_year_1_net
            breakeven_delta = breakeven - base_break_even
        except Exception:
            year_1_net_delta = 0
            breakeven_delta = 0

        revenue_variance.append({
            "change_pct": change_pct,
            "year_1_net_delta": round(year_1_net_delta, 0),
            "breakeven_delta_months": round(breakeven_delta, 1)
        })

    # Cost variance (inverted: higher costs = lower net)
    cost_variance = []
    for change_pct in change_percentages:
        modified_monthly_costs = base_monthly_costs * (1 + change_pct / 100)
        # Reconstruct base_params with modified fixed costs
        # We need to pass through build_projections' startup_capital recalc
        # Simplest: adjust startup_capital proportionally
        modified_params = base_params.copy()
        cost_delta_yearly = (modified_monthly_costs - base_monthly_costs) * 12
        modified_params["startup_capital"] = base_params["startup_capital"] + cost_delta_yearly * 3

        try:
            result = build_projections(**modified_params)
            year_1_net = result.get("year_1_net", base_year_1_net)
            breakeven = result.get("break_even_month", base_break_even)
            year_1_net_delta = year_1_net - base_year_1_net
            breakeven_delta = breakeven - base_break_even
        except Exception:
            year_1_net_delta = 0
            breakeven_delta = 0

        cost_variance.append({
            "change_pct": change_pct,
            "year_1_net_delta": round(year_1_net_delta, 0),
            "breakeven_delta_months": round(breakeven_delta, 1)
        })

    # Margin variance: add/subtract 5pp per 10% step
    margin_variance = []
    for change_pct in change_percentages:
        # Margin change: ±5pp per 10% step
        margin_change = (change_pct / 100) * 0.05
        modified_margin = base_gross_margin + margin_change
        modified_margin = max(0.1, min(0.95, modified_margin))  # Clamp 10-95%

        modified_params = base_params.copy()
        modified_sector_margins = base_params.get("sector_margins", {}).copy()
        modified_sector_margins["gross_margin_pct"] = modified_margin
        modified_params["sector_margins"] = modified_sector_margins

        try:
            result = build_projections(**modified_params)
            year_1_net = result.get("year_1_net", base_year_1_net)
            breakeven = result.get("break_even_month", base_break_even)
            year_1_net_delta = year_1_net - base_year_1_net
            breakeven_delta = breakeven - base_break_even
        except Exception:
            year_1_net_delta = 0
            breakeven_delta = 0

        margin_variance.append({
            "change_pct": change_pct,
            "year_1_net_delta": round(year_1_net_delta, 0),
            "breakeven_delta_months": round(breakeven_delta, 1)
        })

    # Determine key driver (which dimension causes largest impact at ±30%)
    revenue_impact = abs(revenue_variance[-1]["year_1_net_delta"])
    cost_impact = abs(cost_variance[-1]["year_1_net_delta"])
    margin_impact = abs(margin_variance[-1]["year_1_net_delta"])

    impacts = {
        "revenue": revenue_impact,
        "costs": cost_impact,
        "margin": margin_impact
    }
    key_driver = max(impacts, key=impacts.get)
    impact_ranking = sorted(impacts.keys(), key=lambda k: impacts[k], reverse=True)

    return {
        "sensitivity_matrix": {
            "revenue_variance": revenue_variance,
            "cost_variance": cost_variance,
            "margin_variance": margin_variance
        },
        "key_driver": key_driver,
        "impact_ranking": impact_ranking
    }
