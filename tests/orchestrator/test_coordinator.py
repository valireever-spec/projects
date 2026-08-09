"""Tests for OrchestratorCoordinator."""

import pytest
from orchestrator.coordinator import OrchestratorCoordinator
from orchestrator.config import OrchestratorConfig
from orchestrator.state_machine import WorkflowStateMachine
from orchestrator.schemas import (
    ProjectPhase, DesignOutput, Requirement, RequirementType, Gap, SeverityLevel, EffortLevel
)


def test_coordinator_initialization():
    """Test coordinator initializes with config."""
    config = OrchestratorConfig(
        project_name="test_project",
        project_path="/test/path"
    )
    coordinator = OrchestratorCoordinator(config)

    assert coordinator.config.project_name == "test_project"
    assert coordinator.state_machine is not None
    assert coordinator.resource_monitor is not None


def test_state_machine_proposed_to_design():
    """Test state machine transitions from PROPOSED to DESIGN_IN_PROGRESS."""
    sm = WorkflowStateMachine(project_id=1, project_name="test")
    assert sm.state.phase == ProjectPhase.PROPOSED

    success = sm.start_design()
    assert success
    assert sm.state.phase == ProjectPhase.DESIGN_IN_PROGRESS


def test_state_machine_design_review_gate():
    """Test design review gate logic."""
    sm = WorkflowStateMachine(project_id=1, project_name="test")
    sm.start_design()

    # Create design output with no blockers
    design_output = DesignOutput(
        project_id=1,
        findings=["Finding 1"],
        blockers=[]
    )

    success = sm.complete_design(design_output)
    assert success
    assert sm.state.phase == ProjectPhase.DESIGN_REVIEW_GATE

    # Gate should pass (no blockers)
    success = sm.pass_design_gate()
    assert success
    assert sm.state.phase == ProjectPhase.IMPLEMENTATION_IN_PROGRESS


def test_state_machine_design_gate_with_blockers():
    """Test design gate fails when blockers present."""
    sm = WorkflowStateMachine(project_id=1, project_name="test")
    sm.start_design()

    # Create design output with blockers
    design_output = DesignOutput(
        project_id=1,
        findings=["Finding 1"],
        blockers=["Critical security issue"]
    )

    sm.complete_design(design_output)
    assert sm.state.phase == ProjectPhase.DESIGN_REVIEW_GATE

    # Gate should fail (has blockers)
    success = sm.pass_design_gate()
    assert not success
    assert sm.state.phase == ProjectPhase.DESIGN_REVIEW_GATE

    # Should be able to fail gate and go back to design
    success = sm.fail_design_gate()
    assert success
    assert sm.state.phase == ProjectPhase.DESIGN_IN_PROGRESS


def test_state_machine_full_workflow():
    """Test full workflow state transitions."""
    sm = WorkflowStateMachine(project_id=1, project_name="test")

    # Proposed → Design
    assert sm.start_design()
    assert sm.state.phase == ProjectPhase.DESIGN_IN_PROGRESS

    # Design → Review
    design_output = DesignOutput(project_id=1, findings=[], blockers=[])
    assert sm.complete_design(design_output)
    assert sm.state.phase == ProjectPhase.DESIGN_REVIEW_GATE

    # Review → Implementation
    assert sm.pass_design_gate()
    assert sm.state.phase == ProjectPhase.IMPLEMENTATION_IN_PROGRESS

    # Implementation → Verification
    from orchestrator.schemas import ImplementerOutput
    impl_output = ImplementerOutput(project_id=1, blockers=[])
    assert sm.complete_implementation(impl_output)
    assert sm.state.phase == ProjectPhase.VERIFICATION_GATE

    # Verification → Complete
    from orchestrator.schemas import VerifierOutput
    verifier_output = VerifierOutput(project_id=1, approved=True, blockers=[])
    assert sm.pass_verification_gate(verifier_output)
    assert sm.state.phase == ProjectPhase.COMPLETE


def test_coordinator_set_project():
    """Test setting project on coordinator."""
    config = OrchestratorConfig(
        project_name="initial",
        project_path="/initial"
    )
    coordinator = OrchestratorCoordinator(config)

    coordinator.set_project(123, "new_project")
    assert coordinator.state_machine.project_id == 123
    assert coordinator.state_machine.project_name == "new_project"
    assert coordinator.config.project_name == "new_project"


def test_coordinator_get_state():
    """Test getting current project state from coordinator."""
    config = OrchestratorConfig(
        project_name="test",
        project_path="/test"
    )
    coordinator = OrchestratorCoordinator(config)

    state = coordinator.get_state()
    assert state.project_name == "test"
    assert state.phase == ProjectPhase.PROPOSED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
