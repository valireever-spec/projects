import json
from pathlib import Path
from backend.core.config import SESSIONS_DIR
from backend.services.domain_service import get_domain_details
from backend.analytics.risk_scorer import assess_risks
from backend.analytics.regulatory import german_requirements


def assemble_plan(session_id: str) -> dict:
    """
    Assemble complete business plan from session data.

    Returns:
        Structured plan dict with all 8 sections:
        - executive_summary
        - company_description
        - market_analysis
        - financial_plan
        - risk_assessment
        - regulatory_requirements
        - competitive_advantages
        - action_plan
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

        # Get domain details
        domain_details = get_domain_details(domain_slug) or {}

        # Get analyses
        market_analysis = session.get("market_analysis", {})
        financial_projection = session.get("financial_projection", {})
        risk_assessment = assess_risks(domain_slug, legal_form, city, financial_projection)
        regulatory_reqs = german_requirements(domain_slug, legal_form)

        # Build plan sections
        plan = {
            "session_id": session_id,
            "generated_at": _get_timestamp(),

            # Section 1: Executive Summary
            "executive_summary": _build_executive_summary(
                profile, domain_details, market_analysis, financial_projection
            ),

            # Section 2: Company Description
            "company_description": _build_company_description(profile, domain_slug, domain_details, legal_form),

            # Section 3: Market Analysis
            "market_analysis": market_analysis,

            # Section 4: Financial Plan
            "financial_plan": _build_financial_plan(financial_projection),

            # Section 5: Risk Assessment
            "risk_assessment": risk_assessment,

            # Section 6: Regulatory Requirements
            "regulatory_requirements": regulatory_reqs,

            # Section 7: Competitive Advantages
            "competitive_advantages": _build_competitive_advantages(market_analysis, risk_assessment),

            # Section 8: Action Plan
            "action_plan": _build_action_plan(profile, domain_slug, financial_projection, regulatory_reqs),

            # Metadata
            "metadata": {
                "business_name": profile.get("business_name", ""),
                "domain": domain_slug,
                "city": city,
                "legal_form": legal_form,
            }
        }

        return plan
    except Exception as e:
        print(f"Error assembling plan: {e}")
        return {}


def _build_executive_summary(profile: dict, domain_details: dict, market_analysis: dict, financial_proj: dict) -> dict:
    """Build executive summary section."""
    market = market_analysis.get("market", {})
    metrics = financial_proj.get("key_metrics", {})
    y1 = metrics.get("year_1", {})

    return {
        "business_name": profile.get("business_name", ""),
        "elevator_pitch": f"Wir bauen ein {domain_details.get('name_de', '')} Unternehmen in {profile.get('city', '')}.",
        "market_opportunity": f"Marktgröße: {market.get('market_size_estimate', 'N/A')}. Wachstum: {market.get('growth_rate_pct', 0)}%/Jahr.",
        "financial_highlights": {
            "startup_investment": financial_proj.get("startup_costs", {}).get("total", 0),
            "break_even_month": financial_proj.get("break_even_month", 0),
            "year_1_revenue": y1.get("total_revenue", 0),
            "year_1_net_income": y1.get("net_income", 0),
        },
        "key_success_factors": [
            "Schnelles Go-to-Market",
            "Kundengewinnung und -bindung",
            "Operative Effizienz",
            "Kontinuierliche Innovation",
        ]
    }


def _build_company_description(profile: dict, domain_slug: str, domain_details: dict, legal_form: str) -> dict:
    """Build company description section."""
    return {
        "business_name": profile.get("business_name", ""),
        "mission": "Die Mission wird durch das Geschäftskonzept definiert.",
        "vision": "Wir streben danach, ein führendes Unternehmen in unserem Markt zu werden.",
        "business_model": profile.get("unique_value_proposition", ""),
        "target_market": profile.get("target_market", ""),
        "founders": {
            "background": profile.get("founder_background", ""),
            "experience": "Relevant für die Geschäftsidee",
        },
        "location": profile.get("city", ""),
        "legal_form": legal_form,
        "business_domain": domain_details.get("name_de", domain_slug),
    }


def _build_financial_plan(financial_proj: dict) -> dict:
    """Extract financial plan section."""
    return {
        "startup_costs": financial_proj.get("startup_costs", {}),
        "revenue_model": financial_proj.get("revenue_model", ""),
        "monthly_revenue_estimate": financial_proj.get("monthly_revenue_estimate", 0),
        "break_even_analysis": {
            "monthly_revenue_needed": financial_proj.get("break_even_monthly_revenue", 0),
            "break_even_month": financial_proj.get("break_even_month", 0),
            "achievable": financial_proj.get("break_even_achievable", False),
        },
        "key_metrics": financial_proj.get("key_metrics", {}),
        "scenarios": financial_proj.get("scenarios", {}),
        "projections_36_months": {
            "year_1": financial_proj.get("months_1_12", []),
            "year_2": financial_proj.get("months_13_24", []),
            "year_3": financial_proj.get("months_25_36", []),
        }
    }


def _build_competitive_advantages(market_analysis: dict, risk_assessment: dict) -> dict:
    """Build competitive advantages section from market and risk data."""
    competition = market_analysis.get("competition", {})

    return {
        "differentiation_strategies": competition.get("differentiation_opportunities", []),
        "competitive_barriers": competition.get("barriers_to_entry", []),
        "market_position": f"Wettbewerbs-Intensität: {competition.get('level', 'mittel')}",
        "key_advantages": [
            "Spezialisierung und Nischenfokus",
            "Fokus auf Kundenbeziehungen",
            "Schnelle Anpassungsfähigkeit",
            "Innovative Problemlösung",
        ]
    }


def _build_action_plan(profile: dict, domain_slug: str, financial_proj: dict, regulatory_reqs: dict) -> dict:
    """Build 90-day action plan section."""
    return {
        "phase_1_months_1_3": {
            "title": "Gründung & Vorbereitung",
            "tasks": [
                "Gründung durchführen (Gewerbeanmeldung, Handelsregister)",
                f"Geschätzter Aufwand: {regulatory_reqs.get('total_estimated_days', 0)} Tage",
                f"Geschätzte Kosten: €{regulatory_reqs.get('total_estimated_cost', 0)}",
                "Geschäftskonten und Versicherungen einrichten",
                "Website und Online-Präsenz aufbauen",
                "DSGVO-Compliance implementieren",
            ],
            "milestones": [
                "Unternehmensregistration abgeschlossen",
                "Website live",
                "Erste Kundenakquisition gestartet",
            ]
        },
        "phase_2_months_4_6": {
            "title": "Markteinführung & Kundengewinnung",
            "tasks": [
                "Marketing und Kundenakquisition starten",
                "Erstes Kundenfeedback sammeln und integrieren",
                f"Zielmonatliches Umsatzziel erreichen: €{financial_proj.get('monthly_revenue_estimate', 0)}",
                "Prozesse und Systeme optimieren",
                "Team erweitern (wenn nötig)",
            ],
            "milestones": [
                "Erste zahlende Kunden",
                "Break-Even-Weg ist klar",
                "Kundenreferenzen und Bewertungen erhalten",
            ]
        },
        "phase_3_months_7_9": {
            "title": "Skalierung & Stabilisierung",
            "tasks": [
                "Geschäftsmodell validieren und optimieren",
                "Effizienzen erreichen und Kosten reduzieren",
                "Kundenbindung verbessern",
                "Nächste Wachstumsphasen planen",
                "Finanzierung evaluieren (wenn notwendig)",
            ],
            "milestones": [
                "Profitabilität erreicht oder in Sicht",
                "Wiederholungsgeschäft von 30%+ der Kunden",
                "Nächste 12-Monats-Planung abgeschlossen",
            ]
        }
    }


def _get_timestamp() -> str:
    """Get current timestamp."""
    from datetime import datetime
    return datetime.utcnow().isoformat()
