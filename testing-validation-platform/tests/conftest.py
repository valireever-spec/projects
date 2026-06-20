"""
Pytest configuration and shared fixtures for testing-validation-platform tests.
"""

import pytest
import json
import logging
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


# ============================================================================
# TRACKER API MOCK FIXTURES
# ============================================================================


@pytest.fixture
def mock_tracker_url() -> str:
    """URL of mock tracker (typically localhost:8001)."""
    return "http://127.0.0.1:8001"


@pytest.fixture
def mock_project_id() -> int:
    """Project ID in mock tracker."""
    return 1


@pytest.fixture
def mock_project_response() -> Dict[str, Any]:
    """Mock tracker project response."""
    return {
        "id": 1,
        "name": "investing-platform",
        "description": "V-Model tracking for investing-platform",
        "tech_stack": "Python/FastAPI",
    }


@pytest.fixture
def mock_projects_list() -> list:
    """Mock tracker projects list response."""
    return [
        {
            "id": 1,
            "name": "investing-platform",
            "description": "V-Model tracking for investing-platform",
            "tech_stack": "Python/FastAPI",
        },
        {
            "id": 2,
            "name": "other-project",
            "description": "Another project",
            "tech_stack": "Node.js",
        },
    ]


@pytest.fixture
def mock_gap_response() -> Dict[str, Any]:
    """Mock tracker gap/bug response."""
    return {
        "id": 123,
        "project_id": 1,
        "title": "Test Bug",
        "description": "This is a test bug",
        "status": "Discovered",
        "severity": "High",
        "pillar": "Verification & Validation",
        "created_at": "2026-06-20T10:00:00Z",
    }


@pytest.fixture
def mock_gaps_list() -> list:
    """Mock tracker gaps list response."""
    return [
        {
            "id": 1,
            "title": "API timeout",
            "status": "Discovered",
            "severity": "Critical",
            "pillar": "Verification & Validation",
        },
        {
            "id": 2,
            "title": "Missing type hints",
            "status": "In Remediation",
            "severity": "High",
            "pillar": "Build Quality In",
        },
        {
            "id": 3,
            "title": "No test coverage",
            "status": "Done",
            "severity": "Critical",
            "pillar": "Verification & Validation",
        },
    ]


# ============================================================================
# TRACKER CLIENT FIXTURES
# ============================================================================


@pytest.fixture
def tracker_client_with_mocked_api(mock_tracker_url, mock_project_response):
    """TrackerClient instance with mocked API calls."""
    from tracker_client import TrackerClient

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"projects": [mock_project_response]}

        client = TrackerClient(
            tracker_url=mock_tracker_url,
            project_name="investing-platform",
            max_retries=1,  # Fast retries for testing
        )
        return client


@pytest.fixture
def tracker_client_unavailable(mock_tracker_url):
    """TrackerClient instance when tracker is unavailable."""
    from tracker_client import TrackerClient

    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("Tracker unavailable")

        client = TrackerClient(
            tracker_url=mock_tracker_url,
            project_name="investing-platform",
            max_retries=1,
        )
        # project_id will be None due to connection error
        return client


# ============================================================================
# VMODEL_SYNC FIXTURES
# ============================================================================


@pytest.fixture
def sample_requirements_markdown() -> str:
    """Sample markdown with requirements."""
    return """# Functional Requirements

## Overview
Testing document.

## FR-001: Data Ingestion
**Priority:** Critical

## FR-002: Analysis & Indicators
**Priority:** High

## FR-003: Backtesting
**Priority:** Medium

# Non-Functional Requirements

## NFR-001: Performance
**Category:** Performance

## NFR-002: Reliability
**Category:** Reliability

## NFR-003: Security
**Category:** Security
"""


@pytest.fixture
def sample_malformed_markdown() -> str:
    """Markdown with formatting issues."""
    return """
# Random content
This is not properly formatted for requirements parsing.

Some text here
- FR-001 — (missing asterisks, won't parse)
- **NFR-001** No dash separator (won't parse)

✅ This has emoji (shouldn't break parser)
"""


@pytest.fixture
def temp_requirements_file(tmp_path, sample_requirements_markdown):
    """Temporary file with sample requirements."""
    file_path = tmp_path / "FUNCTIONAL_REQUIREMENTS.md"
    file_path.write_text(sample_requirements_markdown)
    return file_path


# ============================================================================
# ENVIRONMENT & CONFIGURATION FIXTURES
# ============================================================================


@pytest.fixture
def mock_env_settings():
    """Mock environment settings."""
    with patch("os.getenv") as mock_getenv:

        def getenv_impl(key, default=None):
            env_vars = {
                "TRACKER_URL": "http://127.0.0.1:8001",
                "PROJECT_NAME": "investing-platform",
                "SYNC_INTERVAL": "300",
                "SYNC_RETRIES": "3",
                "LOG_LEVEL": "INFO",
            }
            return env_vars.get(key, default)

        mock_getenv.side_effect = getenv_impl
        yield mock_getenv


# ============================================================================
# LOGGING FIXTURES
# ============================================================================


@pytest.fixture
def caplog_configured(caplog):
    """Configure caplog for testing with proper level."""
    caplog.set_level(logging.DEBUG)
    return caplog


# ============================================================================
# ERROR SCENARIO FIXTURES
# ============================================================================


@pytest.fixture
def mock_http_errors():
    """Simulate various HTTP errors for testing retry logic."""
    return {
        "timeout": requests.Timeout("Request timed out"),
        "connection": requests.ConnectionError("Connection failed"),
        "500": Mock(status_code=500, text="Internal Server Error"),
        "503": Mock(status_code=503, text="Service Unavailable"),
        "404": Mock(status_code=404, text="Not Found"),
    }


@pytest.fixture
def mock_tracker_intermittent():
    """Mock tracker that fails then succeeds (tests retry logic)."""
    call_count = {"count": 0}

    def tracker_call(*args, **kwargs):
        call_count["count"] += 1
        if call_count["count"] < 3:
            raise requests.ConnectionError("Temporarily unavailable")
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"projects": [{"id": 1, "name": "investing-platform"}]}
        return response

    return tracker_call, call_count


# ============================================================================
# ASSERTION HELPERS
# ============================================================================


@pytest.fixture
def assert_valid_gap_response():
    """Helper to validate gap response structure."""

    def _assert(gap_data: Dict[str, Any]):
        assert "id" in gap_data
        assert "title" in gap_data
        assert "description" in gap_data
        assert "status" in gap_data
        assert gap_data["status"] in ["Discovered", "Prioritized", "In Remediation", "Done"]
        assert "severity" in gap_data
        assert gap_data["severity"] in ["Critical", "High", "Medium", "Low"]
        assert "pillar" in gap_data

    return _assert


@pytest.fixture
def assert_valid_requirement_response():
    """Helper to validate requirement response structure."""

    def _assert(req_data: Dict[str, Any]):
        assert "id" in req_data
        assert "title" in req_data or "description" in req_data
        assert "status" in req_data
        assert req_data["status"] in ["Proposed", "Implemented", "Validated", "Accepted"]
        assert "type" in req_data
        assert req_data["type"] in ["FR", "NFR"]

    return _assert


# ============================================================================
# HOOK: AUTO-SKIP INTEGRATION TESTS IF TRACKER UNAVAILABLE
# ============================================================================


def pytest_configure(config):
    """Configure pytest plugins and markers."""
    config.addinivalue_line(
        "markers",
        "requires_tracker: mark test as requiring tracker API (skipped if unavailable)",
    )


def pytest_runtest_setup(item):
    """Skip tests marked with requires_tracker if tracker is unavailable."""
    if "requires_tracker" in item.keywords:
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=1)
            if response.status_code != 200:
                pytest.skip("Tracker API not available (status != 200)")
        except requests.RequestException:
            pytest.skip("Tracker API not available (connection failed)")
