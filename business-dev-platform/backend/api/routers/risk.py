import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from backend.core.config import SESSIONS_DIR
from backend.analytics.risk_scorer import assess_risks
from backend.analytics.regulatory import german_requirements

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/assess")
async def assess_business_risks(
    session_id: str = Query(...),
    domain: str = Query(...),
):
    """
    Assess business risks across 8 dimensions.

    Returns:
        Dict with {
            overall_risk_level: "low" | "medium" | "high",
            risk_score: 0-100,
            risk_factors: [8 risk dimensions],
            top_3_risks: [highest scoring risks],
            mitigation_plan: [key strategies]
        }
    """
    try:
        # Load session to get legal form
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if not session_file.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        with open(session_file, 'r') as f:
            session = json.load(f)

        profile = session.get("profile", {})
        legal_form = profile.get("legal_form", "Einzelunternehmen")
        city = profile.get("city", "Berlin")

        # Get financial projections if available
        financial_projection = session.get("financial_projection", {})

        # Assess risks
        risk_assessment = assess_risks(domain, legal_form, city, financial_projection)

        return risk_assessment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing risks: {str(e)}")


@router.get("/regulatory")
async def get_regulatory_requirements(
    domain: str = Query(...),
    legal_form: str = Query("Einzelunternehmen"),
):
    """
    Get German regulatory and compliance requirements.

    Returns:
        Dict with {
            requirements: [list of compliance items],
            total_estimated_cost: EUR,
            total_estimated_days: days to complete,
            grouped_by_category: {Registration, Taxes, Licenses, DSGVO, etc.},
            completion_checklist: [items with completed flag]
        }
    """
    try:
        reqs = german_requirements(domain, legal_form)

        return {
            "domain": domain,
            "legal_form": legal_form,
            "requirements": reqs.get("requirements", []),
            "total_estimated_cost": reqs.get("total_estimated_cost", 0),
            "total_estimated_days": reqs.get("total_estimated_days", 0),
            "grouped_by_category": reqs.get("grouped_by_category", {}),
            "completion_checklist": reqs.get("completion_checklist", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching requirements: {str(e)}")


@router.get("/summary")
async def get_risk_summary(
    session_id: str = Query(...),
    domain: str = Query(...),
):
    """
    Get consolidated risk and regulatory summary.

    Returns:
        Combined risk assessment + regulatory requirements
    """
    try:
        # Load session
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if not session_file.exists():
            raise HTTPException(status_code=404, detail="Session not found")

        with open(session_file, 'r') as f:
            session = json.load(f)

        profile = session.get("profile", {})
        legal_form = profile.get("legal_form", "Einzelunternehmen")
        city = profile.get("city", "Berlin")
        financial_projection = session.get("financial_projection", {})

        # Risk assessment
        risk_assessment = assess_risks(domain, legal_form, city, financial_projection)

        # Regulatory requirements
        reqs = german_requirements(domain, legal_form)

        return {
            "risk_assessment": risk_assessment,
            "regulatory_requirements": reqs,
            "overall_complexity": _calculate_overall_complexity(risk_assessment, reqs),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


def _calculate_overall_complexity(risk_assessment: dict, requirements: dict) -> str:
    """Assess overall business complexity."""
    risk_score = risk_assessment.get("risk_score", 10)
    req_cost = requirements.get("total_estimated_cost", 0)
    req_days = requirements.get("total_estimated_days", 0)

    # Combine metrics
    complexity_score = (risk_score * 0.5) + (min(req_cost / 1000, 5) * 0.3) + (min(req_days / 30, 5) * 0.2)

    if complexity_score < 6:
        return "einfach"
    elif complexity_score < 12:
        return "mittel"
    else:
        return "komplex"
