"""
Pydantic models for schema validation across the V-Model tracker.

Validates tracker API responses, requirement objects, and gap/bug objects
to prevent crashes from malformed data.
"""

from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ProjectModel(BaseModel):
    """Tracker project schema."""

    id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        extra = "allow"


class RequirementModel(BaseModel):
    """Requirement schema (FR-XXX, NFR-XXX)."""

    id: Optional[int] = None
    project_id: int
    req_id: str = Field(..., pattern=r"^(FR|NFR)-\d+$")
    description: str = Field(..., min_length=1, max_length=2000)
    status: str = Field(..., regex="^(Proposed|Accepted|Implemented|Validated)$")
    type: str = Field(..., regex="^(FR|NFR)$")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        extra = "allow"

    @validator("type", pre=True, always=True)
    def infer_type_from_req_id(cls, v: str, values: dict[str, Any]) -> str:
        """Infer type from req_id if not provided."""
        if "req_id" in values:
            req_id = values["req_id"]
            if req_id.startswith("FR"):
                return "FR"
            elif req_id.startswith("NFR"):
                return "NFR"
        return v


class GapModel(BaseModel):
    """Gap/Bug schema for tracker."""

    id: Optional[int] = None
    project_id: int
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1, max_length=5000)
    pillar: str = Field(...)
    severity: str = Field(..., regex="^(Critical|High|Medium|Low)$")
    status: str = Field(..., regex="^(Discovered|Prioritized|In Remediation|Done)$")
    requirement_id: Optional[int] = None
    effort: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    solution_summary: Optional[str] = None
    fixed_code_file: Optional[str] = None
    fixed_commit_hash: Optional[str] = None
    fixed_by: Optional[str] = None

    class Config:
        extra = "allow"


class MarkdownRequirementModel(BaseModel):
    """Requirement parsed from markdown file."""

    req_id: str = Field(..., pattern=r"^(FR|NFR)-\d+$")
    description: str = Field(..., min_length=1)
    status: str = Field(default="Proposed", regex="^(Proposed|Accepted|Implemented|Validated)$")
    type: str = Field(regex="^(FR|NFR)$")

    @validator("type", pre=True, always=True)
    def infer_type_from_req_id(cls, v: str, values: dict[str, Any]) -> str:
        """Infer type from req_id."""
        if "req_id" in values:
            req_id = values["req_id"]
            if req_id.startswith("FR"):
                return "FR"
            elif req_id.startswith("NFR"):
                return "NFR"
        return v


class MarkdownGapModel(BaseModel):
    """Gap/bug parsed from V_MODEL_BOARD.md markdown."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    severity: str = Field(default="Medium", regex="^(Critical|High|Medium|Low)$")
    status: str = Field(default="Discovered")


class TrackerHealthModel(BaseModel):
    """Tracker API health check response."""

    status: str = Field(..., regex="^(healthy|degraded|unhealthy)$")
    timestamp: datetime
    version: Optional[str] = None
    uptime_seconds: Optional[int] = None


class ProjectStatusModel(BaseModel):
    """Project status from tracker."""

    id: int
    name: str
    description: Optional[str] = None
    requirement_count: int = 0
    gap_count: int = 0
    maturity_score: int = Field(default=0, ge=0, le=100)
    coverage_percent: int = Field(default=0, ge=0, le=100)
    last_sync: Optional[datetime] = None

    class Config:
        extra = "allow"
