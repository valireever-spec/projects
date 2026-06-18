from backend.data.cache import get, set
from backend.core.config import CACHE_TTL
from backend.data import eurostat, world_bank, ecb, news, wikipedia
from backend.analytics.market_sizer import estimate_market_size
from backend.analytics.competitor_analyzer import analyze_competition
from backend.services.domain_service import get_domain_details
import json


def get_full_market_analysis(domain_slug: str, city: str) -> dict:
    """
    Get comprehensive market analysis for a domain in a specific city.

    Args:
        domain_slug: Domain identifier (e.g., 'online-ernaehrungsberatung')
        city: German city name (e.g., 'Berlin')

    Returns:
        Comprehensive market analysis dict
    """
    # Try cache
    cache_key = f"{domain_slug}_{city}_full_analysis"
    cached = get("market_service", cache_key, CACHE_TTL["google_trends"])
    if cached:
        return cached

    try:
        # Get domain details
        domain_details = get_domain_details(domain_slug)
        if not domain_details:
            return {}

        nace_code = domain_details.get("nace_code", "")

        # Fetch all data sources in parallel (simulated sequentially)
        # Eurostat: sector statistics
        sector_stats = eurostat.get_sector_stats(nace_code) if nace_code else {}

        # World Bank: macro data
        gdp_growth = world_bank.get_gdp_growth()
        inflation = world_bank.get_inflation()

        # ECB: inflation data
        hicp = ecb.get_hicp_inflation()

        # Extract macro metrics
        gdp_data = {
            "gdp_growth": (gdp_growth[-1]["value"] / 100) if gdp_growth else 0.02,
            "inflation": (inflation[-1]["value"] / 100) if inflation else 0.025,
        }

        # News: industry news
        industry_news = news.search_industry_news(
            domain_details.get("name_de", domain_slug),
            language="de",
            page_size=10
        )

        # Wikipedia: industry background
        wiki_summary = wikipedia.get_article_summary(
            domain_details.get("name_de", domain_slug),
            lang="de"
        )

        # Get city population (estimate or lookup)
        city_population = _get_city_population(city)

        # Market sizing
        market_data = estimate_market_size(
            sector_stats,
            gdp_data,
            city_population
        )

        # Competition analysis
        competition_data = analyze_competition(
            industry_news,
            wiki_summary,
            [],  # registrations_data
            nace_code
        )

        # Assemble full analysis
        analysis = {
            "domain_slug": domain_slug,
            "domain_name": domain_details.get("name_de", ""),
            "city": city,
            "city_population": city_population,

            # Market data
            "market": {
                "tam_eur": market_data.get("tam_eur", 0),
                "sam_eur": market_data.get("sam_eur", 0),
                "som_eur": market_data.get("som_eur", 0),
                "growth_rate_pct": market_data.get("growth_rate_pct", 0),
                "maturity": market_data.get("market_maturity", "unknown"),
                "market_size_estimate": market_data.get("market_size_estimate", ""),
                "city_market_estimate": market_data.get("city_market_estimate", ""),
            },

            # Competition
            "competition": {
                "level": competition_data.get("competition_level", "medium"),
                "intensity_score": competition_data.get("intensity_score", 50),
                "key_players": competition_data.get("key_players", []),
                "barriers_to_entry": competition_data.get("barriers_to_entry", []),
                "differentiation_opportunities": competition_data.get("differentiation_opportunities", []),
                "trends": competition_data.get("market_trends", []),
            },

            # News and insights
            "news": {
                "recent_articles": industry_news[:5],
                "article_count": len(industry_news),
            },

            # Wikipedia summary
            "industry_background": wiki_summary[:500] if wiki_summary else "",

            # Macro environment
            "macro": {
                "gdp_growth_pct": gdp_data.get("gdp_growth", 0) * 100,
                "inflation_pct": gdp_data.get("inflation", 0) * 100,
            },

            # Legal requirements
            "legal_forms": domain_details.get("typical_legal_forms", []),
            "required_licenses": domain_details.get("required_licenses", []),
            "sector_margins": domain_details.get("sector_margins", {}),
            "city_wage_index": domain_details.get("city_wage_indices", {}).get(city, 1.0),
        }

        # Cache the analysis
        set("market_service", cache_key, analysis, CACHE_TTL["google_trends"])

        return analysis
    except Exception as e:
        print(f"Error getting market analysis: {e}")
        return {}


def get_market_trends(domain_slug: str) -> dict:
    """Get market trend data for a domain."""
    cache_key = f"{domain_slug}_trends"
    cached = get("market_service", cache_key, CACHE_TTL["google_trends"])
    if cached:
        return cached

    try:
        domain_details = get_domain_details(domain_slug)
        if not domain_details:
            return {}

        # Get Wikipedia article summary for trend keywords
        wiki_text = wikipedia.get_article_summary(
            domain_details.get("name_de", ""),
            lang="de"
        )

        # Extract keywords from Wikipedia (simple frequency analysis)
        keywords = wikipedia.extract_keywords_from_text(wiki_text, limit=5)

        result = {
            "domain_slug": domain_slug,
            "keywords": keywords,
            "industry_summary": wiki_text[:300],
        }

        set("market_service", cache_key, result, CACHE_TTL["google_trends"])
        return result
    except Exception as e:
        print(f"Error getting market trends: {e}")
        return {}


def get_competitor_landscape(domain_slug: str, city: str) -> dict:
    """Get detailed competitor landscape analysis."""
    cache_key = f"{domain_slug}_{city}_competitors"
    cached = get("market_service", cache_key, CACHE_TTL["google_trends"])
    if cached:
        return cached

    try:
        domain_details = get_domain_details(domain_slug)
        if not domain_details:
            return {}

        nace_code = domain_details.get("nace_code", "")

        # Fetch news and Wikipedia data
        industry_news = news.search_industry_news(
            domain_details.get("name_de", ""),
            language="de",
            page_size=15
        )

        wiki_text = wikipedia.get_article_summary(
            domain_details.get("name_de", ""),
            lang="de"
        )

        # Analyze competition
        competition = analyze_competition(
            industry_news,
            wiki_text,
            [],
            nace_code
        )

        result = {
            "domain_slug": domain_slug,
            "city": city,
            "competition_analysis": competition,
            "recent_news_count": len(industry_news),
            "market_dynamics": {
                "barriers_to_entry": competition.get("barriers_to_entry", []),
                "differentiation_options": competition.get("differentiation_opportunities", []),
                "market_trends": competition.get("market_trends", []),
            }
        }

        set("market_service", cache_key, result, CACHE_TTL["google_trends"])
        return result
    except Exception as e:
        print(f"Error analyzing competitor landscape: {e}")
        return {}


def _get_city_population(city: str) -> int:
    """Get population for a German city (hardcoded lookup)."""
    city_populations = {
        "Berlin": 3_645_000,
        "Munich": 1_472_000,
        "Hamburg": 1_852_000,
        "Frankfurt": 753_000,
        "Cologne": 1_086_000,
        "Dresden": 559_000,
        "Düsseldorf": 621_000,
        "Stuttgart": 623_000,
        "Bonn": 327_000,
        "Mannheim": 309_000,
        "Nuremberg": 518_000,
        "Wuppertal": 354_000,
        "Bielefeld": 333_000,
        "Bremen": 569_000,
        "Hanover": 543_000,
        "Augsburg": 298_000,
        "Aachen": 259_000,
        "Leipzig": 597_000,
    }

    return city_populations.get(city, 300_000)  # Default estimate
