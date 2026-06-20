#!/usr/bin/env python3
"""
Client library for investing-platform to interact with tracker.
Enables bidirectional sync: report bugs, update requirements, push solutions.
"""

import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

class TrackerClient:
    """Report bugs and status updates to the central tracker."""

    def __init__(self, tracker_url: str = "http://127.0.0.1:8001", project_name: str = "investing-platform"):
        self.tracker_url = tracker_url
        self.project_name = project_name
        self.project_id = None
        self._get_project_id()

    def _get_project_id(self):
        """Get project ID from tracker, or create project if it doesn't exist."""
        try:
            # Try to find existing project
            resp = requests.get(f"{self.tracker_url}/api/projects")
            projects = resp.json()
            for p in projects:
                if p["name"] == self.project_name:
                    self.project_id = p["id"]
                    print(f"✅ Project '{self.project_name}' found in tracker (ID: {self.project_id})")
                    return

            # Project not found, create it
            print(f"📝 Project '{self.project_name}' not found, creating...")
            create_resp = requests.post(
                f"{self.tracker_url}/api/projects",
                json={
                    "name": self.project_name,
                    "description": f"V-Model tracking for {self.project_name}",
                    "tech_stack": "Python/FastAPI"
                }
            )
            if create_resp.status_code in [200, 201]:
                self.project_id = create_resp.json().get("id")
                print(f"✅ Project created in tracker (ID: {self.project_id})")
            else:
                print(f"❌ Failed to create project: {create_resp.status_code}")
        except Exception as e:
            print(f"❌ Failed to connect to tracker: {e}")

    def report_bug(
        self,
        title: str,
        description: str,
        pillar: str,
        severity: str = "High",
        requirement_id: Optional[int] = None,
        effort: Optional[str] = None
    ) -> bool:
        """
        Report a bug/gap to the tracker.

        Args:
            title: Bug title (e.g., "API returns 500 on invalid symbol")
            description: Detailed description of the issue
            pillar: Which 8-pillar this affects (e.g., "Verification & Validation")
            severity: Critical | High | Medium | Low
            requirement_id: Link to requirement this violates (optional)
            effort: Estimated fix effort (1d, 2d, 1w, etc.)

        Returns:
            True if bug reported successfully
        """
        if not self.project_id:
            print("❌ No project_id; tracker not connected")
            return False

        payload = {
            "project_id": self.project_id,
            "title": title,
            "description": description,
            "pillar": pillar,
            "severity": severity,
            "status": "Discovered",
            "requirement_id": requirement_id,
            "effort": effort
        }

        try:
            resp = requests.post(
                f"{self.tracker_url}/api/projects/{self.project_id}/gaps",
                json=payload
            )
            if resp.status_code in [200, 201]:
                gap_id = resp.json().get("id")
                print(f"✅ Bug reported (Gap #{gap_id}): {title}")
                return True
            else:
                print(f"❌ Failed to report bug: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            print(f"❌ Error reporting bug: {e}")
            return False

    def update_bug_status(
        self,
        gap_id: int,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update bug status (Discovered → In Remediation → Done).

        Args:
            gap_id: Bug ID from tracker
            status: One of: Discovered, Prioritized, In Remediation, Done
            notes: Optional update notes

        Returns:
            True if update successful
        """
        if not self.project_id:
            return False

        payload = {
            "status": status,
            "description": notes if notes else ""
        }

        try:
            resp = requests.patch(
                f"{self.tracker_url}/api/projects/{self.project_id}/gaps/{gap_id}",
                json=payload
            )
            if resp.status_code == 200:
                print(f"✅ Bug #{gap_id} status updated to: {status}")
                return True
            else:
                print(f"❌ Failed to update bug: {resp.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error updating bug: {e}")
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

    def get_open_bugs(self) -> list:
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
