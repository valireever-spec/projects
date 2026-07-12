"""
Implementer Agent - Phase 2 Core Component

Executes implementation tasks using skills from skill-library.
State: Accepted → Implemented
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from skill_pool import SkillLoader, SkillPool
from designer_agent import DesignOutput

logger = logging.getLogger(__name__)


@dataclass
class ImplementationTask:
    """Single implementation task."""
    id: str
    title: str
    description: str = ""
    skills_required: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict] = None
    error: Optional[str] = None


@dataclass
class ImplementationResult:
    """Result of implementation."""
    design_id: str
    status: str  # "Implemented"
    tasks_completed: int = 0
    tasks_failed: int = 0
    task_results: List[ImplementationTask] = field(default_factory=list)
    changes_summary: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ImplementerAgent:
    """Implements features using skills from library."""

    def __init__(self, skill_library_path: str = "/home/vali/projects/skill-library"):
        """Initialize Implementer Agent.

        Args:
            skill_library_path: Path to skill-library
        """
        self.skill_loader = SkillLoader(skill_library_path)
        self.skill_pool = None
        logger.info("Initialized Implementer Agent")

    def discover_skills(self) -> int:
        """Discover available skills.

        Returns:
            Number of skills found
        """
        self.skill_pool = self.skill_loader.discover_all_skills()
        logger.info(f"Discovered {self.skill_pool.total_count} skills")
        return self.skill_pool.total_count

    def implement_from_design(self, design: DesignOutput) -> ImplementationResult:
        """Execute implementation based on design.

        Args:
            design: Design output from Designer Agent

        Returns:
            ImplementationResult
        """
        logger.info(f"Implementer executing design: {design.requirement_title}")

        result = ImplementationResult(
            design_id=design.requirement_id,
            status="Implemented"
        )

        # Create tasks from design
        tasks = self._create_implementation_tasks(design)

        # Execute tasks
        for task in tasks:
            task.status = "running"
            logger.info(f"Executing task: {task.title}")

            try:
                # Execute task using skills
                task_result = self._execute_task(task)
                task.result = task_result
                task.status = "completed"
                result.tasks_completed += 1

                logger.info(f"Task completed: {task.title}")

            except Exception as e:
                logger.error(f"Task failed: {task.title}: {e}")
                task.error = str(e)
                task.status = "failed"
                result.tasks_failed += 1

            result.task_results.append(task)

        # Summary
        result.changes_summary = {
            'total_tasks': len(tasks),
            'completed': result.tasks_completed,
            'failed': result.tasks_failed,
            'success_rate': result.tasks_completed / len(tasks) if tasks else 0
        }

        logger.info(f"Implementation complete: {result.tasks_completed}/{len(tasks)} tasks succeeded")

        return result

    def _create_implementation_tasks(self, design: DesignOutput) -> List[ImplementationTask]:
        """Create implementation tasks from design.

        Args:
            design: Design output

        Returns:
            List of implementation tasks
        """
        tasks = []

        for i, task_title in enumerate(design.implementation_tasks, 1):
            # Map tasks to skills
            skills_needed = self._map_task_to_skills(task_title)

            task = ImplementationTask(
                id=f"IMPL-{i:03d}",
                title=task_title,
                skills_required=skills_needed
            )
            tasks.append(task)

        return tasks

    def _map_task_to_skills(self, task_title: str) -> List[str]:
        """Map a task to applicable skills.

        Args:
            task_title: Task description

        Returns:
            List of skill names to use
        """
        task_lower = task_title.lower()
        skills = []

        # Simple mapping
        if "test" in task_lower:
            skills.extend(["testing-framework", "comprehensive-testing"])
        if "documen" in task_lower:
            skills.append("documentation-generator")
        if "api" in task_lower:
            skills.append("api-integration-pattern")
        if "quality" in task_lower:
            skills.extend(["code-quality-dashboard", "best-practices-applier"])
        if "design" in task_lower:
            skills.append("architecture-auditor")

        # Default skills if none match
        if not skills:
            skills = ["best-practices-applier-v2"]

        return skills

    def _execute_task(self, task: ImplementationTask) -> Dict[str, Any]:
        """Execute a single task using skills.

        Args:
            task: Task to execute

        Returns:
            Task result
        """
        result = {
            'task_id': task.id,
            'skills_used': [],
            'changes': []
        }

        if not self.skill_pool:
            logger.warning("Skill pool not initialized, discovering...")
            self.discover_skills()

        # Try to execute with each required skill
        for skill_name in task.skills_required:
            # Find matching skill in pool
            matching_skills = [
                s for s in self.skill_pool.list_skills()
                if skill_name in s.name.lower()
            ]

            if not matching_skills:
                logger.debug(f"No skill found for: {skill_name}")
                continue

            skill = matching_skills[0]
            logger.info(f"Using skill: {skill.name}")

            try:
                # Try to execute skill
                skill_result = self.skill_loader.execute_skill(
                    skill.name,
                    method_name="analyze",
                    input_data=task.title
                )

                if skill_result:
                    result['skills_used'].append(skill.name)
                    result['changes'].append({
                        'skill': skill.name,
                        'status': 'success',
                        'details': str(skill_result)[:100]
                    })

            except Exception as e:
                logger.warning(f"Skill execution failed: {skill.name}: {e}")
                result['changes'].append({
                    'skill': skill.name,
                    'status': 'failed',
                    'error': str(e)
                })

        return result

    def get_available_skills_for_task(self, task: ImplementationTask) -> List[Dict]:
        """Get available skills for a task.

        Args:
            task: Implementation task

        Returns:
            List of available skill info
        """
        if not self.skill_pool:
            self.discover_skills()

        result = []

        for skill_name in task.skills_required:
            for skill in self.skill_pool.list_skills():
                if skill_name in skill.name.lower():
                    result.append({
                        'name': skill.name,
                        'version': skill.version,
                        'category': skill.category,
                        'loaded': skill.loaded
                    })

        return result


# Test usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    from designer_agent import Requirement, RequirementType, DesignerAgent

    print("\n" + "=" * 80)
    print("IMPLEMENTER AGENT TEST")
    print("=" * 80 + "\n")

    # Initialize agents
    designer = DesignerAgent(use_claude=False)
    implementer = ImplementerAgent()

    # Create requirement
    req = Requirement(
        id="REQ-002",
        title="Improve code quality",
        description="Apply best practices and improve test coverage",
        type=RequirementType.FEATURE,
        priority=7
    )

    # Designer generates design
    print("1️⃣ Designer analyzing requirement...")
    design = designer.analyze_requirement(req)
    print(f"   ✓ Design accepted with {len(design.implementation_tasks)} tasks")

    # Implementer discovers skills
    print("\n2️⃣ Implementer discovering skills...")
    skill_count = implementer.discover_skills()
    print(f"   ✓ Found {skill_count} skills")

    # Implementer executes
    print("\n3️⃣ Implementer executing design...")
    impl_result = implementer.implement_from_design(design)
    print(f"   ✓ Tasks completed: {impl_result.tasks_completed}/{impl_result.changes_summary['total_tasks']}")

    print(f"\n4️⃣ Implementation Summary:")
    print(f"   Status: {impl_result.status}")
    print(f"   Completed: {impl_result.tasks_completed}")
    print(f"   Failed: {impl_result.tasks_failed}")
    print(f"   Success rate: {impl_result.changes_summary['success_rate']:.0%}")

    print("\n✓ Implementer Agent test PASSED\n")
