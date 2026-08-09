"""Workflow state machine for orchestrator."""

from typing import Optional, List
from orchestrator.schemas import ProjectPhase, ProjectState, DesignOutput, ImplementerOutput, VerifierOutput


class WorkflowStateMachine:
    """Manages project workflow state transitions and gate logic."""

    def __init__(self, project_id: int, project_name: str):
        self.project_id = project_id
        self.project_name = project_name
        self.state = ProjectState(
            project_id=project_id,
            project_name=project_name,
            phase=ProjectPhase.PROPOSED
        )

    def start_design(self) -> bool:
        """Transition from PROPOSED to DESIGN_IN_PROGRESS."""
        if self.state.phase != ProjectPhase.PROPOSED:
            return False

        self.state.phase = ProjectPhase.DESIGN_IN_PROGRESS
        return True

    def complete_design(self, designer_output: DesignOutput) -> bool:
        """Transition to DESIGN_REVIEW_GATE after designer completes."""
        if self.state.phase != ProjectPhase.DESIGN_IN_PROGRESS:
            return False

        self.state.designer_output = designer_output
        self.state.blockers = designer_output.blockers
        self.state.phase = ProjectPhase.DESIGN_REVIEW_GATE
        return True

    def pass_design_gate(self) -> bool:
        """Transition from DESIGN_REVIEW_GATE to IMPLEMENTATION_IN_PROGRESS (no blockers)."""
        if self.state.phase != ProjectPhase.DESIGN_REVIEW_GATE:
            return False

        if self.state.blockers:
            return False  # Gate fails; stay in review

        self.state.phase = ProjectPhase.IMPLEMENTATION_IN_PROGRESS
        return True

    def fail_design_gate(self) -> bool:
        """Transition back to DESIGN_IN_PROGRESS if blockers found."""
        if self.state.phase != ProjectPhase.DESIGN_REVIEW_GATE:
            return False

        if not self.state.blockers:
            return False  # No blockers; can't fail gate

        self.state.phase = ProjectPhase.DESIGN_IN_PROGRESS
        return True

    def complete_implementation(self, implementer_output: ImplementerOutput) -> bool:
        """Transition to VERIFICATION_GATE after implementer completes."""
        if self.state.phase != ProjectPhase.IMPLEMENTATION_IN_PROGRESS:
            return False

        self.state.implementer_output = implementer_output
        self.state.blockers = implementer_output.blockers
        self.state.phase = ProjectPhase.VERIFICATION_GATE
        return True

    def pass_verification_gate(self, verifier_output: VerifierOutput) -> bool:
        """Transition from VERIFICATION_GATE to COMPLETE (no blockers)."""
        if self.state.phase != ProjectPhase.VERIFICATION_GATE:
            return False

        self.state.verifier_output = verifier_output
        self.state.blockers = verifier_output.blockers

        if self.state.blockers:
            return False  # Gate fails; stay in verification

        self.state.phase = ProjectPhase.COMPLETE
        return True

    def fail_verification_gate(self) -> bool:
        """Transition back to IMPLEMENTATION_IN_PROGRESS if blockers found."""
        if self.state.phase != ProjectPhase.VERIFICATION_GATE:
            return False

        if not self.state.blockers:
            return False  # No blockers; can't fail gate

        self.state.phase = ProjectPhase.IMPLEMENTATION_IN_PROGRESS
        return True

    def get_current_state(self) -> ProjectState:
        """Return current project state."""
        return self.state

    def can_proceed_to_implementation(self) -> bool:
        """Check if project is ready to move to implementation."""
        return (
            self.state.phase == ProjectPhase.DESIGN_REVIEW_GATE
            and len(self.state.blockers) == 0
        )

    def can_proceed_to_completion(self) -> bool:
        """Check if project is ready to complete."""
        return (
            self.state.phase == ProjectPhase.VERIFICATION_GATE
            and len(self.state.blockers) == 0
        )
