"""
Production Orchestrator - Layer 1 Tests: State Tracking & Verification

Tests for:
- StateSnapshot creation and metrics
- StateDiff comparison and change detection
- FixVerification safety checks
- TaskClassifier task type determination
"""

import pytest
from scripts.orchestrator_layer1_state import (
    TaskType,
    TestResult,
    StateSnapshot,
    StateDiff,
    FixVerification,
    StateComparator,
    StateSnapshotBuilder,
    TaskClassifier,
)


class TestTaskType:
    """Test TaskType enum."""

    def test_all_task_types_defined(self) -> None:
        """All task types are defined."""
        assert TaskType.ANALYZED.value == "analyzed"
        assert TaskType.FIXED.value == "fixed"
        assert TaskType.VERIFIED.value == "verified"
        assert TaskType.DEPLOYED.value == "deployed"


class TestTestResult:
    """Test TestResult model."""

    def test_test_result_creation(self) -> None:
        """Test result created correctly."""
        result = TestResult(test_name="test_foo", passed=True, duration_seconds=0.5)

        assert result.test_name == "test_foo"
        assert result.passed is True
        assert result.duration_seconds == 0.5
        assert result.error_message is None

    def test_test_result_with_error(self) -> None:
        """Test result with error message."""
        result = TestResult(
            test_name="test_bar",
            passed=False,
            duration_seconds=1.2,
            error_message="AssertionError",
        )

        assert result.passed is False
        assert result.error_message == "AssertionError"


class TestStateSnapshot:
    """Test StateSnapshot model."""

    def test_snapshot_creation(self) -> None:
        """Snapshot created correctly."""
        snapshot = StateSnapshot(
            timestamp="2026-07-12T12:00:00",
            file_hashes={"app.py": "hash1", "utils.py": "hash2"},
            tests_passing=5,
            tests_failing=1,
            coverage_percent=80.0,
        )

        assert snapshot.total_files == 0  # Not set in constructor
        assert len(snapshot.file_hashes) == 2
        assert snapshot.test_pass_rate() == pytest.approx(83.33, 0.1)

    def test_test_pass_rate(self) -> None:
        """Test pass rate calculated correctly."""
        snapshot = StateSnapshot(
            timestamp="2026-07-12T12:00:00",
            file_hashes={},
            tests_passing=8,
            tests_failing=2,
            coverage_percent=75.0,
        )

        assert snapshot.test_pass_rate() == 80.0

    def test_test_pass_rate_no_tests(self) -> None:
        """Test pass rate with no tests."""
        snapshot = StateSnapshot(
            timestamp="2026-07-12T12:00:00",
            file_hashes={},
            tests_passing=0,
            tests_failing=0,
            coverage_percent=0.0,
        )

        assert snapshot.test_pass_rate() == 0.0

    def test_snapshot_summary(self) -> None:
        """Snapshot summary generated."""
        snapshot = StateSnapshot(
            timestamp="2026-07-12T12:00:00",
            file_hashes={"app.py": "hash1"},
            tests_passing=5,
            tests_failing=0,
            coverage_percent=85.0,
            total_files=1,
            total_lines=50,
        )

        summary = snapshot.summary()

        assert summary["files"] == 1
        assert summary["tests_passing"] == 5
        assert summary["coverage_percent"] == 85.0
        assert summary["test_pass_rate"] == 100.0


class TestStateDiff:
    """Test StateDiff model."""

    def test_diff_creation(self) -> None:
        """Diff created correctly."""
        before = StateSnapshot(
            timestamp="2026-07-12T12:00:00", file_hashes={}, tests_passing=5
        )
        after = StateSnapshot(
            timestamp="2026-07-12T12:05:00", file_hashes={"app.py": "hash1"}
        )

        diff = StateDiff(before=before, after=after)

        assert diff.before == before
        assert diff.after == after

    def test_any_changes_true(self) -> None:
        """Any changes detected."""
        diff = StateDiff(
            before=StateSnapshot("2026-07-12T12:00:00", {}),
            after=StateSnapshot("2026-07-12T12:05:00", {}),
            files_changed={"app.py"},
        )

        assert diff.any_changes() is True

    def test_any_changes_false(self) -> None:
        """No changes detected."""
        diff = StateDiff(
            before=StateSnapshot("2026-07-12T12:00:00", {}),
            after=StateSnapshot("2026-07-12T12:05:00", {}),
        )

        assert diff.any_changes() is False

    def test_had_regressions_true(self) -> None:
        """Regressions detected."""
        diff = StateDiff(
            before=StateSnapshot("2026-07-12T12:00:00", {}),
            after=StateSnapshot("2026-07-12T12:05:00", {}),
            tests_new_failing={"test_foo"},
        )

        assert diff.had_regressions() is True

    def test_had_regressions_false(self) -> None:
        """No regressions."""
        diff = StateDiff(
            before=StateSnapshot("2026-07-12T12:00:00", {}),
            after=StateSnapshot("2026-07-12T12:05:00", {}),
        )

        assert diff.had_regressions() is False

    def test_tests_improved(self) -> None:
        """Improved tests detected."""
        diff = StateDiff(
            before=StateSnapshot("2026-07-12T12:00:00", {}),
            after=StateSnapshot("2026-07-12T12:05:00", {}),
            tests_new_passing={"test_foo", "test_bar"},
        )

        assert diff.tests_improved() is True

    def test_metrics_improved(self) -> None:
        """Improved metrics detected."""
        diff = StateDiff(
            before=StateSnapshot("2026-07-12T12:00:00", {}),
            after=StateSnapshot("2026-07-12T12:05:00", {}),
            metrics_delta={"performance": 5.0, "coverage": 10.0},
        )

        assert diff.metrics_improved() is True


class TestStateComparator:
    """Test StateComparator."""

    def test_compare_no_changes(self) -> None:
        """Comparison detects no changes."""
        snapshot = StateSnapshot(
            timestamp="2026-07-12T12:00:00",
            file_hashes={"app.py": "hash1"},
            tests_passing=5,
            tests_failing=0,
        )

        diff = StateComparator.compare(snapshot, snapshot)

        assert diff.any_changes() is False
        assert diff.had_regressions() is False

    def test_compare_file_changed(self) -> None:
        """Comparison detects file changes."""
        before = StateSnapshot(
            timestamp="2026-07-12T12:00:00",
            file_hashes={"app.py": "hash1"},
            tests_passing=5,
            tests_failing=0,
        )
        after = StateSnapshot(
            timestamp="2026-07-12T12:05:00",
            file_hashes={"app.py": "hash2"},
            tests_passing=5,
            tests_failing=0,
        )

        diff = StateComparator.compare(before, after)

        assert "app.py" in diff.files_changed
        assert diff.any_changes() is True

    def test_compare_file_added(self) -> None:
        """Comparison detects added files."""
        before = StateSnapshot(
            timestamp="2026-07-12T12:00:00", file_hashes={"app.py": "hash1"}
        )
        after = StateSnapshot(
            timestamp="2026-07-12T12:05:00",
            file_hashes={"app.py": "hash1", "utils.py": "hash2"},
        )

        diff = StateComparator.compare(before, after)

        assert "utils.py" in diff.files_added
        assert diff.any_changes() is True

    def test_compare_tests_regressed(self) -> None:
        """Comparison detects test regressions."""
        before = StateSnapshot(
            timestamp="2026-07-12T12:00:00",
            file_hashes={"app.py": "hash1"},
            test_results={"test_foo": TestResult("test_foo", True, 0.5)},
            tests_passing=1,
            tests_failing=0,
        )
        after = StateSnapshot(
            timestamp="2026-07-12T12:05:00",
            file_hashes={"app.py": "hash2"},
            test_results={"test_foo": TestResult("test_foo", False, 0.5)},
            tests_passing=0,
            tests_failing=1,
        )

        diff = StateComparator.compare(before, after)

        assert "test_foo" in diff.tests_new_failing
        assert diff.had_regressions() is True

    def test_compare_coverage_delta(self) -> None:
        """Comparison calculates coverage delta."""
        before = StateSnapshot(
            timestamp="2026-07-12T12:00:00",
            file_hashes={"app.py": "hash1"},
            coverage_percent=70.0,
        )
        after = StateSnapshot(
            timestamp="2026-07-12T12:05:00",
            file_hashes={"app.py": "hash2"},
            coverage_percent=85.0,
        )

        diff = StateComparator.compare(before, after)

        assert diff.coverage_delta == 15.0


class TestStateSnapshotBuilder:
    """Test StateSnapshotBuilder."""

    def test_builder_creates_snapshot(self) -> None:
        """Builder creates snapshot correctly."""
        snapshot = (
            StateSnapshotBuilder()
            .add_file("app.py", "def hello(): pass")
            .add_test_result("test_foo", True, 0.5)
            .add_metric("coverage", 80.0)
            .set_coverage(80.0)
            .build()
        )

        assert "app.py" in snapshot.file_hashes
        assert "test_foo" in snapshot.test_results
        assert snapshot.metrics["coverage"] == 80.0

    def test_builder_tracks_lines(self) -> None:
        """Builder counts lines."""
        snapshot = (
            StateSnapshotBuilder().add_file("app.py", "line1\nline2\nline3").build()
        )

        assert snapshot.total_lines == 3

    def test_builder_counts_tests(self) -> None:
        """Builder counts passing/failing tests."""
        snapshot = (
            StateSnapshotBuilder()
            .add_test_result("test_foo", True, 0.5)
            .add_test_result("test_bar", True, 0.3)
            .add_test_result("test_baz", False, 0.2)
            .build()
        )

        assert snapshot.tests_passing == 2
        assert snapshot.tests_failing == 1


class TestFixVerification:
    """Test FixVerification."""

    def test_verification_all_checks_pass(self) -> None:
        """Verification passes when all checks pass."""
        before = (
            StateSnapshotBuilder()
            .add_file("app.py", "old code")
            .add_test_result("test_foo", True, 0.5)
            .set_coverage(65.0)
            .build()
        )
        after = (
            StateSnapshotBuilder()
            .add_file("app.py", "new code")
            .add_test_result("test_foo", True, 0.5)
            .add_test_result("test_bar", True, 0.3)
            .set_coverage(80.0)
            .build()
        )
        after.tests_passing = 2
        after.tests_failing = 0

        diff = StateComparator.compare(before, after)
        verification = FixVerification(
            task_id="TASK_001", before=before, after=after, diff=diff
        )
        verification.verify()

        assert verification.changes_made is True
        assert verification.tests_passing is True
        assert verification.no_regressions is True
        assert verification.safe_to_deploy is True

    def test_verification_fails_no_changes(self) -> None:
        """Verification fails if no changes."""
        snapshot = (
            StateSnapshotBuilder()
            .add_file("app.py", "code")
            .add_test_result("test_foo", True, 0.5)
            .set_coverage(80.0)
            .build()
        )

        diff = StateComparator.compare(snapshot, snapshot)
        verification = FixVerification(
            task_id="TASK_001", before=snapshot, after=snapshot, diff=diff
        )
        verification.verify()

        assert verification.changes_made is False
        assert verification.safe_to_deploy is False

    def test_verification_fails_regressions(self) -> None:
        """Verification fails if tests regress."""
        before = (
            StateSnapshotBuilder()
            .add_file("app.py", "old code")
            .add_test_result("test_foo", True, 0.5)
            .set_coverage(80.0)
            .build()
        )
        before.tests_passing = 1
        before.tests_failing = 0

        after = (
            StateSnapshotBuilder()
            .add_file("app.py", "new code")
            .add_test_result("test_foo", False, 0.5)
            .set_coverage(80.0)
            .build()
        )
        after.tests_passing = 0
        after.tests_failing = 1

        diff = StateComparator.compare(before, after)
        verification = FixVerification(
            task_id="TASK_001", before=before, after=after, diff=diff
        )
        verification.verify()

        assert verification.no_regressions is False
        assert verification.safe_to_deploy is False

    def test_verification_fails_low_coverage(self) -> None:
        """Verification fails if coverage too low."""
        before = (
            StateSnapshotBuilder()
            .add_file("app.py", "old code")
            .add_test_result("test_foo", True, 0.5)
            .set_coverage(50.0)  # Below 70%
            .build()
        )
        before.tests_passing = 1
        before.tests_failing = 0

        after = (
            StateSnapshotBuilder()
            .add_file("app.py", "new code")
            .add_test_result("test_foo", True, 0.5)
            .set_coverage(65.0)  # Still below 70%
            .build()
        )
        after.tests_passing = 1
        after.tests_failing = 0

        diff = StateComparator.compare(before, after)
        verification = FixVerification(
            task_id="TASK_001", before=before, after=after, diff=diff
        )
        verification.verify()

        assert verification.safe_to_deploy is False


class TestTaskClassifier:
    """Test TaskClassifier."""

    def test_classify_analyzed(self) -> None:
        """Task classified as ANALYZED when no changes."""
        snapshot = (
            StateSnapshotBuilder()
            .add_file("app.py", "code")
            .add_test_result("test_foo", True, 0.5)
            .build()
        )

        task_type, _ = TaskClassifier.classify(snapshot, snapshot)

        assert task_type == TaskType.ANALYZED

    def test_classify_verified(self) -> None:
        """Task classified as VERIFIED when changes + tests pass."""
        before = (
            StateSnapshotBuilder()
            .add_file("app.py", "old code")
            .add_test_result("test_foo", True, 0.5)
            .build()
        )
        before.tests_passing = 1
        before.tests_failing = 0

        after = (
            StateSnapshotBuilder()
            .add_file("app.py", "new code")
            .add_test_result("test_foo", True, 0.5)
            .add_test_result("test_bar", True, 0.3)
            .build()
        )
        after.tests_passing = 2
        after.tests_failing = 0

        task_type, _ = TaskClassifier.classify(before, after)

        assert task_type == TaskType.VERIFIED

    def test_classify_fixed_with_regressions(self) -> None:
        """Task classified as FIXED when changes but tests regress."""
        before = (
            StateSnapshotBuilder()
            .add_file("app.py", "old code")
            .add_test_result("test_foo", True, 0.5)
            .build()
        )
        before.tests_passing = 1
        before.tests_failing = 0

        after = (
            StateSnapshotBuilder()
            .add_file("app.py", "new code")
            .add_test_result("test_foo", False, 0.5)
            .build()
        )
        after.tests_passing = 0
        after.tests_failing = 1

        task_type, _ = TaskClassifier.classify(before, after)

        assert task_type == TaskType.FIXED


class TestLayer1Integration:
    """Integration tests for Layer 1."""

    def test_end_to_end_analysis(self) -> None:
        """End-to-end analysis workflow."""
        # Build before state
        before = (
            StateSnapshotBuilder()
            .add_file("app.py", "def foo(): pass")
            .add_file("utils.py", "def bar(): pass")
            .add_test_result("test_foo", True, 0.5)
            .add_test_result("test_bar", True, 0.3)
            .add_metric("performance", 75.0)
            .set_coverage(70.0)
            .build()
        )
        before.tests_passing = 2
        before.tests_failing = 0

        # Build after state
        after = (
            StateSnapshotBuilder()
            .add_file("app.py", "def foo(): return 1")
            .add_file("utils.py", "def bar(): return 2")
            .add_test_result("test_foo", True, 0.4)
            .add_test_result("test_bar", True, 0.2)
            .add_test_result("test_integration", True, 0.1)
            .add_metric("performance", 85.0)
            .set_coverage(85.0)
            .build()
        )
        after.tests_passing = 3
        after.tests_failing = 0

        # Analyze
        diff = StateComparator.compare(before, after)

        # Verify
        verification = FixVerification(
            task_id="TASK_INTEGRATION_001", before=before, after=after, diff=diff
        )
        verification.verify()

        # Classify
        task_type, _ = TaskClassifier.classify(before, after)

        # Assert
        assert diff.any_changes() is True
        assert verification.safe_to_deploy is True
        assert task_type == TaskType.VERIFIED


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
