"""Tests for orchestrator schemas."""

import pytest
from orchestrator.schemas import (
    DesignInput, DesignOutput, Requirement, RequirementType, Gap, SeverityLevel, EffortLevel,
    ImplementerInput, ImplementerOutput,
    VerifierInput, VerifierOutput,
    FrameworkType
)


def test_requirement_creation():
    """Test Requirement model."""
    req = Requirement(
        req_id="FR-001",
        title="User Authentication",
        description="Implement JWT-based auth",
        req_type=RequirementType.FUNCTIONAL,
        category="Security",
        acceptance_criteria="User can log in with email/password"
    )

    assert req.req_id == "FR-001"
    assert req.title == "User Authentication"
    assert req.req_type == RequirementType.FUNCTIONAL


def test_gap_creation():
    """Test Gap model."""
    gap = Gap(
        pillar="Security & Privacy by Design",
        rule_id="6.2",
        title="Hardcoded Secrets",
        description="Found API key in .env.example",
        severity=SeverityLevel.CRITICAL,
        effort=EffortLevel.SMALL
    )

    assert gap.pillar == "Security & Privacy by Design"
    assert gap.severity == SeverityLevel.CRITICAL
    assert gap.effort == EffortLevel.SMALL


def test_design_input_creation():
    """Test DesignInput model."""
    design_input = DesignInput(
        project_id=1,
        project_path="/home/vali/projects/test",
        project_name="test_project",
        tech_stack="Python FastAPI + React",
        framework=FrameworkType.CSF_21
    )

    assert design_input.project_id == 1
    assert design_input.framework == FrameworkType.CSF_21
    assert design_input.existing_requirements == []
    assert design_input.existing_gaps == []


def test_design_output_creation():
    """Test DesignOutput model."""
    req = Requirement(
        req_id="FR-001",
        title="Auth",
        description="JWT",
        req_type=RequirementType.FUNCTIONAL
    )

    gap = Gap(
        pillar="Security",
        title="Secrets",
        description="Hardcoded keys",
        severity=SeverityLevel.HIGH,
        effort=EffortLevel.MEDIUM
    )

    output = DesignOutput(
        project_id=1,
        findings=["Finding 1", "Finding 2"],
        proposed_requirements=[req],
        gaps_identified=[gap],
        blockers=[]
    )

    assert output.project_id == 1
    assert len(output.findings) == 2
    assert len(output.proposed_requirements) == 1
    assert len(output.gaps_identified) == 1


def test_implementer_output_creation():
    """Test ImplementerOutput model."""
    from orchestrator.schemas import CodeChange, TestPlan

    change = CodeChange(
        file_path="src/auth.py",
        description="Implement JWT auth",
        rationale="Secure token-based auth"
    )

    test_plan = TestPlan(
        unit_tests=["test_jwt_token", "test_login"],
        coverage_target=90
    )

    output = ImplementerOutput(
        project_id=1,
        code_changes=[change],
        test_plan=test_plan,
        blockers=[]
    )

    assert output.project_id == 1
    assert len(output.code_changes) == 1
    assert output.test_plan.coverage_target == 90


def test_verifier_output_creation():
    """Test VerifierOutput model."""
    from orchestrator.schemas import RequirementValidation

    validation = RequirementValidation(
        req_id="FR-001",
        title="Auth",
        passed=True,
        evidence="All tests pass"
    )

    output = VerifierOutput(
        project_id=1,
        requirement_validation=[validation],
        approved=True,
        blockers=[]
    )

    assert output.project_id == 1
    assert len(output.requirement_validation) == 1
    assert output.approved is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
