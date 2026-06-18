import json
from pathlib import Path
from backend.core.config import DATA_DIR
from backend.data.cache import get, set
from backend.core.config import CACHE_TTL
from backend.analytics.domain_scorer import score_domains as score_domains_func
from backend.models.domain import TrendingDomain


def get_trending_domains(limit: int = 10) -> list[TrendingDomain]:
    """
    Get top trending domains with low competition.

    Returns:
        List of TrendingDomain objects sorted by score (highest first)
    """
    # Try to load from cache
    cached = get("domain_service", "trending_domains", CACHE_TTL["google_trends"])
    if cached:
        return [TrendingDomain(**item) for item in cached]

    try:
        # Load seed data
        domain_data = _load_domain_data()

        # Prepare data for scoring
        trend_data = _prepare_trend_data(domain_data)
        sector_stats = _prepare_sector_stats(domain_data)
        registrations = _prepare_registrations(domain_data)

        # Score domains
        scored = score_domains_func(domain_data, trend_data, sector_stats, registrations)

        # Convert to TrendingDomain models
        trending_domains = []
        for score in scored[:limit]:
            domain_dict = next(
                (d for d in domain_data if d.get("slug") == score.slug), {}
            )

            trending_domain = TrendingDomain(
                slug=score.slug,
                name_de=score.name_de,
                name_en=score.name_en,
                composite_score=score.composite_score,
                grade=score.grade,
                nace_code=domain_dict.get("nace_r2_code", ""),
                trend_momentum=score.trend_momentum,
                market_growth=score.market_growth,
                competition_density=score.competition_density,
                registration_momentum=score.registration_momentum,
                market_size_estimate="€2-5M" if score.market_growth > 15 else "€1-2M",
                trend_sparkline=None,  # TODO: from Google Trends
                wikipedia_summary=None,  # TODO: from Wikipedia API
                top_news=None,  # TODO: from News API
            )
            trending_domains.append(trending_domain)

        # Cache the results
        cache_data = [domain.model_dump() for domain in trending_domains]
        set("domain_service", "trending_domains", cache_data, CACHE_TTL["google_trends"])

        return trending_domains
    except Exception as e:
        print(f"Error getting trending domains: {e}")
        return []


def get_domain_details(slug: str) -> dict | None:
    """Get detailed information about a specific domain."""
    try:
        domain_data = _load_domain_data()
        domain = next((d for d in domain_data if d.get("slug") == slug), None)

        if not domain:
            return None

        return {
            "slug": domain.get("slug"),
            "name_de": domain.get("name_de"),
            "name_en": domain.get("name_en"),
            "nace_code": domain.get("nace_r2_code"),
            "legal_forms": domain.get("typical_legal_forms", []),
            "required_licenses": domain.get("required_licenses", []),
            "sector_margins": domain.get("sector_margins", {}),
            "city_wage_indices": domain.get("city_wage_indices", {}),
        }
    except Exception as e:
        print(f"Error getting domain details: {e}")
        return None


def _load_domain_data() -> list[dict]:
    """Load german_domains.json seed data."""
    try:
        domain_file = DATA_DIR / "german_domains.json"
        if domain_file.exists():
            with open(domain_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading domain data: {e}")

    return []


def _prepare_trend_data(domain_data: list) -> dict:
    """
    Prepare trend data for scoring.

    Returns: {slug: trend_score, ...}
    """
    # TODO: Fetch from Google Trends API
    # For now, return default values
    trend_data = {}
    for domain in domain_data:
        slug = domain.get("slug")
        # Default: all domains start with interest of 50/100
        trend_data[slug] = 50

    return trend_data


def _prepare_sector_stats(domain_data: list) -> dict:
    """
    Prepare sector statistics for scoring.

    Returns: {nace_code: {growth_rate, enterprise_count, ...}, ...}
    """
    # TODO: Fetch from Eurostat API
    # For now, return default estimates
    sector_stats = {}
    for domain in domain_data:
        nace_code = domain.get("nace_r2_code")
        sector_stats[nace_code] = {
            "growth_rate": 0.08,  # Default 8% annual growth
            "enterprise_count": 5000,  # Default estimate
        }

    return sector_stats


def _prepare_registrations(domain_data: list) -> dict:
    """
    Prepare business registration data for scoring.

    Returns: {nace_code: [{registrations}, ...], ...}
    """
    # TODO: Fetch from Eurostat API
    # For now, return empty (will use default in scorer)
    return {}
