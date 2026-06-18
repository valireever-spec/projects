from typing import Literal


def estimate_market_size(
    sector_stats: dict,
    gdp_data: dict,
    city_population: int,
    germany_population: int = 83_000_000,
) -> dict:
    """
    Estimate market size (TAM/SAM/SOM) for a business domain.

    Args:
        sector_stats: Dict with sector turnover, enterprise count, employment
        gdp_data: Dict with GDP growth and macro metrics
        city_population: Population of target city
        germany_population: Total German population

    Returns:
        Dict with {
            total_market_de: Market size in Germany,
            addressable_market_city: Addressable market in city,
            growth_rate_pct: Annual growth rate,
            market_maturity: one of (emerging, growing, mature, declining),
            tam_eur: Total Addressable Market (€),
            sam_eur: Serviceable Available Market (€),
            som_eur: Serviceable Obtainable Market (€),
        }
    """
    # Extract available data
    sector_turnover = sector_stats.get("turnover", 0)
    enterprise_count = sector_stats.get("enterprise_count", 5000)
    gdp_growth = gdp_data.get("gdp_growth", 0.02)  # Default 2%
    inflation = gdp_data.get("inflation", 0.025)   # Default 2.5%

    # TAM: Total Addressable Market (Total German market)
    # Use sector turnover as proxy for market size
    if sector_turnover > 0:
        tam_eur = sector_turnover * 1_000_000  # Convert to EUR
    else:
        # Estimate based on enterprise count and avg revenue
        avg_revenue_per_enterprise = 500_000  # EUR estimate
        tam_eur = enterprise_count * avg_revenue_per_enterprise

    # SAM: Serviceable Available Market
    # Scale down TAM based on city population vs Germany
    city_share = city_population / germany_population
    sam_eur = tam_eur * city_share * 1.2  # 1.2x factor for addressability

    # SOM: Serviceable Obtainable Market
    # Assume realistic capture of 5-15% of SAM in first 3 years
    som_eur = sam_eur * 0.10  # Conservative 10% capture

    # Classify market maturity
    gdp_sector_ratio = gdp_growth / 0.02  # Compare to baseline 2% GDP growth
    if gdp_sector_ratio > 1.5:
        maturity = "emerging"
        growth_multiplier = 1.5
    elif gdp_sector_ratio > 1.0:
        maturity = "growing"
        growth_multiplier = 1.2
    elif gdp_sector_ratio > 0.7:
        maturity = "mature"
        growth_multiplier = 1.05
    else:
        maturity = "declining"
        growth_multiplier = 0.95

    # Adjust growth rate
    annual_growth = gdp_growth * growth_multiplier

    return {
        "tam_eur": round(tam_eur, 0),
        "sam_eur": round(sam_eur, 0),
        "som_eur": round(som_eur, 0),
        "total_market_de": round(tam_eur, 0),
        "addressable_market_city": round(sam_eur, 0),
        "growth_rate_pct": round(annual_growth * 100, 1),
        "market_maturity": maturity,
        "market_size_estimate": _format_market_size(tam_eur),
        "city_market_estimate": _format_market_size(sam_eur),
    }


def estimate_customer_acquisition_cost(
    sector: str,
    channel: str = "online",
) -> float:
    """
    Estimate Customer Acquisition Cost (CAC) by sector and channel.

    Args:
        sector: Industry sector (e.g., 'consulting', 'saas', 'ecommerce')
        channel: Acquisition channel (online, offline, hybrid)

    Returns:
        Estimated CAC in EUR
    """
    # Base CAC by sector (EUR)
    sector_cac = {
        "consulting": 2500,
        "saas": 800,
        "ecommerce": 50,
        "services": 500,
        "coaching": 300,
        "marketplace": 100,
    }

    base_cac = sector_cac.get(sector.lower(), 500)

    # Channel multiplier
    channel_multiplier = {
        "online": 1.0,
        "offline": 2.0,
        "hybrid": 1.5,
    }

    multiplier = channel_multiplier.get(channel.lower(), 1.0)

    return round(base_cac * multiplier, 0)


def estimate_lifetime_value(
    avg_revenue_per_customer: float,
    gross_margin_pct: float = 0.70,
    customer_lifetime_years: float = 3.0,
    churn_rate_monthly: float = 0.05,
) -> float:
    """
    Estimate Customer Lifetime Value (LTV).

    Args:
        avg_revenue_per_customer: Annual revenue per customer (EUR)
        gross_margin_pct: Gross profit margin (0-1)
        customer_lifetime_years: Expected customer lifetime (years)
        churn_rate_monthly: Monthly churn rate (0-1)

    Returns:
        LTV in EUR
    """
    # Calculate lifetime months based on churn rate
    if churn_rate_monthly > 0:
        months_lifetime = (1 / churn_rate_monthly) * 12 / customer_lifetime_years
    else:
        months_lifetime = customer_lifetime_years * 12

    # Limit to expected lifetime
    months_lifetime = min(months_lifetime, customer_lifetime_years * 12)

    ltv = (avg_revenue_per_customer / 12) * months_lifetime * gross_margin_pct

    return round(ltv, 0)


def calculate_market_penetration_target(
    sam_eur: float,
    num_customers_target: int,
    avg_revenue_per_customer: float,
) -> dict:
    """
    Calculate market penetration metrics for a revenue target.

    Args:
        sam_eur: Serviceable Available Market (EUR)
        num_customers_target: Target number of customers
        avg_revenue_per_customer: Average revenue per customer (EUR)

    Returns:
        Dict with penetration metrics
    """
    total_revenue = num_customers_target * avg_revenue_per_customer
    market_penetration_pct = (total_revenue / sam_eur * 100) if sam_eur > 0 else 0

    return {
        "total_revenue": round(total_revenue, 0),
        "market_penetration_pct": round(market_penetration_pct, 2),
        "customers_needed": num_customers_target,
        "penetration_achievable": market_penetration_pct < 5,  # Realistic if <5%
    }


def _format_market_size(size_eur: float) -> str:
    """Format market size in EUR to readable string."""
    if size_eur >= 1_000_000_000:
        return f"€{size_eur/1_000_000_000:.1f}B"
    elif size_eur >= 1_000_000:
        return f"€{size_eur/1_000_000:.1f}M"
    elif size_eur >= 1_000:
        return f"€{size_eur/1_000:.1f}K"
    else:
        return f"€{size_eur:.0f}"
