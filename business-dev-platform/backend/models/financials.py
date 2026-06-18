from pydantic import BaseModel
from enum import Enum
from typing import Optional


class RevenueModel(str, Enum):
    SUBSCRIPTION = "subscription"
    HOURLY = "hourly"
    PRODUCT_SALE = "product_sale"
    COMMISSION = "commission"
    HYBRID = "hybrid"


class StartupCosts(BaseModel):
    legal_registration: float = 0
    equipment: float = 0
    office_setup: float = 0
    working_capital: float = 0
    other: float = 0

    @property
    def total(self) -> float:
        return sum([
            self.legal_registration, self.equipment, self.office_setup,
            self.working_capital, self.other
        ])


class MonthlyOperatingCosts(BaseModel):
    staff: float = 0
    rent_office: float = 0
    utilities: float = 0
    insurance: float = 0
    software_licenses: float = 0
    marketing: float = 0
    administrative: float = 0
    other: float = 0

    @property
    def total(self) -> float:
        return sum([
            self.staff, self.rent_office, self.utilities, self.insurance,
            self.software_licenses, self.marketing, self.administrative, self.other
        ])


class FinancialProjection(BaseModel):
    session_id: str
    revenue_model: RevenueModel
    startup_costs: StartupCosts
    monthly_fixed_costs: float
    monthly_variable_cost_ratio: float  # 0.0 to 1.0
    break_even_monthly_revenue: float
    break_even_month: int  # months from launch
    monthly_revenue_estimate: float  # user input

    # 36-month projections
    months_1_12: list[dict]  # Each month: {month, revenue, costs, ebitda, cumulative_cf}
    months_13_24: list[dict]
    months_25_36: list[dict]

    # Scenarios
    scenarios: dict  # {conservative, base, optimistic} with their metrics

    # Key metrics
    key_metrics: dict = {}

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "revenue_model": "subscription",
                "startup_costs": {
                    "legal_registration": 500,
                    "equipment": 3000,
                    "office_setup": 2000,
                    "working_capital": 5000,
                    "other": 0
                },
                "monthly_fixed_costs": 3500,
                "monthly_variable_cost_ratio": 0.3,
                "break_even_monthly_revenue": 5000,
                "break_even_month": 8,
                "monthly_revenue_estimate": 6000,
                "months_1_12": [],
                "months_13_24": [],
                "months_25_36": [],
                "scenarios": {},
                "key_metrics": {}
            }
        }


class BreakEvenAnalysis(BaseModel):
    monthly_revenue_needed: float
    months_to_breakeven: int
    breakeven_date: str
    cumulative_investment: float
    cumulative_cash_flow_at_breakeven: float
