from fastapi import APIRouter, HTTPException, Query
from backend.services.domain_service import (
    get_trending_domains,
    get_domain_details,
    get_matched_domains,
)
from backend.models.domain import TrendingDomain, FounderProfile, MatchedDomain

router = APIRouter(prefix="/domains", tags=["domains"])


@router.post("/matched", response_model=list[MatchedDomain])
async def get_matched(profile: FounderProfile, limit: int = Query(10, ge=1, le=40)):
    """
    Rank business domains by fit to the founder's edge (skills, channels,
    constraints) rather than raw market heat. This is the edge-first intake:
    market attractiveness is only a small tiebreaker.
    """
    try:
        return get_matched_domains(profile.model_dump(), limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching domains: {str(e)}")


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
