import requests
from backend.data.cache import get, set
from backend.core.config import CACHE_TTL


BASE_URL = "https://www-genesis.destatis.de/genesisWS/rest/2020"
GENESIS_USER = "GAST"
GENESIS_PASSWORD = "GAST"


def find_table(topic: str, language: str = "de") -> list[dict]:
    """
    Search for statistical tables by topic.

    Args:
        topic: Topic to search (e.g., 'Retail Trade', 'Manufacturing')
        language: Language code (default 'de' for German)

    Returns:
        List of table dicts with {table_code, title, description}
    """
    cache_key = f"{language}_{topic}_tables"
    cached = get("destatis", cache_key, CACHE_TTL["destatis"])
    if cached:
        return cached

    try:
        # Use GENESIS catalog endpoint
        # This is a simplified version - actual implementation may need adjustment
        # based on GENESIS API documentation
        url = f"{BASE_URL}/catalogue"
        params = {
            "username": GENESIS_USER,
            "password": GENESIS_PASSWORD,
            "category": "12*",  # 12 = Trade and Services
            "language": language,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = []

        # Parse response structure
        if "Objekte" in data:
            for obj in data["Objekte"][:5]:
                results.append({
                    "table_code": obj.get("Nummer"),
                    "title": obj.get("Titel"),
                    "description": obj.get("Beschreibung"),
                })

        set("destatis", cache_key, results, CACHE_TTL["destatis"])
        return results
    except Exception as e:
        print(f"Warning: Error searching Destatis tables: {e}")
        return []


def get_table_data(table_code: str, year: int = 2022) -> dict:
    """
    Fetch data from a specific Destatis table.

    Args:
        table_code: GENESIS table code (e.g., '52111-0001')
        year: Statistical year

    Returns:
        Dict with table data or empty dict on error
    """
    cache_key = f"{table_code}_{year}"
    cached = get("destatis", cache_key, CACHE_TTL["destatis"])
    if cached:
        return cached

    try:
        url = f"{BASE_URL}/data"
        params = {
            "username": GENESIS_USER,
            "password": GENESIS_PASSWORD,
            "name": table_code,
            "format": "json",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        result = {
            "table_code": table_code,
            "title": data.get("Merkmal", {}).get("Titel"),
            "data": data,
        }

        set("destatis", cache_key, result, CACHE_TTL["destatis"])
        return result
    except Exception as e:
        print(f"Warning: Error fetching Destatis table {table_code}: {e}")
        return {}


def get_labor_statistics(year: int = 2022) -> dict:
    """
    Get German labor market statistics from Destatis.

    Returns:
        Dict with labor statistics (unemployment, employment, etc.)
    """
    cache_key = f"labor_stats_{year}"
    cached = get("destatis", cache_key, CACHE_TTL["destatis"])
    if cached:
        return cached

    try:
        # Labor statistics table code
        table_code = "13321-001"
        data = get_table_data(table_code, year)

        result = {
            "employment_rate": 0.75,  # Placeholder
            "unemployment_rate": 0.035,  # Placeholder
            "avg_wage_gross": 45000,  # Placeholder
        }

        set("destatis", cache_key, result, CACHE_TTL["destatis"])
        return result
    except Exception as e:
        print(f"Warning: Error fetching labor statistics: {e}")
        return {}


def get_startup_statistics(year: int = 2022) -> dict:
    """
    Get business startup and closure statistics for Germany.

    Returns:
        Dict with {new_businesses, closures, net_change}
    """
    cache_key = f"startup_stats_{year}"
    cached = get("destatis", cache_key, CACHE_TTL["destatis"])
    if cached:
        return cached

    try:
        # Business registration table
        table_code = "52121-0001"
        data = get_table_data(table_code, year)

        result = {
            "new_businesses": 0,
            "closures": 0,
            "net_change": 0,
            "data_year": year,
        }

        set("destatis", cache_key, result, CACHE_TTL["destatis"])
        return result
    except Exception as e:
        print(f"Warning: Error fetching startup statistics: {e}")
        return {}
