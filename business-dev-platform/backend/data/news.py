import requests
from backend.data.cache import get, set
from backend.core.config import CACHE_TTL, NEWSAPI_KEY


BASE_URL = "https://newsapi.org/v2"


def search_industry_news(
    query: str,
    language: str = "de",
    page_size: int = 10,
    sort_by: str = "publishedAt"
) -> list[dict]:
    """
    Search for news articles about an industry or topic.

    Args:
        query: Search query (e.g., 'Ernährungsberatung', 'Social Media Marketing')
        language: Language code (default 'de' for German)
        page_size: Number of articles to return (max 100)
        sort_by: Sort order ('publishedAt', 'relevancy', 'popularity')

    Returns:
        List of article dicts with {title, description, url, source, publishedAt, image}
        Returns empty list if API key not configured or error occurs
    """
    if not NEWSAPI_KEY:
        return []

    cache_key = f"{query}_{language}"
    cached = get("news", cache_key, CACHE_TTL["news"])
    if cached:
        return cached

    try:
        params = {
            "q": query,
            "language": language,
            "pageSize": min(page_size, 100),
            "sortBy": sort_by,
            "apiKey": NEWSAPI_KEY,
        }

        response = requests.get(
            f"{BASE_URL}/everything",
            params=params,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()

        articles = []
        if data.get("status") == "ok":
            for article in data.get("articles", [])[:page_size]:
                articles.append({
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "url": article.get("url"),
                    "source": article.get("source", {}).get("name"),
                    "publishedAt": article.get("publishedAt"),
                    "image": article.get("urlToImage"),
                })

        set("news", cache_key, articles, CACHE_TTL["news"])
        return articles
    except Exception as e:
        print(f"Warning: Error fetching news: {e}")
        return []


def get_top_headlines(
    country: str = "de",
    category: str = "business",
    page_size: int = 5
) -> list[dict]:
    """
    Get top headlines for a country and category.

    Args:
        country: Country code (default 'de' for Germany)
        category: Category (business, technology, etc.)
        page_size: Number of headlines to return

    Returns:
        List of headline dicts
    """
    if not NEWSAPI_KEY:
        return []

    cache_key = f"headlines_{country}_{category}"
    cached = get("news", cache_key, CACHE_TTL["news"])
    if cached:
        return cached

    try:
        params = {
            "country": country,
            "category": category,
            "pageSize": min(page_size, 100),
            "apiKey": NEWSAPI_KEY,
        }

        response = requests.get(
            f"{BASE_URL}/top-headlines",
            params=params,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()

        headlines = []
        if data.get("status") == "ok":
            for article in data.get("articles", [])[:page_size]:
                headlines.append({
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "url": article.get("url"),
                    "source": article.get("source", {}).get("name"),
                    "publishedAt": article.get("publishedAt"),
                    "image": article.get("urlToImage"),
                })

        set("news", cache_key, headlines, CACHE_TTL["news"])
        return headlines
    except Exception as e:
        print(f"Warning: Error fetching headlines: {e}")
        return []
