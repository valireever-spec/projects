"""Integration adapter for tracker service."""

import logging
from typing import Optional
import httpx
from orchestrator.config import TrackerConfig
from orchestrator.schemas import (
    DesignOutput, ImplementerOutput, VerifierOutput, Requirement, Gap, SeverityLevel
)

logger = logging.getLogger(__name__)


class TrackerAdapter:
    """HTTP client for tracker API integration."""

    def __init__(self, config: TrackerConfig):
        """Initialize adapter with tracker config."""
        self.config = config
        self.base_url = config.url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=config.timeout_seconds)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def file_design_findings(self, project_id: int, design_output: DesignOutput) -> bool:
        """File designer findings to tracker.

        Args:
            project_id: Project ID in tracker
            design_output: Design findings from designer agent

        Returns:
            True if successful, False otherwise
        """
        try:
            # File proposed requirements
            for req in design_output.proposed_requirements:
                await self._create_requirement(project_id, req)

            # File discovered gaps
            for gap in design_output.gaps_identified:
                await self._create_gap(project_id, gap)

            # Update scorecard with pillar assessments
            for pillar_name, assessment in design_output.pillar_assessments.items():
                await self._update_scorecard(project_id, pillar_name, assessment.status, assessment.evidence or "")

            logger.info(f"Filed design findings for project {project_id}: {len(design_output.proposed_requirements)} requirements, {len(design_output.gaps_identified)} gaps")
            return True

        except Exception as e:
            logger.error(f"Failed to file design findings: {e}", exc_info=True)
            return False

    async def file_implementation_findings(self, project_id: int, impl_output: ImplementerOutput) -> bool:
        """File implementer findings to tracker.

        Args:
            project_id: Project ID in tracker
            impl_output: Implementation findings from implementer agent

        Returns:
            True if successful, False otherwise
        """
        try:
            # File gaps discovered during implementation
            for gap in impl_output.gaps_created:
                await self._create_gap(project_id, gap)

            logger.info(f"Filed implementation findings for project {project_id}: {len(impl_output.gaps_created)} new gaps")
            return True

        except Exception as e:
            logger.error(f"Failed to file implementation findings: {e}", exc_info=True)
            return False

    async def file_verification_findings(self, project_id: int, verifier_output: VerifierOutput) -> bool:
        """File verifier findings to tracker.

        Args:
            project_id: Project ID in tracker
            verifier_output: Verification findings from verifier agent

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update requirement validations
            for req_val in verifier_output.requirement_validation:
                status = "Implemented" if req_val.passed else "Proposed"
                await self._update_requirement_status(project_id, req_val.req_id, status)

            # File gaps found during verification
            for gap in verifier_output.gaps_found + verifier_output.security_findings + verifier_output.quality_findings:
                await self._create_gap(project_id, gap)

            # Update scorecard with CSF assessment
            for pillar_name, assessment in verifier_output.csf_assessment.items():
                await self._update_scorecard(project_id, pillar_name, assessment.status, assessment.evidence or "")

            logger.info(f"Filed verification findings for project {project_id}: {len(verifier_output.requirement_validation)} requirements validated")
            return True

        except Exception as e:
            logger.error(f"Failed to file verification findings: {e}", exc_info=True)
            return False

    async def _create_requirement(self, project_id: int, requirement: Requirement) -> Optional[dict]:
        """Create requirement in tracker.

        Args:
            project_id: Project ID in tracker
            requirement: Requirement to create

        Returns:
            Response dict or None if failed
        """
        try:
            payload = {
                "req_id": requirement.req_id,
                "title": requirement.title,
                "description": requirement.description,
                "req_type": requirement.req_type.value,
                "category": requirement.category,
                "acceptance_criteria": requirement.acceptance_criteria,
                "measurement_method": requirement.measurement_method,
                "target": requirement.target,
                "status": "Proposed",
            }

            response = await self.client.post(
                f"{self.base_url}/api/projects/{project_id}/requirements",
                json=payload
            )

            if response.status_code == 200:
                logger.debug(f"Created requirement {requirement.req_id}")
                return response.json()
            else:
                logger.warning(f"Failed to create requirement {requirement.req_id}: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error creating requirement: {e}", exc_info=True)
            return None

    async def _create_gap(self, project_id: int, gap: Gap) -> Optional[dict]:
        """Create gap in tracker.

        Args:
            project_id: Project ID in tracker
            gap: Gap/bug to create

        Returns:
            Response dict or None if failed
        """
        try:
            payload = {
                "pillar": gap.pillar,
                "rule_id": gap.rule_id,
                "title": gap.title,
                "description": gap.description,
                "status": "Discovered",
                "severity": gap.severity.value,
                "effort": gap.effort.value,
            }

            response = await self.client.post(
                f"{self.base_url}/api/projects/{project_id}/gaps",
                json=payload
            )

            if response.status_code == 200:
                logger.debug(f"Created gap: {gap.title}")
                return response.json()
            else:
                logger.warning(f"Failed to create gap: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error creating gap: {e}", exc_info=True)
            return None

    async def _update_requirement_status(self, project_id: int, req_id: str, status: str) -> bool:
        """Update requirement status in tracker.

        Args:
            project_id: Project ID in tracker
            req_id: Requirement ID (FR-001, etc.)
            status: New status (Proposed, Accepted, Implemented, Validated)

        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {"status": status}
            response = await self.client.put(
                f"{self.base_url}/api/projects/{project_id}/requirements/{req_id}",
                json=payload
            )

            if response.status_code == 200:
                logger.debug(f"Updated requirement {req_id} to {status}")
                return True
            else:
                logger.warning(f"Failed to update requirement {req_id}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error updating requirement: {e}", exc_info=True)
            return False

    async def _update_scorecard(self, project_id: int, pillar: str, status: str, evidence: str) -> bool:
        """Update pillar scorecard in tracker.

        Args:
            project_id: Project ID in tracker
            pillar: Pillar name
            status: Pillar status (Met, Partial, Gap, N/A)
            evidence: Supporting evidence

        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "pillar": pillar,
                "status": status,
                "evidence": evidence,
            }

            response = await self.client.put(
                f"{self.base_url}/api/projects/{project_id}/scorecard",
                json=payload
            )

            if response.status_code == 200:
                logger.debug(f"Updated scorecard for {pillar}")
                return True
            else:
                logger.warning(f"Failed to update scorecard: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error updating scorecard: {e}", exc_info=True)
            return False

    async def fetch_project_state(self, project_id: int) -> Optional[dict]:
        """Fetch current project state from tracker.

        Args:
            project_id: Project ID in tracker

        Returns:
            Project dict or None if failed
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/projects/{project_id}")

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to fetch project: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching project state: {e}", exc_info=True)
            return None
