"""Generate professional HTML reports from business plan data using Jinja2."""
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


def render_html_report(plan: dict) -> str:
    """
    Render a complete business plan as HTML using Jinja2 template.

    Args:
        plan: Dict from plan_service.assemble_plan()

    Returns:
        Professional HTML string ready for browser display/printing to PDF
    """
    # Setup Jinja2 environment
    template_dir = Path(__file__).parent.parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))

    # Load template
    template = env.get_template("business_plan.html.j2")

    # Prepare context for template
    context = {
        "metadata": plan.get("metadata", {}),
        "generated_at": plan.get("generated_at", "N/A"),
        "executive_summary": plan.get("executive_summary", {}),
        "company_description": plan.get("company_description", {}),
        "market_analysis": plan.get("market_analysis", {}),
        "financial_plan": plan.get("financial_plan", {}),
        "risk_assessment": plan.get("risk_assessment", {}),
        "regulatory_requirements": plan.get("regulatory_requirements", {}),
        "competitive_advantages": plan.get("competitive_advantages", {}),
        "action_plan": plan.get("action_plan", {}),
    }

    # Render and return
    return template.render(context)
