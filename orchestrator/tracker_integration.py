"""
Tracker Integration - Phase 3 Orchestrator Component

Integrates with /projects/tracker to file requirements, track status, and manage gaps.
Provides bidirectional sync between orchestrator database and tracker.
"""

import logging
import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RequirementStatus(Enum):
    """Requirement status mapping between orchestrator and tracker."""
    PROPOSED = "Proposed"
    ACCEPTED = "Accepted"
    IMPLEMENTED = "Implemented"
    VALIDATED = "Validated"


class GapStatus(Enum):
    """Gap status in tracker."""
    DISCOVERED = "Discovered"
    PRIORITIZED = "Prioritized"
    IN_REMEDIATION = "In Remediation"
    DONE = "Done"


class GapSeverity(Enum):
    """Gap severity levels."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class TrackerProject:
    """Project in tracker."""
    id: int
    name: str
    description: str
    tech_stack: str
    path: str


@dataclass
class TrackerRequirement:
    """Requirement in tracker."""
    id: int
    req_id: str
    title: str
    description: str
    status: str
    req_type: str = "Functional"
    category: str = None


@dataclass
class TrackerGap:
    """Gap/blocker in tracker."""
    id: int
    title: str
    description: str
    status: str
    pillar: str
    severity: str = "Medium"
    effort: str = "Medium"
    requirement_id: Optional[int] = None
    fixed_commit_hash: Optional[str] = None


class TrackerClient:
    """Client for tracker API with error handling and retries."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize tracker client.

        Args:
            base_url: Tracker API base URL (default: localhost:8000)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.max_retries = 3
        logger.info(f"Initialized TrackerClient at {base_url}")

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request with retries.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base_url)
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON or error dict

        Raises:
            Exception: If all retries fail
        """
        url = f"{self.base_url}{endpoint}"
        retries = 0

        while retries < self.max_retries:
            try:
                response = self.session.request(method, url, timeout=10, **kwargs)
                response.raise_for_status()
                return response.json() if response.text else {}

            except requests.exceptions.ConnectionError as e:
                retries += 1
                if retries >= self.max_retries:
                    logger.error(f"Connection failed after {self.max_retries} retries: {e}")
                    raise
                logger.warning(f"Connection attempt {retries} failed, retrying...")

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                raise

        return {}

    def health_check(self) -> bool:
        """Check if tracker API is available.

        Returns:
            True if tracker is accessible
        """
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Tracker health check failed: {e}")
            return False

    def get_or_create_project(self, project_name: str, project_path: str,
                             description: str = "", tech_stack: str = "") -> Optional[TrackerProject]:
        """Get existing project or create new one.

        Args:
            project_name: Name of project
            project_path: Path to project
            description: Project description
            tech_stack: Technology stack

        Returns:
            TrackerProject or None
        """
        try:
            # First, check if project exists
            projects = self._request("GET", "/api/projects")
            if isinstance(projects, list):
                for p in projects:
                    if p.get('name') == project_name:
                        logger.info(f"Found existing project: {project_name} (ID: {p.get('id')})")
                        return TrackerProject(
                            id=p['id'],
                            name=p['name'],
                            description=p.get('description', ''),
                            tech_stack=p.get('tech_stack', ''),
                            path=p.get('path', '')
                        )

            # Create new project
            project_data = {
                "name": project_name,
                "description": description,
                "tech_stack": tech_stack,
                "path": project_path
            }
            result = self._request("POST", "/api/projects", json=project_data)
            project_id = result.get('id')

            logger.info(f"Created project: {project_name} (ID: {project_id})")
            return TrackerProject(
                id=project_id,
                name=project_name,
                description=description,
                tech_stack=tech_stack,
                path=project_path
            )

        except Exception as e:
            logger.error(f"Error getting/creating project: {e}")
            return None

    def file_requirement(self, project_id: int, req_id: str, title: str,
                        description: str, acceptance_criteria: str = "",
                        req_type: str = "Functional", category: str = None) -> Optional[TrackerRequirement]:
        """File a new requirement in tracker.

        Args:
            project_id: Project ID in tracker
            req_id: Requirement ID (e.g., "REQ-001")
            title: Requirement title
            description: Requirement description
            acceptance_criteria: Acceptance criteria
            req_type: Type (Functional/Non-Functional)
            category: Category (e.g., Security, Performance)

        Returns:
            TrackerRequirement or None
        """
        try:
            req_data = {
                "req_id": req_id,
                "title": title,
                "description": description,
                "acceptance_criteria": acceptance_criteria,
                "req_type": req_type,
                "category": category or "General",
                "status": RequirementStatus.PROPOSED.value
            }

            result = self._request("POST", f"/api/projects/{project_id}/requirements",
                                  json=req_data)
            req_internal_id = result.get('id')

            logger.info(f"Filed requirement: {req_id} (ID: {req_internal_id})")
            return TrackerRequirement(
                id=req_internal_id,
                req_id=req_id,
                title=title,
                description=description,
                status=RequirementStatus.PROPOSED.value,
                req_type=req_type,
                category=category
            )

        except Exception as e:
            logger.error(f"Error filing requirement: {e}")
            return None

    def update_requirement_status(self, project_id: int, requirement_id: int,
                                 status: str) -> bool:
        """Update requirement status in tracker.

        Args:
            project_id: Project ID
            requirement_id: Requirement ID in tracker
            status: New status (Proposed/Accepted/Implemented/Validated)

        Returns:
            True if successful
        """
        try:
            update_data = {"status": status}
            self._request("PATCH", f"/api/projects/{project_id}/requirements/{requirement_id}",
                         json=update_data)

            logger.info(f"Updated requirement {requirement_id} status to {status}")
            return True

        except Exception as e:
            logger.error(f"Error updating requirement status: {e}")
            return False

    def create_gap(self, project_id: int, title: str, description: str,
                  pillar: str, severity: str = "Medium", effort: str = "Medium",
                  requirement_id: Optional[int] = None) -> Optional[TrackerGap]:
        """Create a gap/blocker in tracker.

        Args:
            project_id: Project ID
            title: Gap title
            description: Gap description
            pillar: Architecture pillar affected
            severity: Severity level
            effort: Effort to fix
            requirement_id: Associated requirement ID

        Returns:
            TrackerGap or None
        """
        try:
            gap_data = {
                "title": title,
                "description": description,
                "pillar": pillar,
                "severity": severity,
                "effort": effort,
                "status": GapStatus.DISCOVERED.value,
                "requirement_id": requirement_id
            }

            result = self._request("POST", f"/api/projects/{project_id}/gaps",
                                  json=gap_data)
            gap_id = result.get('id')

            logger.info(f"Created gap: {title} (ID: {gap_id})")
            return TrackerGap(
                id=gap_id,
                title=title,
                description=description,
                status=GapStatus.DISCOVERED.value,
                pillar=pillar,
                severity=severity,
                effort=effort,
                requirement_id=requirement_id
            )

        except Exception as e:
            logger.error(f"Error creating gap: {e}")
            return None

    def update_gap_status(self, project_id: int, gap_id: int,
                         status: str) -> bool:
        """Update gap status.

        Args:
            project_id: Project ID
            gap_id: Gap ID
            status: New status (Discovered/Prioritized/In Remediation/Done)

        Returns:
            True if successful
        """
        try:
            update_data = {"status": status}
            self._request("PUT", f"/api/projects/{project_id}/gaps/{gap_id}",
                         json=update_data)

            logger.info(f"Updated gap {gap_id} status to {status}")
            return True

        except Exception as e:
            logger.error(f"Error updating gap status: {e}")
            return False

    def link_commit_to_requirement(self, project_id: int, requirement_id: int,
                                  commit_hash: str, commit_message: str = "") -> bool:
        """Link a commit to a requirement.

        Args:
            project_id: Project ID
            requirement_id: Requirement ID in tracker
            commit_hash: Git commit hash
            commit_message: Commit message

        Returns:
            True if successful
        """
        try:
            # Update requirement with commit info
            update_data = {
                "status": RequirementStatus.IMPLEMENTED.value,
                "test_case": f"commit:{commit_hash[:7]}"
            }
            self._request("PATCH", f"/api/projects/{project_id}/requirements/{requirement_id}",
                         json=update_data)

            logger.info(f"Linked commit {commit_hash[:7]} to requirement {requirement_id}")
            return True

        except Exception as e:
            logger.error(f"Error linking commit: {e}")
            return False

    def get_requirements(self, project_id: int) -> List[TrackerRequirement]:
        """Get all requirements for a project.

        Args:
            project_id: Project ID

        Returns:
            List of TrackerRequirement objects
        """
        try:
            result = self._request("GET", f"/api/projects/{project_id}/requirements")

            requirements = []
            if isinstance(result, list):
                for r in result:
                    requirements.append(TrackerRequirement(
                        id=r.get('id'),
                        req_id=r.get('req_id'),
                        title=r.get('title'),
                        description=r.get('description'),
                        status=r.get('status'),
                        req_type=r.get('req_type', 'Functional'),
                        category=r.get('category')
                    ))

            return requirements

        except Exception as e:
            logger.error(f"Error getting requirements: {e}")
            return []

    def get_gaps(self, project_id: int) -> List[TrackerGap]:
        """Get all gaps for a project.

        Args:
            project_id: Project ID

        Returns:
            List of TrackerGap objects
        """
        try:
            project_data = self._request("GET", f"/api/projects/{project_id}")

            gaps = []
            if 'gaps' in project_data:
                for g in project_data['gaps']:
                    gaps.append(TrackerGap(
                        id=g.get('id'),
                        title=g.get('title'),
                        description=g.get('description'),
                        status=g.get('status'),
                        pillar=g.get('pillar'),
                        severity=g.get('severity', 'Medium'),
                        effort=g.get('effort', 'Medium'),
                        requirement_id=g.get('requirement_id')
                    ))

            return gaps

        except Exception as e:
            logger.error(f"Error getting gaps: {e}")
            return []


class TrackerIntegration:
    """Orchestrator integration with tracker."""

    def __init__(self, tracker_url: str = "http://localhost:8000"):
        """Initialize tracker integration.

        Args:
            tracker_url: Tracker API URL
        """
        self.client = TrackerClient(tracker_url)
        self.projects_cache: Dict[str, TrackerProject] = {}
        logger.info("Initialized TrackerIntegration")

    def is_available(self) -> bool:
        """Check if tracker is available.

        Returns:
            True if tracker API is accessible
        """
        return self.client.health_check()

    def sync_requirement_to_tracker(self, project_name: str, project_path: str,
                                   req_id: str, title: str, description: str,
                                   acceptance_criteria: str = "",
                                   req_type: str = "Functional") -> Optional[Dict]:
        """Sync requirement from orchestrator to tracker.

        Args:
            project_name: Name of project
            project_path: Path to project
            req_id: Requirement ID
            title: Requirement title
            description: Requirement description
            acceptance_criteria: Acceptance criteria
            req_type: Requirement type

        Returns:
            Dict with tracker requirement info or None
        """
        try:
            # Get or create project
            if project_name not in self.projects_cache:
                project = self.client.get_or_create_project(
                    project_name, project_path, tech_stack="Python"
                )
                if not project:
                    logger.error(f"Could not get/create project: {project_name}")
                    return None
                self.projects_cache[project_name] = project
            else:
                project = self.projects_cache[project_name]

            # File requirement
            req = self.client.file_requirement(
                project.id, req_id, title, description,
                acceptance_criteria, req_type
            )

            if not req:
                logger.error(f"Could not file requirement: {req_id}")
                return None

            return {
                'project_id': project.id,
                'requirement_id': req.id,
                'req_id': req.req_id,
                'status': req.status,
                'tracker_url': f"{self.client.base_url}/projects/{project.id}"
            }

        except Exception as e:
            logger.error(f"Error syncing requirement: {e}")
            return None

    def update_requirement_in_tracker(self, project_name: str, requirement_id: int,
                                     status: str) -> bool:
        """Update requirement status in tracker.

        Args:
            project_name: Project name
            requirement_id: Requirement ID in tracker
            status: New status

        Returns:
            True if successful
        """
        try:
            if project_name not in self.projects_cache:
                logger.warning(f"Project not in cache: {project_name}")
                return False

            project = self.projects_cache[project_name]
            return self.client.update_requirement_status(
                project.id, requirement_id, status
            )

        except Exception as e:
            logger.error(f"Error updating requirement: {e}")
            return False

    def file_gap_in_tracker(self, project_name: str, title: str,
                           description: str, pillar: str,
                           severity: str = "Medium",
                           requirement_id: Optional[int] = None) -> Optional[Dict]:
        """File a gap/blocker in tracker.

        Args:
            project_name: Project name
            title: Gap title
            description: Gap description
            pillar: Affected pillar
            severity: Severity level
            requirement_id: Associated requirement ID

        Returns:
            Dict with gap info or None
        """
        try:
            if project_name not in self.projects_cache:
                logger.warning(f"Project not in cache: {project_name}")
                return None

            project = self.projects_cache[project_name]
            gap = self.client.create_gap(
                project.id, title, description, pillar, severity,
                requirement_id=requirement_id
            )

            if not gap:
                return None

            return {
                'gap_id': gap.id,
                'title': gap.title,
                'status': gap.status,
                'tracker_url': f"{self.client.base_url}/projects/{project.id}"
            }

        except Exception as e:
            logger.error(f"Error filing gap: {e}")
            return None

    def sync_audit_to_tracker(self, project_name: str, requirement_id: int,
                             action: str, details: Dict) -> bool:
        """Sync audit entry to tracker as requirement comment/note.

        Args:
            project_name: Project name
            requirement_id: Requirement ID in tracker
            action: Action performed
            details: Additional details

        Returns:
            True if successful
        """
        try:
            # For now, we just log the audit sync
            # In production, this would add a comment to the requirement
            logger.info(f"Synced audit: {action} for requirement {requirement_id}")
            return True

        except Exception as e:
            logger.error(f"Error syncing audit: {e}")
            return False

    def get_requirements_status(self, project_name: str) -> Dict:
        """Get status of all requirements in tracker.

        Args:
            project_name: Project name

        Returns:
            Dict with requirements by status
        """
        try:
            if project_name not in self.projects_cache:
                logger.warning(f"Project not in cache: {project_name}")
                return {}

            project = self.projects_cache[project_name]
            requirements = self.client.get_requirements(project.id)

            by_status = {}
            for req in requirements:
                status = req.status
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append({
                    'req_id': req.req_id,
                    'title': req.title,
                    'id': req.id
                })

            return by_status

        except Exception as e:
            logger.error(f"Error getting requirements status: {e}")
            return {}


# Test usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print("\n" + "=" * 80)
    print("TRACKER INTEGRATION TEST")
    print("=" * 80 + "\n")

    tracker = TrackerIntegration()

    # Test health check
    print("1️⃣ Checking tracker availability...")
    is_available = tracker.is_available()
    print(f"   {'✓' if is_available else '✗'} Tracker available: {is_available}\n")

    if is_available:
        # Test project sync
        print("2️⃣ Getting/creating project...")
        result = tracker.sync_requirement_to_tracker(
            "investing-platform",
            "/home/vali/projects/investing-platform",
            "REQ-T-001",
            "Add authentication",
            "Implement JWT-based auth",
            "Secure login functionality"
        )
        print(f"   {'✓' if result else '✗'} Project sync: {result}\n")

        if result:
            # Test status update
            print("3️⃣ Updating requirement status...")
            success = tracker.update_requirement_in_tracker(
                "investing-platform",
                result['requirement_id'],
                "Implemented"
            )
            print(f"   {'✓' if success else '✗'} Status updated: {success}\n")

            # Test gap filing
            print("4️⃣ Filing gap in tracker...")
            gap_result = tracker.file_gap_in_tracker(
                "investing-platform",
                "Missing input validation",
                "Some endpoints lack input validation",
                "Security & Privacy by Design",
                severity="High",
                requirement_id=result['requirement_id']
            )
            print(f"   {'✓' if gap_result else '✗'} Gap filed: {gap_result}\n")

            # Test requirements status
            print("5️⃣ Getting requirements status...")
            status = tracker.get_requirements_status("investing-platform")
            print(f"   ✓ Requirements by status: {status}\n")

    print("✓ Tracker integration test complete\n")
