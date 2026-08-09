"""Main orchestrator coordinator: manages agent orchestration and workflow."""

import logging
import asyncio
from typing import Optional
from orchestrator.config import OrchestratorConfig
from orchestrator.state_machine import WorkflowStateMachine
from orchestrator.resource_monitor import ResourceMonitor, ResourceThresholds, ResourceExhausted
from orchestrator.schemas import (
    DesignInput, DesignOutput,
    ImplementerInput, ImplementerOutput,
    VerifierInput, VerifierOutput,
    ProjectState, ProjectPhase
)

logger = logging.getLogger(__name__)


class OrchestratorCoordinator:
    """Orchestrates designer → implementer → verifier workflow.

    Responsibilities:
    - Manage project state machine (Proposed → Complete)
    - Execute agents sequentially (synchronous)
    - Enforce gate logic (block on critical blockers)
    - Track all findings/requirements/gaps
    - Integrate with tracker (file findings)
    """

    def __init__(self, config: OrchestratorConfig, resource_thresholds: Optional[ResourceThresholds] = None):
        """Initialize coordinator with config.

        Args:
            config: Orchestrator configuration
            resource_thresholds: Custom resource thresholds, or default if None
        """
        self.config = config
        self.state_machine = WorkflowStateMachine(
            project_id=getattr(config, '_project_id', 0),  # Will be set per-project
            project_name=config.project_name
        )
        self.resource_monitor = ResourceMonitor(resource_thresholds)
        self._designer_adapter = None
        self._implementer_adapter = None
        self._verifier_adapter = None
        self._tracker_adapter = None

    def set_project(self, project_id: int, project_name: str):
        """Set the project being orchestrated."""
        self.state_machine = WorkflowStateMachine(project_id, project_name)
        self.config.project_name = project_name

    def set_adapters(self, designer, implementer, verifier, tracker):
        """Inject agent and tracker adapters (for testing/DI)."""
        self._designer_adapter = designer
        self._implementer_adapter = implementer
        self._verifier_adapter = verifier
        self._tracker_adapter = tracker

    async def run_workflow(self) -> ProjectState:
        """Execute full workflow: design → implement → verify.

        Returns:
            ProjectState: Final project state after all phases

        Raises:
            RuntimeError: If workflow cannot proceed due to blockers or errors
        """
        logger.info(f"Starting workflow for project: {self.config.project_name}")

        try:
            # Phase 1: Design
            design_output = await self._execute_design_phase()
            if not design_output:
                raise RuntimeError("Design phase failed")

            # Check design gate
            if not self._check_design_gate():
                logger.warning("Design gate failed; project has blockers")
                return self.state_machine.get_current_state()

            # Phase 2: Implementation
            implementer_output = await self._execute_implementation_phase(design_output)
            if not implementer_output:
                raise RuntimeError("Implementation phase failed")

            # Check implementation gate
            if not self._check_implementation_gate():
                logger.warning("Implementation gate failed; project has blockers")
                return self.state_machine.get_current_state()

            # Phase 3: Verification
            verifier_output = await self._execute_verification_phase(design_output, implementer_output)
            if not verifier_output:
                raise RuntimeError("Verification phase failed")

            # Check verification gate
            if not self._check_verification_gate(verifier_output):
                logger.warning("Verification gate failed; project has blockers")
                return self.state_machine.get_current_state()

            logger.info(f"Workflow complete for project: {self.config.project_name}")
            return self.state_machine.get_current_state()

        except Exception as e:
            logger.error(f"Workflow failed: {e}", exc_info=True)
            raise

    async def _execute_design_phase(self) -> Optional[DesignOutput]:
        """Execute designer agent.

        Returns:
            DesignOutput: Designer findings, or None if failed
        """
        logger.info("Design phase: checking resources (HARDENED)")
        logger.info(f"Resources: {self.resource_monitor.get_status_summary()}")

        # LEVEL 1: Pre-flight check
        can_run, reason = self.resource_monitor.can_run_agent()
        if not can_run:
            logger.critical(f"Resources unsafe. Cannot run designer: {reason}")
            return None

        self.state_machine.start_design()

        # LEVEL 2: Start continuous monitoring
        monitor_task = await self.resource_monitor.monitor_during_execution(
            agent_name="Designer",
            timeout_seconds=300  # 5 minutes max
        )

        if not self._designer_adapter:
            raise RuntimeError("Designer adapter not set")

        try:
            design_input = DesignInput(
                project_id=self.state_machine.state.project_id,
                project_path=self.config.project_path,
                project_name=self.config.project_name,
                tech_stack=getattr(self.config, 'tech_stack', 'Unknown'),
                framework=self.config.framework,
                context={}
            )

            design_output = await asyncio.wait_for(
                self._designer_adapter.run(design_input),
                timeout=300
            )
            logger.info(f"Design phase complete: {len(design_output.findings)} findings")

            # File to tracker
            if self._tracker_adapter and self.config.tracker.auto_create_requirements:
                await self._tracker_adapter.file_design_findings(
                    self.state_machine.state.project_id,
                    design_output
                )

            self.state_machine.complete_design(design_output)
            return design_output

        except ResourceExhausted as e:
            logger.critical(f"Design phase: resource exhausted: {e}")
            return None

        except asyncio.TimeoutError:
            logger.critical(f"Design phase: timed out (300s)")
            return None

        except Exception as e:
            logger.error(f"Design phase failed: {e}", exc_info=True)
            return None

        finally:
            # Always cleanup monitoring
            await self.resource_monitor.cleanup()

    async def _execute_implementation_phase(self, design_output: DesignOutput) -> Optional[ImplementerOutput]:
        """Execute implementer agent.

        Args:
            design_output: Designer findings to guide implementation

        Returns:
            ImplementerOutput: Implementation details, or None if failed
        """
        logger.info("Implementation phase: checking resources (HARDENED)")
        logger.info(f"Resources: {self.resource_monitor.get_status_summary()}")

        # LEVEL 1: Pre-flight check
        can_run, reason = self.resource_monitor.can_run_agent()
        if not can_run:
            logger.critical(f"Resources unsafe. Cannot run implementer: {reason}")
            return None

        if not self._implementer_adapter:
            raise RuntimeError("Implementer adapter not set")

        # LEVEL 2: Start continuous monitoring
        monitor_task = await self.resource_monitor.monitor_during_execution(
            agent_name="Implementer",
            timeout_seconds=600  # 10 minutes max
        )

        try:
            implementer_input = ImplementerInput(
                project_id=self.state_machine.state.project_id,
                project_path=self.config.project_path,
                design_findings=design_output,
                target_requirements=design_output.proposed_requirements,
                test_framework="pytest",
            )

            implementer_output = await asyncio.wait_for(
                self._implementer_adapter.run(implementer_input),
                timeout=600
            )
            logger.info(f"Implementation phase complete: {len(implementer_output.code_changes)} changes")

            # File to tracker
            if self._tracker_adapter and self.config.tracker.auto_create_gaps:
                await self._tracker_adapter.file_implementation_findings(
                    self.state_machine.state.project_id,
                    implementer_output
                )

            self.state_machine.complete_implementation(implementer_output)
            return implementer_output

        except ResourceExhausted as e:
            logger.critical(f"Implementation phase: resource exhausted: {e}")
            return None

        except asyncio.TimeoutError:
            logger.critical(f"Implementation phase: timed out (600s)")
            return None

        except Exception as e:
            logger.error(f"Implementation phase failed: {e}", exc_info=True)
            return None

        finally:
            # Always cleanup monitoring
            await self.resource_monitor.cleanup()

    async def _execute_verification_phase(
        self, design_output: DesignOutput, implementer_output: ImplementerOutput
    ) -> Optional[VerifierOutput]:
        """Execute verifier agent.

        Args:
            design_output: Original design for comparison
            implementer_output: Implementation to verify

        Returns:
            VerifierOutput: Verification results, or None if failed
        """
        logger.info("Verification phase: checking resources (HARDENED)")
        logger.info(f"Resources: {self.resource_monitor.get_status_summary()}")

        # LEVEL 1: Pre-flight check
        can_run, reason = self.resource_monitor.can_run_agent()
        if not can_run:
            logger.critical(f"Resources unsafe. Cannot run verifier: {reason}")
            return None

        if not self._verifier_adapter:
            raise RuntimeError("Verifier adapter not set")

        # LEVEL 2: Start continuous monitoring
        monitor_task = await self.resource_monitor.monitor_during_execution(
            agent_name="Verifier",
            timeout_seconds=900  # 15 minutes max
        )

        try:
            verifier_input = VerifierInput(
                project_id=self.state_machine.state.project_id,
                project_path=self.config.project_path,
                code_changes=implementer_output.code_changes,
                original_requirements=design_output.proposed_requirements,
                framework=self.config.framework,
            )

            verifier_output = await asyncio.wait_for(
                self._verifier_adapter.run(verifier_input),
                timeout=900
            )
            logger.info(f"Verification phase complete: approved={verifier_output.approved}")

            # File to tracker
            if self._tracker_adapter and self.config.tracker.auto_create_gaps:
                await self._tracker_adapter.file_verification_findings(
                    self.state_machine.state.project_id,
                    verifier_output
                )

            return verifier_output

        except ResourceExhausted as e:
            logger.critical(f"Verification phase: resource exhausted: {e}")
            return None

        except asyncio.TimeoutError:
            logger.critical(f"Verification phase: timed out (900s)")
            return None

        except Exception as e:
            logger.error(f"Verification phase failed: {e}", exc_info=True)
            return None

        finally:
            # Always cleanup monitoring
            await self.resource_monitor.cleanup()

    def _check_design_gate(self) -> bool:
        """Check if design phase passed gate (no critical blockers).

        Returns:
            True if gate passes (proceed to implementation), False otherwise
        """
        state = self.state_machine.get_current_state()

        if not state.designer_output:
            logger.warning("No design output to gate")
            return False

        blockers = state.designer_output.blockers
        if blockers:
            logger.warning(f"Design gate failed: {len(blockers)} blockers")
            self.state_machine.state.blockers = blockers
            return False

        logger.info("Design gate passed")
        return self.state_machine.pass_design_gate()

    def _check_implementation_gate(self) -> bool:
        """Check if implementation phase passed gate.

        Returns:
            True if gate passes, False otherwise
        """
        state = self.state_machine.get_current_state()

        if not state.implementer_output:
            logger.warning("No implementation output to gate")
            return False

        blockers = state.implementer_output.blockers
        if blockers:
            logger.warning(f"Implementation gate failed: {len(blockers)} blockers")
            self.state_machine.state.blockers = blockers
            return False

        logger.info("Implementation gate passed")
        return True  # Stay in verification gate phase

    def _check_verification_gate(self, verifier_output: VerifierOutput) -> bool:
        """Check if verification phase passed gate.

        Args:
            verifier_output: Verification findings

        Returns:
            True if gate passes (complete), False otherwise
        """
        blockers = verifier_output.blockers

        if not verifier_output.approved:
            logger.warning(f"Verification gate failed: not approved")
            self.state_machine.state.blockers = blockers
            return False

        if blockers:
            logger.warning(f"Verification gate failed: {len(blockers)} blockers")
            self.state_machine.state.blockers = blockers
            return False

        logger.info("Verification gate passed")
        return self.state_machine.pass_verification_gate(verifier_output)

    def get_state(self) -> ProjectState:
        """Get current project state."""
        return self.state_machine.get_current_state()
