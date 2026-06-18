from fastapi import APIRouter, HTTPException
from backend.services.domain_service import get_trending_domains, get_domain_details
from backend.models.domain import TrendingDomain

router = APIRouter(prefix="/domains", tags=["domains"])


@router.get("/trending", response_model=list[TrendingDomain])
async def get_trending():
    """
    Get top 10 trending business domains in Germany with low competition.

    Returns:
        List of TrendingDomain objects sorted by composite score
    """
    try:
        domains = get_trending_domains(limit=10)
        return domains
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending domains: {str(e)}")


@router.get("/{slug}/details")
async def get_domain_details_route(slug: str):
    """
    Get detailed information about a specific domain.

    Args:
        slug: Domain slug identifier

    Returns:
        Domain details including market data, legal requirements, etc.
    """
    try:
        details = get_domain_details(slug)
        if not details:
            raise HTTPException(status_code=404, detail="Domain not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching domain details: {str(e)}")
