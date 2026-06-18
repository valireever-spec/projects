from typing import NamedTuple


class DomainScore(NamedTuple):
    slug: str
    name_de: str
    name_en: str
    composite_score: float
    trend_momentum: float
    market_growth: float
    competition_density: float
    registration_momentum: float
    grade: str


def score_domains(
    domain_data: list,
    trend_data: dict,
    sector_stats: dict,
    registrations: dict,
) -> list[DomainScore]:
    """
    Score and rank domains based on multiple factors.

    Args:
        domain_data: List of domain dicts from german_domains.json
        trend_data: Dict of {slug: interest_value} from Google Trends
        sector_stats: Dict of {nace_code: {turnover, count, ...}}
        registrations: Dict of {nace_code: [registrations_history]}

    Returns:
        Sorted list of DomainScore objects (highest score first)
    """
    scores = []

    for domain in domain_data:
        slug = domain.get("slug")
        name_de = domain.get("name_de", "")
        name_en = domain.get("name_en", "")
        nace_code = domain.get("nace_r2_code", "")

        # Trend momentum (0-30): normalized Google Trends interest
        trend_interest = trend_data.get(slug, trend_data.get(nace_code, 20))
        trend_momentum = min(30, (trend_interest / 100) * 30)

        # Market growth (0-25): sector turnover CAGR or default estimate
        market_growth = _calculate_market_growth(sector_stats, nace_code)

        # Competition density (0-25, inverted): fewer enterprises = higher score
        competition_density = _calculate_competition_score(sector_stats, nace_code)

        # Registration momentum (0-20): new registrations trend
        registration_momentum = _calculate_registration_momentum(registrations, nace_code)

        # Composite score (0-100)
        composite_score = (
            trend_momentum + market_growth + competition_density + registration_momentum
        )

        # Grade based on score
        if composite_score >= 80:
            grade = "Excellent"
        elif composite_score >= 60:
            grade = "Good"
        elif composite_score >= 40:
            grade = "Moderate"
        else:
            grade = "Saturated"

        scores.append(
            DomainScore(
                slug=slug,
                name_de=name_de,
                name_en=name_en,
                composite_score=round(composite_score, 1),
                trend_momentum=round(trend_momentum, 1),
                market_growth=round(market_growth, 1),
                competition_density=round(competition_density, 1),
                registration_momentum=round(registration_momentum, 1),
                grade=grade,
            )
        )

    # Sort by composite score descending
    scores.sort(key=lambda x: x.composite_score, reverse=True)

    return scores


def _calculate_market_growth(sector_stats: dict, nace_code: str) -> float:
    """
    Calculate market growth score (0-25).

    Base on sector turnover CAGR or assume average growth.
    """
    # Default: assume 6% annual growth for most sectors
    growth_rate = sector_stats.get(nace_code, {}).get("growth_rate", 0.06)

    # Map growth rate to 0-25 scale: 3% = 10, 6% = 15, 12% = 25
    if growth_rate <= 0:
        return 5
    elif growth_rate >= 0.12:
        return 25
    else:
        return (growth_rate / 0.12) * 25


def _calculate_competition_score(sector_stats: dict, nace_code: str) -> float:
    """
    Calculate competition density score (0-25, inverted).

    Fewer enterprises per capita = higher score (lower competition).
    """
    # Get enterprise count per sector
    enterprise_count = sector_stats.get(nace_code, {}).get("enterprise_count", 5000)

    # German population ~83 million
    # Lower bound: 100 enterprises = very low competition (25 points)
    # Upper bound: 50000 enterprises = saturated (0 points)
    enterprises_per_1k = (enterprise_count / 83_000) * 1000

    if enterprises_per_1k <= 0.5:
        return 25  # Very low competition
    elif enterprises_per_1k >= 30:
        return 0   # Saturated
    else:
        # Inverted scale
        return 25 - ((enterprises_per_1k / 30) * 25)


def _calculate_registration_momentum(registrations: dict, nace_code: str) -> float:
    """
    Calculate registration momentum score (0-20).

    Based on year-over-year growth in new business registrations.
    """
    reg_history = registrations.get(nace_code, [])

    if len(reg_history) < 2:
        return 10  # Default if no data

    # Compare last year to previous year
    try:
        latest_registrations = float(reg_history[-1].get("registrations", 0))
        previous_registrations = float(reg_history[-2].get("registrations", 0))

        if previous_registrations == 0:
            yoy_growth = 0
        else:
            yoy_growth = (latest_registrations - previous_registrations) / previous_registrations

        # Map growth to 0-20 scale: -10% = 0, 0% = 10, +20% = 20
        if yoy_growth <= -0.1:
            return 0
        elif yoy_growth >= 0.2:
            return 20
        else:
            return ((yoy_growth + 0.1) / 0.3) * 20
    except (ValueError, TypeError, IndexError):
        return 10  # Default
