from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ScorecardEntryCreate(BaseModel):
    pillar: str
    status: str
    evidence: Optional[str] = None

class ScorecardEntry(ScorecardEntryCreate):
    id: int
    project_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

class GapCreate(BaseModel):
    pillar: str
    rule_id: Optional[str] = None
    title: str
    description: str
    status: str = "Discovered"
    severity: Optional[str] = None
    effort: Optional[str] = None
    requirement_id: Optional[int] = None

    # Solution tracking fields
    solution_summary: Optional[str] = None
    fixed_code_file: Optional[str] = None
    fixed_commit_hash: Optional[str] = None
    fixed_at: Optional[datetime] = None
    fixed_by: Optional[str] = None

class Gap(GapCreate):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    path: Optional[str] = None

class Project(ProjectCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    scorecard_entries: List[ScorecardEntry] = []
    gaps: List[Gap] = []

    class Config:
        from_attributes = True

class ProjectWithScore(Project):
    maturity_score: int = 0
    pillar_status: dict = {}
