from datetime import datetime, timedelta
import math


def build_projections(
    domain_slug: str,
    revenue_model: str,
    monthly_revenue_estimate: float,
    city: str,
    legal_form: str,
    startup_capital: float = 50_000,
    employees: int = 1,
    sector_margins: dict | None = None,
    city_wage_index: float = 1.0,
) -> dict:
    """
    Build comprehensive 36-month financial projections.

    Args:
        domain_slug: Business domain
        revenue_model: One of (subscription, hourly, product_sale, commission, hybrid)
        monthly_revenue_estimate: Estimated monthly revenue (EUR)
        city: German city name
        legal_form: Legal structure (Einzelunternehmen, GmbH, etc.)
        startup_capital: Initial capital (EUR)
        employees: Number of founders/employees
        sector_margins: Dict with gross_margin_pct, ebitda_margin_pct
        city_wage_index: Cost of living multiplier

    Returns:
        Dict with complete 36-month financial projections
    """
    # Defaults
    if sector_margins is None:
        sector_margins = {"gross_margin_pct": 0.70, "ebitda_margin_pct": 0.35}

    # Initialize assumptions
    assumptions = _build_assumptions(
        revenue_model,
        monthly_revenue_estimate,
        city,
        legal_form,
        employees,
        sector_margins,
        city_wage_index,
    )

    # Calculate startup costs
    startup_costs = _calculate_startup_costs(
        revenue_model,
        city_wage_index,
        startup_capital,
    )

    # Calculate monthly costs
    monthly_fixed_costs = assumptions["monthly_fixed_costs"]
    monthly_variable_cost_ratio = assumptions["variable_cost_ratio"]

    # Calculate break-even
    break_even_data = _calculate_break_even(
        monthly_fixed_costs,
        monthly_variable_cost_ratio,
        monthly_revenue_estimate,
    )

    # Build 36-month projections
    projections = _build_36_month_projections(
        monthly_revenue_estimate,
        monthly_fixed_costs,
        monthly_variable_cost_ratio,
        assumptions,
        startup_costs,
    )

    # Build scenarios (conservative, base, optimistic)
    scenarios = _build_scenarios(
        monthly_revenue_estimate,
        monthly_fixed_costs,
        monthly_variable_cost_ratio,
        assumptions,
        startup_costs,
    )

    # Calculate key metrics
    key_metrics = _calculate_key_metrics(
        projections,
        startup_costs,
        assumptions,
        break_even_data,
    )

    return {
        "domain_slug": domain_slug,
        "revenue_model": revenue_model,
        "city": city,
        "legal_form": legal_form,
        "startup_capital_provided": startup_capital,

        # Costs breakdown
        "startup_costs": startup_costs,
        "monthly_fixed_costs": round(monthly_fixed_costs, 2),
        "monthly_variable_cost_ratio": round(monthly_variable_cost_ratio, 3),
        "monthly_revenue_estimate": round(monthly_revenue_estimate, 2),

        # Break-even
        "break_even_monthly_revenue": round(break_even_data["monthly_revenue_needed"], 2),
        "break_even_month": break_even_data["break_even_month"],
        "break_even_achievable": break_even_data["achievable"],

        # 36-month projections
        "months_1_12": projections["year_1"],
        "months_13_24": projections["year_2"],
        "months_25_36": projections["year_3"],

        # Scenarios
        "scenarios": scenarios,

        # Key metrics
        "key_metrics": key_metrics,
    }


def _build_assumptions(
    revenue_model: str,
    monthly_revenue: float,
    city: str,
    legal_form: str,
    employees: int,
    sector_margins: dict,
    city_wage_index: float,
) -> dict:
    """Build financial assumptions based on business profile."""
    # Gross margin by revenue model
    gross_margins = {
        "subscription": 0.75,
        "hourly": 0.85,
        "product_sale": 0.55,
        "commission": 0.80,
        "hybrid": 0.70,
    }

    gross_margin = gross_margins.get(revenue_model, 0.70)
    gross_margin = sector_margins.get("gross_margin_pct", gross_margin)

    # Monthly staff cost (per employee)
    # German average: €3,500-4,500 gross per month
    base_salary = 4_000
    salary_with_overhead = base_salary * 1.42  # Add social security, taxes: 42%
    total_staff_cost = salary_with_overhead * employees * city_wage_index

    # Monthly fixed costs (office, software, insurance, etc.)
    # Estimate: 30-40% of monthly revenue or base amount
    office_rent = 800 * city_wage_index  # EUR/month
    utilities = 150
    software = 200
    insurance = 300
    admin = 200
    marketing_base = 500

    fixed_costs = (
        office_rent + utilities + software + insurance + admin + marketing_base +
        total_staff_cost
    )

    # Variable cost ratio
    variable_ratio = 1 - gross_margin

    return {
        "gross_margin": gross_margin,
        "variable_cost_ratio": variable_ratio,
        "monthly_fixed_costs": fixed_costs,
        "staff_cost_per_employee": salary_with_overhead * city_wage_index,
        "total_employees": employees,
    }


def _calculate_startup_costs(
    revenue_model: str,
    city_wage_index: float,
    provided_capital: float,
) -> dict:
    """Calculate one-time startup costs."""
    # Base startup costs by model
    startup_cost_templates = {
        "subscription": {
            "legal": 500,
            "software": 3_000,
            "office": 2_000,
            "marketing": 2_000,
            "working_capital": 5_000,
        },
        "hourly": {
            "legal": 300,
            "equipment": 2_000,
            "office": 1_500,
            "marketing": 1_500,
            "working_capital": 3_000,
        },
        "product_sale": {
            "legal": 500,
            "inventory": 10_000,
            "equipment": 2_000,
            "office": 2_000,
            "working_capital": 8_000,
        },
        "commission": {
            "legal": 400,
            "software": 2_000,
            "office": 1_000,
            "marketing": 2_000,
            "working_capital": 3_000,
        },
        "hybrid": {
            "legal": 500,
            "equipment": 3_000,
            "software": 2_000,
            "office": 2_000,
            "working_capital": 5_000,
        },
    }

    costs = startup_cost_templates.get(revenue_model, startup_cost_templates["hybrid"])

    # Adjust for city wage index
    costs["office"] = int(costs["office"] * city_wage_index)

    total = sum(costs.values())

    return {
        "legal_registration": costs.get("legal", 0),
        "equipment": costs.get("equipment", 0),
        "software": costs.get("software", 0),
        "office_setup": costs.get("office", 0),
        "inventory": costs.get("inventory", 0),
        "marketing": costs.get("marketing", 0),
        "working_capital": costs.get("working_capital", 0),
        "total": total,
        "covered_by_capital": min(total, provided_capital),
        "funding_gap": max(0, total - provided_capital),
    }


def _calculate_break_even(
    monthly_fixed_costs: float,
    variable_cost_ratio: float,
    monthly_revenue_estimate: float,
) -> dict:
    """Calculate break-even point."""
    # BEP = Fixed Costs / Contribution Margin Ratio
    # Contribution Margin Ratio = (Revenue - Variable Costs) / Revenue = 1 - variable_ratio

    cm_ratio = 1 - variable_cost_ratio

    if cm_ratio <= 0:
        return {
            "monthly_revenue_needed": monthly_fixed_costs * 10,  # Fallback
            "break_even_month": 99,
            "achievable": False,
        }

    monthly_revenue_needed = monthly_fixed_costs / cm_ratio

    # How many months to reach BEP?
    if monthly_revenue_estimate > 0:
        # Assume linear ramp-up: month 1 = 30%, month 2 = 50%, month 3+ = 100%
        if monthly_revenue_estimate * 0.30 >= monthly_revenue_needed:
            break_even_month = 1
        elif monthly_revenue_estimate * 0.50 >= monthly_revenue_needed:
            break_even_month = 2
        else:
            months_needed = monthly_revenue_needed / monthly_revenue_estimate
            break_even_month = math.ceil(months_needed)
    else:
        break_even_month = 99

    achievable = break_even_month <= 36  # Achievable within 3 years

    return {
        "monthly_revenue_needed": monthly_revenue_needed,
        "break_even_month": min(break_even_month, 36),
        "achievable": achievable,
    }


def _build_36_month_projections(
    monthly_revenue: float,
    monthly_fixed_costs: float,
    variable_cost_ratio: float,
    assumptions: dict,
    startup_costs: dict,
) -> dict:
    """Build month-by-month projections for 36 months."""
    projections = {"year_1": [], "year_2": [], "year_3": []}

    cumulative_cf = -startup_costs["total"]  # Start with negative (upfront investment)

    # Revenue ramp-up curve: 30%, 50%, 70%, 90%, 100% over first 5 months
    ramp_curve = [0.30, 0.50, 0.70, 0.90, 1.0] + [1.0] * 31

    for month in range(1, 37):
        ramp_factor = ramp_curve[month - 1]
        revenue = monthly_revenue * ramp_factor

        # Variable costs scale with revenue
        variable_costs = revenue * variable_cost_ratio

        # Total costs
        total_costs = monthly_fixed_costs + variable_costs

        # EBITDA
        ebitda = revenue - total_costs

        # Simple tax (ignore for first 12 months, then apply 25% corporate tax)
        tax = max(0, ebitda * 0.25) if month > 12 else 0

        # Net income
        net_income = ebitda - tax

        # Cumulative cash flow
        cumulative_cf += net_income

        projection = {
            "month": month,
            "revenue": round(revenue, 2),
            "variable_costs": round(variable_costs, 2),
            "fixed_costs": round(monthly_fixed_costs, 2),
            "total_costs": round(total_costs, 2),
            "ebitda": round(ebitda, 2),
            "tax": round(tax, 2),
            "net_income": round(net_income, 2),
            "cumulative_cf": round(cumulative_cf, 2),
        }

        if month <= 12:
            projections["year_1"].append(projection)
        elif month <= 24:
            projections["year_2"].append(projection)
        else:
            projections["year_3"].append(projection)

    return projections


def _build_scenarios(
    monthly_revenue: float,
    monthly_fixed_costs: float,
    variable_cost_ratio: float,
    assumptions: dict,
    startup_costs: dict,
) -> dict:
    """Build 3 scenarios: conservative (0.6x), base (1.0x), optimistic (1.5x)."""
    scenarios = {}

    for scenario_name, multiplier in [
        ("conservative", 0.6),
        ("base", 1.0),
        ("optimistic", 1.5),
    ]:
        scenario_revenue = monthly_revenue * multiplier

        # Run 36-month projection for this scenario
        proj = _build_36_month_projections(
            scenario_revenue,
            monthly_fixed_costs,
            variable_cost_ratio,
            assumptions,
            startup_costs,
        )

        # Extract key metrics
        year_1 = proj["year_1"]
        year_3 = proj["year_3"]

        total_year_1_revenue = sum(m["revenue"] for m in year_1)
        total_year_1_costs = sum(m["total_costs"] for m in year_1)
        year_1_net = sum(m["net_income"] for m in year_1)

        year_3_final = year_3[-1] if year_3 else year_1[-1]

        scenarios[scenario_name] = {
            "multiplier": multiplier,
            "monthly_revenue": round(scenario_revenue, 2),
            "year_1_revenue": round(total_year_1_revenue, 2),
            "year_1_net_income": round(year_1_net, 2),
            "year_3_monthly_revenue": round(year_3_final["revenue"], 2),
            "year_3_monthly_ebitda": round(year_3_final["ebitda"], 2),
            "break_even_month": _find_break_even_month(proj),
            "year_3_cumulative_cf": round(year_3_final["cumulative_cf"], 2),
        }

    return scenarios


def _find_break_even_month(projections: dict) -> int:
    """Find first month with positive cumulative cash flow."""
    for year_data in [projections["year_1"], projections["year_2"], projections["year_3"]]:
        for month_data in year_data:
            if month_data["cumulative_cf"] >= 0:
                return month_data["month"]
    return 37  # Doesn't break even within 3 years


def _calculate_key_metrics(
    projections: dict,
    startup_costs: dict,
    assumptions: dict,
    break_even_data: dict,
) -> dict:
    """Calculate business KPIs."""
    year_1 = projections["year_1"]
    year_3 = projections["year_3"]

    # Year 1 metrics
    year_1_revenue = sum(m["revenue"] for m in year_1)
    year_1_ebitda = sum(m["ebitda"] for m in year_1)
    year_1_net = sum(m["net_income"] for m in year_1)
    year_1_margin = (year_1_ebitda / year_1_revenue * 100) if year_1_revenue > 0 else 0

    # Year 3 metrics
    year_3_revenue = sum(m["revenue"] for m in year_3)
    year_3_ebitda = sum(m["ebitda"] for m in year_3)
    year_3_margin = (year_3_ebitda / year_3_revenue * 100) if year_3_revenue > 0 else 0

    # Final month profitability
    final_month = year_3[-1] if year_3 else year_1[-1]

    # Payback period (months to recover initial investment)
    final_cf = final_month["cumulative_cf"]
    if final_cf > 0:
        payback_months = break_even_data["break_even_month"]
    else:
        payback_months = 37

    return {
        "year_1": {
            "total_revenue": round(year_1_revenue, 2),
            "ebitda": round(year_1_ebitda, 2),
            "net_income": round(year_1_net, 2),
            "ebitda_margin_pct": round(year_1_margin, 1),
        },
        "year_3": {
            "total_revenue": round(year_3_revenue, 2),
            "ebitda": round(year_3_ebitda, 2),
            "ebitda_margin_pct": round(year_3_margin, 1),
        },
        "final_month": {
            "monthly_revenue": round(final_month["revenue"], 2),
            "monthly_ebitda": round(final_month["ebitda"], 2),
            "cumulative_cash_flow": round(final_month["cumulative_cf"], 2),
        },
        "payback_period_months": payback_months,
        "operational_breakeven_month": break_even_data["break_even_month"],
        "startup_investment": round(startup_costs["total"], 2),
    }
