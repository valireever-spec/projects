from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.services.financial_service import (
    get_financial_projections,
    compare_scenarios,
    estimate_funding_requirement,
    get_confidence_assessment,
    get_sensitivity_analysis,
)

router = APIRouter(prefix="/financials", tags=["financials"])


class FinancialProjectionRequest(BaseModel):
    session_id: str
    revenue_model: str  # subscription, hourly, product_sale, commission, hybrid
    monthly_revenue_estimate: float


@router.post("/project")
async def project_financials(request: FinancialProjectionRequest):
    """
    Calculate 36-month financial projections.

    Returns:
        Complete financial model with:
        - Startup costs breakdown
        - 36-month P&L (year 1: monthly, years 2-3: quarterly)
        - Break-even analysis
        - 3 scenarios (conservative/base/optimistic)
        - Key metrics (payback period, margins, etc.)
    """
    try:
        projections = get_financial_projections(
            session_id=request.session_id,
            revenue_model=request.revenue_model,
            monthly_revenue=request.monthly_revenue_estimate,
        )

        if not projections:
            raise HTTPException(status_code=404, detail="Could not generate projections")

        return projections
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating projections: {str(e)}")


@router.get("/{session_id}/summary")
async def get_financial_summary(
    session_id: str,
    revenue_model: str = Query(...),
    monthly_revenue: float = Query(...),
):
    """
    Get financial summary (key metrics only, not full projections).

    Returns:
        Dict with year_1, year_3, payback period, etc.
    """
    try:
        projections = get_financial_projections(session_id, revenue_model, monthly_revenue)

        if not projections:
            raise HTTPException(status_code=404, detail="Summary not found")

        return {
            "startup_costs_total": projections.get("startup_costs", {}).get("total", 0),
            "break_even_month": projections.get("break_even_month", 0),
            "key_metrics": projections.get("key_metrics", {}),
            "scenarios": projections.get("scenarios", {}),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/{session_id}/scenarios")
async def compare_financial_scenarios(
    session_id: str,
    revenue_model: str = Query(...),
    monthly_revenue: float = Query(...),
):
    """
    Compare conservative vs base vs optimistic scenarios.

    Returns:
        Side-by-side comparison with recommendation
    """
    try:
        comparison = compare_scenarios(session_id, revenue_model, monthly_revenue)

        if not comparison:
            raise HTTPException(status_code=404, detail="Scenarios not found")

        return comparison
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing scenarios: {str(e)}")


@router.get("/{session_id}/funding")
async def get_funding_requirement(
    session_id: str,
    revenue_model: str = Query(...),
    monthly_revenue: float = Query(...),
):
    """
    Estimate funding requirement to reach profitability.

    Returns:
        Funding analysis with total requirement and breakdown
    """
    try:
        funding = estimate_funding_requirement(session_id, revenue_model, monthly_revenue)

        if not funding:
            raise HTTPException(status_code=404, detail="Funding analysis not found")

        return funding
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing funding: {str(e)}")


@router.get("/{session_id}/confidence")
async def get_projection_confidence(
    session_id: str,
    revenue_model: str = Query(...),
    monthly_revenue: float = Query(...),
):
    """
    Get confidence score for financial projections.

    Returns:
        {
            "confidence_score": 72,
            "confidence_tier": "medium",
            "confidence_band_pct": 25,
            "drivers": [...],
            "warnings": [...]
        }
    """
    try:
        confidence = get_confidence_assessment(session_id, revenue_model, monthly_revenue)

        if not confidence:
            raise HTTPException(status_code=404, detail="Confidence assessment not found")

        return confidence
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing confidence: {str(e)}")


@router.get("/{session_id}/sensitivity")
async def get_sensitivity_analysis_endpoint(
    session_id: str,
    revenue_model: str = Query(...),
    monthly_revenue: float = Query(...),
):
    """
    Get sensitivity analysis for financial projections.

    Returns:
        {
            "sensitivity_matrix": {
                "revenue_variance": [...],
                "cost_variance": [...],
                "margin_variance": [...]
            },
            "key_driver": "revenue",
            "impact_ranking": [...]
        }
    """
    try:
        sensitivity = get_sensitivity_analysis(session_id, revenue_model, monthly_revenue)

        if not sensitivity:
            raise HTTPException(status_code=404, detail="Sensitivity analysis not found")

        return sensitivity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sensitivity: {str(e)}")
