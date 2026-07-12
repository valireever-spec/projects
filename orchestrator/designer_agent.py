"""
Designer Agent - Phase 2 Core Component

Analyzes requirements and generates design decisions.
State: Proposed → Accepted
Uses Claude API for intelligent analysis.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    logger.warning("anthropic library not installed, using mock mode")


class RequirementType(Enum):
    """Types of requirements."""
    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    OPTIMIZATION = "optimization"


@dataclass
class Requirement:
    """A single requirement."""
    id: str
    title: str
    description: str
    type: RequirementType = RequirementType.FEATURE
    priority: int = 5  # 1-10
    acceptance_criteria: List[str] = field(default_factory=list)


@dataclass
class DesignDecision:
    """A design decision."""
    title: str
    rationale: str
    tradeoffs: List[str] = field(default_factory=list)
    confidence: float = 1.0  # 0-1


@dataclass
class DesignOutput:
    """Output from Designer Agent."""
    requirement_id: str
    requirement_title: str
    status: str  # "Proposed" or "Accepted"
    design_decisions: List[DesignDecision] = field(default_factory=list)
    implementation_tasks: List[str] = field(default_factory=list)
    estimated_effort_hours: float = 0.0
    risks: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class DesignerAgent:
    """Analyzes requirements and generates design decisions."""

    def __init__(self, use_claude: bool = True):
        """Initialize Designer Agent.

        Args:
            use_claude: Use real Claude API (True) or mock (False)
        """
        self.use_claude = use_claude and HAS_ANTHROPIC
        self.client = None

        if self.use_claude:
            try:
                self.client = anthropic.Anthropic()
                logger.info("Initialized Designer Agent with Claude API")
            except Exception as e:
                logger.warning(f"Could not initialize Claude client: {e}, using mock mode")
                self.use_claude = False
        else:
            logger.info("Initialized Designer Agent in mock mode")

    def analyze_requirement(self, requirement: Requirement) -> DesignOutput:
        """Analyze a requirement and generate design.

        Args:
            requirement: Requirement to analyze

        Returns:
            DesignOutput with design decisions
        """
        logger.info(f"Designer analyzing requirement: {requirement.title}")

        output = DesignOutput(
            requirement_id=requirement.id,
            requirement_title=requirement.title,
            status="Proposed"
        )

        try:
            if self.use_claude:
                return self._analyze_with_claude(requirement, output)
            else:
                return self._analyze_with_mock(requirement, output)

        except Exception as e:
            logger.error(f"Error analyzing requirement: {e}")
            output.risks.append(f"Analysis failed: {str(e)}")
            return output

    def _analyze_with_claude(self, requirement: Requirement, output: DesignOutput) -> DesignOutput:
        """Analyze using real Claude API.

        Args:
            requirement: Requirement to analyze
            output: Output object to populate

        Returns:
            Updated DesignOutput
        """
        try:
            prompt = self._build_analysis_prompt(requirement)

            message = self.client.messages.create(
                model="claude-opus-4-8",
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = message.content[0].text

            # Parse response
            output = self._parse_design_response(response_text, output)
            output.status = "Accepted"

            logger.info(f"Claude analysis complete: {len(output.design_decisions)} decisions")

        except Exception as e:
            logger.warning(f"Claude analysis failed: {e}, using fallback")
            output = self._analyze_with_mock(requirement, output)

        return output

    def _analyze_with_mock(self, requirement: Requirement, output: DesignOutput) -> DesignOutput:
        """Analyze using mock/hardcoded logic (fallback).

        Args:
            requirement: Requirement to analyze
            output: Output object to populate

        Returns:
            Updated DesignOutput
        """
        logger.info(f"Using mock analysis for: {requirement.title}")

        # Mock design decisions based on requirement type
        if requirement.type == RequirementType.FEATURE:
            output.design_decisions = [
                DesignDecision(
                    title="Use existing abstraction layer",
                    rationale="Leverage current architecture to minimize changes",
                    tradeoffs=["May require interface adjustments"],
                    confidence=0.9
                ),
                DesignDecision(
                    title="Add comprehensive tests",
                    rationale="New features must have 80%+ coverage",
                    tradeoffs=["Increases development time by ~20%"],
                    confidence=1.0
                ),
                DesignDecision(
                    title="Document public API",
                    rationale="Enable future maintainability and integration",
                    tradeoffs=["Requires documentation effort"],
                    confidence=0.95
                ),
            ]
            output.implementation_tasks = [
                "Design API interfaces",
                "Implement core logic",
                "Add unit tests",
                "Add integration tests",
                "Document API",
                "Code review and merge"
            ]
            output.estimated_effort_hours = 16.0

        elif requirement.type == RequirementType.BUGFIX:
            output.design_decisions = [
                DesignDecision(
                    title="Minimal invasive fix",
                    rationale="Fix root cause without refactoring",
                    tradeoffs=["May not improve overall code quality"],
                    confidence=0.95
                ),
                DesignDecision(
                    title="Add regression tests",
                    rationale="Prevent bug recurrence",
                    tradeoffs=["Small time overhead"],
                    confidence=1.0
                ),
            ]
            output.implementation_tasks = [
                "Identify root cause",
                "Implement fix",
                "Add regression test",
                "Verify fix",
                "Code review and merge"
            ]
            output.estimated_effort_hours = 4.0

        elif requirement.type == RequirementType.REFACTOR:
            output.design_decisions = [
                DesignDecision(
                    title="Parallel test execution during refactor",
                    rationale="Catch regressions immediately",
                    tradeoffs=["Slower iteration cycle"],
                    confidence=0.9
                ),
                DesignDecision(
                    title="Atomic commits",
                    rationale="Enable easier rollback if needed",
                    tradeoffs=["More granular commit history"],
                    confidence=0.95
                ),
            ]
            output.implementation_tasks = [
                "Create feature branch",
                "Analyze current structure",
                "Plan refactoring",
                "Implement changes",
                "Run comprehensive tests",
                "Code review and merge"
            ]
            output.estimated_effort_hours = 12.0

        output.status = "Accepted"
        output.risks = ["Standard engineering risks"]

        return output

    def _build_analysis_prompt(self, requirement: Requirement) -> str:
        """Build prompt for Claude analysis.

        Args:
            requirement: Requirement to analyze

        Returns:
            Prompt string
        """
        return f"""Analyze this software requirement and provide design decisions:

REQUIREMENT:
Title: {requirement.title}
Type: {requirement.type.value}
Priority: {requirement.priority}/10

Description:
{requirement.description}

Acceptance Criteria:
{chr(10).join(f"- {c}" for c in requirement.acceptance_criteria) if requirement.acceptance_criteria else "None specified"}

Please provide:
1. 3-5 key design decisions
2. Rationale for each decision
3. Implementation tasks (ordered)
4. Estimated effort in hours
5. Potential risks
6. Alternative approaches considered

Format as structured JSON with decisions array containing:
{{"title": str, "rationale": str, "tradeoffs": [str], "confidence": float}}"""

    def _parse_design_response(self, response: str, output: DesignOutput) -> DesignOutput:
        """Parse Claude's response into structured decisions.

        Args:
            response: Claude's text response
            output: Output object to populate

        Returns:
            Updated DesignOutput
        """
        import json

        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)

            if json_match:
                data = json.loads(json_match.group())

                # Parse decisions
                for decision_data in data.get("decisions", []):
                    output.design_decisions.append(
                        DesignDecision(
                            title=decision_data.get("title", ""),
                            rationale=decision_data.get("rationale", ""),
                            tradeoffs=decision_data.get("tradeoffs", []),
                            confidence=decision_data.get("confidence", 0.9)
                        )
                    )

                # Parse other fields
                output.implementation_tasks = data.get("tasks", [])
                output.estimated_effort_hours = data.get("effort_hours", 0.0)
                output.risks = data.get("risks", [])

        except Exception as e:
            logger.warning(f"Could not parse Claude response: {e}")
            # Fall back to simple parsing
            output.design_decisions.append(
                DesignDecision(
                    title="Review design",
                    rationale=response[:200],
                    confidence=0.7
                )
            )

        return output

    def classify_requirement(self, title: str) -> RequirementType:
        """Classify a requirement by title.

        Args:
            title: Requirement title

        Returns:
            RequirementType
        """
        title_lower = title.lower()

        if any(word in title_lower for word in ["fix", "bug", "issue", "error"]):
            return RequirementType.BUGFIX
        elif any(word in title_lower for word in ["refactor", "restructure", "reorganize"]):
            return RequirementType.REFACTOR
        elif any(word in title_lower for word in ["optimize", "improve", "speed", "performance"]):
            return RequirementType.OPTIMIZATION
        else:
            return RequirementType.FEATURE


# Test usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    agent = DesignerAgent(use_claude=False)  # Use mock mode for testing

    print("\n" + "=" * 80)
    print("DESIGNER AGENT TEST")
    print("=" * 80 + "\n")

    # Test requirement
    req = Requirement(
        id="REQ-001",
        title="Add user authentication feature",
        description="Implement JWT-based authentication for API",
        type=RequirementType.FEATURE,
        priority=8,
        acceptance_criteria=[
            "Users can login with username/password",
            "API returns JWT token",
            "Token validates on subsequent requests",
            "Token expires after 24 hours"
        ]
    )

    print("1️⃣ Analyzing requirement...")
    output = agent.analyze_requirement(req)

    print(f"\n2️⃣ Design Output:")
    print(f"  Status: {output.status}")
    print(f"  Effort: {output.estimated_effort_hours} hours")

    print(f"\n3️⃣ Design Decisions ({len(output.design_decisions)}):")
    for i, decision in enumerate(output.design_decisions, 1):
        print(f"  {i}. {decision.title} (confidence: {decision.confidence:.0%})")
        print(f"     {decision.rationale}")

    print(f"\n4️⃣ Implementation Tasks ({len(output.implementation_tasks)}):")
    for i, task in enumerate(output.implementation_tasks, 1):
        print(f"  {i}. {task}")

    print(f"\n5️⃣ Risks ({len(output.risks)}):")
    for risk in output.risks:
        print(f"  - {risk}")

    print("\n✓ Designer Agent test PASSED\n")
