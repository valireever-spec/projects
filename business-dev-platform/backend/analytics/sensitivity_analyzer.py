"""
Sensitivity analysis for financial projections.

Varies revenue, fixed costs, and gross margin across a -30%..+30% range and
reports the impact on Year-1 net income and break-even month.

Design note: rather than re-calling build_projections (which recomputes fixed
costs from the profile and ignores direct overrides), this drives the projection
engine directly with the base inputs. That lets each lever move independently —
in particular the cost lever actually changes fixed costs, and the base net is
computed the same way as every variance point so deltas are self-consistent.
"""

from backend.analytics.financial_model import (
    _build_36_month_projections,
    _calculate_break_even,
)

CHANGE_PERCENTAGES = [-30, -20, -10, 0, 10, 20, 30]

# Gross margin shifts by this many points per 10% step (so ±30% => ±1.5pp).
_MARGIN_STEP_PER_10PCT = 0.05


def build_sensitivity_matrix(base_params: dict, base_result: dict) -> dict:
    """
    Build a sensitivity matrix by varying revenue, cost, and margin at 7 points.

    Args:
        base_params: profile inputs; supplies monthly_revenue_estimate and
            startup_capital.
        base_result: build_projections() output (or an equivalent dict);
            supplies monthly_fixed_costs and the gross margin (either directly as
            gross_margin_pct or via monthly_variable_cost_ratio).

    Returns:
        {
            "sensitivity_matrix": {
                "revenue_variance": [ {change_pct, year_1_net_delta, breakeven_delta_months}, ...7 ],
                "cost_variance":    [ ...7 ],
                "margin_variance":  [ ...7 ],
            },
            "key_driver": "revenue" | "costs" | "margin",
            "impact_ranking": [...3, largest impact first],
        }
    """
    base_revenue = base_params.get("monthly_revenue_estimate", 0) or 0
    base_startup = base_params.get("startup_capital", 0) or 0
    base_fixed = base_result.get("monthly_fixed_costs", 0) or 0
    base_gross = _base_gross_margin(base_result)
    base_var_ratio = 1 - base_gross

    base_net = _year1_net(base_revenue, base_fixed, base_var_ratio, base_startup)
    base_be = _break_even_month(base_revenue, base_fixed, base_var_ratio)

    revenue_variance = []
    cost_variance = []
    margin_variance = []

    for change_pct in CHANGE_PERCENTAGES:
        factor = 1 + change_pct / 100

        # Revenue lever.
        rev = base_revenue * factor
        revenue_variance.append(_point(
            change_pct,
            _year1_net(rev, base_fixed, base_var_ratio, base_startup) - base_net,
            _break_even_month(rev, base_fixed, base_var_ratio) - base_be,
        ))

        # Cost lever (fixed costs move directly).
        fixed = base_fixed * factor
        cost_variance.append(_point(
            change_pct,
            _year1_net(base_revenue, fixed, base_var_ratio, base_startup) - base_net,
            _break_even_month(base_revenue, fixed, base_var_ratio) - base_be,
        ))

        # Margin lever (gross margin shifts a few points, clamped).
        margin = base_gross + (change_pct / 100) * _MARGIN_STEP_PER_10PCT
        margin = max(0.1, min(0.95, margin))
        var_ratio = 1 - margin
        margin_variance.append(_point(
            change_pct,
            _year1_net(base_revenue, base_fixed, var_ratio, base_startup) - base_net,
            _break_even_month(base_revenue, base_fixed, var_ratio) - base_be,
        ))

    impacts = {
        "revenue": abs(revenue_variance[-1]["year_1_net_delta"]),
        "costs": abs(cost_variance[-1]["year_1_net_delta"]),
        "margin": abs(margin_variance[-1]["year_1_net_delta"]),
    }
    impact_ranking = sorted(impacts, key=impacts.get, reverse=True)

    return {
        "sensitivity_matrix": {
            "revenue_variance": revenue_variance,
            "cost_variance": cost_variance,
            "margin_variance": margin_variance,
        },
        "key_driver": impact_ranking[0],
        "impact_ranking": impact_ranking,
    }


def _base_gross_margin(base_result: dict) -> float:
    """Gross margin from either an explicit field or the variable-cost ratio."""
    if base_result.get("gross_margin_pct") is not None:
        return base_result["gross_margin_pct"]
    if base_result.get("monthly_variable_cost_ratio") is not None:
        return 1 - base_result["monthly_variable_cost_ratio"]
    return 0.60  # Reasonable default when neither is present.


def _year1_net(revenue: float, fixed: float, var_ratio: float, startup: float) -> float:
    """Year-1 net income for a given set of levers, via the projection engine."""
    proj = _build_36_month_projections(revenue, fixed, var_ratio, {}, {"total": startup})
    return sum(m["net_income"] for m in proj["year_1"])


def _break_even_month(revenue: float, fixed: float, var_ratio: float) -> int:
    """Operational break-even month for a given set of levers."""
    return _calculate_break_even(fixed, var_ratio, revenue)["break_even_month"]


def _point(change_pct: int, net_delta: float, breakeven_delta: float) -> dict:
    return {
        "change_pct": change_pct,
        "year_1_net_delta": round(net_delta, 0),
        "breakeven_delta_months": round(breakeven_delta, 1),
    }
