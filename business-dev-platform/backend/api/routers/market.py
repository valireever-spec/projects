from fastapi import APIRouter, HTTPException, Query
from backend.services.market_service import (
    get_full_market_analysis,
    get_market_trends,
    get_competitor_landscape,
)

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/analysis")
async def get_market_analysis(
    domain: str = Query(..., description="Domain slug (e.g., 'online-ernaehrungsberatung')"),
    city: str = Query("Berlin", description="German city name"),
):
    """
    Get comprehensive market analysis for a domain in a city.

    Returns:
        Dict with TAM/SAM/SOM, competition level, trends, news, regulations
    """
    try:
        analysis = get_full_market_analysis(domain, city)
        if not analysis:
            raise HTTPException(status_code=404, detail="Domain or analysis not found")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing market: {str(e)}")


@router.get("/trends")
async def get_trends(
    domain: str = Query(..., description="Domain slug"),
):
    """
    Get market trend data for a domain.

    Returns:
        Dict with keywords, industry summary, trend indicators
    """
    try:
        trends = get_market_trends(domain)
        if not trends:
            raise HTTPException(status_code=404, detail="Trends not found")
        return trends
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trends: {str(e)}")


@router.get("/competitors")
async def get_competitors(
    domain: str = Query(..., description="Domain slug"),
    city: str = Query("Berlin", description="City name"),
):
    """
    Get competitor landscape analysis.

    Returns:
        Dict with competitor names, competition level, differentiation ideas
    """
    try:
        landscape = get_competitor_landscape(domain, city)
        if not landscape:
            raise HTTPException(status_code=404, detail="Competitor analysis not found")
        return landscape
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing competitors: {str(e)}")
