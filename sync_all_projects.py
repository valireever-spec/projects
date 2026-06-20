#!/usr/bin/env python3
"""
Sync V-Model data from all projects to central tracker.
"""

import logging
import requests
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TRACKER_URL = "http://127.0.0.1:8001"
PROJECTS_ROOT = Path("/home/vali/projects")

def _estimate_effort(severity: str) -> str:
    """Estimate effort based on severity."""
    effort_map = {
        "Critical": "High",
        "High": "High",
        "Medium": "Medium",
        "Low": "Low"
    }
    return effort_map.get(severity, "Medium")

def get_or_create_project(project_name: str) -> Optional[int]:
    """Get project ID or create it."""
    try:
        # Check if exists
        resp = requests.get(f"{TRACKER_URL}/api/projects")
        projects = resp.json()
        for p in projects:
            if p["name"] == project_name:
                logger.info(f"✅ Found project '{project_name}' (ID: {p['id']})")
                return p["id"]

        # Create if not found
        logger.info(f"📝 Creating project '{project_name}'...")
        create_resp = requests.post(
            f"{TRACKER_URL}/api/projects",
            json={
                "name": project_name,
                "description": f"V-Model tracking for {project_name}",
                "tech_stack": "Multi-project"
            }
        )
        if create_resp.status_code in [200, 201]:
            project_id = create_resp.json().get("id")
            logger.info(f"✅ Project created (ID: {project_id})")
            return project_id
    except Exception as e:
        logger.error(f"❌ Failed to get/create project: {e}")
    return None

def parse_vmodel_board(file_path: Path) -> List[Dict[str, Any]]:
    """Parse bugs from V_MODEL_BOARD.md."""
    if not file_path.exists():
        return []

    bugs = []
    content = file_path.read_text()

    # Look for section: "### Open Gaps/Bugs"
    if "### Open Gaps/Bugs" not in content:
        return bugs

    start = content.find("### Open Gaps/Bugs")
    end = content.find("###", start + 1)
    section = content[start:end] if end > 0 else content[start:]

    bug_pattern = r'^- \*\*(.+?)\*\*\s*🔍'

    for line in section.split('\n'):
        match = re.match(bug_pattern, line)
        if match:
            title = match.group(1).strip()
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

    return bugs

def push_bugs_to_tracker(project_id: int, bugs: List[Dict[str, Any]]) -> int:
    """Push bugs to tracker (idempotent)."""
    if not bugs:
        return 0

    created = 0
    updated = 0

    # Fetch existing
    try:
        proj_resp = requests.get(f"{TRACKER_URL}/api/projects/{project_id}", timeout=5)
        existing_bugs = proj_resp.json().get("gaps", [])
    except Exception as e:
        logger.warning(f"Could not fetch existing bugs: {e}")
        existing_bugs = []

    for bug in bugs:
        try:
            existing_bug = None
            for existing in existing_bugs:
                if existing.get("title") == bug["title"]:
                    existing_bug = existing
                    break

            if existing_bug:
                resp = requests.put(
                    f"{TRACKER_URL}/api/projects/{project_id}/gaps/{existing_bug['id']}",
                    json={
                        "title": bug["title"],
                        "description": bug["description"],
                        "severity": bug["severity"],
                        "status": bug["status"],
                        "pillar": "Verification & Validation",
                        "effort": _estimate_effort(bug["severity"])
                    }
                )
                if resp.status_code in [200, 201]:
                    updated += 1
            else:
                resp = requests.post(
                    f"{TRACKER_URL}/api/projects/{project_id}/gaps",
                    json={
                        "title": bug["title"],
                        "description": bug["description"],
                        "severity": bug["severity"],
                        "status": bug["status"],
                        "pillar": "Verification & Validation",
                        "effort": _estimate_effort(bug["severity"])
                    }
                )
                if resp.status_code in [200, 201]:
                    created += 1
        except Exception as e:
            logger.error(f"❌ {bug['title'][:50]}: {e}")

    total = created + updated
    logger.info(f"✅ Bugs: {created} created, {updated} updated (total {total}/{len(bugs)})")
    return total

def parse_requirements(file_path: Path) -> List[Dict[str, Any]]:
    """Parse requirements from markdown file (same as vmodel_sync.py)."""
    if not file_path.exists():
        return []

    requirements = []
    content = file_path.read_text()

    # Pattern 1: Bullet list format: - **FR-001** — Description
    bullet_pattern = r'^- \*\*([A-Z]+\-\d+)\*\*\s+[-–]\s+(.+?)(?:\s*\(([^)]+)\))?$'

    # Pattern 2: Header format: ## FR-001: Description
    header_pattern = r'^##\s+([A-Z]+\-\d+):\s+(.+?)$'

    for line in content.split('\n'):
        # Try bullet format first
        match = re.match(bullet_pattern, line)
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
        else:
            # Try header format
            match = re.match(header_pattern, line)
            if match:
                req_id = match.group(1)
                description = match.group(2).strip()

                requirements.append({
                    "req_id": req_id,
                    "description": description,
                    "status": "Proposed",
                    "type": "FR" if req_id.startswith("FR") else "NFR"
                })

    return requirements

def push_requirements_to_tracker(project_id: int, requirements: List[Dict[str, Any]]) -> int:
    """Push requirements to tracker (idempotent)."""
    if not requirements:
        return 0

    created = 0
    updated = 0

    # Fetch existing
    try:
        resp = requests.get(f"{TRACKER_URL}/api/projects/{project_id}/requirements", timeout=5)
        existing_reqs = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        logger.warning(f"Could not fetch existing requirements: {e}")
        existing_reqs = []

    for req in requirements:
        try:
            existing_req = None
            for existing in existing_reqs:
                if existing.get("req_id") == req["req_id"]:
                    existing_req = existing
                    break

            if existing_req:
                resp = requests.put(
                    f"{TRACKER_URL}/api/projects/{project_id}/requirements/{existing_req['id']}",
                    json={
                        "req_id": req["req_id"],
                        "description": req["description"],
                        "status": req["status"],
                        "req_type": req["type"],
                        "category": "FR" if req["type"] == "FR" else "NFR"
                    }
                )
                if resp.status_code in [200, 201]:
                    updated += 1
            else:
                resp = requests.post(
                    f"{TRACKER_URL}/api/projects/{project_id}/requirements",
                    json={
                        "req_id": req["req_id"],
                        "description": req["description"],
                        "status": req["status"],
                        "req_type": req["type"],
                        "category": "FR" if req["type"] == "FR" else "NFR"
                    }
                )
                if resp.status_code in [200, 201]:
                    created += 1
        except Exception as e:
            logger.error(f"  ❌ {req['req_id']}: {e}")

    total = created + updated
    logger.info(f"✅ Requirements: {created} created, {updated} updated (total {total}/{len(requirements)})")
    return total

def sync_project(project_name: str, project_path: Path) -> bool:
    """Sync a single project."""
    logger.info("=" * 60)
    logger.info(f"🔄 Syncing: {project_name}")
    logger.info("=" * 60)

    # Get or create project
    project_id = get_or_create_project(project_name)
    if not project_id:
        logger.error("❌ Could not get/create project")
        return False

    # Parse and sync requirements
    fr_path = project_path / "FUNCTIONAL_REQUIREMENTS.md"
    nfr_path = project_path / "NONFUNCTIONAL_REQUIREMENTS.md"

    all_requirements = []
    if fr_path.exists():
        all_requirements.extend(parse_requirements(fr_path))
    if nfr_path.exists():
        all_requirements.extend(parse_requirements(nfr_path))

    if all_requirements:
        req_count = push_requirements_to_tracker(project_id, all_requirements)
    else:
        logger.info("📋 No requirements found")

    # Parse and sync bugs
    vmodel_path = project_path / "V_MODEL_BOARD.md"
    bugs = parse_vmodel_board(vmodel_path)
    logger.info(f"🐛 Parsed {len(bugs)} bugs from V_MODEL_BOARD.md")

    # Push to tracker
    if bugs:
        bug_count = push_bugs_to_tracker(project_id, bugs)
        logger.info(f"📤 Synced {bug_count} bugs")
    else:
        logger.info("📤 No bugs to sync")

    logger.info("=" * 60)
    return True

def main():
    """Sync all projects."""
    logger.info("\n" + "=" * 60)
    logger.info("MULTI-PROJECT V-MODEL SYNC")
    logger.info("=" * 60 + "\n")

    projects_to_sync = [
        ("business-dev-platform", PROJECTS_ROOT / "business-dev-platform"),
        ("network-automation", PROJECTS_ROOT / "network-automation"),
        ("skill-creator", PROJECTS_ROOT / "skill-creator"),
        ("testing-validation-platform", PROJECTS_ROOT / "testing-validation-platform"),
    ]

    successful = 0
    for proj_name, proj_path in projects_to_sync:
        if proj_path.exists():
            if sync_project(proj_name, proj_path):
                successful += 1
            logger.info("")
        else:
            logger.warning(f"⚠️ Project not found: {proj_path}\n")

    logger.info("=" * 60)
    logger.info(f"✅ Sync complete: {successful}/{len(projects_to_sync)} projects")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
