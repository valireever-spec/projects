import json
from pathlib import Path
from backend.core.config import SESSIONS_DIR
from backend.analytics.financial_model import build_projections
from backend.analytics.confidence_scorer import calculate_confidence_score
from backend.analytics.sensitivity_analyzer import build_sensitivity_matrix
from backend.services.domain_service import get_domain_details


def get_financial_projections(session_id: str, revenue_model: str, monthly_revenue: float) -> dict:
    """
    Get financial projections for a session.

    Args:
        session_id: Session UUID
        revenue_model: Revenue model type
        monthly_revenue: Estimated monthly revenue (EUR)

    Returns:
        Complete financial projections dict
    """
    try:
        # Load session
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if not session_file.exists():
            return {}

        with open(session_file, 'r') as f:
            session = json.load(f)

        profile = session.get("profile", {})
        domain_slug = profile.get("domain_slug", "")
        city = profile.get("city", "Berlin")
        legal_form = profile.get("legal_form", "Einzelunternehmen")
        initial_capital = float(profile.get("initial_capital", 50_000))

        # Get domain details
        domain_details = get_domain_details(domain_slug) or {}

        # Build projections
        projections = build_projections(
            domain_slug=domain_slug,
            revenue_model=revenue_model,
            monthly_revenue_estimate=monthly_revenue,
            city=city,
            legal_form=legal_form,
            startup_capital=initial_capital,
            employees=1,  # Founder initially
            sector_margins=domain_details.get("sector_margins"),
            city_wage_index=domain_details.get("city_wage_indices", {}).get(city, 1.0),
        )

        # Save to session
        session["financial_projection"] = projections
        with open(session_file, 'w') as f:
            json.dump(session, f, default=str)

        return projections
    except Exception as e:
        print(f"Error getting financial projections: {e}")
        return {}


def get_revenue_projections_for_scenario(
    session_id: str,
    revenue_model: str,
    monthly_revenue: float,
    scenario: str = "base",
) -> dict:
    """
    Get revenue projections for a specific scenario.

    Args:
        session_id: Session ID
        revenue_model: Revenue model
        monthly_revenue: Base monthly revenue
        scenario: One of (conservative, base, optimistic)

    Returns:
        Scenario-specific projection data
    """
    projections = get_financial_projections(session_id, revenue_model, monthly_revenue)

    if not projections or "scenarios" not in projections:
        return {}

    scenarios = projections.get("scenarios", {})
    scenario_data = scenarios.get(scenario, {})

    return {
        "scenario": scenario,
        "monthly_revenue": scenario_data.get("monthly_revenue", 0),
        "year_1_revenue": scenario_data.get("year_1_revenue", 0),
        "year_1_net_income": scenario_data.get("year_1_net_income", 0),
        "year_3_monthly_revenue": scenario_data.get("year_3_monthly_revenue", 0),
        "break_even_month": scenario_data.get("break_even_month", 0),
        "year_3_cumulative_cf": scenario_data.get("year_3_cumulative_cf", 0),
    }


def compare_scenarios(
    session_id: str,
    revenue_model: str,
    monthly_revenue: float,
) -> dict:
    """
    Compare all three scenarios side-by-side.

    Returns:
        Dict with comparative analysis
    """
    projections = get_financial_projections(session_id, revenue_model, monthly_revenue)

    if not projections or "scenarios" not in projections:
        return {}

    scenarios = projections.get("scenarios", {})

    comparison = {
        "base_revenue": monthly_revenue,
        "scenarios": {
            "conservative": {
                "multiplier": 0.6,
                "monthly_revenue": scenarios.get("conservative", {}).get("monthly_revenue", 0),
                "year_1_net_income": scenarios.get("conservative", {}).get("year_1_net_income", 0),
                "break_even_month": scenarios.get("conservative", {}).get("break_even_month", 0),
                "year_3_cumulative_cf": scenarios.get("conservative", {}).get("year_3_cumulative_cf", 0),
            },
            "base": {
                "multiplier": 1.0,
                "monthly_revenue": scenarios.get("base", {}).get("monthly_revenue", 0),
                "year_1_net_income": scenarios.get("base", {}).get("year_1_net_income", 0),
                "break_even_month": scenarios.get("base", {}).get("break_even_month", 0),
                "year_3_cumulative_cf": scenarios.get("base", {}).get("year_3_cumulative_cf", 0),
            },
            "optimistic": {
                "multiplier": 1.5,
                "monthly_revenue": scenarios.get("optimistic", {}).get("monthly_revenue", 0),
                "year_1_net_income": scenarios.get("optimistic", {}).get("year_1_net_income", 0),
                "break_even_month": scenarios.get("optimistic", {}).get("break_even_month", 0),
                "year_3_cumulative_cf": scenarios.get("optimistic", {}).get("year_3_cumulative_cf", 0),
            },
        },
        "recommendation": _get_scenario_recommendation(scenarios),
    }

    return comparison


def _get_scenario_recommendation(scenarios: dict) -> dict:
    """Get recommendation on which scenario is most realistic."""
    base = scenarios.get("base", {})
    conservative = scenarios.get("conservative", {})
    optimistic = scenarios.get("optimistic", {})

    base_breakeven = base.get("break_even_month", 37)
    cons_breakeven = conservative.get("break_even_month", 37)
    opt_breakeven = optimistic.get("break_even_month", 37)

    if base_breakeven <= 12:
        recommendation = "base"
        reasoning = "Base scenario reaches break-even within 12 months - realistic and achievable"
    elif cons_breakeven <= 12:
        recommendation = "conservative"
        reasoning = "Even conservative scenario is profitable - very safe planning"
    elif base_breakeven <= 24:
        recommendation = "base"
        reasoning = "Base scenario breaks even in year 2 - good growth trajectory"
    else:
        recommendation = "conservative"
        reasoning = "Consider conservative planning until you validate customer demand"

    return {
        "recommended_scenario": recommendation,
        "reasoning": reasoning,
    }


def estimate_funding_requirement(
    session_id: str,
    revenue_model: str,
    monthly_revenue: float,
    months_to_profitability: int = 12,
) -> dict:
    """
    Estimate funding needed to reach profitability.

    Args:
        session_id: Session ID
        revenue_model: Revenue model
        monthly_revenue: Estimated monthly revenue
        months_to_profitability: Target months to profitability

    Returns:
        Funding requirement analysis
    """
    projections = get_financial_projections(session_id, revenue_model, monthly_revenue)

    if not projections:
        return {}

    months = projections.get("months_1_12", [])
    startup_costs = projections.get("startup_costs", {})

    # Find minimum cash balance
    cumulative_cf = -startup_costs.get("total", 0)
    min_cash = cumulative_cf

    for month_data in months:
        cumulative_cf = month_data.get("cumulative_cf", 0)
        min_cash = min(min_cash, cumulative_cf)

    # Additional funding needed = the worst negative point
    funding_gap = abs(min_cash) if min_cash < 0 else 0

    return {
        "startup_investment_needed": startup_costs.get("total", 0),
        "operating_capital_needed": funding_gap,
        "total_funding_required": startup_costs.get("total", 0) + funding_gap,
        "months_to_profitability": min(projections.get("key_metrics", {}).get("operational_breakeven_month", 37), 36),
        "self_funded_possible": funding_gap < 10_000,  # Less than €10K gap
    }


def _get_or_build_projection(session_id: str, revenue_model: str, monthly_revenue: float) -> dict:
    """
    Get or build financial projection, using cached version if present.

    Args:
        session_id: Session ID
        revenue_model: Revenue model type
        monthly_revenue: Estimated monthly revenue

    Returns:
        Projection dict
    """
    try:
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if not session_file.exists():
            return {}

        with open(session_file, 'r') as f:
            session = json.load(f)

        # Return cached projection if present
        if "financial_projection" in session:
            return session["financial_projection"]

        # Otherwise build and cache
        return get_financial_projections(session_id, revenue_model, monthly_revenue)
    except Exception:
        return {}


def _extract_model_params(session_id: str, revenue_model: str, monthly_revenue: float) -> dict:
    """
    Extract base parameters needed for sensitivity analysis.

    Args:
        session_id: Session ID
        revenue_model: Revenue model type
        monthly_revenue: Estimated monthly revenue

    Returns:
        Dict with domain_slug, revenue_model, monthly_revenue_estimate, city, legal_form, startup_capital, employees, sector_margins
    """
    try:
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if not session_file.exists():
            return {}

        with open(session_file, 'r') as f:
            session = json.load(f)

        profile = session.get("profile", {})
        domain_slug = profile.get("domain_slug", "")
        city = profile.get("city", "Berlin")
        legal_form = profile.get("legal_form", "Einzelunternehmen")
        initial_capital = float(profile.get("initial_capital", 50_000))

        # Get domain details
        domain_details = get_domain_details(domain_slug) or {}

        return {
            "domain_slug": domain_slug,
            "revenue_model": revenue_model,
            "monthly_revenue_estimate": monthly_revenue,
            "city": city,
            "legal_form": legal_form,
            "startup_capital": initial_capital,
            "employees": 1,
            "sector_margins": domain_details.get("sector_margins"),
            "city_wage_index": domain_details.get("city_wage_indices", {}).get(city, 1.0),
        }
    except Exception:
        return {}


def get_confidence_assessment(session_id: str, revenue_model: str, monthly_revenue: float) -> dict:
    """
    Get confidence assessment for financial projections.

    Args:
        session_id: Session ID
        revenue_model: Revenue model type
        monthly_revenue: Estimated monthly revenue

    Returns:
        Confidence score dict with tier, band, drivers, warnings
    """
    try:
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if not session_file.exists():
            return {}

        with open(session_file, 'r') as f:
            session = json.load(f)

        projection = _get_or_build_projection(session_id, revenue_model, monthly_revenue)
        domain_score = session.get("domain_score", {})
        risk_assessment = session.get("risk_assessment", {})
        profile = session.get("profile", {})

        return calculate_confidence_score(domain_score, projection, risk_assessment, profile)
    except Exception as e:
        print(f"Error assessing confidence: {e}")
        return {}


def get_sensitivity_analysis(session_id: str, revenue_model: str, monthly_revenue: float) -> dict:
    """
    Get sensitivity analysis for financial projections.

    Args:
        session_id: Session ID
        revenue_model: Revenue model type
        monthly_revenue: Estimated monthly revenue

    Returns:
        Sensitivity matrix with variance by revenue/costs/margin and key driver
    """
    try:
        projection = _get_or_build_projection(session_id, revenue_model, monthly_revenue)
        base_params = _extract_model_params(session_id, revenue_model, monthly_revenue)

        if not projection or not base_params:
            return {}

        return build_sensitivity_matrix(base_params, projection)
    except Exception as e:
        print(f"Error analyzing sensitivity: {e}")
        return {}
