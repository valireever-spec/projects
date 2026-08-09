"""Agent I/O contracts: Pydantic schemas for Designer, Implementer, Verifier."""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class FrameworkType(str, Enum):
    """Framework choices for validation."""
    CSF_21 = "CSF-21"
    PILLAR_8 = "8-pillar"
    HYBRID = "hybrid"


class SeverityLevel(str, Enum):
    """Gap/issue severity."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class EffortLevel(str, Enum):
    """Effort estimate for fixing a gap."""
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class RequirementType(str, Enum):
    """Requirement type."""
    FUNCTIONAL = "Functional"
    NON_FUNCTIONAL = "Non-Functional"


class RequirementStatus(str, Enum):
    """Requirement lifecycle status."""
    PROPOSED = "Proposed"
    ACCEPTED = "Accepted"
    IMPLEMENTED = "Implemented"
    VALIDATED = "Validated"


class GapStatus(str, Enum):
    """Gap/bug lifecycle status."""
    DISCOVERED = "Discovered"
    PRIORITIZED = "Prioritized"
    IN_REMEDIATION = "In Remediation"
    DONE = "Done"


# ============================================================================
# DESIGNER AGENT
# ============================================================================

class DesignInput(BaseModel):
    """Input for Designer agent."""
    project_id: int
    project_path: str
    project_name: str
    tech_stack: str = Field(..., description="e.g., Python FastAPI + React + PostgreSQL")
    phase: str = Field(default="Initial", description="Current phase name")
    focus_area: Optional[str] = Field(default=None, description="What to focus design on")
    framework: FrameworkType = Field(default=FrameworkType.CSF_21, description="Validation framework")
    existing_requirements: List[Dict[str, Any]] = Field(default_factory=list, description="Known requirements")
    existing_gaps: List[Dict[str, Any]] = Field(default_factory=list, description="Known gaps to avoid re-discovery")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context (CSF score, maturity, etc.)")


class PillarAssessment(BaseModel):
    """Assessment for a single pillar."""
    pillar_name: str
    score: Optional[int] = Field(None, description="Numeric score 0-100")
    status: str = Field(..., description="Met, Partial, Gap, N/A")
    gaps: List[str] = Field(default_factory=list, description="Identified gaps")
    evidence: Optional[str] = Field(None, description="Supporting evidence")


class Gap(BaseModel):
    """A discovered gap or issue."""
    pillar: str
    rule_id: Optional[str] = None
    title: str
    description: str
    severity: SeverityLevel = SeverityLevel.MEDIUM
    effort: EffortLevel = EffortLevel.MEDIUM
    linked_requirement: Optional[str] = None


class Requirement(BaseModel):
    """A proposed requirement."""
    req_id: str = Field(..., description="FR-001, NFR-001, etc.")
    title: str
    description: str
    req_type: RequirementType
    category: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    measurement_method: Optional[str] = None
    target: Optional[str] = None
    linked_pillar: Optional[str] = None


class DesignOutput(BaseModel):
    """Output from Designer agent."""
    project_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    findings: List[str] = Field(default_factory=list, description="High-level insights/recommendations")
    proposed_requirements: List[Requirement] = Field(default_factory=list)
    gaps_identified: List[Gap] = Field(default_factory=list)
    pillar_assessments: Dict[str, PillarAssessment] = Field(default_factory=dict)
    risk_assessment: Dict[str, List[str]] = Field(
        default_factory=lambda: {"critical": [], "high": [], "medium": []},
        description="Risks by severity"
    )
    next_steps: List[str] = Field(default_factory=list, description="Recommended actions for Implementer")
    blockers: List[str] = Field(default_factory=list, description="Issues blocking progress")


# ============================================================================
# IMPLEMENTER AGENT
# ============================================================================

class ImplementerInput(BaseModel):
    """Input for Implementer agent."""
    project_id: int
    project_path: str
    design_findings: DesignOutput
    target_requirements: List[Requirement] = Field(default_factory=list, description="Requirements to implement")
    test_framework: str = Field(default="pytest", description="pytest, jest, etc.")
    ci_system: str = Field(default="GitHub Actions", description="CI/CD system")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Performance budgets, deadlines, etc.")
    existing_code_summary: Optional[Dict[str, Any]] = None


class CodeChange(BaseModel):
    """A code change to make."""
    file_path: str
    description: str
    rationale: str
    priority: int = Field(default=1, ge=1, description="1=highest")


class TestPlan(BaseModel):
    """Test planning details."""
    unit_tests: List[str] = Field(default_factory=list)
    integration_tests: List[str] = Field(default_factory=list)
    e2e_tests: List[str] = Field(default_factory=list)
    coverage_target: int = Field(default=85, ge=0, le=100)


class Commit(BaseModel):
    """Logical commit in sequence."""
    message: str
    files_changed: List[str]
    rationale: str


class ImplementerOutput(BaseModel):
    """Output from Implementer agent."""
    project_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    code_changes: List[CodeChange] = Field(default_factory=list)
    test_plan: TestPlan = Field(default_factory=TestPlan)
    gaps_created: List[Gap] = Field(default_factory=list, description="Gaps discovered during implementation")
    implementation_risks: List[str] = Field(default_factory=list)
    verification_checklist: Dict[str, List[str]] = Field(default_factory=dict, description="What Verifier should check")
    commits: List[Commit] = Field(default_factory=list, description="Logical commit sequence")
    blockers: List[str] = Field(default_factory=list, description="Issues blocking acceptance")


# ============================================================================
# VERIFIER AGENT
# ============================================================================

class VerifierInput(BaseModel):
    """Input for Verifier agent."""
    project_id: int
    project_path: str
    code_changes: List[CodeChange] = Field(default_factory=list)
    original_requirements: List[Requirement] = Field(default_factory=list)
    test_results: Dict[str, Any] = Field(default_factory=dict, description="Test run output")
    framework: FrameworkType = Field(default=FrameworkType.CSF_21)
    audit_rules: List[Dict[str, Any]] = Field(default_factory=list, description="Security, performance, quality rules")


class RequirementValidation(BaseModel):
    """Validation result for one requirement."""
    req_id: str
    title: str
    passed: bool
    evidence: str
    gaps_if_failed: List[Gap] = Field(default_factory=list)


class VerifierOutput(BaseModel):
    """Output from Verifier agent."""
    project_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    requirement_validation: List[RequirementValidation] = Field(default_factory=list)
    security_findings: List[Gap] = Field(default_factory=list)
    quality_findings: List[Gap] = Field(default_factory=list)
    csf_assessment: Dict[str, PillarAssessment] = Field(default_factory=dict)
    gaps_found: List[Gap] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list, description="Issues blocking acceptance")
    recommendations: List[str] = Field(default_factory=list, description="Changes needed before merge")
    approved: bool = Field(default=False, description="Ready for production")


# ============================================================================
# ORCHESTRATOR STATE
# ============================================================================

class ProjectPhase(str, Enum):
    """Project workflow phase."""
    PROPOSED = "Proposed"
    DESIGN_IN_PROGRESS = "Design In Progress"
    DESIGN_REVIEW_GATE = "Design Review Gate"
    IMPLEMENTATION_IN_PROGRESS = "Implementation In Progress"
    VERIFICATION_GATE = "Verification Gate"
    COMPLETE = "Complete"


class ProjectState(BaseModel):
    """Current state of a project in orchestrator."""
    project_id: int
    project_name: str
    phase: ProjectPhase
    designer_output: Optional[DesignOutput] = None
    implementer_output: Optional[ImplementerOutput] = None
    verifier_output: Optional[VerifierOutput] = None
    blockers: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
