"""V-Model Dashboard API — Requirements, bugs, and progress tracking."""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

router = APIRouter()


def _load_vmodel_board() -> Dict[str, Any]:
    """Load V_MODEL_BOARD.md and parse it into structured data."""
    try:
        board_path = Path("/home/vali/projects/investing-platform/V_MODEL_BOARD.md")
        if not board_path.exists():
            return _empty_board()

        content = board_path.read_text()

        # Parse summary
        summary = {"total_requirements": 0, "total_bugs": 0}
        if "Total Requirements:" in content:
            parts = content[content.find("Total Requirements:"):].split("\n")[0]
            if "**" in parts:
                summary["total_requirements"] = int(parts.split("**")[1])
        if "Total Bugs" in content:
            parts = content[content.find("Total Bugs"):].split("\n")[0]
            summary["total_bugs"] = int(parts.split(":")[1].strip() if ":" in parts else 0)

        # Parse coverage
        coverage = "0%"
        if "Coverage:" in content:
            line = [l for l in content.split("\n") if "Coverage:" in l]
            if line:
                coverage = line[0].split("Coverage:")[1].strip().split("(")[0].strip()

        # Parse health status
        health = {}
        if "| Status | Count |" in content:
            start = content.find("| Status | Count |")
            section = content[start:start+500]
            for line in section.split("\n")[2:]:
                if "✅" in line or "✔️" in line or "📋" in line or "📝" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        status = parts[1].strip()
                        count = parts[2].strip()
                        health[status] = int(count) if count.isdigit() else 0

        return {
            "last_updated": datetime.now().isoformat(),
            "source": "V_MODEL_BOARD.md (auto-synced from tracker)",
            "summary": summary,
            "coverage": coverage,
            "health": health,
            "full_board": content
        }
    except Exception as e:
        return _empty_board()


def _empty_board() -> Dict[str, Any]:
    """Return empty V-Model board structure."""
    return {
        "last_updated": datetime.now().isoformat(),
        "source": "Not synced yet",
        "summary": {"total_requirements": 0, "total_bugs": 0},
        "coverage": "0%",
        "health": {},
        "full_board": "V_MODEL_BOARD.md not found. Sync with tracker first."
    }


def _parse_requirements(content: str) -> List[Dict[str, Any]]:
    """Extract requirements from V_MODEL_BOARD.md."""
    requirements = []

    # Parse Functional Requirements
    if "### Functional Requirements (FR)" in content:
        start = content.find("### Functional Requirements (FR)")
        end = content.find("### Non-Functional Requirements", start)
        section = content[start:end]

        for line in section.split("\n"):
            if line.startswith("- **FR-"):
                req_id = line.split("**")[1]
                status_emoji = "📝"
                if "✅" in line:
                    status_emoji = "✅"
                elif "✔️" in line:
                    status_emoji = "✔️"
                elif "📋" in line:
                    status_emoji = "📋"

                title = line.split(req_id + "**")[1].strip() if req_id in line else ""
                gap_count = 0
                if "⚠️ Linked gaps:" in line:
                    gap_count = int(line.split("⚠️ Linked gaps:")[1].strip())

                requirements.append({
                    "id": req_id,
                    "type": "FR",
                    "status": status_emoji,
                    "title": title,
                    "linked_gaps": gap_count
                })

    # Parse Non-Functional Requirements
    if "### Non-Functional Requirements (NFR)" in content:
        start = content.find("### Non-Functional Requirements (NFR)")
        end = content.find("---", start)
        section = content[start:end]

        for line in section.split("\n"):
            if line.startswith("- **NFR-"):
                req_id = line.split("**")[1]
                status_emoji = "📝"
                if "✅" in line:
                    status_emoji = "✅"
                elif "✔️" in line:
                    status_emoji = "✔️"
                elif "📋" in line:
                    status_emoji = "📋"

                title = line.split(req_id + "**")[1].strip() if req_id in line else ""
                requirements.append({
                    "id": req_id,
                    "type": "NFR",
                    "status": status_emoji,
                    "title": title,
                    "linked_gaps": 0
                })

    return requirements


def _parse_bugs(content: str) -> List[Dict[str, Any]]:
    """Extract open bugs/gaps from V_MODEL_BOARD.md."""
    bugs = []

    if "### Open Gaps/Bugs" in content:
        start = content.find("### Open Gaps/Bugs")
        end = content.find("### Requirements Needing Validation", start)
        section = content[start:end]

        for line in section.split("\n"):
            if line.startswith("- **"):
                bug_title = line.split("** ")[0].replace("- **", "").strip()
                status = "Discovered"
                severity = "Medium"

                if "🔍" in line:
                    status = "Discovered"
                if "Critical" in section[section.find(bug_title):section.find(bug_title)+200]:
                    severity = "Critical"
                elif "High" in section[section.find(bug_title):section.find(bug_title)+200]:
                    severity = "High"
                elif "Low" in section[section.find(bug_title):section.find(bug_title)+200]:
                    severity = "Low"

                bugs.append({
                    "title": bug_title,
                    "status": status,
                    "severity": severity,
                    "description": ""
                })

    return bugs


@router.get("/vmodel/board", response_model=Dict[str, Any])
async def get_vmodel_board():
    """Get V-Model board summary (requirements, bugs, coverage)."""
    board = _load_vmodel_board()
    requirements = _parse_requirements(board.get("full_board", ""))
    bugs = _parse_bugs(board.get("full_board", ""))

    return {
        "last_updated": board["last_updated"],
        "source": board["source"],
        "summary": board["summary"],
        "coverage": board["coverage"],
        "health": board["health"],
        "requirements": requirements,
        "bugs": bugs
    }


@router.get("/vmodel/requirements", response_model=Dict[str, Any])
async def get_requirements():
    """Get all requirements (FR and NFR) with status."""
    board = _load_vmodel_board()
    requirements = _parse_requirements(board.get("full_board", ""))

    fr = [r for r in requirements if r["type"] == "FR"]
    nfr = [r for r in requirements if r["type"] == "NFR"]

    return {
        "functional": fr,
        "nonfunctional": nfr,
        "total": len(requirements)
    }


@router.get("/vmodel/bugs", response_model=Dict[str, Any])
async def get_bugs():
    """Get all open bugs/gaps with severity and status."""
    board = _load_vmodel_board()
    bugs = _parse_bugs(board.get("full_board", ""))

    critical = [b for b in bugs if b["severity"] == "Critical"]
    high = [b for b in bugs if b["severity"] == "High"]
    medium = [b for b in bugs if b["severity"] == "Medium"]
    low = [b for b in bugs if b["severity"] == "Low"]

    return {
        "all": bugs,
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low,
        "total": len(bugs),
        "critical_count": len(critical),
        "high_count": len(high)
    }


@router.post("/vmodel/requirement/{req_id}/update-status")
async def update_requirement_status(req_id: str, status: str):
    """Update requirement status (calls tracker integration)."""
    try:
        from backend.core.tracker_integration import update_feature_status
        success = update_feature_status(
            requirement_id=req_id,
            status=status,
            notes=f"Status updated via dashboard at {datetime.now().isoformat()}"
        )
        return {"success": success, "requirement_id": req_id, "new_status": status}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/vmodel/coverage", response_model=Dict[str, Any])
async def get_coverage():
    """Get V-Model coverage metrics (validated vs total)."""
    board = _load_vmodel_board()
    health = board.get("health", {})
    coverage = board.get("coverage", "0%")

    total = board["summary"].get("total_requirements", 0)
    validated = health.get("✅ Validated", 0)
    implemented = health.get("✔️ Implemented", 0)

    return {
        "coverage_percent": coverage,
        "validated_count": validated,
        "validated_total": total,
        "implementation_count": implemented,
        "by_status": health
    }
