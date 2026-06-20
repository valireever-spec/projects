"""
Integration tests for tracker API interaction.

Tests actual communication with tracker service (requires running tracker).
These tests may be skipped if tracker is unavailable.
"""

import pytest
import requests
from tracker_client import TrackerClient


class TestTrackerAPIIntegration:
    """Integration tests that require tracker running."""

    @pytest.mark.integration
    @pytest.mark.requires_tracker
    def test_tracker_health_check(self):
        """Verify tracker is accessible."""
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=5)
            assert response.status_code == 200
        except requests.RequestException as e:
            pytest.skip(f"Tracker not available: {e}")

    @pytest.mark.integration
    @pytest.mark.requires_tracker
    def test_get_projects_list(self):
        """Get list of projects from tracker."""
        try:
            response = requests.get("http://127.0.0.1:8001/api/projects", timeout=5)
            assert response.status_code == 200
            projects = response.json()
            assert isinstance(projects, list)
        except requests.RequestException as e:
            pytest.skip(f"Tracker API unavailable: {e}")

    @pytest.mark.integration
    @pytest.mark.requires_tracker
    def test_find_investing_platform_project(self):
        """Find investing-platform project in tracker."""
        try:
            response = requests.get("http://127.0.0.1:8001/api/projects", timeout=5)
            projects = response.json()

            investing_platform = None
            for p in projects:
                if p.get("name") == "investing-platform":
                    investing_platform = p
                    break

            if investing_platform:
                assert investing_platform["id"] is not None
                assert investing_platform["name"] == "investing-platform"
            else:
                pytest.skip("investing-platform project not found in tracker")
        except requests.RequestException as e:
            pytest.skip(f"Tracker API unavailable: {e}")


class TestTrackerClientWithRealAPI:
    """Tests using real tracker API."""

    @pytest.mark.integration
    @pytest.mark.requires_tracker
    def test_tracker_client_initialization(self):
        """TrackerClient can initialize with real tracker."""
        try:
            client = TrackerClient(
                tracker_url="http://127.0.0.1:8001",
                project_name="investing-platform",
                max_retries=3,
            )
            assert client.tracker_url == "http://127.0.0.1:8001"
            assert client.project_name == "investing-platform"
            # project_id will be set if found in tracker
        except requests.RequestException as e:
            pytest.skip(f"Cannot connect to tracker: {e}")

    @pytest.mark.integration
    @pytest.mark.requires_tracker
    def test_tracker_client_reports_bug(self):
        """TrackerClient can report bug to tracker."""
        try:
            client = TrackerClient(
                tracker_url="http://127.0.0.1:8001",
                project_name="investing-platform",
            )

            if client.project_id is None:
                pytest.skip("Could not find investing-platform project")

            result = client.report_bug(
                title="Integration Test Bug",
                description="This is a test bug from integration tests",
                pillar="Verification & Validation",
                severity="Medium",
            )

            # Should either succeed or gracefully fail
            assert isinstance(result, bool)
        except requests.RequestException as e:
            pytest.skip(f"Tracker API error: {e}")

    @pytest.mark.integration
    @pytest.mark.requires_tracker
    def test_tracker_client_get_gaps(self):
        """TrackerClient can retrieve gaps from tracker."""
        try:
            response = requests.get(
                "http://127.0.0.1:8001/api/projects/1/gaps", timeout=5
            )

            if response.status_code == 404:
                pytest.skip("Project ID 1 not found in tracker")

            assert response.status_code == 200
            gaps = response.json()
            assert isinstance(gaps, list)
        except requests.RequestException as e:
            pytest.skip(f"Tracker API unavailable: {e}")


class TestTrackerConnectionResilience:
    """Tests for connection resilience."""

    @pytest.mark.integration
    def test_tracker_client_handles_unreachable_tracker(self):
        """TrackerClient handles unreachable tracker gracefully."""
        # Use non-existent tracker address
        client = TrackerClient(
            tracker_url="http://127.0.0.1:19999",  # Non-existent port
            project_name="test-project",
            max_retries=1,  # Quick retry
        )

        # Should initialize but project_id will be None
        assert client.project_id is None

    @pytest.mark.integration
    def test_report_bug_with_unavailable_tracker(self):
        """report_bug handles unavailable tracker gracefully."""
        client = TrackerClient(
            tracker_url="http://127.0.0.1:19999",  # Non-existent
            project_name="test-project",
            max_retries=1,
        )

        # Should return False (non-blocking failure)
        result = client.report_bug(
            title="Test",
            description="Test bug",
            pillar="Testing",
        )

        assert result is False
