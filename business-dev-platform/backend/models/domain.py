from pydantic import BaseModel, Field
from typing import Optional, Literal


class FounderProfile(BaseModel):
    """Edge-first intake: who the founder is, not what the market is doing."""
    skills: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=lambda: ["de"])
    capital_level: Literal["low", "medium", "high"] = "medium"
    maintenance_preference: Literal["low", "medium", "high"] = "medium"
    remote_only: bool = False


class MatchedDomain(BaseModel):
    slug: str
    name_de: str
    name_en: str
    fit_score: float
    fit_grade: str  # "Strong fit", "Good fit", "Possible", "Weak fit"
    skill_match: float
    channel_match: float
    language_leverage: float
    constraint_fit: float
    market_signal: float
    matched_skills: list[str]
    matched_channels: list[str]
    reasons: list[str]


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
