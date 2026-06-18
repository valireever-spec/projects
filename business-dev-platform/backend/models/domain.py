from pydantic import BaseModel
from typing import Optional


class DomainScore(BaseModel):
    slug: str
    name_de: str
    name_en: str
    composite_score: float
    trend_momentum: float
    market_growth: float
    competition_density: float
    registration_momentum: float
    grade: str  # "Excellent", "Good", "Moderate", "Saturated"


class TrendingDomain(BaseModel):
    slug: str
    name_de: str
    name_en: str
    composite_score: float
    grade: str
    nace_code: str
    trend_momentum: float
    market_growth: float
    competition_density: float
    registration_momentum: float
    market_size_estimate: Optional[str] = None
    trend_sparkline: Optional[list[float]] = None
    wikipedia_summary: Optional[str] = None
    top_news: Optional[list[dict]] = None


class CompetitorEntry(BaseModel):
    name: str
    description: Optional[str] = None
    market_position: Optional[str] = None


class DomainDetails(BaseModel):
    domain: TrendingDomain
    market_size_eur: Optional[float] = None
    growth_rate_percent: Optional[float] = None
    competition_level: str  # "low", "medium", "high"
    key_competitors: Optional[list[CompetitorEntry]] = None
    barriers_to_entry: Optional[list[str]] = None
    recent_news: Optional[list[dict]] = None
    trend_data: Optional[dict] = None
