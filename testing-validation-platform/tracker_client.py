#!/usr/bin/env python3
"""
Client library for investing-platform to interact with tracker.
Enables bidirectional sync: report bugs, update requirements, push solutions.
"""

import requests
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Import validators for API response validation
try:
    from backend.validators import validate_response
    from backend.models import ProjectModel, GapModel
    from backend.logging_config import LogContext
except ImportError:
    # Fallback if imports unavailable
    validate_response = None
    ProjectModel = None
    GapModel = None
    LogContext = None


class TrackerClient:
    """Report bugs and status updates to the central tracker."""

    def __init__(
        self,
        tracker_url: Optional[str] = None,
        project_name: Optional[str] = None,
        max_retries: int = 3,
    ):
        # Use settings if not provided
        if tracker_url is None or project_name is None:
            try:
                from backend.config import settings
                tracker_url = tracker_url or settings.tracker_url
                project_name = project_name or settings.project_name
            except ImportError:
                tracker_url = tracker_url or "http://127.0.0.1:8001"
                project_name = project_name or "investing-platform"

        self.tracker_url = tracker_url
        self.project_name = project_name
        self.project_id = None
        self.max_retries = max_retries
        self._get_project_id()

    def _get_project_id(self) -> None:
        """Get project ID from tracker, or create project if it doesn't exist.

        With retry logic: if tracker is temporarily unavailable, retries with
        exponential backoff before giving up. If all retries fail, logs warning
        but allows system to continue (non-blocking).
        """
        from backend.utils import call_with_retry

        def _fetch_or_create_project() -> Optional[int]:
            """Fetch existing project or create new one."""
            start_time: float = time.time()
            try:
                # Try to find existing project
                resp = requests.get(
                    f"{self.tracker_url}/api/projects",
                    timeout=10
                )
                duration_ms: float = (time.time() - start_time) * 1000

                if resp.status_code != 200:
                    logger.warning(
                        f"Tracker list_projects failed",
                        extra={
                            "status_code": resp.status_code,
                            "duration_ms": duration_ms,
                            "error_message": resp.text[:100],
                        }
                    )
                    raise ConnectionError(f"Tracker API returned {resp.status_code}")

                projects = resp.json()
                for p in projects:
                    if p.get("name") == self.project_name:
                        logger.info(
                            f"Project found in tracker",
                            extra={
                                "project_name": self.project_name,
                                "project_id": p["id"],
                                "duration_ms": duration_ms,
                            }
                        )
                        return p["id"]

                # Project not found, create it
                logger.info(
                    f"Creating project in tracker",
                    extra={"project_name": self.project_name}
                )
                create_resp = requests.post(
                    f"{self.tracker_url}/api/projects",
                    json={
                        "name": self.project_name,
                        "description": f"V-Model tracking for {self.project_name}",
                        "tech_stack": "Python/FastAPI",
                    },
                    timeout=10,
                )
                create_duration_ms: float = (time.time() - start_time) * 1000

                if create_resp.status_code in [200, 201]:
                    project_data: Dict[str, Any] = create_resp.json()
                    project_id: int = int(project_data.get("id", 0))
                    logger.info(
                        f"Project created in tracker",
                        extra={
                            "project_id": project_id,
                            "project_name": self.project_name,
                            "duration_ms": create_duration_ms,
                        }
                    )
                    return project_id
                else:
                    logger.error(
                        f"Failed to create project",
                        extra={
                            "status_code": create_resp.status_code,
                            "duration_ms": create_duration_ms,
                        }
                    )
                    raise ConnectionError(f"Failed to create project: {create_resp.status_code}")

            except requests.RequestException as e:
                logger.warning(
                    f"Network error contacting tracker",
                    extra={"error": str(e)}
                )
                raise ConnectionError(f"Cannot reach tracker at {self.tracker_url}") from e

        try:
            # Try with retry logic
            self.project_id = call_with_retry(
                _fetch_or_create_project,
                max_attempts=self.max_retries,
                initial_delay=2,
            )
        except ConnectionError as e:
            logger.warning(
                f"Failed to connect to tracker, gap reporting disabled",
                extra={
                    "max_retries": self.max_retries,
                    "tracker_url": self.tracker_url,
                    "error": str(e),
                }
            )

    def report_bug(
        self,
        title: str,
        description: str,
        pillar: str,
        severity: str = "High",
        requirement_id: Optional[int] = None,
        effort: Optional[str] = None,
    ) -> bool:
        """Report a bug/gap to the tracker with retry logic.

        Args:
            title: Bug title (e.g., "API returns 500 on invalid symbol")
            description: Detailed description of the issue
            pillar: Which 8-pillar this affects (e.g., "Verification & Validation")
            severity: Critical | High | Medium | Low
            requirement_id: Link to requirement this violates (optional)
            effort: Estimated fix effort (1d, 2d, 1w, etc.)

        Returns:
            True if bug reported successfully, False if tracker unavailable (non-blocking)
        """
        if not self.project_id:
            logger.warning(
                "Tracker not connected, gap reporting disabled",
                extra={"project_name": self.project_name}
            )
            return False

        def _post_gap() -> bool:
            """Post gap to tracker."""
            start_time: float = time.time()
            payload: Dict[str, Any] = {
                "project_id": self.project_id,
                "title": title,
                "description": description,
                "pillar": pillar,
                "severity": severity,
                "status": "Discovered",
                "requirement_id": requirement_id,
                "effort": effort,
            }

            resp = requests.post(
                f"{self.tracker_url}/api/projects/{self.project_id}/gaps",
                json=payload,
                timeout=10,
            )
            duration_ms: float = (time.time() - start_time) * 1000

            if resp.status_code in [200, 201]:
                gap_data: Dict[str, Any] = resp.json()
                gap_id: int = gap_data.get("id", 0)
                logger.info(
                    "Bug reported to tracker",
                    extra={
                        "gap_id": gap_id,
                        "title": title,
                        "severity": severity,
                        "pillar": pillar,
                        "duration_ms": duration_ms,
                    }
                )
                return True
            else:
                logger.error(
                    "Failed to report bug",
                    extra={
                        "status_code": resp.status_code,
                        "error_message": resp.text[:100],
                        "duration_ms": duration_ms,
                    }
                )
                raise ConnectionError(f"Tracker returned {resp.status_code}")

        try:
            from backend.utils import call_with_retry
            return call_with_retry(
                _post_gap,
                max_attempts=self.max_retries,
                initial_delay=2,
            )
        except (ConnectionError, requests.RequestException) as e:
            logger.warning(
                "Failed to report bug after retries",
                extra={
                    "error": str(e),
                    "max_retries": self.max_retries,
                }
            )
            return False

    def update_bug_status(
        self,
        gap_id: int,
        status: str,
        notes: Optional[str] = None,
    ) -> bool:
        """Update bug status with retry logic.

        Args:
            gap_id: Bug ID from tracker
            status: One of: Discovered, Prioritized, In Remediation, Done
            notes: Optional update notes

        Returns:
            True if update successful, False if tracker unavailable (non-blocking)
        """
        if not self.project_id:
            logger.warning("⚠️ No project_id; tracker not connected.")
            return False

        def _patch_gap() -> bool:
            """Patch gap status in tracker."""
            payload = {
                "status": status,
                "description": notes if notes else "",
            }

            resp = requests.patch(
                f"{self.tracker_url}/api/projects/{self.project_id}/gaps/{gap_id}",
                json=payload,
                timeout=10,
            )
            if resp.status_code == 200:
                logger.info(f"✅ Bug #{gap_id} status updated to: {status}")
                return True
            else:
                logger.error(f"❌ Failed to update bug: {resp.status_code}")
                raise ConnectionError(f"Tracker returned {resp.status_code}")

        try:
            from backend.utils import call_with_retry
            return call_with_retry(
                _patch_gap,
                max_attempts=self.max_retries,
                initial_delay=2,
            )
        except (ConnectionError, requests.RequestException) as e:
            logger.warning(f"⚠️ Failed to update bug status after retries: {e}. Continuing anyway.")
            return False

    def mark_bug_fixed(
        self,
        gap_id: int,
        solution_summary: str,
        code_file: str,
        commit_hash: str,
        fixed_by: str = "investing-platform-team"
    ) -> bool:
        """
        Mark bug as fixed and document the solution.

        Args:
            gap_id: Bug ID from tracker
            solution_summary: What was changed to fix it
            code_file: File that was changed (e.g., "backend/api/routers/signals.py:125-145")
            commit_hash: Git commit that fixed it
            fixed_by: Who fixed it (username or team name)

        Returns:
            True if update successful
        """
        if not self.project_id:
            return False

        payload = {
            "status": "Done",
            "solution_summary": solution_summary,
            "fixed_code_file": code_file,
            "fixed_commit_hash": commit_hash,
            "fixed_by": fixed_by
        }

        try:
            resp = requests.patch(
                f"{self.tracker_url}/api/projects/{self.project_id}/gaps/{gap_id}",
                json=payload
            )
            if resp.status_code == 200:
                print(f"✅ Bug #{gap_id} marked FIXED with solution documented")
                return True
            else:
                print(f"❌ Failed to mark bug fixed: {resp.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error marking bug fixed: {e}")
            return False

    def update_requirement_status(
        self,
        req_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update requirement status (Proposed → Accepted → Implemented → Validated).

        Args:
            req_id: Requirement ID (e.g., "FR-001", "NFR-005")
            status: One of: Proposed, Accepted, Implemented, Validated
            notes: Implementation notes

        Returns:
            True if update successful
        """
        if not self.project_id:
            return False

        try:
            # First, find the requirement by req_id
            resp = requests.get(
                f"{self.tracker_url}/api/projects/{self.project_id}/requirements"
            )
            requirements = resp.json()

            req = next((r for r in requirements if r["req_id"] == req_id), None)
            if not req:
                print(f"❌ Requirement {req_id} not found")
                return False

            payload = {
                "status": status,
                "description": notes if notes else ""
            }

            resp = requests.patch(
                f"{self.tracker_url}/api/projects/{self.project_id}/requirements/{req['id']}",
                json=payload
            )
            if resp.status_code == 200:
                print(f"✅ Requirement {req_id} status updated to: {status}")
                return True
            else:
                print(f"❌ Failed to update requirement: {resp.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error updating requirement: {e}")
            return False

    def get_project_status(self) -> Optional[Dict[str, Any]]:
        """Fetch current project status from tracker."""
        if not self.project_id:
            return None

        try:
            resp = requests.get(
                f"{self.tracker_url}/api/projects/{self.project_id}"
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            print(f"❌ Error fetching project status: {e}")
            return None

    def get_open_bugs(self) -> list[dict[str, Any]]:
        """Fetch all open bugs for this project."""
        if not self.project_id:
            return []

        try:
            resp = requests.get(
                f"{self.tracker_url}/api/projects/{self.project_id}"
            )
            if resp.status_code == 200:
                return resp.json().get("gaps", [])
            return []
        except Exception as e:
            print(f"❌ Error fetching open bugs: {e}")
            return []


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = TrackerClient()

    # Example 1: Report a new bug found during testing
    client.report_bug(
        title="Composite signal returns NaN for penny stocks",
        description="When running composite signal on penny stocks (< $1), the ML factor returns NaN due to invalid feature scaling",
        pillar="Build Quality In",
        severity="High"
    )

    # Example 2: Update bug status to "In Remediation"
    client.update_bug_status(
        gap_id=5,
        status="In Remediation",
        notes="Investigation complete. Root cause: ML model trained on standard stocks. Fix in progress."
    )

    # Example 3: Mark bug as fixed
    client.mark_bug_fixed(
        gap_id=2,
        solution_summary="Added TTL expiration check in composite_signal.py. Cache now auto-invalidates every 3600 seconds instead of staying indefinitely.",
        code_file="backend/analytics/composite_signal.py:245-265",
        commit_hash="f3e5d1a2b8c9"
    )

    # Example 4: Update requirement status
    client.update_requirement_status(
        req_id="FR-001",
        status="Implemented",
        notes="Data ingestion fully working with adaptive 90-day catchup. All test cases pass."
    )

    # Example 5: Get current status
    status = client.get_project_status()
    if status:
        print(f"\n📊 Project Status:")
        print(f"   Gaps: {status.get('gap_count')}")
        print(f"   Maturity: {status.get('maturity_score')}%")
