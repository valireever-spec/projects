from typing import Literal


def analyze_competition(
    news_articles: list[dict],
    wikipedia_text: str,
    registrations_data: list[dict],
    nace_code: str = "",
) -> dict:
    """
    Analyze competition level and dynamics.

    Args:
        news_articles: List of recent news articles (from NewsAPI)
        wikipedia_text: Industry background text (from Wikipedia)
        registrations_data: Historical business registration data
        nace_code: NACE sector code

    Returns:
        Dict with {
            competition_level: "low" | "medium" | "high",
            intensity_score: 0-100,
            key_players: [list of competitor names],
            barriers_to_entry: [list of barriers],
            differentiation_opportunities: [list of ideas],
            market_trends: [list of trends],
        }
    """
    # Calculate competition intensity
    intensity_score = _calculate_competition_intensity(
        news_articles,
        registrations_data
    )

    # Classify competition level
    if intensity_score < 30:
        competition_level = "low"
    elif intensity_score < 65:
        competition_level = "medium"
    else:
        competition_level = "high"

    # Extract competitors from news
    key_players = _extract_competitor_names(news_articles)

    # Identify barriers to entry
    barriers = _identify_barriers_to_entry(nace_code, wikipedia_text)

    # Suggest differentiation opportunities
    differentiation = _suggest_differentiation(news_articles, wikipedia_text)

    # Extract market trends
    trends = _extract_market_trends(news_articles, wikipedia_text)

    return {
        "competition_level": competition_level,
        "intensity_score": round(intensity_score, 0),
        "key_players": key_players,
        "barriers_to_entry": barriers,
        "differentiation_opportunities": differentiation,
        "market_trends": trends,
    }


def _calculate_competition_intensity(
    news_articles: list[dict],
    registrations_data: list[dict],
) -> float:
    """Calculate competition intensity score 0-100."""
    score = 50  # Neutral default

    # Factor 1: News volume (more news = more competitive)
    # More than 10 recent articles = high competition
    news_factor = min(len(news_articles) / 10 * 25, 25)
    score += news_factor

    # Factor 2: Registration trends (accelerating registrations = more competition)
    if len(registrations_data) >= 2:
        try:
            latest = float(registrations_data[-1].get("registrations", 0))
            previous = float(registrations_data[-2].get("registrations", 0))

            if previous > 0:
                yoy_growth = (latest - previous) / previous
                if yoy_growth > 0.15:  # >15% growth = high competition
                    score += 20
                elif yoy_growth > 0.05:
                    score += 10
        except (ValueError, TypeError):
            pass

    # Factor 3: Saturation (too many articles on the same topic)
    # Check for duplicate headlines
    headlines = [a.get("title", "") for a in news_articles]
    if len(headlines) > len(set(headlines)):
        # Many duplicates = saturated coverage
        score += 5

    return min(max(score, 0), 100)


def _extract_competitor_names(news_articles: list[dict]) -> list[str]:
    """Extract likely competitor names from news articles."""
    competitors = set()

    # Common German company indicators
    company_indicators = [
        "GmbH", "AG", "KG", "UG", "Einzelunternehmen", "Freelancer"
    ]

    for article in news_articles:
        title = article.get("title", "")
        description = article.get("description", "")
        text = f"{title} {description}".lower()

        # Look for company names (simple heuristic: capitalized words near indicators)
        words = title.split()
        for i, word in enumerate(words):
            if any(indicator.lower() in word.lower() for indicator in company_indicators):
                # Get the company name (word before indicator)
                if i > 0:
                    company = words[i - 1]
                    if len(company) > 2 and company[0].isupper():
                        competitors.add(company)

    return sorted(list(competitors))[:5]


def _identify_barriers_to_entry(nace_code: str, wikipedia_text: str) -> list[str]:
    """Identify barriers to entry for a sector."""
    barriers = []

    # Hardcoded barriers by NACE code
    nace_barriers = {
        "68.": ["Real estate licensing", "Capital requirements", "Regulatory oversight"],
        "69.": ["Legal qualifications required", "Audit requirements", "Insurance requirements"],
        "70.": ["Industry expertise needed", "Client relationships", "Reputation building"],
        "72.": ["Technical expertise required", "Client lock-in", "Proprietary systems"],
        "85.": ["Certifications required", "Accreditation needed", "Regulatory approval"],
        "86.": ["Professional credentials", "Licensing requirements", "Liability insurance"],
    }

    # Check NACE code
    for code, code_barriers in nace_barriers.items():
        if nace_code.startswith(code):
            barriers.extend(code_barriers)
            break

    # Generic barriers
    if not barriers:
        barriers = [
            "Building brand awareness",
            "Customer acquisition cost",
            "Initial capital investment",
        ]

    # Add from Wikipedia if available
    if wikipedia_text:
        if "certification" in wikipedia_text.lower():
            barriers.append("Professional certification")
        if "license" in wikipedia_text.lower():
            barriers.append("Legal licensing")
        if "capital" in wikipedia_text.lower():
            barriers.append("Capital requirements")

    return list(set(barriers))[:5]


def _suggest_differentiation(news_articles: list[dict], wikipedia_text: str) -> list[str]:
    """Suggest differentiation opportunities."""
    suggestions = [
        "Specialize in niche segment or customer type",
        "Offer superior customer service",
        "Focus on sustainability/eco-friendly approach",
        "Build community or loyalty program",
        "Leverage digital-first or online-only model",
    ]

    # Enhance based on article content
    article_text = " ".join([
        a.get("title", "") + " " + a.get("description", "")
        for a in news_articles
    ]).lower()

    if "online" in article_text or "digital" in article_text:
        suggestions.append("Differentiate offline/hybrid offering")

    if "traditional" in article_text:
        suggestions.append("Modernize with technology and automation")

    if "expensive" in article_text or "premium" in article_text:
        suggestions.append("Offer affordable/value alternative")

    if "personalized" in article_text:
        suggestions.append("Focus on standardized/scalable model")

    return suggestions[:5]


def _extract_market_trends(news_articles: list[dict], wikipedia_text: str) -> list[str]:
    """Extract current market trends from news and context."""
    trends = []

    # Keywords indicating trends
    trend_keywords = {
        "sustainability": "Growing focus on sustainable/eco-friendly solutions",
        "digital": "Digital transformation acceleration",
        "automation": "Increasing automation of processes",
        "remote": "Rising remote/distributed work models",
        "ai": "AI and automation adoption",
        "personalization": "Growing demand for personalized experiences",
        "niche": "Shift toward specialized niches",
        "regulation": "Increased regulatory scrutiny",
        "competition": "Increasing competition and price pressure",
        "wellness": "Growing health and wellness awareness",
    }

    # Scan articles
    article_text = " ".join([
        a.get("title", "") + " " + a.get("description", "")
        for a in news_articles
    ]).lower()

    combined_text = (article_text + " " + wikipedia_text.lower())

    for keyword, trend in trend_keywords.items():
        if keyword in combined_text:
            trends.append(trend)

    # If no trends found, return generic ones
    if not trends:
        trends = [
            "Growing market demand",
            "Increasing professionalization",
            "Digital channel adoption",
        ]

    return trends[:5]


def get_competitive_advantage_matrix() -> dict:
    """
    Generic competitive advantage framework.

    Returns:
        Matrix of possible advantages and their difficulty
    """
    return {
        "cost_leadership": {
            "advantage": "Lowest cost provider",
            "difficulty": "high",
            "sustainability": "low",
            "examples": ["Discount retailers", "Budget airlines"]
        },
        "differentiation": {
            "advantage": "Unique value proposition",
            "difficulty": "high",
            "sustainability": "high",
            "examples": ["Premium brands", "Innovative products"]
        },
        "focus_low_cost": {
            "advantage": "Niche low-cost leader",
            "difficulty": "medium",
            "sustainability": "medium",
            "examples": ["Regional players", "Specialty shops"]
        },
        "focus_differentiation": {
            "advantage": "Specialized premium offering",
            "difficulty": "medium",
            "sustainability": "high",
            "examples": ["Boutique agencies", "Expert consultants"]
        },
    }
