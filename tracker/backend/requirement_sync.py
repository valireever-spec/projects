"""
Bidirectional sync between tracker database and project requirement files.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class RequirementSyncManager:
    """Manages bidirectional sync between database and markdown files."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.func_req_path = self.project_path / "requirements" / "FUNCTIONAL_REQUIREMENTS.md"
        self.nonfunc_req_path = self.project_path / "NONFUNCTIONAL_REQUIREMENTS.md"

    def write_functional_requirements(self, requirements: List[Dict]) -> Tuple[bool, str]:
        """Write functional requirements back to markdown file."""
        try:
            content = self._generate_functional_markdown(requirements)
            self.func_req_path.parent.mkdir(parents=True, exist_ok=True)
            self.func_req_path.write_text(content)
            return True, f"Wrote {len(requirements)} functional requirements"
        except Exception as e:
            return False, f"Failed to write functional requirements: {e}"

    def write_nonfunctional_requirements(self, requirements: List[Dict]) -> Tuple[bool, str]:
        """Write non-functional requirements back to markdown file."""
        try:
            content = self._generate_nonfunctional_markdown(requirements)
            self.nonfunc_req_path.parent.mkdir(parents=True, exist_ok=True)
            self.nonfunc_req_path.write_text(content)
            return True, f"Wrote {len(requirements)} non-functional requirements"
        except Exception as e:
            return False, f"Failed to write non-functional requirements: {e}"

    def _generate_functional_markdown(self, requirements: List[Dict]) -> str:
        """Generate markdown content for functional requirements."""
        lines = [
            "# Functional Requirements: investing-platform\n",
            "Complete specification of all features and use cases.\n",
            "\n---\n",
            "## Overview\n",
            "**Status:** Auto-synced from tracker on " + datetime.now().isoformat() + "\n",
            "\n",
        ]

        for req in requirements:
            lines.append(f"## {req['req_id']}: {req['title']}\n")
            lines.append(f"\n**Category:** {req.get('category', 'N/A')}\n")

            # Parse description to extract actor and use case
            description = req.get('description', '')
            lines.append(f"\n{description}\n")

            # Parse acceptance criteria
            criteria = req.get('acceptance_criteria', [])
            if criteria:
                lines.append("\n### Acceptance Criteria\n")
                if isinstance(criteria, str):
                    try:
                        criteria = json.loads(criteria)
                    except:
                        criteria = [{"description": criteria}]

                for criterion in criteria:
                    if isinstance(criterion, dict):
                        crit_id = criterion.get('id', '')
                        crit_desc = criterion.get('description', '')
                        lines.append(f"- **{crit_id}**: {crit_desc}\n")
                    else:
                        lines.append(f"- {criterion}\n")

            # Parse test cases
            tests = req.get('test_case', [])
            if tests:
                lines.append("\n### Test Cases\n")
                if isinstance(tests, str):
                    try:
                        tests = json.loads(tests)
                    except:
                        tests = [tests]

                for test in tests:
                    lines.append(f"- `{test}`\n")

            lines.append("\n---\n\n")

        return "".join(lines)

    def _generate_nonfunctional_markdown(self, requirements: List[Dict]) -> str:
        """Generate markdown content for non-functional requirements."""
        lines = [
            "# Non-Functional Requirements: investing-platform\n",
            "Specification of system qualities: performance, reliability, security, maintainability.\n",
            "\n---\n",
            "## Overview\n",
            "**Status:** Auto-synced from tracker on " + datetime.now().isoformat() + "\n",
            "\n",
        ]

        for req in requirements:
            lines.append(f"## {req['req_id']}: {req['title']}\n")
            lines.append(f"\n**Category:** {req.get('category', 'N/A')}\n")

            if req.get('description'):
                lines.append(f"\n**Requirement:**\n{req['description']}\n")

            if req.get('measurement_method'):
                lines.append(f"\n**Measurement Method:**\n{req['measurement_method']}\n")

            if req.get('target'):
                lines.append(f"\n**Target:**\n{req['target']}\n")

            if req.get('test_case'):
                lines.append(f"\n**Test Case:**\n```\n{req['test_case']}\n```\n")

            lines.append("\n---\n\n")

        return "".join(lines)

    def get_sync_status(self, db_requirements: List[Dict]) -> Dict:
        """Check if database and files are in sync."""
        func_exists = self.func_req_path.exists()
        nonfunc_exists = self.nonfunc_req_path.exists()

        func_reqs = [r for r in db_requirements if r['req_type'] == 'Functional']
        nonfunc_reqs = [r for r in db_requirements if r['req_type'] == 'Non-Functional']

        return {
            "synced": func_exists and nonfunc_exists,
            "functional_file_exists": func_exists,
            "nonfunctional_file_exists": nonfunc_exists,
            "functional_in_db": len(func_reqs),
            "nonfunctional_in_db": len(nonfunc_reqs),
            "total_in_db": len(db_requirements),
            "last_sync": None,  # Would track in metadata
        }


def sync_requirements_to_files(project_path: str, requirements: List[Dict]) -> Dict:
    """Sync requirements from tracker to project files."""
    manager = RequirementSyncManager(project_path)

    func_reqs = [r for r in requirements if r['req_type'] == 'Functional']
    nonfunc_reqs = [r for r in requirements if r['req_type'] == 'Non-Functional']

    results = {
        "status": "success",
        "functional": None,
        "nonfunctional": None,
        "errors": []
    }

    if func_reqs:
        success, msg = manager.write_functional_requirements(func_reqs)
        results["functional"] = {"success": success, "message": msg}
        if not success:
            results["errors"].append(msg)

    if nonfunc_reqs:
        success, msg = manager.write_nonfunctional_requirements(nonfunc_reqs)
        results["nonfunctional"] = {"success": success, "message": msg}
        if not success:
            results["errors"].append(msg)

    if results["errors"]:
        results["status"] = "partial"

    return results
