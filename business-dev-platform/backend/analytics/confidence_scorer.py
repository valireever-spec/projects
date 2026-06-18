"""
Confidence scoring for financial projections.
Synthesizes domain quality, revenue model, competition, financial assumptions, and regulatory clarity.
Returns confidence tier (high/medium/low) and confidence band (±15/25/40%).
"""


def calculate_confidence_score(domain_score: dict, financial_projection: dict, risk_assessment: dict, profile: dict) -> dict:
    """
    Calculate confidence score for financial projections.

    Args:
        domain_score: Domain scoring result with 'grade', 'data_quality_flags', 'total_score'
        financial_projection: Financial model output with break_even_month, year_1_net, etc.
        risk_assessment: Risk matrix with overall_risk_score
        profile: Business profile with 'legal_form', 'revenue_model'

    Returns:
        {
            "confidence_score": 72,
            "confidence_tier": "medium",
            "confidence_band_pct": 25,
            "drivers": [
                {"factor": "domain_data_quality", "score": 70, "weight": 0.30},
                {"factor": "revenue_model_maturity", "score": 85, "weight": 0.25},
                ...
            ],
            "warnings": ["..."]
        }
    """

    # 1. Domain Data Quality (30%)
    domain_grade = domain_score.get("grade", "moderate").lower()
    grade_scores = {
        "excellent": 100,
        "good": 80,
        "moderate": 60,
        "saturated": 40
    }
    domain_quality = grade_scores.get(domain_grade, 60)

    # Deduct for defaults that fired
    data_quality_flags = domain_score.get("data_quality_flags", [])
    domain_quality -= 10 * len(data_quality_flags)
    domain_quality = max(0, min(100, domain_quality))

    # 2. Revenue Model Maturity (25%)
    revenue_model = profile.get("revenue_model", "").lower()
    revenue_maturity = {
        "hourly": 90,
        "subscription": 85,
        "product_sale": 80,
        "commission": 75,
        "hybrid": 70,
        "unknown": 50
    }
    revenue_score = revenue_maturity.get(revenue_model, 50)

    # 3. Competition Certainty (20%)
    # Infer from domain score competition component
    competition_component = domain_score.get("competition_component", 12.5)
    if competition_component >= 20:
        competition_certainty = 90
    elif competition_component >= 15:
        competition_certainty = 70
    else:
        competition_certainty = 50

    # 4. Financial Assumptions (15%)
    break_even_month = financial_projection.get("break_even_month", 12)
    if break_even_month <= 6:
        financial_score = 90
    elif break_even_month <= 12:
        financial_score = 80
    elif break_even_month <= 18:
        financial_score = 65
    elif break_even_month <= 24:
        financial_score = 50
    else:
        financial_score = 30

    # 5. Regulatory Clarity (10%)
    legal_form = profile.get("legal_form", "").strip()
    regulatory_scores = {
        "Einzelunternehmen": 90,
        "Freiberufler": 90,
        "GbR": 75,
        "UG": 75,
        "GmbH": 65,
        "AG": 50
    }
    regulatory_score = regulatory_scores.get(legal_form, 60)

    # Weighted average
    weights = {
        "domain_quality": 0.30,
        "revenue_score": 0.25,
        "competition_certainty": 0.20,
        "financial_score": 0.15,
        "regulatory_score": 0.10
    }

    confidence_score = (
        domain_quality * weights["domain_quality"] +
        revenue_score * weights["revenue_score"] +
        competition_certainty * weights["competition_certainty"] +
        financial_score * weights["financial_score"] +
        regulatory_score * weights["regulatory_score"]
    )
    confidence_score = round(confidence_score, 1)

    # Determine tier and band
    if confidence_score >= 75:
        tier = "high"
        band_pct = 15
    elif confidence_score >= 50:
        tier = "medium"
        band_pct = 25
    else:
        tier = "low"
        band_pct = 40

    # Build drivers list
    drivers = [
        {"factor": "domain_data_quality", "score": domain_quality, "weight": weights["domain_quality"]},
        {"factor": "revenue_model_maturity", "score": revenue_score, "weight": weights["revenue_score"]},
        {"factor": "competition_certainty", "score": competition_certainty, "weight": weights["competition_certainty"]},
        {"factor": "financial_assumptions", "score": financial_score, "weight": weights["financial_score"]},
        {"factor": "regulatory_clarity", "score": regulatory_score, "weight": weights["regulatory_score"]},
    ]

    # Generate warnings
    warnings = []
    if len(data_quality_flags) > 0:
        warnings.append(f"Domain data incomplete ({len(data_quality_flags)} defaults applied)")
    if break_even_month > 18:
        warnings.append(f"Long runway to profitability ({break_even_month} months)")
    if legal_form in ["AG", "GmbH"]:
        warnings.append(f"Complex legal form {legal_form} increases regulatory overhead")

    return {
        "confidence_score": confidence_score,
        "confidence_tier": tier,
        "confidence_band_pct": band_pct,
        "drivers": drivers,
        "warnings": warnings
    }
