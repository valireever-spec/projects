"""
Production-Grade Orchestrator - Layer 5: Task Classification & Reporting

Core capabilities:
- Explicit task status classification (ANALYZED, FIXED, VERIFIED, DEPLOYED)
- Before/after metrics reporting
- Comprehensive audit trails
- Confidence-based reporting
- Integration with Layers 1-4
"""

import json
import hashlib
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Explicit task status classification."""

    ANALYZED = "analyzed"  # Findings only, no changes
    FIXED = "fixed"  # Changes made, awaiting verification
    VERIFIED = "verified"  # Changes + tests pass, no regressions
    DEPLOYED = "deployed"  # Live in production


class AuditAction(Enum):
    """Actions to audit."""

    ANALYZE = "analyze"
    PLAN = "plan"
    EXECUTE = "execute"
    TEST = "test"
    VERIFY = "verify"
    DEPLOY = "deploy"
    ROLLBACK = "rollback"


@dataclass
class TaskMetrics:
    """Metrics for a task (before/after)."""

    test_pass_rate: float  # 0-100%
    coverage_percent: float  # 0-100%
    code_quality_score: float  # 0-100
    performance_score: float  # 0-100 (throughput, latency)
    security_score: float  # 0-100
    reliability_score: float  # 0-100

    def overall_score(self) -> float:
        """Calculate overall score."""
        scores = [
            self.test_pass_rate,
            self.coverage_percent,
            self.code_quality_score,
            self.performance_score,
            self.security_score,
            self.reliability_score,
        ]
        return sum(scores) / len(scores) if scores else 0.0

    def improvement(self, other: "TaskMetrics") -> Dict[str, float]:
        """Calculate improvement vs another metrics set."""
        return {
            "test_pass_rate": self.test_pass_rate - other.test_pass_rate,
            "coverage": self.coverage_percent - other.coverage_percent,
            "code_quality": self.code_quality_score - other.code_quality_score,
            "performance": self.performance_score - other.performance_score,
            "security": self.security_score - other.security_score,
            "reliability": self.reliability_score - other.reliability_score,
            "overall": self.overall_score() - other.overall_score(),
        }


@dataclass
class AuditEntry:
    """Audit trail entry."""

    timestamp: str
    action: AuditAction
    actor: str
    resource: str
    details: Dict[str, Any] = field(default_factory=dict)
    result: str = "success"  # success, failure, warning
    error_message: Optional[str] = None

    def summary(self) -> str:
        """Get audit entry summary."""
        return f"[{self.timestamp}] {self.action.value.upper()} {self.resource} by {self.actor} ({self.result})"


@dataclass
class TaskReport:
    """Comprehensive report for a single task."""

    task_id: str
    status: TaskStatus
    timestamp: str
    title: str
    description: str
    before_metrics: TaskMetrics
    after_metrics: TaskMetrics
    confidence_percent: float = 100.0
    audit_trail: List[AuditEntry] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def metrics_improvement(self) -> Dict[str, float]:
        """Get metrics improvement."""
        return self.after_metrics.improvement(self.before_metrics)

    def improved_metrics(self) -> List[str]:
        """Get list of improved metrics."""
        improvements = self.metrics_improvement()
        return [k for k, v in improvements.items() if v > 0]

    def degraded_metrics(self) -> List[str]:
        """Get list of degraded metrics."""
        improvements = self.metrics_improvement()
        return [k for k, v in improvements.items() if v < 0]

    def summary(self) -> Dict[str, Any]:
        """Get task report summary."""
        improvements = self.metrics_improvement()

        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "title": self.title,
            "timestamp": self.timestamp,
            "confidence": self.confidence_percent,
            "before": asdict(self.before_metrics),
            "after": asdict(self.after_metrics),
            "improvements": improvements,
            "improved_metrics": self.improved_metrics(),
            "degraded_metrics": self.degraded_metrics(),
            "findings_count": len(self.findings),
            "recommendations_count": len(self.recommendations),
            "audit_entries": len(self.audit_trail),
        }


@dataclass
class DeploymentReport:
    """Comprehensive deployment report."""

    deployment_id: str
    timestamp: str
    environment: str
    status: str  # success, partial, failed
    started_at: str
    completed_at: str
    task_reports: List[TaskReport] = field(default_factory=list)
    total_changes: int = 0
    failed_changes: int = 0
    tests_run: int = 0
    tests_passed: int = 0
    overall_confidence: float = 100.0

    def pass_rate(self) -> float:
        """Calculate test pass rate."""
        if self.tests_run == 0:
            return 0.0
        return (self.tests_passed / self.tests_run) * 100

    def success_rate(self) -> float:
        """Calculate change success rate."""
        if self.total_changes == 0:
            return 100.0
        return ((self.total_changes - self.failed_changes) / self.total_changes) * 100

    def tasks_by_status(self) -> Dict[str, int]:
        """Count tasks by status."""
        counts = {status.value: 0 for status in TaskStatus}
        for report in self.task_reports:
            counts[report.status.value] += 1
        return counts

    def summary(self) -> Dict[str, Any]:
        """Get deployment summary."""
        return {
            "deployment_id": self.deployment_id,
            "timestamp": self.timestamp,
            "environment": self.environment,
            "status": self.status,
            "duration_minutes": self._duration_minutes(),
            "tasks_total": len(self.task_reports),
            "tasks_by_status": self.tasks_by_status(),
            "total_changes": self.total_changes,
            "failed_changes": self.failed_changes,
            "change_success_rate": self.success_rate(),
            "tests_passed": self.tests_passed,
            "tests_total": self.tests_run,
            "test_pass_rate": self.pass_rate(),
            "overall_confidence": self.overall_confidence,
        }

    def _duration_minutes(self) -> float:
        """Calculate deployment duration in minutes."""
        try:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.completed_at)
            return (end - start).total_seconds() / 60
        except (ValueError, TypeError):
            return 0.0


class TaskClassifier:
    """Classifies tasks based on state and results."""

    @staticmethod
    def classify(
        task_id: str,
        changes_made: bool,
        tests_passed: bool,
        no_regressions: bool,
        coverage_threshold: float = 70.0,
    ) -> Tuple[TaskStatus, float]:
        """Classify task and return status with confidence."""
        # ANALYZED: No changes made
        if not changes_made:
            return TaskStatus.ANALYZED, 100.0

        # FIXED: Changes made but not verified
        if changes_made and not tests_passed:
            return TaskStatus.FIXED, 50.0

        # VERIFIED: Changes + tests pass + no regressions
        if changes_made and tests_passed and no_regressions:
            return TaskStatus.VERIFIED, 95.0

        # DEPLOYED: All verification passed + coverage OK
        if all([changes_made, tests_passed, no_regressions]):
            return TaskStatus.DEPLOYED, 100.0

        return TaskStatus.FIXED, 60.0


class ReportGenerator:
    """Generates comprehensive reports."""

    def __init__(self):
        self.task_reports: Dict[str, TaskReport] = {}
        self.deployment_reports: Dict[str, DeploymentReport] = {}

    def create_task_report(
        self,
        task_id: str,
        status: TaskStatus,
        title: str,
        description: str,
        before_metrics: TaskMetrics,
        after_metrics: TaskMetrics,
    ) -> TaskReport:
        """Create a task report."""
        report = TaskReport(
            task_id=task_id,
            status=status,
            timestamp=datetime.now().isoformat(),
            title=title,
            description=description,
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            confidence_percent=self._calculate_confidence(
                status, before_metrics, after_metrics
            ),
        )

        self.task_reports[task_id] = report
        return report

    def create_deployment_report(
        self,
        deployment_id: str,
        environment: str,
        task_reports: List[TaskReport],
        total_changes: int = 0,
        failed_changes: int = 0,
        tests_run: int = 0,
        tests_passed: int = 0,
    ) -> DeploymentReport:
        """Create a deployment report."""
        report = DeploymentReport(
            deployment_id=deployment_id,
            timestamp=datetime.now().isoformat(),
            environment=environment,
            status=self._determine_status(failed_changes, total_changes),
            started_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
            task_reports=task_reports,
            total_changes=total_changes,
            failed_changes=failed_changes,
            tests_run=tests_run,
            tests_passed=tests_passed,
            overall_confidence=self._calculate_deployment_confidence(task_reports),
        )

        self.deployment_reports[deployment_id] = report
        return report

    def add_audit_entry(
        self,
        task_id: str,
        action: AuditAction,
        actor: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
        result: str = "success",
        error_message: Optional[str] = None,
    ) -> None:
        """Add audit entry to task report."""
        if task_id not in self.task_reports:
            return

        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            action=action,
            actor=actor,
            resource=resource,
            details=details or {},
            result=result,
            error_message=error_message,
        )

        self.task_reports[task_id].audit_trail.append(entry)

    def add_findings(self, task_id: str, findings: List[str]) -> None:
        """Add findings to task report."""
        if task_id in self.task_reports:
            self.task_reports[task_id].findings.extend(findings)

    def add_recommendations(self, task_id: str, recommendations: List[str]) -> None:
        """Add recommendations to task report."""
        if task_id in self.task_reports:
            self.task_reports[task_id].recommendations.extend(recommendations)

    def get_task_report(self, task_id: str) -> Optional[TaskReport]:
        """Get task report by ID."""
        return self.task_reports.get(task_id)

    def get_deployment_report(self, deployment_id: str) -> Optional[DeploymentReport]:
        """Get deployment report by ID."""
        return self.deployment_reports.get(deployment_id)

    def export_reports(self) -> Dict[str, Any]:
        """Export all reports as JSON."""
        return {
            "tasks": {
                task_id: report.summary()
                for task_id, report in self.task_reports.items()
            },
            "deployments": {
                deployment_id: report.summary()
                for deployment_id, report in self.deployment_reports.items()
            },
        }

    @staticmethod
    def _calculate_confidence(
        status: TaskStatus,
        before: TaskMetrics,
        after: TaskMetrics,
    ) -> float:
        """Calculate task confidence based on status and metrics."""
        if status == TaskStatus.ANALYZED:
            return 100.0
        elif status == TaskStatus.VERIFIED:
            # Confidence based on coverage and overall score
            coverage_confidence = min(100.0, (after.coverage_percent / 70.0) * 100)
            quality_confidence = after.overall_score()
            return (coverage_confidence + quality_confidence) / 2
        elif status == TaskStatus.DEPLOYED:
            return 99.0
        else:
            return 50.0

    @staticmethod
    def _determine_status(failed_changes: int, total_changes: int) -> str:
        """Determine deployment status."""
        if failed_changes == 0:
            return "success"
        elif failed_changes < total_changes / 2:
            return "partial"
        else:
            return "failed"

    @staticmethod
    def _calculate_deployment_confidence(task_reports: List[TaskReport]) -> float:
        """Calculate overall deployment confidence."""
        if not task_reports:
            return 0.0
        avg_confidence = sum(r.confidence_percent for r in task_reports) / len(
            task_reports
        )
        return min(100.0, avg_confidence)


class TaskSummary:
    """Summary of task statuses."""

    def __init__(self):
        self.analyzed_count = 0
        self.fixed_count = 0
        self.verified_count = 0
        self.deployed_count = 0

    def add_task(self, status: TaskStatus) -> None:
        """Add task to summary."""
        if status == TaskStatus.ANALYZED:
            self.analyzed_count += 1
        elif status == TaskStatus.FIXED:
            self.fixed_count += 1
        elif status == TaskStatus.VERIFIED:
            self.verified_count += 1
        elif status == TaskStatus.DEPLOYED:
            self.deployed_count += 1

    def total_tasks(self) -> int:
        """Get total task count."""
        return (
            self.analyzed_count
            + self.fixed_count
            + self.verified_count
            + self.deployed_count
        )

    def completion_rate(self) -> float:
        """Calculate completion rate (deployed / total)."""
        total = self.total_tasks()
        if total == 0:
            return 0.0
        return (self.deployed_count / total) * 100

    def summary(self) -> Dict[str, int]:
        """Get summary dictionary."""
        return {
            "analyzed": self.analyzed_count,
            "fixed": self.fixed_count,
            "verified": self.verified_count,
            "deployed": self.deployed_count,
            "total": self.total_tasks(),
        }


def main() -> None:
    """Demo Layer 5 task classification and reporting."""
    print("=" * 80)
    print("LAYER 5: TASK CLASSIFICATION & REPORTING")
    print("=" * 80 + "\n")

    # Create report generator
    generator = ReportGenerator()

    # Create metrics
    print("📊 Creating task metrics...\n")
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
        coverage_percent=82.0,
        code_quality_score=88.0,
        performance_score=85.0,
        security_score=90.0,
        reliability_score=88.0,
    )

    print(f"   Before overall score: {before.overall_score():.1f}")
    print(f"   After overall score: {after.overall_score():.1f}")

    print()

    # Create task report
    print("📝 Creating task report...\n")
    task_report = generator.create_task_report(
        task_id="TASK_001",
        status=TaskStatus.VERIFIED,
        title="Refactor authentication module",
        description="Split monolithic auth module into smaller components",
        before_metrics=before,
        after_metrics=after,
    )

    print(f"   Task ID: {task_report.task_id}")
    print(f"   Status: {task_report.status.value.upper()}")
    print(f"   Confidence: {task_report.confidence_percent:.1f}%")
    print(f"   Improved metrics: {len(task_report.improved_metrics())}")

    print()

    # Add audit entries
    print("📋 Adding audit trail...\n")
    generator.add_audit_entry(
        "TASK_001",
        AuditAction.ANALYZE,
        "claude",
        "auth_module",
        {"lines_analyzed": 500},
    )
    generator.add_audit_entry(
        "TASK_001",
        AuditAction.EXECUTE,
        "claude",
        "auth_module",
        {"files_modified": 3},
    )
    generator.add_audit_entry(
        "TASK_001",
        AuditAction.VERIFY,
        "pytest",
        "test_suite",
        {"tests_passed": 120},
    )

    print(f"   Audit entries: {len(task_report.audit_trail)}")
    for entry in task_report.audit_trail:
        print(f"   - {entry.summary()}")

    print()

    # Create deployment report
    print("🚀 Creating deployment report...\n")
    deployment = generator.create_deployment_report(
        deployment_id="DEPLOY_001",
        environment="staging",
        task_reports=[task_report],
        total_changes=10,
        failed_changes=0,
        tests_run=150,
        tests_passed=145,
    )

    print(f"   Deployment ID: {deployment.deployment_id}")
    print(f"   Environment: {deployment.environment}")
    print(f"   Status: {deployment.status}")
    print(f"   Test pass rate: {deployment.pass_rate():.1f}%")
    print(f"   Overall confidence: {deployment.overall_confidence:.1f}%")

    print()

    # Summary
    print("📊 SUMMARY")
    print("=" * 80)
    summary = deployment.summary()
    print(json.dumps(summary, indent=2))
    print("=" * 80)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
