"""
Production-Grade Orchestrator - Layer 1: State Tracking & Verification

Core concepts:
- Before/after snapshots with explicit state capture
- Dependency tracking (import graph)
- Test results and metrics
- Explicit task classification: ANALYZED vs FIXED vs VERIFIED vs DEPLOYED
- Verification that changes actually work (not just syntax valid)
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Explicit task classification."""

    ANALYZED = "analyzed"  # Just reports findings, no changes
    FIXED = "fixed"  # Code changed, awaiting verification
    VERIFIED = "verified"  # Changed + tests pass, no regressions
    DEPLOYED = "deployed"  # Live in production


@dataclass
class TestResult:
    """Result of a single test."""

    test_name: str
    passed: bool
    duration_seconds: float
    error_message: Optional[str] = None


@dataclass
class StateSnapshot:
    """Complete snapshot of codebase state at a point in time."""

    timestamp: str
    file_hashes: Dict[str, str]  # filepath -> SHA256 hash
    test_results: Dict[str, TestResult] = field(
        default_factory=dict
    )  # test_name -> result
    metrics: Dict[str, float] = field(default_factory=dict)  # metric_name -> value
    dependencies: Dict[str, Set[str]] = field(default_factory=dict)  # file -> imports
    total_files: int = 0
    total_lines: int = 0
    tests_passing: int = 0
    tests_failing: int = 0
    coverage_percent: float = 0.0

    def test_pass_rate(self) -> float:
        """Percentage of tests passing."""
        total = self.tests_passing + self.tests_failing
        if total == 0:
            return 0.0
        return (self.tests_passing / total) * 100

    def summary(self) -> Dict[str, object]:
        """Get snapshot summary."""
        return {
            "timestamp": self.timestamp,
            "files": self.total_files,
            "lines_of_code": self.total_lines,
            "tests_passing": self.tests_passing,
            "tests_failing": self.tests_failing,
            "test_pass_rate": self.test_pass_rate(),
            "coverage_percent": self.coverage_percent,
            "file_count": len(self.file_hashes),
            "dependency_count": len(self.dependencies),
        }


@dataclass
class StateDiff:
    """Difference between two state snapshots."""

    before: StateSnapshot
    after: StateSnapshot
    files_changed: Set[str] = field(default_factory=set)
    files_added: Set[str] = field(default_factory=set)
    files_deleted: Set[str] = field(default_factory=set)
    tests_new_passing: Set[str] = field(default_factory=set)
    tests_new_failing: Set[str] = field(default_factory=set)
    metrics_delta: Dict[str, float] = field(default_factory=dict)
    coverage_delta: float = 0.0

    def any_changes(self) -> bool:
        """Whether any files changed."""
        return bool(self.files_changed or self.files_added or self.files_deleted)

    def had_regressions(self) -> bool:
        """Whether any tests regressed."""
        return len(self.tests_new_failing) > 0

    def tests_improved(self) -> bool:
        """Whether tests improved."""
        return len(self.tests_new_passing) > 0 and not self.had_regressions()

    def metrics_improved(self) -> bool:
        """Whether metrics improved overall."""
        if not self.metrics_delta:
            return False
        # Check if most metrics improved (positive delta)
        positive = sum(1 for v in self.metrics_delta.values() if v > 0)
        return positive > len(self.metrics_delta) / 2

    def summary(self) -> Dict[str, object]:
        """Summarize the diff."""
        return {
            "files_changed": len(self.files_changed),
            "files_added": len(self.files_added),
            "files_deleted": len(self.files_deleted),
            "tests_new_passing": len(self.tests_new_passing),
            "tests_new_failing": len(self.tests_new_failing),
            "regressions": self.had_regressions(),
            "tests_improved": self.tests_improved(),
            "metrics_improved": self.metrics_improved(),
            "coverage_delta": self.coverage_delta,
        }


@dataclass
class FixVerification:
    """Verification that a fix actually worked."""

    task_id: str
    before: StateSnapshot
    after: StateSnapshot
    diff: StateDiff

    changes_made: bool = False  # File hashes changed
    tests_passing: bool = False  # Tests pass in after state
    metrics_improved: bool = False  # Metrics better than before
    no_regressions: bool = False  # No tests regressed
    safe_to_deploy: bool = False  # All checks passed

    def verify(self) -> None:
        """Run verification checks."""
        # Check 1: Did anything change?
        self.changes_made = self.diff.any_changes()

        # Check 2: Are tests passing?
        self.tests_passing = (
            self.after.tests_failing == 0 and self.after.tests_passing > 0
        )

        # Check 3: Did metrics improve?
        self.metrics_improved = self.diff.metrics_improved()

        # Check 4: No regressions?
        self.no_regressions = not self.diff.had_regressions()

        # Check 5: Safe to deploy?
        self.safe_to_deploy = (
            self.changes_made
            and self.tests_passing
            and self.no_regressions
            and self.after.coverage_percent >= 70.0
        )

    def is_verified(self) -> bool:
        """Whether fix is verified (safe to deploy)."""
        return self.safe_to_deploy

    def summary(self) -> Dict[str, object]:
        """Summarize verification results."""
        return {
            "task_id": self.task_id,
            "changes_made": self.changes_made,
            "tests_passing": self.tests_passing,
            "metrics_improved": self.metrics_improved,
            "no_regressions": self.no_regressions,
            "safe_to_deploy": self.safe_to_deploy,
            "verified": self.is_verified(),
            "before_state": self.before.summary(),
            "after_state": self.after.summary(),
            "diff": self.diff.summary(),
        }


class StateComparator:
    """Compares two state snapshots to generate diffs."""

    @staticmethod
    def compare(before: StateSnapshot, after: StateSnapshot) -> StateDiff:
        """Compare two snapshots and generate diff."""
        diff = StateDiff(before=before, after=after)

        # Detect file changes
        diff.files_changed = set()
        for filepath in before.file_hashes:
            if filepath in after.file_hashes:
                if before.file_hashes[filepath] != after.file_hashes[filepath]:
                    diff.files_changed.add(filepath)

        # Detect added files
        diff.files_added = set(after.file_hashes.keys()) - set(
            before.file_hashes.keys()
        )

        # Detect deleted files
        diff.files_deleted = set(before.file_hashes.keys()) - set(
            after.file_hashes.keys()
        )

        # Detect test changes
        before_passing = {
            name for name, result in before.test_results.items() if result.passed
        }
        after_passing = {
            name for name, result in after.test_results.items() if result.passed
        }

        diff.tests_new_passing = after_passing - before_passing
        diff.tests_new_failing = before_passing - after_passing

        # Calculate coverage delta
        diff.coverage_delta = after.coverage_percent - before.coverage_percent

        # Calculate metric deltas
        for metric_name in before.metrics:
            if metric_name in after.metrics:
                diff.metrics_delta[metric_name] = (
                    after.metrics[metric_name] - before.metrics[metric_name]
                )

        return diff


class StateSnapshotBuilder:
    """Builder for creating state snapshots."""

    def __init__(self) -> None:
        self.timestamp = datetime.now().isoformat()
        self.file_hashes: Dict[str, str] = {}
        self.test_results: Dict[str, TestResult] = {}
        self.metrics: Dict[str, float] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        self.total_files = 0
        self.total_lines = 0
        self.coverage_percent = 0.0

    def add_file(self, filepath: str, content: str) -> "StateSnapshotBuilder":
        """Add file to snapshot with hash."""
        file_hash = hashlib.sha256(content.encode()).hexdigest()
        self.file_hashes[filepath] = file_hash
        self.total_files += 1
        self.total_lines += len(content.split("\n"))
        return self

    def add_test_result(
        self, test_name: str, passed: bool, duration: float, error: Optional[str] = None
    ) -> "StateSnapshotBuilder":
        """Add test result."""
        self.test_results[test_name] = TestResult(
            test_name=test_name,
            passed=passed,
            duration_seconds=duration,
            error_message=error,
        )
        return self

    def add_metric(self, metric_name: str, value: float) -> "StateSnapshotBuilder":
        """Add metric."""
        self.metrics[metric_name] = value
        return self

    def add_dependency(
        self, file_path: str, imports: Set[str]
    ) -> "StateSnapshotBuilder":
        """Add dependency tracking."""
        self.dependencies[file_path] = imports
        return self

    def set_coverage(self, coverage_percent: float) -> "StateSnapshotBuilder":
        """Set coverage percentage."""
        self.coverage_percent = coverage_percent
        return self

    def build(self) -> StateSnapshot:
        """Build and return snapshot."""
        snapshot = StateSnapshot(
            timestamp=self.timestamp,
            file_hashes=self.file_hashes,
            test_results=self.test_results,
            metrics=self.metrics,
            dependencies=self.dependencies,
            total_files=self.total_files,
            total_lines=self.total_lines,
            coverage_percent=self.coverage_percent,
        )
        snapshot.tests_passing = sum(1 for r in self.test_results.values() if r.passed)
        snapshot.tests_failing = len(self.test_results) - snapshot.tests_passing
        return snapshot


class TaskClassifier:
    """Classifies tasks based on state changes."""

    @staticmethod
    def classify(before: StateSnapshot, after: StateSnapshot) -> Tuple[TaskType, str]:
        """Classify task based on before/after states."""
        diff = StateComparator.compare(before, after)

        # ANALYZED: No changes made
        if not diff.any_changes():
            return TaskType.ANALYZED, "No code changes detected"

        # FIXED: Changes made but not verified
        if diff.any_changes() and diff.had_regressions():
            return TaskType.FIXED, "Changes made but tests regressed"

        # VERIFIED: Changes made, tests pass, no regressions
        if (
            diff.any_changes()
            and not diff.had_regressions()
            and after.test_pass_rate() >= 70.0
        ):
            return TaskType.VERIFIED, "Changes verified by tests"

        # Default to FIXED if any changes
        return TaskType.FIXED, "Changes made, awaiting verification"


def main() -> None:
    """Demo Layer 1 state tracking."""
    print("=" * 80)
    print("LAYER 1: STATE TRACKING & VERIFICATION")
    print("=" * 80 + "\n")

    # Build before state
    print("📸 Capturing BEFORE state...\n")
    before = (
        StateSnapshotBuilder()
        .add_file("app.py", "def hello(): pass")
        .add_file("utils.py", "def util(): pass")
        .add_test_result("test_hello", passed=True, duration=0.5)
        .add_test_result("test_util", passed=True, duration=0.3)
        .add_metric("performance_score", 75.0)
        .add_metric("maintainability", 80.0)
        .add_dependency("app.py", {"utils"})
        .set_coverage(65.0)
        .build()
    )

    print(f"   Files: {before.total_files}")
    print(f"   Tests passing: {before.tests_passing}")
    print(f"   Coverage: {before.coverage_percent}%")
    print()

    # Build after state (with improvements)
    print("📸 Capturing AFTER state...\n")
    after = (
        StateSnapshotBuilder()
        .add_file("app.py", "def hello(): return 'world'")
        .add_file("utils.py", "def util(): return None")
        .add_test_result("test_hello", passed=True, duration=0.4)
        .add_test_result("test_util", passed=True, duration=0.3)
        .add_test_result("test_integration", passed=True, duration=0.6)
        .add_metric("performance_score", 82.0)
        .add_metric("maintainability", 85.0)
        .add_dependency("app.py", {"utils"})
        .set_coverage(80.0)
        .build()
    )

    print(f"   Files: {after.total_files}")
    print(f"   Tests passing: {after.tests_passing}")
    print(f"   Coverage: {after.coverage_percent}%")
    print()

    # Compare
    print("🔍 Analyzing changes...\n")
    diff = StateComparator.compare(before, after)
    print(f"   Files changed: {len(diff.files_changed)}")
    print(f"   Files added: {len(diff.files_added)}")
    print(f"   Tests new passing: {len(diff.tests_new_passing)}")
    print(f"   Coverage delta: {diff.coverage_delta:+.1f}%")
    print()

    # Verify
    print("✅ Verifying fix...\n")
    verification = FixVerification(
        task_id="TASK_001", before=before, after=after, diff=diff
    )
    verification.verify()

    print(f"   Changes made: {verification.changes_made}")
    print(f"   Tests passing: {verification.tests_passing}")
    print(f"   Metrics improved: {verification.metrics_improved}")
    print(f"   No regressions: {verification.no_regressions}")
    print(f"   Safe to deploy: {verification.safe_to_deploy}")
    print()

    # Classify
    print("📋 Classifying task...\n")
    task_type, reason = TaskClassifier.classify(before, after)
    print(f"   Type: {task_type.value.upper()}")
    print(f"   Reason: {reason}")
    print()

    # Summary
    print("📊 VERIFICATION REPORT")
    print("=" * 80)
    summary = verification.summary()
    print(json.dumps(summary, indent=2))
    print("=" * 80)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
