from pydantic import BaseModel
from typing import Optional


class RiskFactor(BaseModel):
    name: str
    description: str
    likelihood: int  # 1-5
    impact: int     # 1-5
    mitigation_strategies: list[str] = []

    @property
    def risk_score(self) -> int:
        return self.likelihood * self.impact


class RegulatoryRequirement(BaseModel):
    category: str  # "Registration", "Tax", "Licenses", "DSGVO", etc.
    requirement: str
    authority: str
    estimated_cost_eur: Optional[float] = None
    estimated_days: Optional[int] = None
    description: Optional[str] = None
    reference_url: Optional[str] = None


class RiskMatrix(BaseModel):
    session_id: str
    overall_risk_level: str  # "low", "medium", "high"
    risk_score: int  # 0-100
    risk_factors: list[RiskFactor]
    top_3_risks: list[RiskFactor]
    mitigation_plan: list[str]


class RegulatoryChecklist(BaseModel):
    session_id: str
    domain_slug: str
    legal_form: str
    country: str = "DE"
    requirements: list[RegulatoryRequirement]
    estimated_total_cost: float = 0
    estimated_total_days: int = 0

    @property
    def grouped_requirements(self) -> dict:
        """Group requirements by category."""
        grouped = {}
        for req in self.requirements:
            if req.category not in grouped:
                grouped[req.category] = []
            grouped[req.category].append(req)
        return grouped
