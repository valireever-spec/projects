"""
Push tracker data back to each project's local board files.
Each project maintains its own V-Model and bug tracking state.
"""

import json
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from .models import Project, Requirement, Gap
from .requirement_linking import RequirementLinker


class ProjectBoardSyncer:
    """Syncs tracker data (requirements + bugs) to each project's local board."""

    @staticmethod
    def generate_project_board(db: Session, project: Project) -> str:
        """
        Generate a comprehensive board file for a project showing:
        - V-Model requirements status (FR/NFR coverage)
        - Bug tracker integration (linked gaps)
        - Health metrics
        """

        requirements = db.query(Requirement).filter(
            Requirement.project_id == project.id
        ).all()

        gaps = db.query(Gap).filter(Gap.project_id == project.id).all()

        # Build board content
        lines = [
            f"# {project.name} — V-Model & Bug Tracking Board",
            "",
            f"**Last Updated:** {datetime.now().isoformat()}",
            f"**Source:** Auto-synced from tracker",
            "",
            "---",
            "",
        ]

        # Summary section
        functional_reqs = [r for r in requirements if r.req_type == "Functional"]
        nonfunctional_reqs = [r for r in requirements if r.req_type == "Non-Functional"]

        lines.extend([
            "## Summary",
            "",
            f"- **Total Requirements:** {len(requirements)}",
            f"  - Functional (FR): {len(functional_reqs)}",
            f"  - Non-Functional (NFR): {len(nonfunctional_reqs)}",
            f"- **Total Bugs/Gaps:** {len(gaps)}",
            "",
        ])

        # Health section
        lines.extend([
            "## Health Status",
            "",
        ])

        # Calculate metrics
        proposed = len([r for r in requirements if r.status == "Proposed"])
        accepted = len([r for r in requirements if r.status == "Accepted"])
        implemented = len([r for r in requirements if r.status == "Implemented"])
        validated = len([r for r in requirements if r.status == "Validated"])

        coverage = (validated / len(requirements) * 100) if requirements else 0

        lines.extend([
            f"**Coverage: {coverage:.1f}% ({validated}/{len(requirements)} validated)**",
            "",
            f"| Status | Count |",
            f"|--------|-------|",
            f"| ✅ Validated | {validated} |",
            f"| ✔️ Implemented | {implemented} |",
            f"| 📋 Accepted | {accepted} |",
            f"| 📝 Proposed | {proposed} |",
            "",
        ])

        # V-Model Left Leg (Requirements)
        lines.extend([
            "---",
            "",
            "## V-Model: Left Leg (Requirements)",
            "",
            "### Functional Requirements (FR)",
            "",
        ])

        if not functional_reqs:
            lines.append("*No functional requirements defined*")
        else:
            for req in sorted(functional_reqs, key=lambda r: r.req_id):
                linked_gaps = db.query(Gap).filter(Gap.requirement_id == req.id).all()
                status_icon = {
                    "Validated": "✅",
                    "Implemented": "✔️",
                    "Accepted": "📋",
                    "Proposed": "📝"
                }.get(req.status, "❓")

                lines.append(f"- **{req.req_id}** {status_icon} {req.title}")
                if req.category:
                    lines.append(f"  - Category: {req.category}")
                if linked_gaps:
                    lines.append(f"  - ⚠️ Linked gaps: {len(linked_gaps)}")

        lines.extend([
            "",
            "### Non-Functional Requirements (NFR)",
            "",
        ])

        if not nonfunctional_reqs:
            lines.append("*No non-functional requirements defined*")
        else:
            for req in sorted(nonfunctional_reqs, key=lambda r: r.req_id):
                linked_gaps = db.query(Gap).filter(Gap.requirement_id == req.id).all()
                status_icon = {
                    "Validated": "✅",
                    "Implemented": "✔️",
                    "Accepted": "📋",
                    "Proposed": "📝"
                }.get(req.status, "❓")

                lines.append(f"- **{req.req_id}** {status_icon} {req.title}")
                if req.category:
                    lines.append(f"  - Category: {req.category}")
                if req.target:
                    lines.append(f"  - Target: {req.target}")
                if linked_gaps:
                    lines.append(f"  - ⚠️ Linked gaps: {len(linked_gaps)}")

        # V-Model Right Leg (Validation/Bugs)
        lines.extend([
            "",
            "---",
            "",
            "## V-Model: Right Leg (Validation & Bug Tracking)",
            "",
            "### Open Gaps/Bugs",
            "",
        ])

        if not gaps:
            lines.append("✅ *No open gaps or bugs*")
        else:
            for gap in sorted(gaps, key=lambda g: (g.requirement_id or 0, g.id)):
                status_icon = {
                    "Discovered": "🔍",
                    "Prioritized": "🔴",
                    "In Remediation": "🔧",
                    "Done": "✅"
                }.get(gap.status, "❓")

                lines.append(f"- **{gap.title}** {status_icon}")
                lines.append(f"  - Status: {gap.status}")
                if gap.severity:
                    lines.append(f"  - Severity: {gap.severity}")
                if gap.effort:
                    lines.append(f"  - Effort: {gap.effort}")
                if gap.requirement_id:
                    req = db.query(Requirement).filter(
                        Requirement.id == gap.requirement_id
                    ).first()
                    if req:
                        lines.append(f"  - Violates: {req.req_id}")
                if gap.description:
                    lines.append(f"  - Description: {gap.description}")

                # Solution info if gap is fixed
                if gap.solution_summary:
                    lines.append(f"  - **Solution:** {gap.solution_summary}")
                if gap.fixed_code_file:
                    lines.append(f"  - **Code:** {gap.fixed_code_file}")
                if gap.fixed_commit_hash:
                    lines.append(f"  - **Commit:** {gap.fixed_commit_hash}")
                if gap.fixed_by:
                    lines.append(f"  - **Fixed by:** {gap.fixed_by}")
                if gap.fixed_at:
                    lines.append(f"  - **Fixed:** {gap.fixed_at.strftime('%Y-%m-%d %H:%M')}")

        # Requirements needing validation
        lines.extend([
            "",
            "### Requirements Needing Validation",
            "",
        ])

        unvalidated = [r for r in requirements if r.status != "Validated"]
        if not unvalidated:
            lines.append("✅ *All requirements validated*")
        else:
            for req in sorted(unvalidated, key=lambda r: r.req_id):
                lines.append(f"- **{req.req_id}** ({req.status}) {req.title}")

        # Traceability
        lines.extend([
            "",
            "---",
            "",
            "## Traceability",
            "",
            "| Requirement | Type | Status | Gaps | Tests |",
            "|-------------|------|--------|------|-------|",
        ])

        for req in sorted(requirements, key=lambda r: r.req_id):
            linked_gaps = db.query(Gap).filter(Gap.requirement_id == req.id).all()
            test_cases = "✅" if req.test_case else "❌"
            req_type_abbr = req.req_type[0] if req.req_type else "?"
            lines.append(
                f"| {req.req_id} | {req_type_abbr} | {req.status} | "
                f"{len(linked_gaps)} | {test_cases} |"
            )

        lines.extend([
            "",
            "---",
            "",
            f"*Generated by tracker auto-export at {datetime.now().isoformat()}*",
            "*This file is auto-generated. Edit requirements in the tracker and they sync here.*",
        ])

        return "\n".join(lines)

    @staticmethod
    def write_project_board(project: Project, content: str) -> bool:
        """Write board file to project."""
        try:
            if not project.path:
                return False

            board_path = Path(project.path) / "V_MODEL_BOARD.md"
            board_path.write_text(content)
            return True
        except Exception as e:
            print(f"❌ Failed to write board for {project.name}: {e}")
            return False

    @staticmethod
    def sync_all_projects(db: Session) -> dict:
        """Sync tracker data to all project boards."""
        projects = db.query(Project).all()

        results = {
            "synced": 0,
            "failed": 0,
            "projects": []
        }

        for project in projects:
            content = ProjectBoardSyncer.generate_project_board(db, project)
            success = ProjectBoardSyncer.write_project_board(project, content)

            if success:
                results["synced"] += 1
                results["projects"].append({"name": project.name, "status": "✅"})
            else:
                results["failed"] += 1
                results["projects"].append({"name": project.name, "status": "❌"})

        return results
