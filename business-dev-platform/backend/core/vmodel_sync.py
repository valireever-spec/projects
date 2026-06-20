"""
Sync V-Model data from project files to central tracker.

Reads FUNCTIONAL_REQUIREMENTS.md, NONFUNCTIONAL_REQUIREMENTS.md, and V_MODEL_BOARD.md,
then pushes all requirements and bugs to the tracker API.
"""

import logging
import requests
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

TRACKER_URL = "http://127.0.0.1:8001"
PROJECT_NAME = "business-dev-platform"
PROJECT_ID = 1  # Will be set by tracker_client


def get_project_id() -> Optional[int]:
    """Get or create project in tracker."""
    try:
        # Try to find project
        resp = requests.get(f"{TRACKER_URL}/api/projects")
        projects = resp.json()
        for p in projects:
            if p["name"] == PROJECT_NAME:
                logger.info(f"✅ Found project '{PROJECT_NAME}' in tracker (ID: {p['id']})")
                return p["id"]

        # Create if not found
        logger.info(f"📝 Creating project '{PROJECT_NAME}' in tracker...")
        create_resp = requests.post(
            f"{TRACKER_URL}/api/projects",
            json={
                "name": PROJECT_NAME,
                "description": f"V-Model tracking for {PROJECT_NAME}",
                "tech_stack": "Python/FastAPI"
            }
        )
        if create_resp.status_code in [200, 201]:
            project_id = create_resp.json().get("id")
            logger.info(f"✅ Project created (ID: {project_id})")
            return project_id
    except Exception as e:
        logger.error(f"❌ Failed to get/create project: {e}")
    return None


def parse_markdown_requirements(file_path: Path) -> List[Dict[str, Any]]:
    """Parse requirements from markdown file."""
    if not file_path.exists():
        logger.warning(f"⚠️ File not found: {file_path}")
        return []

    requirements = []
    content = file_path.read_text()

    # Match lines like: - **FR-001** — Description (Status)
    # or: - **NFR-001** — Description
    pattern = r'^- \*\*([A-Z]+\-\d+)\*\*\s+[-–]\s+(.+?)(?:\s*\(([^)]+)\))?$'

    for line in content.split('\n'):
        match = re.match(pattern, line)
        if match:
            req_id = match.group(1)
            description = match.group(2).strip()
            status = match.group(3) or "Proposed"

            requirements.append({
                "req_id": req_id,
                "description": description,
                "status": status,
                "type": "FR" if req_id.startswith("FR") else "NFR"
            })

    logger.info(f"📋 Parsed {len(requirements)} requirements from {file_path.name}")
    return requirements


def parse_vmodel_board_bugs(file_path: Path) -> List[Dict[str, Any]]:
    """Parse bugs/gaps from V_MODEL_BOARD.md."""
    if not file_path.exists():
        logger.warning(f"⚠️ File not found: {file_path}")
        return []

    bugs = []
    content = file_path.read_text()

    # Look for section: "### Open Gaps/Bugs"
    if "### Open Gaps/Bugs" not in content:
        return bugs

    # Extract section
    start = content.find("### Open Gaps/Bugs")
    end = content.find("###", start + 1)
    section = content[start:end] if end > 0 else content[start:]

    # Match bug lines: - **Title** 🔍
    # Extract title and severity from description
    bug_pattern = r'^- \*\*(.+?)\*\*\s*🔍'

    for line in section.split('\n'):
        match = re.match(bug_pattern, line)
        if match:
            title = match.group(1).strip()

            # Default severity
            severity = "Medium"
            if "Critical" in section[section.find(title):section.find(title) + 200]:
                severity = "Critical"
            elif "High" in section[section.find(title):section.find(title) + 200]:
                severity = "High"
            elif "Low" in section[section.find(title):section.find(title) + 200]:
                severity = "Low"

            bugs.append({
                "title": title,
                "description": title,
                "severity": severity,
                "status": "Discovered"
            })

    logger.info(f"🐛 Parsed {len(bugs)} bugs from V_MODEL_BOARD.md")
    return bugs


def push_requirements_to_tracker(project_id: int, requirements: List[Dict[str, Any]]) -> int:
    """Push requirements to tracker."""
    created_count = 0

    for req in requirements:
        try:
            resp = requests.post(
                f"{TRACKER_URL}/api/projects/{project_id}/requirements",
                json={
                    "req_id": req["req_id"],
                    "description": req["description"],
                    "status": req["status"],
                    "type": req["type"]
                }
            )
            if resp.status_code in [200, 201]:
                created_count += 1
                logger.debug(f"  ✅ {req['req_id']}")
            else:
                logger.debug(f"  ⚠️ {req['req_id']}: {resp.status_code}")
        except Exception as e:
            logger.error(f"  ❌ {req['req_id']}: {e}")

    logger.info(f"✅ Pushed {created_count}/{len(requirements)} requirements to tracker")
    return created_count


def push_bugs_to_tracker(project_id: int, bugs: List[Dict[str, Any]]) -> int:
    """Push bugs/gaps to tracker."""
    created_count = 0

    for bug in bugs:
        try:
            resp = requests.post(
                f"{TRACKER_URL}/api/projects/{project_id}/gaps",
                json={
                    "title": bug["title"],
                    "description": bug["description"],
                    "severity": bug["severity"],
                    "status": bug["status"],
                    "pillar": "Verification & Validation"
                }
            )
            if resp.status_code in [200, 201]:
                created_count += 1
                logger.debug(f"  ✅ {bug['title'][:50]}")
            else:
                logger.debug(f"  ⚠️ {bug['title'][:50]}: {resp.status_code}")
        except Exception as e:
            logger.error(f"  ❌ {bug['title'][:50]}: {e}")

    logger.info(f"✅ Pushed {created_count}/{len(bugs)} bugs to tracker")
    return created_count


def sync_vmodel_to_tracker():
    """Main sync function - reads local files and pushes to tracker."""
    logger.info("=" * 60)
    logger.info(f"🔄 Starting V-Model sync for {PROJECT_NAME}")
    logger.info("=" * 60)

    # Get project ID
    project_id = get_project_id()
    if not project_id:
        logger.error("❌ Could not get/create project in tracker")
        return False

    # Find project root
    project_root = Path(__file__).parent.parent.parent

    # Parse requirements
    fr_path = project_root / "FUNCTIONAL_REQUIREMENTS.md"
    nfr_path = project_root / "NONFUNCTIONAL_REQUIREMENTS.md"
    vmodel_path = project_root / "V_MODEL_BOARD.md"

    logger.info(f"📂 Project root: {project_root}")

    all_requirements = []
    all_requirements.extend(parse_markdown_requirements(fr_path))
    all_requirements.extend(parse_markdown_requirements(nfr_path))

    bugs = parse_vmodel_board_bugs(vmodel_path)

    # Push to tracker
    logger.info("\n📤 Pushing to tracker...")
    req_count = push_requirements_to_tracker(project_id, all_requirements)
    bug_count = push_bugs_to_tracker(project_id, bugs)

    logger.info("\n" + "=" * 60)
    logger.info(f"✅ Sync complete: {req_count} requirements, {bug_count} bugs")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sync_vmodel_to_tracker()
