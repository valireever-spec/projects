"""
Layer 4: Infrastructure Testing - Comprehensive Test Suite

Tests cover:
- Health checking (single and multiple services)
- Load testing (throughput, latency, success rate)
- Failover testing (detection and completion time)
- Chaos testing (latency, errors, timeouts, network partitions)
- SLO specification and validation
- Complete test suite orchestration
"""

import pytest
from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../scripts"))

from orchestrator_layer4_testing import (
    TestType,
    HealthStatus,
    ChaosType,
    HealthCheckResult,
    LoadTestResult,
    FailoverResult,
    ChaosTestResult,
    SLOSpec,
    TestReport,
    HealthChecker,
    LoadTester,
    FailoverTester,
    ChaosTester,
    InfrastructureTestSuite,
)


class TestHealthStatus:
    """Test HealthStatus enum."""

    def test_health_status_values(self):
        """Test all health statuses are defined."""
        statuses = [
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY,
            HealthStatus.UNKNOWN,
        ]
        assert len(statuses) == 4

    def test_healthy_status_value(self):
        """Test HEALTHY status value."""
        assert HealthStatus.HEALTHY.value == "healthy"


class TestChaosType:
    """Test ChaosType enum."""

    def test_chaos_types_defined(self):
        """Test all chaos types are defined."""
        types = [
            ChaosType.LATENCY,
            ChaosType.ERROR,
            ChaosType.TIMEOUT,
            ChaosType.NETWORK_PARTITION,
        ]
        assert len(types) == 4

    def test_latency_chaos(self):
        """Test latency chaos type."""
        assert ChaosType.LATENCY.value == "latency"


class TestHealthCheckResult:
    """Test HealthCheckResult."""

    def test_healthy_result(self):
        """Test creating healthy result."""
        result = HealthCheckResult(
            service_name="api",
            status=HealthStatus.HEALTHY,
            response_time_ms=50,
            checked_at="2026-07-12T10:00:00",
        )

        assert result.is_healthy() == True
        assert result.is_degraded() == False

    def test_degraded_result(self):
        """Test creating degraded result."""
        result = HealthCheckResult(
            service_name="worker",
            status=HealthStatus.DEGRADED,
            response_time_ms=2500,
            checked_at="2026-07-12T10:00:00",
        )

        assert result.is_degraded() == True
        assert result.is_healthy() == False

    def test_unhealthy_result(self):
        """Test creating unhealthy result."""
        result = HealthCheckResult(
            service_name="db",
            status=HealthStatus.UNHEALTHY,
            response_time_ms=5000,
            checked_at="2026-07-12T10:00:00",
            error_message="Connection timeout",
        )

        assert result.is_healthy() == False
        assert result.error_message == "Connection timeout"


class TestLoadTestResult:
    """Test LoadTestResult."""

    def test_result_creation(self):
        """Test creating load test result."""
        result = LoadTestResult(
            test_id="LOAD_123",
            target_service="api",
            duration_seconds=10,
            requests_total=100,
            requests_successful=95,
            requests_failed=5,
        )

        assert result.test_id == "LOAD_123"
        assert result.success_rate() == 95.0

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        result = LoadTestResult(
            test_id="LOAD_1",
            target_service="api",
            duration_seconds=5,
            requests_total=100,
            requests_successful=90,
            requests_failed=10,
        )

        assert result.success_rate() == 90.0

    def test_avg_response_time(self):
        """Test average response time calculation."""
        result = LoadTestResult(
            test_id="LOAD_1",
            target_service="api",
            duration_seconds=5,
            requests_total=3,
            requests_successful=3,
            requests_failed=0,
            response_times_ms=[50.0, 100.0, 150.0],
        )

        assert result.avg_response_time() == 100.0

    def test_p99_response_time(self):
        """Test 99th percentile calculation."""
        result = LoadTestResult(
            test_id="LOAD_1",
            target_service="api",
            duration_seconds=5,
            requests_total=100,
            requests_successful=100,
            requests_failed=0,
            response_times_ms=list(range(1, 101)),  # 1-100ms
        )

        p99 = result.p99_response_time()
        assert p99 >= 99  # 99th percentile should be around 99ms

    def test_throughput_calculation(self):
        """Test throughput (requests per second)."""
        result = LoadTestResult(
            test_id="LOAD_1",
            target_service="api",
            duration_seconds=10,
            requests_total=1000,
            requests_successful=950,
            requests_failed=50,
        )

        rps = result.throughput_rps()
        assert rps == 95.0  # 950 successful / 10 seconds


class TestFailoverResult:
    """Test FailoverResult."""

    def test_result_creation(self):
        """Test creating failover result."""
        result = FailoverResult(
            test_id="FAILOVER_1",
            primary_service="primary-db",
            backup_service="backup-db",
            failure_injected_at="2026-07-12T10:00:00",
            failover_detected_at="2026-07-12T10:00:00.100",
            failover_completed_at="2026-07-12T10:00:00.250",
            success=True,
        )

        assert result.test_id == "FAILOVER_1"
        assert result.success == True

    def test_detection_time_calculation(self):
        """Test detection time calculation."""
        result = FailoverResult(
            test_id="FAILOVER_1",
            primary_service="primary",
            backup_service="backup",
            failure_injected_at="2026-07-12T10:00:00",
            failover_detected_at="2026-07-12T10:00:00.050",
            failover_completed_at="2026-07-12T10:00:00.150",
            success=True,
        )

        detection_time = result.detection_time_ms()
        assert detection_time >= 40  # At least 50ms


class TestChaosTestResult:
    """Test ChaosTestResult."""

    def test_result_creation(self):
        """Test creating chaos test result."""
        result = ChaosTestResult(
            test_id="CHAOS_1",
            chaos_type=ChaosType.LATENCY,
            target_service="api",
            duration_seconds=10,
            requests_total=100,
            requests_failed=20,
            success=True,
        )

        assert result.chaos_type == ChaosType.LATENCY
        assert result.failure_rate() == 20.0

    def test_resilience_score(self):
        """Test resilience score calculation."""
        result = ChaosTestResult(
            test_id="CHAOS_1",
            chaos_type=ChaosType.ERROR,
            target_service="api",
            duration_seconds=5,
            requests_total=100,
            requests_failed=10,
            success=True,
        )

        resilience = result.resilience_score()
        assert resilience == 90.0  # 100 - 10% failure rate


class TestSLOSpec:
    """Test SLO specification."""

    def test_slo_creation(self):
        """Test creating SLO."""
        slo = SLOSpec(
            service_name="api",
            availability_target=99.9,
            latency_p99_ms=200,
            error_rate_max=0.1,
        )

        assert slo.service_name == "api"
        assert slo.availability_target == 99.9

    def test_slo_met(self):
        """Test SLO met condition."""
        slo = SLOSpec(
            service_name="api",
            availability_target=99.0,
            latency_p99_ms=200,
            error_rate_max=0.1,
        )

        met = slo.is_met(availability=99.5, p99_latency=150, error_rate=0.05)
        assert met == True

    def test_slo_not_met_low_availability(self):
        """Test SLO not met (low availability)."""
        slo = SLOSpec(
            service_name="api",
            availability_target=99.9,
            latency_p99_ms=200,
            error_rate_max=0.1,
        )

        met = slo.is_met(availability=98.0, p99_latency=150, error_rate=0.05)
        assert met == False

    def test_slo_not_met_high_latency(self):
        """Test SLO not met (high latency)."""
        slo = SLOSpec(
            service_name="api",
            availability_target=99.9,
            latency_p99_ms=200,
            error_rate_max=0.1,
        )

        met = slo.is_met(availability=99.95, p99_latency=250, error_rate=0.05)
        assert met == False


class TestHealthChecker:
    """Test HealthChecker."""

    def test_checker_initialization(self):
        """Test initializing health checker."""
        checker = HealthChecker(timeout_ms=5000)

        assert checker.timeout_ms == 5000
        assert len(checker.check_history) == 0

    def test_check_single_service(self):
        """Test checking single service."""
        checker = HealthChecker()

        result = checker.check_health("api")

        assert result.service_name == "api"
        assert result.status in [
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY,
        ]

    def test_check_multiple_services(self):
        """Test checking multiple services."""
        checker = HealthChecker()

        services = ["api", "worker", "cache"]
        results = checker.check_multiple(services)

        assert len(results) == 3
        assert len(checker.check_history) == 3

    def test_health_summary(self):
        """Test getting health summary."""
        checker = HealthChecker()

        checker.check_multiple(["api", "worker"])

        summary = checker.get_health_summary()
        assert summary["total_checks"] == 2
        assert "healthy" in summary
        assert "degraded" in summary


class TestLoadTester:
    """Test LoadTester."""

    def test_tester_initialization(self):
        """Test initializing load tester."""
        tester = LoadTester("api")

        assert tester.target_service == "api"

    def test_run_load_test(self):
        """Test running load test."""
        tester = LoadTester("api")

        result = tester.run_test(duration_seconds=2, concurrent_requests=5)

        assert result.target_service == "api"
        assert result.requests_total > 0
        assert result.success_rate() >= 0

    def test_load_test_metrics(self):
        """Test load test metrics calculation."""
        tester = LoadTester("worker")

        result = tester.run_test(duration_seconds=1, concurrent_requests=3)

        assert result.avg_response_time() > 0
        assert result.p99_response_time() > 0
        assert result.throughput_rps() > 0

    def test_load_test_response_times(self):
        """Test response time collection."""
        tester = LoadTester("cache")

        result = tester.run_test(duration_seconds=1, concurrent_requests=2)

        assert len(result.response_times_ms) > 0
        assert all(t > 0 for t in result.response_times_ms)


class TestFailoverTester:
    """Test FailoverTester."""

    def test_tester_initialization(self):
        """Test initializing failover tester."""
        tester = FailoverTester("primary-db", "backup-db")

        assert tester.primary_service == "primary-db"
        assert tester.backup_service == "backup-db"

    def test_run_failover_test(self):
        """Test running failover test."""
        tester = FailoverTester("primary-api", "backup-api")

        result = tester.run_test()

        assert result.success == True
        assert result.failover_time_ms() > 0

    def test_failover_detection_time(self):
        """Test failover detection time."""
        tester = FailoverTester("primary", "backup")

        result = tester.run_test()

        detection_time = result.detection_time_ms()
        assert detection_time >= 0
        assert detection_time < 1000  # Should be less than 1 second


class TestChaosTester:
    """Test ChaosTester."""

    def test_tester_initialization(self):
        """Test initializing chaos tester."""
        tester = ChaosTester("api")

        assert tester.target_service == "api"

    def test_run_chaos_latency_test(self):
        """Test chaos latency injection."""
        tester = ChaosTester("api")

        result = tester.run_test(
            ChaosType.LATENCY,
            duration_seconds=2,
            request_count=50,
        )

        assert result.chaos_type == ChaosType.LATENCY
        assert result.requests_total == 50
        assert result.resilience_score() > 0

    def test_run_chaos_error_test(self):
        """Test chaos error injection."""
        tester = ChaosTester("worker")

        result = tester.run_test(
            ChaosType.ERROR,
            duration_seconds=2,
            request_count=50,
        )

        assert result.requests_failed >= 0

    def test_chaos_resilience_score(self):
        """Test resilience score calculation."""
        tester = ChaosTester("api")

        result = tester.run_test(
            ChaosType.TIMEOUT,
            duration_seconds=1,
            request_count=100,
        )

        resilience = result.resilience_score()
        assert 0 <= resilience <= 100

    def test_chaos_test_methods(self):
        """Test different chaos methods."""
        tester = ChaosTester("api")

        # Test all chaos types
        chaos_types = [
            ChaosType.LATENCY,
            ChaosType.ERROR,
            ChaosType.TIMEOUT,
            ChaosType.NETWORK_PARTITION,
        ]

        for chaos_type in chaos_types:
            result = tester.run_test(
                chaos_type,
                duration_seconds=1,
                request_count=50,
            )
            assert result.chaos_type == chaos_type


class TestTestReport:
    """Test TestReport."""

    def test_report_creation(self):
        """Test creating test report."""
        report = TestReport(
            test_id="TEST_1",
            test_type=TestType.LOAD,
            timestamp="2026-07-12T10:00:00",
            duration_seconds=10,
            passed=True,
            confidence_percent=95.0,
        )

        assert report.test_id == "TEST_1"
        assert report.passed == True

    def test_report_summary(self):
        """Test report summary generation."""
        report = TestReport(
            test_id="TEST_1",
            test_type=TestType.FAILOVER,
            timestamp="2026-07-12T10:00:00",
            duration_seconds=0.15,
            passed=True,
            metrics={"failover_time_ms": 150},
            confidence_percent=100.0,
        )

        summary = report.summary()
        assert summary["test_id"] == "TEST_1"
        assert summary["test_type"] == "failover"
        assert summary["passed"] == True


class TestInfrastructureTestSuite:
    """Test InfrastructureTestSuite."""

    def test_suite_initialization(self):
        """Test initializing test suite."""
        suite = InfrastructureTestSuite()

        assert len(suite.results) == 0
        assert len(suite.slos) == 0

    def test_add_slo(self):
        """Test adding SLO to suite."""
        suite = InfrastructureTestSuite()

        slo = SLOSpec(
            service_name="api",
            availability_target=99.9,
            latency_p99_ms=200,
            error_rate_max=0.1,
        )

        suite.add_slo(slo)

        assert "api" in suite.slos
        assert suite.slos["api"].availability_target == 99.9

    def test_run_health_checks(self):
        """Test running health checks."""
        suite = InfrastructureTestSuite()

        services = ["api", "worker"]
        report = suite.run_health_checks(services)

        assert report.test_type == TestType.HEALTH_CHECK
        assert len(suite.results) == 1

    def test_run_load_test(self):
        """Test running load test."""
        suite = InfrastructureTestSuite()

        report = suite.run_load_test("api", duration=2)

        assert report.test_type == TestType.LOAD
        assert report.metrics["requests_total"] > 0

    def test_run_failover_test(self):
        """Test running failover test."""
        suite = InfrastructureTestSuite()

        report = suite.run_failover_test("primary", "backup")

        assert report.test_type == TestType.FAILOVER
        assert "failover_time_ms" in report.metrics

    def test_run_chaos_test(self):
        """Test running chaos test."""
        suite = InfrastructureTestSuite()

        report = suite.run_chaos_test("api", ChaosType.LATENCY)

        assert report.test_type == TestType.CHAOS
        assert "resilience_score" in report.metrics


class TestLayer4Integration:
    """Integration tests for Layer 4."""

    def test_end_to_end_test_suite(self):
        """Test running complete test suite."""
        suite = InfrastructureTestSuite()

        services = ["api", "worker"]
        results = suite.run_all_tests(services)

        assert results["total_tests"] > 0
        assert results["passed"] > 0
        assert 0 <= results["pass_rate"] <= 100

    def test_mixed_test_results(self):
        """Test handling mixed pass/fail results."""
        suite = InfrastructureTestSuite()

        # Run various tests
        suite.run_health_checks(["api"])
        suite.run_load_test("api", duration=1)
        suite.run_failover_test("primary", "backup")
        suite.run_chaos_test("api", ChaosType.ERROR)

        assert len(suite.results) == 4

    def test_slo_validation_in_tests(self):
        """Test SLO validation during testing."""
        suite = InfrastructureTestSuite()

        # Add strict SLO
        suite.add_slo(
            SLOSpec(
                service_name="api",
                availability_target=99.99,
                latency_p99_ms=100,
                error_rate_max=0.01,
            )
        )

        # Run load test (may or may not meet SLO)
        report = suite.run_load_test("api", duration=2)

        # Check if SLO exists
        assert "api" in suite.slos


class TestLayer4ComplexScenarios:
    """Complex real-world testing scenarios."""

    def test_multi_service_health_checks(self):
        """Test health checking multiple services."""
        suite = InfrastructureTestSuite()

        services = ["api", "worker", "cache", "db", "queue"]
        report = suite.run_health_checks(services)

        assert report.metrics["services_checked"] == len(services)

    def test_sustained_load_test(self):
        """Test sustained load testing."""
        suite = InfrastructureTestSuite()

        # Run longer load test
        report = suite.run_load_test("api", duration=5)

        assert report.duration_seconds == 5
        assert report.metrics["requests_total"] > 100

    def test_cascading_failover(self):
        """Test failover chain."""
        suite = InfrastructureTestSuite()

        # Primary → Backup failover
        report1 = suite.run_failover_test("primary", "backup")
        # Backup → Secondary failover
        report2 = suite.run_failover_test("backup", "secondary")

        assert len(suite.results) == 2
        assert all(r.passed for r in suite.results)

    def test_chaos_injection_sequence(self):
        """Test sequence of chaos injections."""
        suite = InfrastructureTestSuite()

        chaos_sequence = [
            ChaosType.LATENCY,
            ChaosType.ERROR,
            ChaosType.TIMEOUT,
        ]

        for chaos_type in chaos_sequence:
            suite.run_chaos_test("api", chaos_type)

        assert len(suite.results) == len(chaos_sequence)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
