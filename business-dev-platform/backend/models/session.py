from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional


class WizardStep(str, Enum):
    DOMAIN_SELECTION = "domain_selection"
    BUSINESS_PROFILE = "business_profile"
    MARKET_ANALYSIS = "market_analysis"
    FINANCIAL_MODEL = "financial_model"
    RISK_ASSESSMENT = "risk_assessment"
    PLAN_REVIEW = "plan_review"


class BusinessProfile(BaseModel):
    business_name: Optional[str] = None
    domain_slug: Optional[str] = None
    legal_form: Optional[str] = None
    city: Optional[str] = None
    target_market: Optional[str] = None
    unique_value_proposition: Optional[str] = None
    founder_background: Optional[str] = None
    initial_capital: Optional[float] = None


class BusinessPlanSession(BaseModel):
    session_id: str
    created_at: datetime
    updated_at: datetime
    current_step: WizardStep
    completed_steps: list[WizardStep] = []
    profile: BusinessProfile = BusinessProfile()
    market_analysis: Optional[dict] = None
    financial_projection: Optional[dict] = None
    risk_matrix: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2026-05-17T12:00:00",
                "updated_at": "2026-05-17T12:05:00",
                "current_step": "domain_selection",
                "completed_steps": [],
                "profile": {},
                "market_analysis": None,
                "financial_projection": None,
                "risk_matrix": None,
            }
        }
