import requests
from backend.data.cache import get, set
from backend.core.config import CACHE_TTL


BASE_URL = "https://api.worldbank.org/v2/country"


def get_gdp_growth(country: str = "DE", last_n_years: int = 5) -> list:
    """
    Get GDP growth rate for the last N years.

    Args:
        country: Country code (default 'DE' for Germany)
        last_n_years: Number of years to fetch

    Returns:
        List of dicts with {year, value}
    """
    return _fetch_indicator(country, "NY.GDP.MKTP.KD.ZG", last_n_years)


def get_gni_per_capita(country: str = "DE", last_n_years: int = 5) -> list:
    """Get Gross National Income per capita."""
    return _fetch_indicator(country, "NY.GNP.PCAP.CD", last_n_years)


def get_inflation(country: str = "DE", last_n_years: int = 5) -> list:
    """Get inflation rate (Consumer Price Index annual %)."""
    return _fetch_indicator(country, "FP.CPI.TOTL.ZG", last_n_years)


def get_ease_of_business(country: str = "DE") -> dict:
    """Get Ease of Doing Business ranking."""
    return _fetch_single_indicator(country, "IC.BUS.EASE.XQ")


def _fetch_indicator(country: str, indicator: str, last_n_years: int) -> list:
    """
    Fetch time series data for an indicator.

    Returns:
        List of dicts with {year, value}
    """
    cache_key = f"{country}_{indicator}"
    cached = get("world_bank", cache_key, CACHE_TTL["world_bank"])
    if cached:
        return cached

    try:
        url = f"{BASE_URL}/{country}/indicator/{indicator}"
        params = {
            "format": "json",
            "per_page": 100,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if len(data) < 2:
            return []

        result = []
        for entry in data[1]:
            try:
                year = int(entry.get("date", "0"))
                value = float(entry.get("value", 0)) if entry.get("value") else 0
                result.append({"year": year, "value": value})
            except (ValueError, TypeError):
                pass

        # Sort by year descending, take last N years
        result = sorted(result, key=lambda x: x["year"], reverse=True)[:last_n_years]
        result = sorted(result, key=lambda x: x["year"])  # Re-sort ascending for display

        set("world_bank", cache_key, result, CACHE_TTL["world_bank"])
        return result
    except Exception as e:
        print(f"Error fetching World Bank indicator {indicator}: {e}")
        return []


def _fetch_single_indicator(country: str, indicator: str) -> dict:
    """Fetch single value indicator."""
    cache_key = f"{country}_{indicator}_single"
    cached = get("world_bank", cache_key, CACHE_TTL["world_bank"])
    if cached:
        return cached

    try:
        url = f"{BASE_URL}/{country}/indicator/{indicator}"
        params = {
            "format": "json",
            "per_page": 5,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if len(data) < 2 or not data[1]:
            return {}

        entry = data[1][0]
        result = {
            "year": entry.get("date"),
            "value": float(entry.get("value")) if entry.get("value") else 0,
        }

        set("world_bank", cache_key, result, CACHE_TTL["world_bank"])
        return result
    except Exception as e:
        print(f"Error fetching World Bank indicator {indicator}: {e}")
        return {}
