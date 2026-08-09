"""Designer agent adapter: Claude integration."""

import logging
import os
from typing import Optional
from anthropic import Anthropic
from orchestrator.schemas import DesignInput, DesignOutput, Requirement, RequirementType, Gap, SeverityLevel, EffortLevel, PillarAssessment
from orchestrator.config import AgentConfig

logger = logging.getLogger(__name__)


class DesignerAdapter:
    """Adapter for Designer agent using Claude."""

    def __init__(self, config: AgentConfig):
        """Initialize designer adapter.

        Args:
            config: AgentConfig with model, timeout, etc.
        """
        self.config = config
        self.model = config.model
        self.timeout = config.timeout_seconds

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)

    async def run(self, design_input: DesignInput) -> DesignOutput:
        """Run designer agent against a project.

        Args:
            design_input: Design task input

        Returns:
            DesignOutput with findings, requirements, gaps, assessments
        """
        logger.info(f"Designer: Starting analysis of {design_input.project_name}")

        # Build prompt
        prompt = self._build_prompt(design_input)

        try:
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse response
            design_output = self._parse_response(response.content[0].text, design_input)
            logger.info(f"Designer: Analysis complete. {len(design_output.proposed_requirements)} requirements, {len(design_output.gaps_identified)} gaps")

            return design_output

        except Exception as e:
            logger.error(f"Designer failed: {e}", exc_info=True)
            # Return empty output on failure (coordinator will handle)
            return DesignOutput(project_id=design_input.project_id)

    def _build_prompt(self, design_input: DesignInput) -> str:
        """Build Claude prompt for design analysis."""
        return f"""You are a software architecture designer. Analyze the following project and provide:
1. High-level findings about the codebase
2. Proposed requirements for improvement
3. Identified gaps/issues
4. Assessment of CSF pillars (if CSF-21 framework)
5. Risk assessment
6. Next steps for implementation

Project Information:
- Name: {design_input.project_name}
- Path: {design_input.project_path}
- Tech Stack: {design_input.tech_stack}
- Phase: {design_input.phase}
- Framework: {design_input.framework.value}

Existing Requirements ({len(design_input.existing_requirements)}):
{self._format_list(design_input.existing_requirements)}

Existing Gaps ({len(design_input.existing_gaps)}):
{self._format_list(design_input.existing_gaps)}

Additional Context:
{self._format_dict(design_input.context)}

{f"Focus Area: {design_input.focus_area}" if design_input.focus_area else ""}

Provide your analysis in the following JSON format:
{{
    "findings": ["finding1", "finding2", ...],
    "proposed_requirements": [
        {{"req_id": "FR-001", "title": "...", "description": "...", "req_type": "Functional", "category": "...", "acceptance_criteria": "..."}},
        ...
    ],
    "gaps_identified": [
        {{"pillar": "Security & Privacy", "rule_id": "6.2", "title": "...", "description": "...", "severity": "High", "effort": "Medium"}},
        ...
    ],
    "pillar_assessments": {{
        "Security & Privacy by Design": {{"score": 75, "status": "Partial", "gaps": [...], "evidence": "..."}},
        ...
    }},
    "risk_assessment": {{"critical": [...], "high": [...], "medium": [...]}},
    "next_steps": ["step1", "step2", ...],
    "blockers": ["blocker1", "blocker2", ...]
}}

Focus on:
- Architecture quality and CSF pillar compliance
- Security issues (hardcoded secrets, injection vulnerabilities, CORS, etc.)
- Test coverage and quality gates
- Performance and scalability risks
- Dependency management and version pinning
- Error handling and observability

Respond ONLY with valid JSON, no markdown formatting or extra text."""

    def _parse_response(self, response_text: str, design_input: DesignInput) -> DesignOutput:
        """Parse Claude response into DesignOutput.

        Args:
            response_text: Claude's response (should be JSON)
            design_input: Original input for reference

        Returns:
            DesignOutput object
        """
        import json

        try:
            # Parse JSON response
            data = json.loads(response_text)

            # Extract fields
            findings = data.get("findings", [])
            risk_assessment = data.get("risk_assessment", {})
            next_steps = data.get("next_steps", [])
            blockers = data.get("blockers", [])

            # Parse proposed requirements
            proposed_requirements = []
            for req_data in data.get("proposed_requirements", []):
                try:
                    req = Requirement(
                        req_id=req_data.get("req_id", "FR-000"),
                        title=req_data.get("title", ""),
                        description=req_data.get("description", ""),
                        req_type=RequirementType(req_data.get("req_type", "Functional")),
                        category=req_data.get("category"),
                        acceptance_criteria=req_data.get("acceptance_criteria"),
                        measurement_method=req_data.get("measurement_method"),
                        target=req_data.get("target"),
                    )
                    proposed_requirements.append(req)
                except Exception as e:
                    logger.warning(f"Failed to parse requirement: {e}")

            # Parse gaps
            gaps_identified = []
            for gap_data in data.get("gaps_identified", []):
                try:
                    gap = Gap(
                        pillar=gap_data.get("pillar", "Unknown"),
                        rule_id=gap_data.get("rule_id"),
                        title=gap_data.get("title", ""),
                        description=gap_data.get("description", ""),
                        severity=SeverityLevel(gap_data.get("severity", "Medium")),
                        effort=EffortLevel(gap_data.get("effort", "Medium")),
                    )
                    gaps_identified.append(gap)
                except Exception as e:
                    logger.warning(f"Failed to parse gap: {e}")

            # Parse pillar assessments
            pillar_assessments = {}
            for pillar_name, assessment_data in data.get("pillar_assessments", {}).items():
                try:
                    assessment = PillarAssessment(
                        pillar_name=pillar_name,
                        score=assessment_data.get("score"),
                        status=assessment_data.get("status", "Gap"),
                        gaps=assessment_data.get("gaps", []),
                        evidence=assessment_data.get("evidence"),
                    )
                    pillar_assessments[pillar_name] = assessment
                except Exception as e:
                    logger.warning(f"Failed to parse pillar assessment: {e}")

            # Build output
            output = DesignOutput(
                project_id=design_input.project_id,
                findings=findings,
                proposed_requirements=proposed_requirements,
                gaps_identified=gaps_identified,
                pillar_assessments=pillar_assessments,
                risk_assessment=risk_assessment,
                next_steps=next_steps,
                blockers=blockers,
            )

            return output

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            # Return empty output on parse failure
            return DesignOutput(project_id=design_input.project_id, blockers=["Parse error in Claude response"])

    @staticmethod
    def _format_list(items: list) -> str:
        """Format list for prompt."""
        if not items:
            return "None"
        return "\n".join(f"- {item}" for item in items[:5])

    @staticmethod
    def _format_dict(d: dict) -> str:
        """Format dict for prompt."""
        if not d:
            return "None"
        return "\n".join(f"- {k}: {v}" for k, v in list(d.items())[:5])
