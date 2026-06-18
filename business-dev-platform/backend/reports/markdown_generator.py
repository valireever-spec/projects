"""Generate professional Markdown reports from business plan data."""
from datetime import datetime


def render_markdown(plan: dict) -> str:
    """
    Render a complete business plan as Markdown.

    Args:
        plan: Dict from plan_service.assemble_plan()

    Returns:
        Professional Markdown string ready for download/display
    """
    lines = []

    # Title and metadata
    lines.append(f"# Geschäftsplan: {plan.get('metadata', {}).get('business_name', 'Unnamed Business')}")
    lines.append("")
    lines.append(f"**Erstellt am:** {plan.get('generated_at', 'N/A')}")
    lines.append(f"**Geschäftsdomäne:** {plan.get('metadata', {}).get('domain', 'N/A')}")
    lines.append(f"**Standort:** {plan.get('metadata', {}).get('city', 'N/A')}")
    lines.append(f"**Rechtsform:** {plan.get('metadata', {}).get('legal_form', 'N/A')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of Contents
    lines.append("## Inhaltsverzeichnis")
    lines.append("")
    lines.append("1. [Executive Summary](#executive-summary)")
    lines.append("2. [Unternehmensbeschreibung](#unternehmensbeschreibung)")
    lines.append("3. [Marktanalyse](#marktanalyse)")
    lines.append("4. [Finanzplan](#finanzplan)")
    lines.append("5. [Risikobewertung](#risikobewertung)")
    lines.append("6. [Regulatorische Anforderungen](#regulatorische-anforderungen)")
    lines.append("7. [Wettbewerbsvorteile](#wettbewerbsvorteile)")
    lines.append("8. [Aktionsplan](#aktionsplan)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 1: Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    summary = plan.get("executive_summary", {})
    lines.append(f"**Geschäftsname:** {summary.get('business_name', '')}")
    lines.append("")
    lines.append("### Geschäftsidee")
    lines.append(f"{summary.get('elevator_pitch', '')}")
    lines.append("")
    lines.append("### Marktgelegenheit")
    lines.append(f"{summary.get('market_opportunity', '')}")
    lines.append("")
    lines.append("### Finanzielle Highlights")
    highlights = summary.get("financial_highlights", {})
    lines.append("")
    lines.append(f"- **Startinvestitionen:** €{highlights.get('startup_investment', 0):,.0f}")
    lines.append(f"- **Break-Even Monat:** Monat {highlights.get('break_even_month', 0)}")
    lines.append(f"- **Umsatz Jahr 1:** €{highlights.get('year_1_revenue', 0):,.0f}")
    lines.append(f"- **Nettoeinkommen Jahr 1:** €{highlights.get('year_1_net_income', 0):,.0f}")
    lines.append("")
    lines.append("### Erfolgsfaktoren")
    lines.append("")
    for factor in summary.get("key_success_factors", []):
        lines.append(f"- {factor}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 2: Company Description
    lines.append("## Unternehmensbeschreibung")
    lines.append("")
    company = plan.get("company_description", {})
    lines.append(f"### Mission")
    lines.append(f"{company.get('mission', '')}")
    lines.append("")
    lines.append("### Vision")
    lines.append(f"{company.get('vision', '')}")
    lines.append("")
    lines.append("### Geschäftsmodell")
    lines.append(f"{company.get('business_model', '')}")
    lines.append("")
    lines.append("### Zielmarkt")
    lines.append(f"{company.get('target_market', '')}")
    lines.append("")
    lines.append("### Gründer")
    founders = company.get("founders", {})
    lines.append(f"- **Hintergrund:** {founders.get('background', '')}")
    lines.append(f"- **Erfahrung:** {founders.get('experience', '')}")
    lines.append("")
    lines.append("### Unternehmensdetails")
    lines.append(f"- **Standort:** {company.get('location', '')}")
    lines.append(f"- **Rechtsform:** {company.get('legal_form', '')}")
    lines.append(f"- **Geschäftsdomäne:** {company.get('business_domain', '')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 3: Market Analysis
    lines.append("## Marktanalyse")
    lines.append("")
    market = plan.get("market_analysis", {})

    # Market sizing
    market_data = market.get("market", {})
    lines.append("### Marktgröße und Wachstum")
    lines.append(f"- **Geschätzter Marktumfang:** {market_data.get('market_size_estimate', 'N/A')}")
    lines.append(f"- **Wachstumsrate:** {market_data.get('growth_rate_pct', 0)}% pro Jahr")
    lines.append(f"- **Marktreife:** {market_data.get('market_maturity', 'N/A')}")
    lines.append("")

    # Competition
    competition = market.get("competition", {})
    lines.append("### Wettbewerb")
    lines.append(f"- **Wettbewerbsintensität:** {competition.get('level', 'mittel').capitalize()}")
    lines.append(f"- **Hauptwettbewerber:** {', '.join(competition.get('main_players', [])) or 'N/A'}")
    lines.append("")
    lines.append("#### Markteintrittsbarrieren")
    for barrier in competition.get("barriers_to_entry", []):
        lines.append(f"- {barrier}")
    lines.append("")
    lines.append("#### Differenzierungsmöglichkeiten")
    for diff in competition.get("differentiation_opportunities", []):
        lines.append(f"- {diff}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 4: Financial Plan
    lines.append("## Finanzplan")
    lines.append("")
    financial = plan.get("financial_plan", {})

    lines.append("### Startkapital")
    startup = financial.get("startup_costs", {})
    lines.append(f"- **Gesamtbudget:** €{startup.get('total', 0):,.0f}")
    for category, amount in startup.items():
        if category != "total":
            lines.append(f"- **{category.replace('_', ' ').title()}:** €{amount:,.0f}")
    lines.append("")

    lines.append("### Einnahmemodell")
    lines.append(f"{financial.get('revenue_model', 'N/A')}")
    lines.append("")
    lines.append(f"**Geschätzte monatliche Einnahmen:** €{financial.get('monthly_revenue_estimate', 0):,.0f}")
    lines.append("")

    lines.append("### Break-Even Analyse")
    breakeven = financial.get("break_even_analysis", {})
    lines.append(f"- **Monatlich erforderlich:** €{breakeven.get('monthly_revenue_needed', 0):,.0f}")
    lines.append(f"- **Break-Even Monat:** {breakeven.get('break_even_month', 0)}")
    lines.append(f"- **Erreichbar:** {'Ja' if breakeven.get('achievable') else 'Nein'}")
    lines.append("")

    lines.append("### Szenarien (36 Monate)")
    scenarios = financial.get("scenarios", {})
    if scenarios:
        lines.append("")
        lines.append("| Szenario | Jahr 1 Umsatz | Jahr 3 Umsatz | EBITDA Marge Jahr 1 |")
        lines.append("|----------|---------------|---------------|---------------------|")
        for scenario_name, scenario_data in scenarios.items():
            yr1_rev = scenario_data.get("year_1", {}).get("total_revenue", 0)
            yr3_rev = scenario_data.get("year_3", {}).get("total_revenue", 0)
            ebitda_margin = scenario_data.get("year_1", {}).get("ebitda_margin_pct", 0)
            lines.append(f"| {scenario_name.replace('_', ' ').title()} | €{yr1_rev:,.0f} | €{yr3_rev:,.0f} | {ebitda_margin:.1f}% |")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Section 5: Risk Assessment
    lines.append("## Risikobewertung")
    lines.append("")
    risk = plan.get("risk_assessment", {})

    lines.append(f"**Gesamtes Risiko:** {risk.get('overall_risk_level', 'N/A').upper()}")
    lines.append(f"**Risikowert (0-100):** {risk.get('risk_score', 0)}")
    lines.append("")

    lines.append("### Risikoanalyse (8 Dimensionen)")
    lines.append("")
    factors = risk.get("risk_factors", [])
    for factor in factors:
        status = "🟢" if factor.get("color") == "green" else "🟡" if factor.get("color") == "yellow" else "🟠" if factor.get("color") == "orange" else "🔴"
        lines.append(f"{status} **{factor.get('name', '')}** (Wert: {factor.get('score', 0)})")
        lines.append(f"   {factor.get('description', '')}")
        lines.append("")

    lines.append("### Top 3 Risiken")
    lines.append("")
    for i, risk_item in enumerate(risk.get("top_3_risks", []), 1):
        lines.append(f"{i}. **{risk_item.get('title', '')}**")
        lines.append(f"   - **Beschreibung:** {risk_item.get('description', '')}")
        lines.append(f"   - **Mitigation:** {risk_item.get('mitigation', '')}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Section 6: Regulatory Requirements
    lines.append("## Regulatorische Anforderungen")
    lines.append("")
    reqs = plan.get("regulatory_requirements", {})

    lines.append(f"**Geschätzte Gesamtkosten:** €{reqs.get('total_estimated_cost', 0):,.0f}")
    lines.append(f"**Geschätzte Tage:** {reqs.get('total_estimated_days', 0)}")
    lines.append("")

    grouped = reqs.get("grouped_by_category", {})
    for category, requirements in grouped.items():
        lines.append(f"### {category}")
        lines.append("")
        for req in requirements:
            lines.append(f"**{req.get('requirement', '')}**")
            lines.append(f"- Behörde: {req.get('authority', '')}")
            lines.append(f"- Kosten: €{req.get('estimated_cost_eur', 0)}")
            lines.append(f"- Dauer: {req.get('estimated_days', 0)} Tage")
            lines.append(f"- Beschreibung: {req.get('description', '')}")
            lines.append("")

    lines.append("---")
    lines.append("")

    # Section 7: Competitive Advantages
    lines.append("## Wettbewerbsvorteile")
    lines.append("")
    advantages = plan.get("competitive_advantages", {})

    lines.append("### Differenzierungsstrategien")
    for strategy in advantages.get("differentiation_strategies", []):
        lines.append(f"- {strategy}")
    lines.append("")

    lines.append("### Wettbewerbsbarrieren")
    for barrier in advantages.get("competitive_barriers", []):
        lines.append(f"- {barrier}")
    lines.append("")

    lines.append(f"### Marktposition")
    lines.append(f"{advantages.get('market_position', '')}")
    lines.append("")

    lines.append("### Schlüsselvorteil")
    for advantage in advantages.get("key_advantages", []):
        lines.append(f"- {advantage}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 8: Action Plan
    lines.append("## 90-Tage-Aktionsplan")
    lines.append("")
    action_plan = plan.get("action_plan", {})

    for phase_key in ["phase_1_months_1_3", "phase_2_months_4_6", "phase_3_months_7_9"]:
        phase = action_plan.get(phase_key, {})
        lines.append(f"### {phase.get('title', '')}")
        lines.append("")

        lines.append("**Aufgaben:**")
        for task in phase.get("tasks", []):
            lines.append(f"- {task}")
        lines.append("")

        lines.append("**Meilensteine:**")
        for milestone in phase.get("milestones", []):
            lines.append(f"- ☐ {milestone}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*Bericht generiert am {datetime.utcnow().strftime('%d.%m.%Y um %H:%M UTC')}*")

    return "\n".join(lines)
