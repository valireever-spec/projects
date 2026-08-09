"""
Layer 5: Task Classification & Reporting - Comprehensive Test Suite

Tests cover:
- Task status classification (ANALYZED, FIXED, VERIFIED, DEPLOYED)
- Metrics tracking and improvement calculation
- Audit trail tracking
- Comprehensive task and deployment reporting
- Report generation and export
"""

import pytest
from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../scripts"))

from orchestrator_layer5_reporting import (
    TaskStatus,
    AuditAction,
    TaskMetrics,
    AuditEntry,
    TaskReport,
    DeploymentReport,
    TaskClassifier,
    ReportGenerator,
    TaskSummary,
)


class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_task_statuses_defined(self):
        """Test all task statuses are defined."""
        statuses = [
            TaskStatus.ANALYZED,
            TaskStatus.FIXED,
            TaskStatus.VERIFIED,
            TaskStatus.DEPLOYED,
        ]
        assert len(statuses) == 4

    def test_analyzed_status(self):
        """Test ANALYZED status."""
        assert TaskStatus.ANALYZED.value == "analyzed"

    def test_deployed_status(self):
        """Test DEPLOYED status."""
        assert TaskStatus.DEPLOYED.value == "deployed"


class TestAuditAction:
    """Test AuditAction enum."""

    def test_audit_actions_defined(self):
        """Test all audit actions are defined."""
        actions = [
            AuditAction.ANALYZE,
            AuditAction.PLAN,
            AuditAction.EXECUTE,
            AuditAction.TEST,
            AuditAction.VERIFY,
            AuditAction.DEPLOY,
            AuditAction.ROLLBACK,
        ]
        assert len(actions) == 7


class TestTaskMetrics:
    """Test TaskMetrics."""

    def test_metrics_creation(self):
        """Test creating metrics."""
        metrics = TaskMetrics(
            test_pass_rate=95.0,
            coverage_percent=85.0,
            code_quality_score=90.0,
            performance_score=80.0,
            security_score=92.0,
            reliability_score=88.0,
        )

        assert metrics.test_pass_rate == 95.0
        assert metrics.coverage_percent == 85.0

    def test_overall_score(self):
        """Test overall score calculation."""
        metrics = TaskMetrics(
            test_pass_rate=100.0,
            coverage_percent=100.0,
            code_quality_score=100.0,
            performance_score=100.0,
            security_score=100.0,
            reliability_score=100.0,
        )

        assert metrics.overall_score() == 100.0

    def test_overall_score_average(self):
        """Test overall score is average of all metrics."""
        metrics = TaskMetrics(
            test_pass_rate=80.0,
            coverage_percent=80.0,
            code_quality_score=80.0,
            performance_score=80.0,
            security_score=80.0,
            reliability_score=80.0,
        )

        assert metrics.overall_score() == 80.0

    def test_improvement_calculation(self):
        """Test improvement calculation."""
        before = TaskMetrics(
            test_pass_rate=80.0,
            coverage_percent=65.0,
            code_quality_score=75.0,
            performance_score=70.0,
            security_score=80.0,
            reliability_score=75.0,
        )

        after = TaskMetrics(
            test_pass_rate=95.0,
            coverage_percent=85.0,
            code_quality_score=90.0,
            performance_score=85.0,
            security_score=92.0,
            reliability_score=90.0,
        )

        improvement = after.improvement(before)

        assert improvement["test_pass_rate"] == 15.0
        assert improvement["coverage"] == 20.0
        assert improvement["code_quality"] == 15.0

    def test_negative_improvement(self):
        """Test negative improvement (degradation)."""
        before = TaskMetrics(90.0, 80.0, 85.0, 80.0, 90.0, 85.0)
        after = TaskMetrics(85.0, 75.0, 80.0, 75.0, 85.0, 80.0)

        improvement = after.improvement(before)
        assert improvement["test_pass_rate"] == -5.0


class TestAuditEntry:
    """Test AuditEntry."""

    def test_audit_entry_creation(self):
        """Test creating audit entry."""
        entry = AuditEntry(
            timestamp="2026-07-12T10:00:00",
            action=AuditAction.EXECUTE,
            actor="claude",
            resource="auth_module",
        )

        assert entry.action == AuditAction.EXECUTE
        assert entry.actor == "claude"

    def test_audit_entry_summary(self):
        """Test audit entry summary."""
        entry = AuditEntry(
            timestamp="2026-07-12T10:00:00",
            action=AuditAction.VERIFY,
            actor="pytest",
            resource="test_suite",
            result="success",
        )

        summary = entry.summary()
        assert "VERIFY" in summary
        assert "test_suite" in summary

    def test_audit_entry_with_error(self):
        """Test audit entry with error."""
        entry = AuditEntry(
            timestamp="2026-07-12T10:00:00",
            action=AuditAction.DEPLOY,
            actor="orchestrator",
            resource="api_service",
            result="failure",
            error_message="Deployment timeout",
        )

        assert entry.result == "failure"
        assert entry.error_message == "Deployment timeout"


class TestTaskReport:
    """Test TaskReport."""

    def test_report_creation(self):
        """Test creating task report."""
        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        report = TaskReport(
            task_id="TASK_001",
            status=TaskStatus.VERIFIED,
            timestamp="2026-07-12T10:00:00",
            title="Refactor module",
            description="Split into components",
            before_metrics=before,
            after_metrics=after,
        )

        assert report.task_id == "TASK_001"
        assert report.status == TaskStatus.VERIFIED

    def test_metrics_improvement_in_report(self):
        """Test metrics improvement in report."""
        before = TaskMetrics(80.0, 60.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        report = TaskReport(
            task_id="TASK_001",
            status=TaskStatus.VERIFIED,
            timestamp="2026-07-12T10:00:00",
            title="Fix bugs",
            description="Bug fixes",
            before_metrics=before,
            after_metrics=after,
        )

        improvement = report.metrics_improvement()
        assert improvement["coverage"] == 25.0

    def test_improved_and_degraded_metrics(self):
        """Test tracking improved vs degraded metrics."""
        before = TaskMetrics(90.0, 80.0, 85.0, 80.0, 90.0, 85.0)
        after = TaskMetrics(85.0, 85.0, 95.0, 75.0, 92.0, 88.0)

        report = TaskReport(
            task_id="TASK_001",
            status=TaskStatus.VERIFIED,
            timestamp="2026-07-12T10:00:00",
            title="Refactor",
            description="Code improvement",
            before_metrics=before,
            after_metrics=after,
        )

        improved = report.improved_metrics()
        degraded = report.degraded_metrics()

        assert len(improved) > 0
        assert len(degraded) > 0

    def test_report_summary(self):
        """Test report summary generation."""
        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        report = TaskReport(
            task_id="TASK_001",
            status=TaskStatus.VERIFIED,
            timestamp="2026-07-12T10:00:00",
            title="Optimization",
            description="Performance improvement",
            before_metrics=before,
            after_metrics=after,
            confidence_percent=95.0,
        )

        summary = report.summary()
        assert summary["task_id"] == "TASK_001"
        assert summary["status"] == "verified"
        assert summary["confidence"] == 95.0

    def test_audit_trail_in_report(self):
        """Test audit trail in report."""
        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        report = TaskReport(
            task_id="TASK_001",
            status=TaskStatus.VERIFIED,
            timestamp="2026-07-12T10:00:00",
            title="Fix",
            description="Bug fix",
            before_metrics=before,
            after_metrics=after,
        )

        entry = AuditEntry(
            timestamp="2026-07-12T10:00:00",
            action=AuditAction.ANALYZE,
            actor="claude",
            resource="module",
        )

        report.audit_trail.append(entry)
        assert len(report.audit_trail) == 1


class TestDeploymentReport:
    """Test DeploymentReport."""

    def test_report_creation(self):
        """Test creating deployment report."""
        report = DeploymentReport(
            deployment_id="DEPLOY_001",
            timestamp="2026-07-12T10:00:00",
            environment="staging",
            status="success",
            started_at="2026-07-12T10:00:00",
            completed_at="2026-07-12T10:05:00",
            total_changes=10,
            failed_changes=0,
            tests_run=100,
            tests_passed=98,
        )

        assert report.deployment_id == "DEPLOY_001"
        assert report.environment == "staging"

    def test_pass_rate_calculation(self):
        """Test test pass rate calculation."""
        report = DeploymentReport(
            deployment_id="DEPLOY_1",
            timestamp="2026-07-12T10:00:00",
            environment="prod",
            status="success",
            started_at="2026-07-12T10:00:00",
            completed_at="2026-07-12T10:05:00",
            tests_run=100,
            tests_passed=95,
        )

        assert report.pass_rate() == 95.0

    def test_success_rate_calculation(self):
        """Test change success rate calculation."""
        report = DeploymentReport(
            deployment_id="DEPLOY_1",
            timestamp="2026-07-12T10:00:00",
            environment="prod",
            status="partial",
            started_at="2026-07-12T10:00:00",
            completed_at="2026-07-12T10:05:00",
            total_changes=10,
            failed_changes=2,
        )

        assert report.success_rate() == 80.0

    def test_tasks_by_status(self):
        """Test counting tasks by status."""
        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        task1 = TaskReport(
            task_id="T1",
            status=TaskStatus.VERIFIED,
            timestamp="2026-07-12T10:00:00",
            title="Task 1",
            description="Desc",
            before_metrics=before,
            after_metrics=after,
        )

        task2 = TaskReport(
            task_id="T2",
            status=TaskStatus.VERIFIED,
            timestamp="2026-07-12T10:00:00",
            title="Task 2",
            description="Desc",
            before_metrics=before,
            after_metrics=after,
        )

        task3 = TaskReport(
            task_id="T3",
            status=TaskStatus.ANALYZED,
            timestamp="2026-07-12T10:00:00",
            title="Task 3",
            description="Desc",
            before_metrics=before,
            after_metrics=after,
        )

        report = DeploymentReport(
            deployment_id="DEPLOY_1",
            timestamp="2026-07-12T10:00:00",
            environment="prod",
            status="success",
            started_at="2026-07-12T10:00:00",
            completed_at="2026-07-12T10:05:00",
            task_reports=[task1, task2, task3],
        )

        by_status = report.tasks_by_status()
        assert by_status["verified"] == 2
        assert by_status["analyzed"] == 1

    def test_deployment_summary(self):
        """Test deployment summary."""
        report = DeploymentReport(
            deployment_id="DEPLOY_001",
            timestamp="2026-07-12T10:00:00",
            environment="staging",
            status="success",
            started_at="2026-07-12T10:00:00",
            completed_at="2026-07-12T10:30:00",
            total_changes=20,
            failed_changes=0,
            tests_run=200,
            tests_passed=198,
            overall_confidence=96.5,
        )

        summary = report.summary()
        assert summary["deployment_id"] == "DEPLOY_001"
        assert summary["environment"] == "staging"
        assert summary["test_pass_rate"] == 99.0
        assert summary["overall_confidence"] == 96.5


class TestTaskClassifier:
    """Test TaskClassifier."""

    def test_classify_analyzed(self):
        """Test classifying ANALYZED task."""
        status, confidence = TaskClassifier.classify(
            "TASK_1",
            changes_made=False,
            tests_passed=True,
            no_regressions=True,
        )

        assert status == TaskStatus.ANALYZED
        assert confidence == 100.0

    def test_classify_fixed(self):
        """Test classifying FIXED task."""
        status, confidence = TaskClassifier.classify(
            "TASK_1",
            changes_made=True,
            tests_passed=False,
            no_regressions=True,
        )

        assert status == TaskStatus.FIXED
        assert confidence == 50.0

    def test_classify_verified(self):
        """Test classifying VERIFIED task."""
        status, confidence = TaskClassifier.classify(
            "TASK_1",
            changes_made=True,
            tests_passed=True,
            no_regressions=True,
        )

        assert status == TaskStatus.VERIFIED
        assert confidence == 95.0

    def test_classify_deployed(self):
        """Test classifying DEPLOYED task."""
        status, confidence = TaskClassifier.classify(
            "TASK_1",
            changes_made=True,
            tests_passed=True,
            no_regressions=True,
            coverage_threshold=70.0,
        )

        assert confidence > 90.0


class TestReportGenerator:
    """Test ReportGenerator."""

    def test_generator_initialization(self):
        """Test initializing report generator."""
        generator = ReportGenerator()

        assert len(generator.task_reports) == 0
        assert len(generator.deployment_reports) == 0

    def test_create_task_report(self):
        """Test creating task report through generator."""
        generator = ReportGenerator()

        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        report = generator.create_task_report(
            task_id="TASK_001",
            status=TaskStatus.VERIFIED,
            title="Module refactor",
            description="Refactored authentication module",
            before_metrics=before,
            after_metrics=after,
        )

        assert "TASK_001" in generator.task_reports
        assert report.status == TaskStatus.VERIFIED

    def test_add_audit_entry(self):
        """Test adding audit entry."""
        generator = ReportGenerator()

        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        generator.create_task_report(
            "TASK_001",
            TaskStatus.VERIFIED,
            "Test",
            "Desc",
            before,
            after,
        )

        generator.add_audit_entry(
            "TASK_001",
            AuditAction.ANALYZE,
            "claude",
            "auth_module",
        )

        report = generator.get_task_report("TASK_001")
        assert len(report.audit_trail) == 1

    def test_add_findings(self):
        """Test adding findings."""
        generator = ReportGenerator()

        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        generator.create_task_report(
            "TASK_001",
            TaskStatus.VERIFIED,
            "Test",
            "Desc",
            before,
            after,
        )

        generator.add_findings("TASK_001", ["Issue A", "Issue B"])

        report = generator.get_task_report("TASK_001")
        assert len(report.findings) == 2

    def test_add_recommendations(self):
        """Test adding recommendations."""
        generator = ReportGenerator()

        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        generator.create_task_report(
            "TASK_001",
            TaskStatus.VERIFIED,
            "Test",
            "Desc",
            before,
            after,
        )

        generator.add_recommendations("TASK_001", ["Use new pattern", "Add tests"])

        report = generator.get_task_report("TASK_001")
        assert len(report.recommendations) == 2

    def test_create_deployment_report(self):
        """Test creating deployment report."""
        generator = ReportGenerator()

        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        task_report = generator.create_task_report(
            "TASK_001",
            TaskStatus.VERIFIED,
            "Test",
            "Desc",
            before,
            after,
        )

        deployment = generator.create_deployment_report(
            deployment_id="DEPLOY_001",
            environment="staging",
            task_reports=[task_report],
            total_changes=5,
            failed_changes=0,
            tests_run=50,
            tests_passed=48,
        )

        assert "DEPLOY_001" in generator.deployment_reports
        assert deployment.environment == "staging"

    def test_get_task_report(self):
        """Test retrieving task report."""
        generator = ReportGenerator()

        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        generator.create_task_report(
            "TASK_001",
            TaskStatus.VERIFIED,
            "Test",
            "Desc",
            before,
            after,
        )

        report = generator.get_task_report("TASK_001")
        assert report is not None
        assert report.task_id == "TASK_001"

    def test_export_reports(self):
        """Test exporting reports as JSON."""
        generator = ReportGenerator()

        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        generator.create_task_report(
            "TASK_001",
            TaskStatus.VERIFIED,
            "Test",
            "Desc",
            before,
            after,
        )

        exported = generator.export_reports()
        assert "tasks" in exported
        assert "TASK_001" in exported["tasks"]


class TestTaskSummary:
    """Test TaskSummary."""

    def test_summary_initialization(self):
        """Test initializing task summary."""
        summary = TaskSummary()

        assert summary.total_tasks() == 0

    def test_add_tasks(self):
        """Test adding tasks to summary."""
        summary = TaskSummary()

        summary.add_task(TaskStatus.ANALYZED)
        summary.add_task(TaskStatus.VERIFIED)
        summary.add_task(TaskStatus.DEPLOYED)

        assert summary.total_tasks() == 3
        assert summary.analyzed_count == 1
        assert summary.verified_count == 1
        assert summary.deployed_count == 1

    def test_completion_rate(self):
        """Test calculating completion rate."""
        summary = TaskSummary()

        summary.add_task(TaskStatus.DEPLOYED)
        summary.add_task(TaskStatus.DEPLOYED)
        summary.add_task(TaskStatus.FIXED)
        summary.add_task(TaskStatus.ANALYZED)

        assert summary.completion_rate() == 50.0

    def test_summary_dictionary(self):
        """Test getting summary as dictionary."""
        summary = TaskSummary()

        summary.add_task(TaskStatus.ANALYZED)
        summary.add_task(TaskStatus.VERIFIED)
        summary.add_task(TaskStatus.DEPLOYED)

        data = summary.summary()
        assert data["total"] == 3
        assert data["analyzed"] == 1


class TestLayer5Integration:
    """Integration tests for Layer 5."""

    def test_complete_workflow(self):
        """Test complete workflow from classification to reporting."""
        generator = ReportGenerator()

        # Create metrics
        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        # Create task report
        task = generator.create_task_report(
            "TASK_001",
            TaskStatus.VERIFIED,
            "Refactor auth",
            "Split module",
            before,
            after,
        )

        # Add audit entries
        generator.add_audit_entry(
            "TASK_001",
            AuditAction.ANALYZE,
            "claude",
            "auth_module",
        )
        generator.add_audit_entry(
            "TASK_001",
            AuditAction.VERIFY,
            "pytest",
            "tests",
        )

        # Create deployment
        deployment = generator.create_deployment_report(
            "DEPLOY_001",
            "staging",
            [task],
            total_changes=10,
            failed_changes=0,
            tests_run=100,
            tests_passed=98,
        )

        assert deployment.pass_rate() == 98.0
        assert len(task.audit_trail) == 2

    def test_multi_task_deployment(self):
        """Test deployment with multiple tasks."""
        generator = ReportGenerator()

        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        # Create multiple tasks
        tasks = []
        for i in range(1, 4):
            task = generator.create_task_report(
                f"TASK_00{i}",
                TaskStatus.VERIFIED,
                f"Task {i}",
                f"Description {i}",
                before,
                after,
            )
            tasks.append(task)

        # Create deployment
        deployment = generator.create_deployment_report(
            "DEPLOY_001",
            "prod",
            tasks,
            total_changes=30,
            failed_changes=0,
            tests_run=300,
            tests_passed=297,
        )

        assert len(deployment.task_reports) == 3
        assert deployment.tasks_by_status()["verified"] == 3

    def test_report_with_mixed_statuses(self):
        """Test reporting with mixed task statuses."""
        generator = ReportGenerator()

        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        task1 = generator.create_task_report(
            "TASK_001",
            TaskStatus.ANALYZED,
            "Analysis",
            "Findings only",
            before,
            after,
        )

        task2 = generator.create_task_report(
            "TASK_002",
            TaskStatus.FIXED,
            "Fix",
            "Awaiting test",
            before,
            after,
        )

        task3 = generator.create_task_report(
            "TASK_003",
            TaskStatus.VERIFIED,
            "Verified fix",
            "Tests pass",
            before,
            after,
        )

        deployment = generator.create_deployment_report(
            "DEPLOY_001",
            "staging",
            [task1, task2, task3],
        )

        by_status = deployment.tasks_by_status()
        assert by_status["analyzed"] == 1
        assert by_status["fixed"] == 1
        assert by_status["verified"] == 1


class TestLayer5ComplexScenarios:
    """Complex real-world reporting scenarios."""

    def test_large_deployment_reporting(self):
        """Test reporting for large deployments."""
        generator = ReportGenerator()

        before = TaskMetrics(75.0, 60.0, 70.0, 65.0, 75.0, 70.0)
        after = TaskMetrics(92.0, 82.0, 88.0, 82.0, 90.0, 85.0)

        # Create 50 tasks
        tasks = []
        for i in range(50):
            status = [
                TaskStatus.ANALYZED,
                TaskStatus.FIXED,
                TaskStatus.VERIFIED,
                TaskStatus.DEPLOYED,
            ][i % 4]

            task = generator.create_task_report(
                f"TASK_{i:03d}",
                status,
                f"Task {i}",
                f"Description {i}",
                before,
                after,
            )
            tasks.append(task)

        deployment = generator.create_deployment_report(
            "DEPLOY_LARGE",
            "prod",
            tasks,
            total_changes=500,
            failed_changes=5,
            tests_run=5000,
            tests_passed=4900,
        )

        assert deployment.success_rate() == 99.0
        assert deployment.pass_rate() == 98.0
        assert len(deployment.task_reports) == 50

    def test_audit_trail_completeness(self):
        """Test complete audit trail tracking."""
        generator = ReportGenerator()

        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)

        generator.create_task_report(
            "TASK_001",
            TaskStatus.DEPLOYED,
            "Full workflow",
            "Complete task",
            before,
            after,
        )

        # Add complete audit trail
        actions = [
            AuditAction.ANALYZE,
            AuditAction.PLAN,
            AuditAction.EXECUTE,
            AuditAction.TEST,
            AuditAction.VERIFY,
            AuditAction.DEPLOY,
        ]

        for action in actions:
            generator.add_audit_entry(
                "TASK_001",
                action,
                "system",
                "task_execution",
            )

        report = generator.get_task_report("TASK_001")
        assert len(report.audit_trail) == len(actions)

    def test_metrics_aggregation_across_tasks(self):
        """Test aggregating metrics across multiple tasks."""
        generator = ReportGenerator()

        before = TaskMetrics(80.0, 65.0, 75.0, 70.0, 80.0, 75.0)
        after1 = TaskMetrics(90.0, 75.0, 85.0, 80.0, 90.0, 85.0)
        after2 = TaskMetrics(95.0, 85.0, 90.0, 85.0, 92.0, 88.0)
        after3 = TaskMetrics(88.0, 78.0, 83.0, 78.0, 88.0, 83.0)

        task1 = generator.create_task_report(
            "TASK_001",
            TaskStatus.VERIFIED,
            "Task 1",
            "Desc",
            before,
            after1,
        )

        task2 = generator.create_task_report(
            "TASK_002",
            TaskStatus.VERIFIED,
            "Task 2",
            "Desc",
            before,
            after2,
        )

        task3 = generator.create_task_report(
            "TASK_003",
            TaskStatus.VERIFIED,
            "Task 3",
            "Desc",
            before,
            after3,
        )

        deployment = generator.create_deployment_report(
            "DEPLOY_001",
            "prod",
            [task1, task2, task3],
        )

        # Each task should have different improvements
        improvements1 = task1.metrics_improvement()
        improvements2 = task2.metrics_improvement()
        improvements3 = task3.metrics_improvement()

        assert improvements1["overall"] < improvements2["overall"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
