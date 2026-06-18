import requests
from backend.data.cache import get, set
from backend.core.config import CACHE_TTL


def search_articles(query: str, lang: str = "de", limit: int = 3) -> list[dict]:
    """
    Search Wikipedia for articles related to a query.

    Args:
        query: Search query (e.g., 'Ernährungsberatung')
        lang: Language code (default 'de' for German Wikipedia)
        limit: Number of results to return

    Returns:
        List of dicts with {title, snippet, url}
    """
    cache_key = f"{lang}_{query}_search"
    cached = get("wikipedia", cache_key, CACHE_TTL["wikipedia"])
    if cached:
        return cached

    try:
        # Use German Wikipedia if lang='de', else English
        base_url = f"https://{lang}.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "srnamespace": 0,
        }

        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = []

        for result in data.get("query", {}).get("search", [])[:limit]:
            results.append({
                "title": result.get("title"),
                "snippet": result.get("snippet"),
                "url": f"https://{lang}.wikipedia.org/wiki/{result.get('title', '').replace(' ', '_')}",
            })

        set("wikipedia", cache_key, results, CACHE_TTL["wikipedia"])
        return results
    except Exception as e:
        print(f"Warning: Error searching Wikipedia: {e}")
        return []


def get_article_extract(title: str, lang: str = "de", chars: int = 500) -> str:
    """
    Get a text extract from a Wikipedia article.

    Args:
        title: Article title
        lang: Language code
        chars: Number of characters to extract (max 1500)

    Returns:
        Article extract text or empty string on error
    """
    cache_key = f"{lang}_{title}_extract"
    cached = get("wikipedia", cache_key, CACHE_TTL["wikipedia"])
    if cached:
        return cached

    try:
        base_url = f"https://{lang}.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts",
            "explaintext": True,
            "exintro": True,
            "exlimit": 1,
            "exchars": min(chars, 1500),
        }

        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        pages = data.get("query", {}).get("pages", {})

        if pages:
            page_id = list(pages.keys())[0]
            extract = pages[page_id].get("extract", "")
            set("wikipedia", cache_key, extract, CACHE_TTL["wikipedia"])
            return extract

        return ""
    except Exception as e:
        print(f"Warning: Error fetching Wikipedia extract: {e}")
        return ""


def get_article_summary(query: str, lang: str = "de") -> str:
    """
    Get a summary of an article by searching and extracting.

    Args:
        query: Topic or article title to search for
        lang: Language code

    Returns:
        Combined summary text or empty string on error
    """
    try:
        # First, search for the article
        search_results = search_articles(query, lang=lang, limit=1)

        if not search_results:
            return ""

        title = search_results[0]["title"]

        # Then get the full extract
        extract = get_article_extract(title, lang=lang)

        return extract
    except Exception as e:
        print(f"Warning: Error getting article summary: {e}")
        return ""


def extract_keywords_from_text(text: str, limit: int = 10) -> list[str]:
    """
    Simple keyword extraction from Wikipedia text (word frequency).

    Args:
        text: Text to analyze
        limit: Number of keywords to return

    Returns:
        List of keywords sorted by frequency
    """
    if not text:
        return []

    # Simple word frequency analysis
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "up", "about", "into", "through", "during",
        "der", "die", "das", "und", "oder", "in", "zu", "mit", "von", "ist",
        "sich", "des", "dem", "den", "ihre", "ihr", "sein", "seine", "als"
    }

    words = text.lower().split()
    word_freq = {}

    for word in words:
        # Clean punctuation
        word = word.strip('.,!?;:-"\'')

        if len(word) > 3 and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and return top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:limit]]
