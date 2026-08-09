"""Integration tests for Designer → Tracker flow."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from orchestrator.coordinator import OrchestratorCoordinator
from orchestrator.config import OrchestratorConfig, AgentConfig, TrackerConfig
from orchestrator.adapters.designer_adapter import DesignerAdapter
from orchestrator.adapters.tracker_adapter import TrackerAdapter
from orchestrator.schemas import (
    DesignInput, DesignOutput, Requirement, RequirementType, Gap, SeverityLevel, EffortLevel
)


@pytest.fixture
def coordinator_config():
    """Create test coordinator config."""
    return OrchestratorConfig(
        project_name="test_project",
        project_path="/test/project",
        agents={
            "designer": AgentConfig(model="claude-opus-4-8"),
            "implementer": AgentConfig(),
            "verifier": AgentConfig()
        },
        tracker=TrackerConfig(url="http://localhost:8000")
    )


@pytest.fixture
def mock_tracker_adapter():
    """Create mock tracker adapter."""
    adapter = AsyncMock(spec=TrackerAdapter)
    adapter.file_design_findings = AsyncMock(return_value=True)
    adapter.file_implementation_findings = AsyncMock(return_value=True)
    adapter.file_verification_findings = AsyncMock(return_value=True)
    return adapter


@pytest.fixture
def mock_designer_adapter():
    """Create mock designer adapter."""
    # Create sample design output
    req = Requirement(
        req_id="FR-001",
        title="User Authentication",
        description="Implement JWT-based auth",
        req_type=RequirementType.FUNCTIONAL,
        category="Security"
    )

    gap = Gap(
        pillar="Security & Privacy by Design",
        rule_id="6.2",
        title="Hardcoded Secrets",
        description="Found API key in config",
        severity=SeverityLevel.HIGH,
        effort=EffortLevel.MEDIUM
    )

    design_output = DesignOutput(
        project_id=1,
        findings=["Finding 1", "Finding 2"],
        proposed_requirements=[req],
        gaps_identified=[gap],
        blockers=[]
    )

    adapter = AsyncMock(spec=DesignerAdapter)
    adapter.run = AsyncMock(return_value=design_output)
    return adapter


@pytest.mark.asyncio
async def test_designer_output_structure(mock_designer_adapter):
    """Test designer output has expected structure."""
    design_input = DesignInput(
        project_id=1,
        project_path="/test",
        project_name="test",
        tech_stack="Python FastAPI"
    )

    output = await mock_designer_adapter.run(design_input)

    assert output.project_id == 1
    assert len(output.findings) > 0
    assert len(output.proposed_requirements) > 0
    assert len(output.gaps_identified) > 0


@pytest.mark.asyncio
async def test_tracker_file_design_findings(mock_tracker_adapter):
    """Test tracker adapter files design findings."""
    req = Requirement(
        req_id="FR-001",
        title="Auth",
        description="JWT",
        req_type=RequirementType.FUNCTIONAL
    )

    gap = Gap(
        pillar="Security",
        title="Secrets",
        description="Keys",
        severity=SeverityLevel.HIGH,
        effort=EffortLevel.MEDIUM
    )

    design_output = DesignOutput(
        project_id=1,
        findings=["Finding"],
        proposed_requirements=[req],
        gaps_identified=[gap],
        blockers=[]
    )

    result = await mock_tracker_adapter.file_design_findings(1, design_output)

    assert result is True
    mock_tracker_adapter.file_design_findings.assert_called_once()


@pytest.mark.asyncio
async def test_coordinator_workflow_with_mocks(
    coordinator_config, mock_designer_adapter, mock_tracker_adapter
):
    """Test full coordinator workflow with mocked adapters."""
    coordinator = OrchestratorCoordinator(coordinator_config)
    coordinator.set_adapters(
        designer=mock_designer_adapter,
        implementer=None,  # Not used in this test
        verifier=None,     # Not used in this test
        tracker=mock_tracker_adapter
    )

    # Run design phase
    design_output = await coordinator._execute_design_phase()

    assert design_output is not None
    assert len(design_output.proposed_requirements) > 0
    assert len(design_output.gaps_identified) > 0

    # Verify tracker was called
    mock_tracker_adapter.file_design_findings.assert_called_once()


@pytest.mark.asyncio
async def test_coordinator_design_gate_pass(
    coordinator_config, mock_designer_adapter, mock_tracker_adapter
):
    """Test design gate passes when no blockers."""
    coordinator = OrchestratorCoordinator(coordinator_config)
    coordinator.set_adapters(
        designer=mock_designer_adapter,
        implementer=None,
        verifier=None,
        tracker=mock_tracker_adapter
    )

    # Execute design
    await coordinator._execute_design_phase()

    # Check gate (should pass)
    assert coordinator._check_design_gate() is True
    assert coordinator.state_machine.state.phase.value == "Implementation In Progress"


def test_coordinator_resource_check(coordinator_config):
    """Test coordinator checks resources before agent execution."""
    coordinator = OrchestratorCoordinator(coordinator_config)

    # Get resource status
    can_run, reason = coordinator.resource_monitor.can_run_agent()

    # Should return tuple
    assert isinstance(can_run, bool)
    assert reason is None or isinstance(reason, str)


def test_coordinator_get_state_summary(coordinator_config):
    """Test coordinator provides state summary."""
    coordinator = OrchestratorCoordinator(coordinator_config)

    state = coordinator.get_state()

    assert state.project_name == "test_project"
    assert state.phase.value == "Proposed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
