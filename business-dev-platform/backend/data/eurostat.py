import requests
from backend.data.cache import get, set
from backend.core.config import CACHE_TTL


BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def get_sector_stats(nace_code: str, geo: str = "DE", year: int = 2022) -> dict:
    """
    Get Structural Business Statistics for a sector.

    Args:
        nace_code: NACE revision 2 code (e.g., '86.90' for other professional activities)
        geo: Geographic code (default 'DE' for Germany)
        year: Statistical year

    Returns:
        Dict with enterprise_count, turnover, employment, or empty if unavailable
    """
    cache_key = f"{geo}_{nace_code}_{year}"
    cached = get("eurostat", cache_key, CACHE_TTL["eurostat"])
    if cached:
        return cached

    try:
        # Structural Business Statistics (SBS) - turnover by NACE
        params = {
            "filter": f"nace_r2:{nace_code},geo:{geo},time:{year}",
            "format": "JSON",
        }

        response = requests.get(
            f"{BASE_URL}/sbs_sc_sca_r2",
            params=params,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        result = _parse_eurostat_response(data)

        set("eurostat", cache_key, result, CACHE_TTL["eurostat"])
        return result
    except Exception as e:
        print(f"Error fetching Eurostat sector stats: {e}")
        return {}


def get_business_registrations(geo: str = "DE", last_n_years: int = 3) -> list:
    """
    Get new business registrations trend.

    Args:
        geo: Geographic code
        last_n_years: Number of years to fetch

    Returns:
        List of dicts with {year, quarter, registrations}
    """
    cache_key = f"{geo}_registrations_{last_n_years}"
    cached = get("eurostat", cache_key, CACHE_TTL["eurostat"])
    if cached:
        return cached

    try:
        # New business registrations dataset
        params = {
            "filter": f"geo:{geo}",
            "format": "JSON",
        }

        response = requests.get(
            f"{BASE_URL}/tin00138",
            params=params,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        result = _parse_registrations_response(data, last_n_years)

        set("eurostat", cache_key, result, CACHE_TTL["eurostat"])
        return result
    except Exception as e:
        print(f"Error fetching Eurostat registrations: {e}")
        return []


def _parse_eurostat_response(data: dict) -> dict:
    """Parse Eurostat JSON response."""
    try:
        if "value" not in data or "dimension" not in data:
            return {}

        values = data.get("value", {})
        dimensions = data.get("dimension", {})

        # Extract first available value
        if values:
            first_key = next(iter(values.keys()))
            value = float(values[first_key])
        else:
            value = 0

        return {
            "turnover": value if value else 0,
            "enterprise_count": 0,  # Placeholder
            "employment": 0,         # Placeholder
            "data_available": bool(values),
        }
    except (KeyError, ValueError, StopIteration):
        return {
            "turnover": 0,
            "enterprise_count": 0,
            "employment": 0,
            "data_available": False,
        }


def _parse_registrations_response(data: dict, last_n_years: int) -> list:
    """Parse Eurostat new business registrations response."""
    try:
        if "value" not in data:
            return []

        values = data.get("value", {})
        result = []

        for key, value in list(values.items())[-last_n_years * 4:]:
            try:
                result.append({
                    "period": key,
                    "registrations": float(value),
                })
            except (ValueError, TypeError):
                pass

        return result
    except Exception:
        return []
