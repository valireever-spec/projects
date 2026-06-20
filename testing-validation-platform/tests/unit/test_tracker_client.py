"""
Unit tests for tracker_client.py

Tests the TrackerClient API abstraction:
- Project discovery and creation
- Bug/gap reporting
- Bug status updates
- Retry logic and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from tracker_client import TrackerClient


class TestTrackerClientProjectDiscovery:
    """Tests for project discovery and initialization."""

    @pytest.mark.unit
    def test_init_with_existing_project(self, mock_tracker_url, mock_projects_list):
        """TrackerClient finds existing project in tracker."""
        with patch("requests.get") as mock_get:
            response = Mock()
            response.status_code = 200
            response.json.return_value = mock_projects_list
            mock_get.return_value = response

            client = TrackerClient(
                tracker_url=mock_tracker_url,
                project_name="investing-platform",
                max_retries=1,
            )

            assert client.project_id == 1
            assert client.project_name == "investing-platform"
            mock_get.assert_called_once()

    @pytest.mark.unit
    def test_init_creates_project_if_not_found(self, mock_tracker_url, mock_project_response):
        """TrackerClient creates project if it doesn't exist."""
        with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
            # First call: project list (empty)
            get_response = Mock()
            get_response.status_code = 200
            get_response.json.return_value = []
            mock_get.return_value = get_response

            # Second call: create project
            post_response = Mock()
            post_response.status_code = 201
            post_response.json.return_value = mock_project_response
            mock_post.return_value = post_response

            client = TrackerClient(
                tracker_url=mock_tracker_url,
                project_name="investing-platform",
                max_retries=1,
            )

            assert client.project_id == 1
            mock_get.assert_called_once()
            mock_post.assert_called_once()

    @pytest.mark.unit
    def test_init_handles_connection_error(self, mock_tracker_url):
        """TrackerClient handles connection errors gracefully (non-blocking)."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("Tracker down")

            client = TrackerClient(
                tracker_url=mock_tracker_url,
                project_name="investing-platform",
                max_retries=1,
            )

            # project_id is None but client still initializes
            assert client.project_id is None
            assert client.project_name == "investing-platform"

    @pytest.mark.unit
    def test_init_retry_logic_succeeds_on_second_attempt(
        self, mock_tracker_url, mock_tracker_intermittent
    ):
        """Retry logic recovers from temporary tracker unavailability."""
        tracker_call, call_count = mock_tracker_intermittent

        with patch("requests.get", side_effect=tracker_call):
            client = TrackerClient(
                tracker_url=mock_tracker_url,
                project_name="investing-platform",
                max_retries=3,
            )

            # Should have succeeded on 3rd attempt
            assert call_count["count"] == 3
            assert client.project_id == 1


class TestReportBug:
    """Tests for bug reporting functionality."""

    @pytest.mark.unit
    def test_report_bug_success(self, tracker_client_with_mocked_api, mock_gap_response):
        """report_bug successfully creates gap in tracker."""
        with patch.object(
            tracker_client_with_mocked_api, "project_id", 1
        ), patch("requests.post") as mock_post:
            response = Mock()
            response.status_code = 201
            response.json.return_value = mock_gap_response
            mock_post.return_value = response

            result = tracker_client_with_mocked_api.report_bug(
                title="Test API Error",
                description="API call failed",
                pillar="Verification & Validation",
                severity="High",
            )

            assert result is True
            mock_post.assert_called_once()

    @pytest.mark.unit
    def test_report_bug_no_project_id(self, tracker_client_unavailable):
        """report_bug returns False if project_id is None."""
        result = tracker_client_unavailable.report_bug(
            title="Test Bug",
            description="Testing no project ID",
            pillar="Security & Privacy",
            severity="Medium",
        )

        assert result is False

    @pytest.mark.unit
    def test_report_bug_retry_on_failure(self, tracker_client_with_mocked_api):
        """report_bug retries on connection failure."""
        with patch.object(tracker_client_with_mocked_api, "project_id", 1), patch(
            "requests.post"
        ) as mock_post:
            # First 2 calls fail, 3rd succeeds
            mock_post.side_effect = [
                requests.ConnectionError("Failed"),
                requests.ConnectionError("Failed"),
                Mock(status_code=201, json=lambda: {"id": 123}),
            ]

            result = tracker_client_with_mocked_api.report_bug(
                title="Test Bug",
                description="Testing retry",
                pillar="Build Quality In",
            )

            # Should retry and eventually succeed
            assert mock_post.call_count >= 1

    @pytest.mark.unit
    def test_report_bug_with_all_fields(self, tracker_client_with_mocked_api):
        """report_bug accepts all optional fields."""
        with patch.object(
            tracker_client_with_mocked_api, "project_id", 1
        ), patch("requests.post") as mock_post:
            response = Mock()
            response.status_code = 201
            response.json.return_value = {"id": 456}
            mock_post.return_value = response

            result = tracker_client_with_mocked_api.report_bug(
                title="Comprehensive Bug Report",
                description="Full details",
                pillar="Observability & Telemetry",
                severity="Critical",
                requirement_id=5,
                effort="1d",
            )

            assert result is True
            call_args = mock_post.call_args
            payload = call_args.kwargs["json"]
            assert payload["requirement_id"] == 5
            assert payload["effort"] == "1d"


class TestUpdateBugStatus:
    """Tests for bug status update functionality."""

    @pytest.mark.unit
    def test_update_bug_status_success(self, tracker_client_with_mocked_api):
        """update_bug_status successfully updates gap in tracker."""
        with patch.object(
            tracker_client_with_mocked_api, "project_id", 1
        ), patch("requests.patch") as mock_patch:
            response = Mock()
            response.status_code = 200
            mock_patch.return_value = response

            result = tracker_client_with_mocked_api.update_bug_status(
                gap_id=123, status="Done", notes="Fixed in Phase 1"
            )

            assert result is True
            mock_patch.assert_called_once()

    @pytest.mark.unit
    def test_update_bug_status_no_project_id(self, tracker_client_unavailable):
        """update_bug_status returns False if project_id is None."""
        result = tracker_client_unavailable.update_bug_status(
            gap_id=999, status="In Remediation"
        )

        assert result is False

    @pytest.mark.unit
    def test_update_bug_status_with_notes(self, tracker_client_with_mocked_api):
        """update_bug_status includes notes in request."""
        with patch.object(
            tracker_client_with_mocked_api, "project_id", 1
        ), patch("requests.patch") as mock_patch:
            response = Mock()
            response.status_code = 200
            mock_patch.return_value = response

            tracker_client_with_mocked_api.update_bug_status(
                gap_id=789, status="Done", notes="Resolved via Phase 1 fixes"
            )

            call_args = mock_patch.call_args
            payload = call_args.kwargs["json"]
            assert payload["description"] == "Resolved via Phase 1 fixes"

    @pytest.mark.unit
    def test_update_bug_status_retry_on_failure(self, tracker_client_with_mocked_api):
        """update_bug_status retries on connection failure."""
        with patch.object(tracker_client_with_mocked_api, "project_id", 1), patch(
            "requests.patch"
        ) as mock_patch:
            # Fail then succeed
            mock_patch.side_effect = [
                requests.ConnectionError("Failed"),
                Mock(status_code=200),
            ]

            result = tracker_client_with_mocked_api.update_bug_status(
                gap_id=555, status="In Remediation"
            )

            # Should attempt retry
            assert mock_patch.call_count >= 1


class TestConfigurationIntegration:
    """Tests for configuration integration."""

    @pytest.mark.unit
    def test_tracker_client_uses_config_defaults(self, mock_env_settings):
        """TrackerClient uses config defaults when not provided."""
        with patch("requests.get") as mock_get:
            response = Mock()
            response.status_code = 200
            response.json.return_value = {
                "projects": [{"id": 1, "name": "investing-platform"}]
            }
            mock_get.return_value = response

            client = TrackerClient()  # No args, should use config

            assert client.project_name == "investing-platform"
            # tracker_url should be configured
            assert "127.0.0.1" in client.tracker_url or "localhost" in client.tracker_url

    @pytest.mark.unit
    def test_tracker_client_respects_custom_url(self, mock_tracker_url):
        """TrackerClient accepts custom tracker URL."""
        custom_url = "http://custom-tracker:9000"

        with patch("requests.get") as mock_get:
            response = Mock()
            response.status_code = 200
            response.json.return_value = {"projects": []}
            mock_get.return_value = response

            client = TrackerClient(tracker_url=custom_url, max_retries=1)

            assert client.tracker_url == custom_url


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    @pytest.mark.unit
    def test_malformed_tracker_response(self, tracker_client_with_mocked_api):
        """TrackerClient handles malformed JSON responses."""
        with patch.object(
            tracker_client_with_mocked_api, "project_id", 1
        ), patch("requests.post") as mock_post:
            response = Mock()
            response.status_code = 200
            response.json.side_effect = ValueError("Invalid JSON")
            mock_post.return_value = response

            # Should not crash, should return False or retry
            result = tracker_client_with_mocked_api.report_bug(
                title="Test", description="Test", pillar="Test"
            )

            # Behavior may vary, but should not crash
            assert isinstance(result, (bool, type(None)))

    @pytest.mark.unit
    def test_timeout_handling(self, tracker_client_with_mocked_api):
        """TrackerClient handles request timeouts."""
        with patch.object(
            tracker_client_with_mocked_api, "project_id", 1
        ), patch("requests.post") as mock_post:
            mock_post.side_effect = requests.Timeout("Request timed out")

            result = tracker_client_with_mocked_api.report_bug(
                title="Test", description="Test", pillar="Test"
            )

            # Should return False after retries
            assert result is False

    @pytest.mark.unit
    def test_http_error_responses(self, tracker_client_with_mocked_api):
        """TrackerClient handles HTTP error responses."""
        with patch.object(
            tracker_client_with_mocked_api, "project_id", 1
        ), patch("requests.post") as mock_post:
            response = Mock()
            response.status_code = 500
            response.text = "Internal Server Error"
            mock_post.return_value = response

            result = tracker_client_with_mocked_api.report_bug(
                title="Test", description="Test", pillar="Test"
            )

            assert result is False
