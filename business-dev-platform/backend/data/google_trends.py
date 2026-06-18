from pytrends.request import TrendReq
from backend.data.cache import get, set
from backend.core.config import CACHE_TTL


def get_trending_searches(geo: str = "DE", language: str = "de") -> list[str]:
    """
    Fetch daily trending searches in a country.

    Args:
        geo: Geographic code (default 'DE' for Germany)
        language: Language code (default 'de' for German)

    Returns:
        List of trending search queries
    """
    cache_key = f"{geo}_{language}_trending"
    cached = get("google_trends", cache_key, CACHE_TTL["google_trends"])
    if cached:
        return cached

    try:
        pytrends = TrendReq(hl=language, tz=0)
        trending_searches = pytrends.trending_searches(pn=geo)

        # Convert DataFrame to list of strings
        results = trending_searches.values.flatten().tolist() if trending_searches is not None else []

        set("google_trends", cache_key, results, CACHE_TTL["google_trends"])
        return results
    except Exception as e:
        print(f"Warning: Error fetching Google Trends: {e}. Using empty list.")
        return []


def get_interest_over_time(keywords: list[str], geo: str = "DE", timeframe: str = "today 12-m") -> dict:
    """
    Get interest over time for keywords over the past 12 months.

    Args:
        keywords: List of keywords to track
        geo: Geographic code
        timeframe: Time range (default 'today 12-m' for last 12 months)

    Returns:
        Dict with {keyword: [values_over_time]} or empty dict on error
    """
    if not keywords:
        return {}

    cache_key = f"{geo}_{'_'.join(keywords[:3])}_interest"
    cached = get("google_trends", cache_key, CACHE_TTL["google_trends"])
    if cached:
        return cached

    try:
        pytrends = TrendReq(hl="de", tz=0)

        # Limit to 5 keywords (Google Trends API limit)
        keywords_to_fetch = keywords[:5]

        pytrends.build_payload(
            kw_list=keywords_to_fetch,
            cat=0,
            timeframe=timeframe,
            geo=geo,
            gprop=""
        )

        interest_data = pytrends.interest_over_time()

        if interest_data.empty:
            return {}

        # Convert to dict format
        result = {}
        for keyword in keywords_to_fetch:
            if keyword in interest_data.columns:
                result[keyword] = interest_data[keyword].tolist()

        set("google_trends", cache_key, result, CACHE_TTL["google_trends"])
        return result
    except Exception as e:
        print(f"Warning: Error fetching interest over time: {e}")
        return {}


def get_related_queries(keyword: str, geo: str = "DE") -> dict:
    """
    Get related and rising queries for a keyword.

    Args:
        keyword: Keyword to analyze
        geo: Geographic code

    Returns:
        Dict with {top_related: [...], rising_related: [...]}
    """
    cache_key = f"{geo}_{keyword}_related"
    cached = get("google_trends", cache_key, CACHE_TTL["google_trends"])
    if cached:
        return cached

    try:
        pytrends = TrendReq(hl="de", tz=0)
        pytrends.build_payload(
            kw_list=[keyword],
            cat=0,
            timeframe="today 12-m",
            geo=geo,
            gprop=""
        )

        related_queries = pytrends.related_queries()

        result = {
            "top_related": [],
            "rising_related": [],
        }

        if keyword in related_queries:
            queries_data = related_queries[keyword]

            # Top related queries
            if queries_data["top"] is not None:
                result["top_related"] = queries_data["top"]["query"].tolist()[:5]

            # Rising related queries
            if queries_data["rising"] is not None:
                result["rising_related"] = queries_data["rising"]["query"].tolist()[:5]

        set("google_trends", cache_key, result, CACHE_TTL["google_trends"])
        return result
    except Exception as e:
        print(f"Warning: Error fetching related queries: {e}")
        return {"top_related": [], "rising_related": []}


def calculate_trend_momentum(interest_data: dict, keyword: str) -> float:
    """
    Calculate trend momentum as a score 0-100 based on interest trajectory.

    Args:
        interest_data: Dict from get_interest_over_time()
        keyword: Keyword to analyze

    Returns:
        Momentum score 0-100 (0 = declining, 100 = rapidly growing)
    """
    if keyword not in interest_data or not interest_data[keyword]:
        return 50  # Default neutral

    values = interest_data[keyword]

    if len(values) < 2:
        return 50

    # Calculate slope: (last_3_months - first_3_months) / first_3_months
    first_third = sum(values[:len(values)//3]) / max(len(values)//3, 1)
    last_third = sum(values[-len(values)//3:]) / max(len(values)//3, 1)

    if first_third == 0:
        return 50

    growth_rate = (last_third - first_third) / first_third

    # Map growth rate to 0-100 scale
    # -100% decline = 0, 0% flat = 50, +100% growth = 100
    momentum = 50 + (growth_rate * 50)
    return max(0, min(100, momentum))
