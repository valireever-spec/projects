"""
Integration with central tracker for bug reporting and requirement tracking.

This module provides utilities to report bugs and update requirement status to the
central tracker automatically when errors occur or features are implemented.
"""

import logging
import traceback
from typing import Optional
from tracker_client import TrackerClient

logger = logging.getLogger(__name__)

# Global tracker client instance
_tracker_client: Optional[TrackerClient] = None


def get_tracker_client() -> Optional[TrackerClient]:
    """Get or initialize the tracker client singleton.

    Returns:
        TrackerClient instance, or None if initialization failed
    """
    global _tracker_client
    try:
        if _tracker_client is None:
            _tracker_client = TrackerClient()
        return _tracker_client
    except Exception as e:
        logger.warning(f"Failed to initialize tracker client: {e}")
        return None


def report_api_error(
    endpoint: str,
    error_message: str,
    error_type: str = "API Error",
    severity: str = "High",
    additional_info: str = ""
) -> bool:
    """
    Report an API error to the tracker.

    Args:
        endpoint: The API endpoint that failed (e.g., "/api/signals")
        error_message: Description of the error
        error_type: Type of error (API Error, Timeout, Database Error, etc.)
        severity: Critical, High, Medium, Low
        additional_info: Additional context about the error

    Returns:
        True if reported successfully, False otherwise
    """
    try:
        client = get_tracker_client()
        if not client:
            return False

        title = f"{error_type}: {endpoint}"
        description = f"Endpoint: {endpoint}\n\nError: {error_message}"

        if additional_info:
            description += f"\n\nContext: {additional_info}"

        return client.report_bug(
            title=title,
            description=description,
            pillar="Verification & Validation",
            severity=severity
        )
    except Exception as e:
        logger.error(f"Failed to report API error to tracker: {e}")
        return False


def report_test_failure(
    test_name: str,
    failure_reason: str,
    requirement_id: Optional[str] = None
) -> bool:
    """
    Report a test failure to the tracker.

    Args:
        test_name: Name of the failed test
        failure_reason: Why the test failed
        requirement_id: Optional requirement this test validates (e.g., "FR-002")

    Returns:
        True if reported successfully, False otherwise
    """
    try:
        client = get_tracker_client()
        if not client:
            return False

        return client.report_bug(
            title=f"Test Failed: {test_name}",
            description=f"Test: {test_name}\n\nFailure: {failure_reason}",
            pillar="Verification & Validation",
            severity="High",
            requirement_id=requirement_id
        )
    except Exception as e:
        logger.error(f"Failed to report test failure to tracker: {e}")
        return False


def update_feature_status(
    requirement_id: str,
    status: str,
    notes: str = ""
) -> bool:
    """
    Update requirement status when a feature is completed.

    Args:
        requirement_id: Requirement ID (e.g., "FR-002", "NFR-001")
        status: New status (Proposed, Accepted, Implemented, Validated)
        notes: Optional notes about the update

    Returns:
        True if updated successfully, False otherwise
    """
    try:
        client = get_tracker_client()
        if not client:
            return False

        return client.update_requirement_status(
            req_id=requirement_id,
            status=status,
            notes=notes
        )
    except Exception as e:
        logger.error(f"Failed to update requirement status in tracker: {e}")
        return False


def mark_bug_fixed(
    gap_id: int,
    solution_summary: str,
    code_file: str,
    commit_hash: str,
    fixed_by: str = "investing-platform-team"
) -> bool:
    """
    Mark a bug as fixed with complete solution documentation.

    Args:
        gap_id: Bug ID from tracker
        solution_summary: What was changed to fix the bug
        code_file: File and lines that were changed (e.g., "backend/api/routers/chart.py:42-50")
        commit_hash: Git commit hash that fixed the bug
        fixed_by: Who fixed the bug

    Returns:
        True if updated successfully, False otherwise
    """
    try:
        client = get_tracker_client()
        if not client:
            return False

        return client.mark_bug_fixed(
            gap_id=gap_id,
            solution_summary=solution_summary,
            code_file=code_file,
            commit_hash=commit_hash,
            fixed_by=fixed_by
        )
    except Exception as e:
        logger.error(f"Failed to mark bug as fixed in tracker: {e}")
        return False


def get_project_health() -> Optional[dict]:
    """
    Get current project health metrics from tracker.

    Returns:
        Project health dict with gap_count, maturity_score, etc., or None if failed
    """
    try:
        client = get_tracker_client()
        if not client:
            return None

        return client.get_project_status()
    except Exception as e:
        logger.error(f"Failed to get project health from tracker: {e}")
        return None


def get_open_bugs() -> Optional[list]:
    """
    Get list of all open bugs for this project from tracker.

    Returns:
        List of bugs, or None if failed
    """
    try:
        client = get_tracker_client()
        if not client:
            return None

        return client.get_open_bugs()
    except Exception as e:
        logger.error(f"Failed to get open bugs from tracker: {e}")
        return None
