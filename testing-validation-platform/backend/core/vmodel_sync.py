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
PROJECT_NAME = "investing-platform"
PROJECT_ID = 1  # Will be set by tracker_client


def get_project_id() -> Optional[int]:
    """Get or create project in tracker.

    Returns:
        Project ID if found or created, None on error.
    """
    try:
        # Try to find project
        resp: requests.Response = requests.get(f"{TRACKER_URL}/api/projects")
        projects: list[dict[str, Any]] = resp.json()
        for p in projects:
            if p.get("name") == PROJECT_NAME:
                logger.info(f"✅ Found project '{PROJECT_NAME}' in tracker (ID: {p['id']})")
                return int(p["id"])

        # Create if not found
        logger.info(f"📝 Creating project '{PROJECT_NAME}' in tracker...")
        create_resp: requests.Response = requests.post(
            f"{TRACKER_URL}/api/projects",
            json={
                "name": PROJECT_NAME,
                "description": f"V-Model tracking for {PROJECT_NAME}",
                "tech_stack": "Python/FastAPI"
            }
        )
        if create_resp.status_code in [200, 201]:
            project_data: dict[str, Any] = create_resp.json()
            project_id: int = int(project_data.get("id", 0))
            logger.info(f"✅ Project created (ID: {project_id})")
            return project_id
    except Exception as e:
        logger.error(f"❌ Failed to get/create project: {e}")
    return None


def parse_markdown_requirements(file_path: Path) -> List[Dict[str, Any]]:
    """Parse requirements from markdown file.

    Args:
        file_path: Path to markdown file (FUNCTIONAL_REQUIREMENTS.md or NONFUNCTIONAL_REQUIREMENTS.md)

    Returns:
        List of requirement dicts with keys: req_id, description, status, type
    """
    if not file_path.exists():
        logger.warning(f"⚠️ File not found: {file_path}")
        return []

    requirements: List[Dict[str, Any]] = []
    content: str = file_path.read_text()

    # Match lines like: - **FR-001** — Description (Status)
    # or: - **NFR-001** — Description
    pattern: str = r'^- \*\*([A-Z]+\-\d+)\*\*\s+[-–]\s+(.+?)(?:\s*\(([^)]+)\))?$'

    for line in content.split('\n'):
        match = re.match(pattern, line)
        if match:
            req_id: str = match.group(1)
            description: str = match.group(2).strip()
            status: str = match.group(3) or "Proposed"

            requirements.append({
                "req_id": req_id,
                "description": description,
                "status": status,
                "type": "FR" if req_id.startswith("FR") else "NFR"
            })

    logger.info(f"📋 Parsed {len(requirements)} requirements from {file_path.name}")
    return requirements


def parse_vmodel_board_bugs(file_path: Path) -> List[Dict[str, Any]]:
    """Parse bugs/gaps from V_MODEL_BOARD.md.

    Args:
        file_path: Path to V_MODEL_BOARD.md file

    Returns:
        List of bug dicts with keys: title, description, severity, status
    """
    if not file_path.exists():
        logger.warning(f"⚠️ File not found: {file_path}")
        return []

    bugs: List[Dict[str, Any]] = []
    content: str = file_path.read_text()

    # Look for section: "### Open Gaps/Bugs"
    if "### Open Gaps/Bugs" not in content:
        return bugs

    # Extract section
    start: int = content.find("### Open Gaps/Bugs")
    end: int = content.find("###", start + 1)
    section: str = content[start:end] if end > 0 else content[start:]

    # Match bug lines: - **Title** 🔍
    bug_pattern: str = r'^- \*\*(.+?)\*\*\s*🔍'

    for line in section.split('\n'):
        match = re.match(bug_pattern, line)
        if match:
            title: str = match.group(1).strip()

            # Determine severity from context
            severity: str = "Medium"
            title_section: str = section[max(0, section.find(title) - 50):min(len(section), section.find(title) + 250)]
            if "Critical" in title_section:
                severity = "Critical"
            elif "High" in title_section:
                severity = "High"
            elif "Low" in title_section:
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
    """Push requirements to tracker.

    Args:
        project_id: Tracker project ID
        requirements: List of requirement dicts from parse_markdown_requirements

    Returns:
        Number of requirements successfully created
    """
    created_count: int = 0

    for req in requirements:
        try:
            resp: requests.Response = requests.post(
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
    """Push bugs/gaps to tracker.

    Args:
        project_id: Tracker project ID
        bugs: List of bug dicts from parse_vmodel_board_bugs

    Returns:
        Number of bugs successfully created
    """
    created_count: int = 0

    for bug in bugs:
        try:
            resp: requests.Response = requests.post(
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


def sync_vmodel_to_tracker() -> bool:
    """Main sync function - reads local files and pushes to tracker.

    Returns:
        True if sync completed successfully, False if project initialization failed
    """
    logger.info("=" * 60)
    logger.info(f"🔄 Starting V-Model sync for {PROJECT_NAME}")
    logger.info("=" * 60)

    # Get project ID
    project_id: Optional[int] = get_project_id()
    if not project_id:
        logger.error("❌ Could not get/create project in tracker")
        return False

    # Find project root
    project_root: Path = Path(__file__).parent.parent.parent

    # Parse requirements
    fr_path: Path = project_root / "FUNCTIONAL_REQUIREMENTS.md"
    nfr_path: Path = project_root / "NONFUNCTIONAL_REQUIREMENTS.md"
    vmodel_path: Path = project_root / "V_MODEL_BOARD.md"

    logger.info(f"📂 Project root: {project_root}")

    all_requirements: List[Dict[str, Any]] = []
    all_requirements.extend(parse_markdown_requirements(fr_path))
    all_requirements.extend(parse_markdown_requirements(nfr_path))

    bugs: List[Dict[str, Any]] = parse_vmodel_board_bugs(vmodel_path)

    # Push to tracker
    logger.info("\n📤 Pushing to tracker...")
    req_count: int = push_requirements_to_tracker(project_id, all_requirements)
    bug_count: int = push_bugs_to_tracker(project_id, bugs)

    logger.info("\n" + "=" * 60)
    logger.info(f"✅ Sync complete: {req_count} requirements, {bug_count} bugs")
    logger.info("=" * 60)

    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sync_vmodel_to_tracker()
