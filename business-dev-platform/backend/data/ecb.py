import requests
from backend.data.cache import get, set
from backend.core.config import CACHE_TTL


BASE_URL = "https://data-api.ecb.europa.eu/service/data"

# Fallback values if API is unavailable
FALLBACK_INFLATION = 2.8  # percent
FALLBACK_EURIBOR = 3.2    # percent
FALLBACK_POLICY_RATE = 4.0  # percent


def get_hicp_inflation(last_n_months: int = 12, country: str = "DE") -> list:
    """
    Get Harmonised Index of Consumer Prices (HICP) inflation data.

    Args:
        last_n_months: Number of months to fetch
        country: Country code (default 'DE' for Germany)

    Returns:
        List of dicts with {month, inflation_pct}
    """
    cache_key = f"{country}_hicp_{last_n_months}"
    cached = get("ecb", cache_key, CACHE_TTL["ecb"])
    if cached:
        return cached

    try:
        # HICP for Germany (series: ICP.M.DE.N.000000.4.ANR)
        url = f"{BASE_URL}/ICP/M.{country}.N.000000.4.ANR"
        params = {"format": "json"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        observations = data.get("observations", {})

        result = []
        for period, obs_list in list(observations.items())[-last_n_months:]:
            try:
                if obs_list:
                    value = float(obs_list[0].get("value", 0))
                    result.append({"period": period, "inflation_pct": value})
            except (ValueError, TypeError, IndexError):
                pass

        set("ecb", cache_key, result, CACHE_TTL["ecb"])
        return result
    except Exception as e:
        print(f"Warning: Error fetching ECB inflation data: {e}. Using fallback.")
        return [{"period": "latest", "inflation_pct": FALLBACK_INFLATION}]


def get_euribor_rate(tenor: str = "3M") -> float:
    """
    Get EURIBOR rate (Euro Interbank Offered Rate).

    Args:
        tenor: Rate tenor (default '3M' for 3-month)

    Returns:
        Float percentage rate
    """
    cache_key = f"euribor_{tenor}"
    cached = get("ecb", cache_key, CACHE_TTL["ecb"])
    if cached:
        return cached.get("rate", FALLBACK_EURIBOR)

    try:
        # EURIBOR series: EURIBOR3MD_
        url = f"{BASE_URL}/FM/M.U2.EUR.RT0.MM.EURIBOR{tenor}D_.HSTA"
        params = {"format": "json"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        observations = data.get("observations", {})

        if observations:
            last_period = max(observations.keys())
            last_obs = observations[last_period]
            if last_obs:
                value = float(last_obs[0].get("value", FALLBACK_EURIBOR))
                result = {"rate": value}
                set("ecb", cache_key, result, CACHE_TTL["ecb"])
                return value

        return FALLBACK_EURIBOR
    except Exception as e:
        print(f"Warning: Error fetching ECB EURIBOR rate: {e}. Using fallback.")
        return FALLBACK_EURIBOR


def get_ecb_policy_rate() -> float:
    """
    Get ECB deposit facility rate (monetary policy rate).

    Returns:
        Float percentage rate
    """
    cache_key = "ecb_policy_rate"
    cached = get("ecb", cache_key, CACHE_TTL["ecb"])
    if cached:
        return cached.get("rate", FALLBACK_POLICY_RATE)

    try:
        # ECB deposit facility rate
        url = f"{BASE_URL}/FM/M.U2.EUR.RT0.DF.HSTA"
        params = {"format": "json"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        observations = data.get("observations", {})

        if observations:
            last_period = max(observations.keys())
            last_obs = observations[last_period]
            if last_obs:
                value = float(last_obs[0].get("value", FALLBACK_POLICY_RATE))
                result = {"rate": value}
                set("ecb", cache_key, result, CACHE_TTL["ecb"])
                return value

        return FALLBACK_POLICY_RATE
    except Exception as e:
        print(f"Warning: Error fetching ECB policy rate: {e}. Using fallback.")
        return FALLBACK_POLICY_RATE
