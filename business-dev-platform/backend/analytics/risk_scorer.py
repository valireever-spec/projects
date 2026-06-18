from typing import Literal


def assess_risks(
    domain: str,
    legal_form: str,
    city: str,
    financial_projection: dict | None = None,
) -> dict:
    """
    Assess business risks across 8 dimensions.

    Args:
        domain: Business domain slug
        legal_form: Legal structure
        city: German city
        financial_projection: Financial projections dict (optional)

    Returns:
        Dict with {
            overall_risk_level: "low" | "medium" | "high",
            risk_score: 0-100,
            risk_factors: [list of 8 RiskFactor dicts],
            top_3_risks: [top 3 by score],
            mitigation_plan: [list of strategies]
        }
    """
    # Initialize risk factors (8 dimensions)
    risk_factors = [
        _assess_market_saturation_risk(domain),
        _assess_regulatory_risk(domain, legal_form),
        _assess_funding_risk(financial_projection),
        _assess_labor_market_risk(domain, city),
        _assess_technology_disruption_risk(domain),
        _assess_macro_economic_risk(),
        _assess_operational_risk(domain, legal_form),
        _assess_competition_risk(domain),
    ]

    # Calculate overall risk score
    total_score = sum(rf["score"] for rf in risk_factors)
    avg_score = total_score / len(risk_factors)

    # Classify overall risk level
    if avg_score < 8:
        overall_level = "low"
    elif avg_score < 15:
        overall_level = "medium"
    else:
        overall_level = "high"

    # Get top 3 risks
    risk_factors_sorted = sorted(risk_factors, key=lambda x: x["score"], reverse=True)
    top_3 = risk_factors_sorted[:3]

    # Generate mitigation plan
    mitigation_plan = []
    for risk in top_3:
        mitigation_plan.extend(risk["mitigation_strategies"][:2])

    return {
        "overall_risk_level": overall_level,
        "risk_score": round(avg_score, 1),
        "risk_factors": risk_factors,
        "top_3_risks": top_3,
        "mitigation_plan": mitigation_plan[:5],
    }


def _assess_market_saturation_risk(domain: str) -> dict:
    """Assess risk of market saturation and competition."""
    # Domain-specific saturation risk
    saturation_risk = {
        "online-ernaehrungsberatung": 2,      # Growing market, moderate saturation
        "social-media-agentur": 3,            # More saturated
        "virtueller-assistent": 2,            # Growing market
        "blockchain-consulting": 2,           # Emerging, low saturation
        "nachhaltigkeitsconsulting": 1,       # Emerging, low saturation
    }

    likelihood = saturation_risk.get(domain, 3)  # Default moderate
    impact = 3  # Market saturation typically has medium impact

    return {
        "name": "Marktübersättigung",
        "description": "Risiko, dass der Markt zu viele Konkurrenten anzieht und Preise/Margen drückt",
        "likelihood": likelihood,
        "impact": impact,
        "score": likelihood * impact,
        "color": _get_risk_color(likelihood * impact),
        "mitigation_strategies": [
            "Spezialisieren Sie sich auf eine Nische oder ein spezifisches Kundensegment",
            "Investieren Sie früh in Markenaufbau und Kundenloyalität",
            "Entwickeln Sie einzigartige oder patentierbare Differenzierungsmerkmale",
            "Bauen Sie Kundenabhängigkeiten oder Switching Costs auf",
        ]
    }


def _assess_regulatory_risk(domain: str, legal_form: str) -> dict:
    """Assess regulatory and compliance risk."""
    # Higher risk for regulated sectors
    regulated_domains = {
        "consulting-gastronomie": 4,
        "psychologische-beratung": 4,
        "immobilien-makler": 3,
        "accounting-dienstleistung": 3,
        "online-fitness-coaching": 2,
    }

    likelihood = regulated_domains.get(domain, 2)  # Default low-medium
    impact = 4  # Regulatory issues have high impact

    # Increase if high-risk legal form (AG requires more compliance)
    if legal_form == "AG":
        likelihood = min(likelihood + 1, 5)

    return {
        "name": "Regulatorisches Risiko",
        "description": "Änderungen in Gesetzen, Lizenzen oder behördlichen Anforderungen",
        "likelihood": likelihood,
        "impact": impact,
        "score": likelihood * impact,
        "color": _get_risk_color(likelihood * impact),
        "mitigation_strategies": [
            "Konsultieren Sie einen Anwalt oder Steuerberater vor der Gründung",
            "Monitorieren Sie gesetzliche Änderungen in Ihrer Branche",
            "Binden Sie Compliance früh in Ihre Prozesse ein",
            "Bauen Sie Reserven für Compliance-Kosten ein",
        ]
    }


def _assess_funding_risk(financial_projection: dict | None) -> dict:
    """Assess funding and cash flow risk."""
    likelihood = 3
    impact = 5  # Cash flow problems are critical

    # If projections available, assess based on break-even
    if financial_projection:
        breakeven_month = financial_projection.get("break_even_month", 12)
        if breakeven_month > 24:
            likelihood = 4  # High risk if >2 years to profitability
        elif breakeven_month <= 12:
            likelihood = 2  # Low risk if <1 year to profitability

    return {
        "name": "Finanzierungs-/Liquiditätsrisiko",
        "description": "Risiko von Cashflow-Engpässen vor Erreichen der Rentabilität",
        "likelihood": likelihood,
        "impact": impact,
        "score": likelihood * impact,
        "color": _get_risk_color(likelihood * impact),
        "mitigation_strategies": [
            "Sichern Sie ausreichend Startkapital (mindestens 3-6 Monate Betrieb)",
            "Verhandeln Sie günstige Zahlungsbedingungen mit Lieferanten",
            "Implementieren Sie aggressives Forderungsmanagement",
            "Planen Sie Linien von privaten Investoren oder Darlehen ein",
        ]
    }


def _assess_labor_market_risk(domain: str, city: str) -> dict:
    """Assess labor market and talent acquisition risk."""
    # Tech-heavy domains have higher labor risk
    tech_heavy = {
        "webshop-erstellung": 3,
        "software-entwicklung": 3,
        "it-support": 2,
        "digitales-marketing": 2,
    }

    likelihood = tech_heavy.get(domain, 2)  # Default low-medium

    # Berlin, Munich, Hamburg have tighter labor markets
    tight_cities = {"Berlin": 1, "Munich": 2, "Hamburg": 1}
    if city in tight_cities:
        likelihood += tight_cities[city]
    likelihood = min(likelihood, 5)

    impact = 2  # Labor risk typically medium impact for startups

    return {
        "name": "Arbeitsmarktrisiko",
        "description": "Schwierigkeit, qualifizierte Mitarbeiter zu finden und zu halten",
        "likelihood": likelihood,
        "impact": impact,
        "score": likelihood * impact,
        "color": _get_risk_color(likelihood * impact),
        "mitigation_strategies": [
            "Bauen Sie eine starke Unternehmenskultur und EVP auf",
            "Nutzen Sie Remote-Arbeit um Talente aus ganz Deutschland zu rekrutieren",
            "Bieten Sie Equity/Beteiligung an statt nur Gehalt",
            "Investieren Sie in Schulung und Entwicklung",
        ]
    }


def _assess_technology_disruption_risk(domain: str) -> dict:
    """Assess risk of technology disruption."""
    # AI/ML, automation-vulnerable sectors have higher risk
    disruption_prone = {
        "content-agentur": 3,
        "copywriting": 3,
        "virtueller-assistent": 2,
        "social-media-agentur": 2,
        "video-produktion": 2,
    }

    likelihood = disruption_prone.get(domain, 2)  # Default low-medium
    impact = 4  # Disruption impact can be high

    return {
        "name": "Technologie-Disruptions-Risiko",
        "description": "Risiko, dass neue Technologien (AI, Automatisierung) Ihr Geschäftsmodell obsolet machen",
        "likelihood": likelihood,
        "impact": impact,
        "score": likelihood * impact,
        "color": _get_risk_color(likelihood * impact),
        "mitigation_strategies": [
            "Überwachen Sie neue Technologien und Trends in Ihrer Branche",
            "Bilden Sie sich und Ihr Team kontinuierlich weiter",
            "Entwickeln Sie Fähigkeiten, die nicht einfach automatisierbar sind",
            "Bauen Sie auf menschliche Beziehungen und Vertrauen",
        ]
    }


def _assess_macro_economic_risk() -> dict:
    """Assess macroeconomic risk (inflation, recession, interest rates)."""
    # Generic macro risk for Germany (2026 outlook)
    likelihood = 2  # Moderate likelihood of macro headwinds
    impact = 3  # Macro impact varies by sector

    return {
        "name": "Makroökonomisches Risiko",
        "description": "Rezession, Inflation, Zinssätze, Devisenrisiken",
        "likelihood": likelihood,
        "impact": impact,
        "score": likelihood * impact,
        "color": _get_risk_color(likelihood * impact),
        "mitigation_strategies": [
            "Bauen Sie Financial Resilience auf (Cashreserven, Kreditlinien)",
            "Diversifizieren Sie Einnahmequellen und Kundenbasis",
            "Monitorieren Sie Zentralbank-Entscheidungen und Konjunkturdaten",
            "Passen Sie Preismodell an Inflation und Marktschwankungen an",
        ]
    }


def _assess_operational_risk(domain: str, legal_form: str) -> dict:
    """Assess operational execution risk."""
    # AG/GmbH have more operational overhead
    legal_form_risk = {
        "AG": 3,
        "GmbH": 2,
        "UG": 2,
        "GbR": 2,
        "Einzelunternehmen": 1,
        "Freiberufler": 1,
    }

    likelihood = legal_form_risk.get(legal_form, 2)
    impact = 3  # Operational failures have medium impact

    return {
        "name": "Betriebliches Risiko",
        "description": "Risiko bei der Ausführung (Prozesse, Systeme, Management, menschliche Fehler)",
        "likelihood": likelihood,
        "impact": impact,
        "score": likelihood * impact,
        "color": _get_risk_color(likelihood * impact),
        "mitigation_strategies": [
            "Dokumentieren Sie alle kritischen Prozesse",
            "Investieren Sie in angemessene Tools und Systeme",
            "Implementieren Sie Qualitätskontrolle von Anfang an",
            "Bauen Sie redundante Kapazitäten für kritische Funktionen auf",
        ]
    }


def _assess_competition_risk(domain: str) -> dict:
    """Assess competitive intensity and substitution risk."""
    # High-competition domains
    competition_high = {
        "social-media-agentur": 4,
        "seo-beratung": 4,
        "content-agentur": 3,
        "affiliate-marketing": 3,
    }

    likelihood = competition_high.get(domain, 2)  # Default low-medium
    impact = 3  # Competition impact medium

    return {
        "name": "Wettbewerbsrisiko",
        "description": "Intensive Konkurrenz, Preisdruck, oder Ersatz durch ähnliche Lösungen",
        "likelihood": likelihood,
        "impact": impact,
        "score": likelihood * impact,
        "color": _get_risk_color(likelihood * impact),
        "mitigation_strategies": [
            "Definieren Sie eine klare und eindeutige Positionierung",
            "Bauen Sie Kundenbeziehungen und Loyalität auf",
            "Investieren Sie in kontinuierliche Innovation",
            "Überwachen Sie Wettbewerber und bewahren Sie Agilität",
        ]
    }


def _get_risk_color(score: int) -> str:
    """Map risk score to color."""
    if score <= 5:
        return "green"     # Low risk
    elif score <= 10:
        return "yellow"    # Medium risk
    elif score <= 15:
        return "orange"    # High risk
    else:
        return "red"       # Critical risk
