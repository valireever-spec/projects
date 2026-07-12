"""
Production-Grade Orchestrator - Layer 4: Infrastructure Testing

Core capabilities:
- Failover testing (simulate primary failure, verify backup takeover)
- Load testing (measure performance under load)
- Chaos testing (inject failures, verify resilience)
- Health checks (continuous service monitoring)
- Observability (metrics collection, SLO enforcement)
"""

import time
import json
import hashlib
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
from statistics import mean, median, stdev

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Types of infrastructure tests."""

    FAILOVER = "failover"
    LOAD = "load"
    CHAOS = "chaos"
    HEALTH_CHECK = "health_check"


class HealthStatus(Enum):
    """Service health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ChaosType(Enum):
    """Types of chaos injection."""

    LATENCY = "latency"  # Add delay
    ERROR = "error"  # Inject errors
    TIMEOUT = "timeout"  # Force timeout
    NETWORK_PARTITION = "network_partition"  # Simulate network failure


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    service_name: str
    status: HealthStatus
    response_time_ms: float
    checked_at: str
    error_message: Optional[str] = None

    def is_healthy(self) -> bool:
        """Check if service is healthy."""
        return self.status == HealthStatus.HEALTHY

    def is_degraded(self) -> bool:
        """Check if service is degraded."""
        return self.status == HealthStatus.DEGRADED


@dataclass
class LoadTestResult:
    """Result of a load test."""

    test_id: str
    target_service: str
    duration_seconds: int
    requests_total: int
    requests_successful: int
    requests_failed: int
    response_times_ms: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.requests_total == 0:
            return 0.0
        return (self.requests_successful / self.requests_total) * 100

    def avg_response_time(self) -> float:
        """Calculate average response time."""
        if not self.response_times_ms:
            return 0.0
        return mean(self.response_times_ms)

    def p99_response_time(self) -> float:
        """Calculate 99th percentile response time."""
        if not self.response_times_ms:
            return 0.0
        sorted_times = sorted(self.response_times_ms)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def throughput_rps(self) -> float:
        """Calculate requests per second."""
        if self.duration_seconds == 0:
            return 0.0
        return self.requests_successful / self.duration_seconds


@dataclass
class FailoverResult:
    """Result of a failover test."""

    test_id: str
    primary_service: str
    backup_service: str
    failure_injected_at: str
    failover_detected_at: str
    failover_completed_at: str
    success: bool
    errors: List[str] = field(default_factory=list)

    def detection_time_ms(self) -> float:
        """Calculate time to detect failure."""
        start = datetime.fromisoformat(self.failure_injected_at)
        end = datetime.fromisoformat(self.failover_detected_at)
        return (end - start).total_seconds() * 1000

    def failover_time_ms(self) -> float:
        """Calculate total failover time."""
        start = datetime.fromisoformat(self.failure_injected_at)
        end = datetime.fromisoformat(self.failover_completed_at)
        return (end - start).total_seconds() * 1000


@dataclass
class ChaosTestResult:
    """Result of a chaos test."""

    test_id: str
    chaos_type: ChaosType
    target_service: str
    duration_seconds: int
    requests_total: int
    requests_failed: int
    success: bool
    error_messages: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def failure_rate(self) -> float:
        """Calculate failure rate."""
        if self.requests_total == 0:
            return 0.0
        return (self.requests_failed / self.requests_total) * 100

    def resilience_score(self) -> float:
        """Score resilience (0-100)."""
        if self.requests_total == 0:
            return 100.0
        # Resilience is inverse of failure rate
        return 100.0 - self.failure_rate()


@dataclass
class SLOSpec:
    """Service Level Objective specification."""

    service_name: str
    availability_target: float  # e.g., 99.9 (three nines)
    latency_p99_ms: float  # e.g., 200ms
    error_rate_max: float  # e.g., 0.1 (0.1%)

    def is_met(
        self,
        availability: float,
        p99_latency: float,
        error_rate: float,
    ) -> bool:
        """Check if SLO is met."""
        return (
            availability >= self.availability_target
            and p99_latency <= self.latency_p99_ms
            and error_rate <= self.error_rate_max
        )


@dataclass
class TestReport:
    """Complete test report."""

    test_id: str
    test_type: TestType
    timestamp: str
    duration_seconds: float
    passed: bool
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_percent: float = 100.0

    def summary(self) -> Dict[str, Any]:
        """Get report summary."""
        return {
            "test_id": self.test_id,
            "test_type": self.test_type.value,
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "passed": self.passed,
            "metrics": self.metrics,
            "error_count": len(self.errors),
            "confidence_percent": self.confidence_percent,
        }


class HealthChecker:
    """Performs health checks on services."""

    def __init__(self, timeout_ms: float = 5000):
        self.timeout_ms = timeout_ms
        self.check_history: List[HealthCheckResult] = []

    def check_health(self, service_name: str) -> HealthCheckResult:
        """Check service health (simulated)."""
        start_time = time.time()

        # Simulate service check
        time.sleep(0.01)  # 10ms simulated check

        response_time_ms = (time.time() - start_time) * 1000

        # Determine status based on response time
        if response_time_ms > self.timeout_ms:
            status = HealthStatus.UNHEALTHY
        elif response_time_ms > self.timeout_ms * 0.5:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        result = HealthCheckResult(
            service_name=service_name,
            status=status,
            response_time_ms=response_time_ms,
            checked_at=datetime.now().isoformat(),
        )

        self.check_history.append(result)
        return result

    def check_multiple(self, service_names: List[str]) -> List[HealthCheckResult]:
        """Check multiple services."""
        return [self.check_health(name) for name in service_names]

    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary."""
        healthy = sum(1 for r in self.check_history if r.is_healthy())
        degraded = sum(1 for r in self.check_history if r.is_degraded())
        unhealthy = sum(
            1 for r in self.check_history if r.status == HealthStatus.UNHEALTHY
        )

        return {
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "total_checks": len(self.check_history),
        }


class LoadTester:
    """Performs load tests on services."""

    def __init__(self, target_service: str):
        self.target_service = target_service

    def run_test(
        self,
        duration_seconds: int = 10,
        concurrent_requests: int = 10,
    ) -> LoadTestResult:
        """Run a load test."""
        result = LoadTestResult(
            test_id=self._generate_test_id(),
            target_service=self.target_service,
            duration_seconds=duration_seconds,
            requests_total=0,
            requests_successful=0,
            requests_failed=0,
        )

        # Simulate load test
        import random

        start_time = time.time()
        request_count = 0

        while time.time() - start_time < duration_seconds:
            # Simulate concurrent requests
            for _ in range(concurrent_requests):
                request_count += 1

                # Simulate request with random response time (20-100ms)
                response_time = random.uniform(20, 100)
                result.response_times_ms.append(response_time)

                # 95% success rate in normal operation
                if random.random() < 0.95:
                    result.requests_successful += 1
                else:
                    result.requests_failed += 1
                    result.errors.append(f"Request {request_count} failed")

            time.sleep(0.01)

        result.requests_total = request_count

        return result

    @staticmethod
    def _generate_test_id() -> str:
        """Generate unique test ID."""
        timestamp = datetime.now().isoformat()
        return f"LOAD_{hashlib.md5(timestamp.encode()).hexdigest()[:8].upper()}"


class FailoverTester:
    """Tests failover scenarios."""

    def __init__(self, primary_service: str, backup_service: str):
        self.primary_service = primary_service
        self.backup_service = backup_service

    def run_test(self) -> FailoverResult:
        """Run failover test."""
        failure_time = datetime.now()

        # Simulate primary failure detection (50ms)
        time.sleep(0.05)
        detected_time = datetime.now()

        # Simulate failover to backup (100ms)
        time.sleep(0.10)
        completed_time = datetime.now()

        result = FailoverResult(
            test_id=self._generate_test_id(),
            primary_service=self.primary_service,
            backup_service=self.backup_service,
            failure_injected_at=failure_time.isoformat(),
            failover_detected_at=detected_time.isoformat(),
            failover_completed_at=completed_time.isoformat(),
            success=True,
        )

        return result

    @staticmethod
    def _generate_test_id() -> str:
        """Generate unique test ID."""
        timestamp = datetime.now().isoformat()
        return f"FAILOVER_{hashlib.md5(timestamp.encode()).hexdigest()[:8].upper()}"


class ChaosTester:
    """Injects chaos and verifies resilience."""

    def __init__(self, target_service: str):
        self.target_service = target_service

    def run_test(
        self,
        chaos_type: ChaosType,
        duration_seconds: int = 10,
        request_count: int = 100,
    ) -> ChaosTestResult:
        """Run a chaos test."""
        result = ChaosTestResult(
            test_id=self._generate_test_id(),
            chaos_type=chaos_type,
            target_service=self.target_service,
            duration_seconds=duration_seconds,
            requests_total=request_count,
            requests_failed=0,
            success=True,
        )

        # Simulate chaos injection
        import random

        for i in range(request_count):
            # Simulate injection impact
            if chaos_type == ChaosType.LATENCY:
                # Latency: 30% of requests affected
                if random.random() < 0.3:
                    result.requests_failed += 1
                    result.error_messages.append(f"Request {i} timeout due to latency")

            elif chaos_type == ChaosType.ERROR:
                # Error injection: 20% of requests fail
                if random.random() < 0.2:
                    result.requests_failed += 1
                    result.error_messages.append(
                        f"Request {i} failed with injected error"
                    )

            elif chaos_type == ChaosType.TIMEOUT:
                # Timeout: 25% of requests timeout
                if random.random() < 0.25:
                    result.requests_failed += 1
                    result.error_messages.append(f"Request {i} timed out")

            elif chaos_type == ChaosType.NETWORK_PARTITION:
                # Network partition: 40% of requests fail
                if random.random() < 0.4:
                    result.requests_failed += 1
                    result.error_messages.append(
                        f"Request {i} failed due to network partition"
                    )

        # Test passes if resilience score > 50 (less than 50% failure rate)
        result.success = result.resilience_score() > 50

        return result

    @staticmethod
    def _generate_test_id() -> str:
        """Generate unique test ID."""
        timestamp = datetime.now().isoformat()
        return f"CHAOS_{hashlib.md5(timestamp.encode()).hexdigest()[:8].upper()}"


class InfrastructureTestSuite:
    """Runs complete infrastructure test suite."""

    def __init__(self):
        self.results: List[TestReport] = []
        self.slos: Dict[str, SLOSpec] = {}

    def add_slo(self, slo: SLOSpec) -> None:
        """Add SLO specification."""
        self.slos[slo.service_name] = slo

    def run_health_checks(self, services: List[str]) -> TestReport:
        """Run health checks."""
        checker = HealthChecker()
        results = checker.check_multiple(services)

        # All healthy = test passes
        all_healthy = all(r.is_healthy() for r in results)

        report = TestReport(
            test_id=self._generate_test_id(),
            test_type=TestType.HEALTH_CHECK,
            timestamp=datetime.now().isoformat(),
            duration_seconds=0.1,
            passed=all_healthy,
            metrics={
                "services_checked": len(services),
                "healthy_count": sum(1 for r in results if r.is_healthy()),
                "degraded_count": sum(1 for r in results if r.is_degraded()),
                "unhealthy_count": sum(
                    1 for r in results if r.status == HealthStatus.UNHEALTHY
                ),
                "avg_response_time_ms": mean(r.response_time_ms for r in results)
                if results
                else 0,
            },
            confidence_percent=100.0 if all_healthy else 50.0,
        )

        self.results.append(report)
        return report

    def run_load_test(self, service: str, duration: int = 10) -> TestReport:
        """Run load test."""
        tester = LoadTester(service)
        result = tester.run_test(duration_seconds=duration, concurrent_requests=10)

        # Test passes if success rate > 90%
        passed = result.success_rate() >= 90

        report = TestReport(
            test_id=self._generate_test_id(),
            test_type=TestType.LOAD,
            timestamp=datetime.now().isoformat(),
            duration_seconds=duration,
            passed=passed,
            metrics={
                "requests_total": result.requests_total,
                "requests_successful": result.requests_successful,
                "requests_failed": result.requests_failed,
                "success_rate": result.success_rate(),
                "avg_response_time_ms": result.avg_response_time(),
                "p99_response_time_ms": result.p99_response_time(),
                "throughput_rps": result.throughput_rps(),
            },
            confidence_percent=result.success_rate(),
        )

        self.results.append(report)
        return report

    def run_failover_test(self, primary: str, backup: str) -> TestReport:
        """Run failover test."""
        tester = FailoverTester(primary, backup)
        result = tester.run_test()

        # Failover passes if completed < 200ms
        failover_time = result.failover_time_ms()
        passed = failover_time < 200 and result.success

        report = TestReport(
            test_id=self._generate_test_id(),
            test_type=TestType.FAILOVER,
            timestamp=datetime.now().isoformat(),
            duration_seconds=failover_time / 1000,
            passed=passed,
            metrics={
                "detection_time_ms": result.detection_time_ms(),
                "failover_time_ms": failover_time,
                "primary_service": primary,
                "backup_service": backup,
            },
            confidence_percent=100.0 if passed else 30.0,
        )

        self.results.append(report)
        return report

    def run_chaos_test(self, service: str, chaos_type: ChaosType) -> TestReport:
        """Run chaos test."""
        tester = ChaosTester(service)
        result = tester.run_test(
            chaos_type=chaos_type, duration_seconds=5, request_count=100
        )

        # Calculate metrics
        resilience = result.resilience_score()
        failure_rate = result.failure_rate()

        report = TestReport(
            test_id=self._generate_test_id(),
            test_type=TestType.CHAOS,
            timestamp=datetime.now().isoformat(),
            duration_seconds=5,
            passed=result.success,
            metrics={
                "chaos_type": chaos_type.value,
                "requests_total": result.requests_total,
                "requests_failed": result.requests_failed,
                "failure_rate": failure_rate,
                "resilience_score": resilience,
            },
            confidence_percent=resilience,
        )

        self.results.append(report)
        return report

    def run_all_tests(self, services: List[str]) -> Dict[str, Any]:
        """Run complete test suite."""
        print("\n🧪 Running complete infrastructure test suite...\n")

        # Health checks
        print("  ✓ Running health checks...")
        self.run_health_checks(services)

        # Load tests
        for service in services:
            print(f"  ✓ Running load test for {service}...")
            self.run_load_test(service, duration=5)

        # Failover tests
        if len(services) >= 2:
            print(f"  ✓ Running failover test ({services[0]} → {services[1]})...")
            self.run_failover_test(services[0], services[1])

        # Chaos tests
        for service in services[:1]:  # Test first service
            for chaos_type in [ChaosType.LATENCY, ChaosType.ERROR]:
                print(f"  ✓ Running chaos test ({chaos_type.value}) for {service}...")
                self.run_chaos_test(service, chaos_type)

        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        return {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "reports": [r.summary() for r in self.results],
        }

    @staticmethod
    def _generate_test_id() -> str:
        """Generate unique test ID."""
        timestamp = datetime.now().isoformat()
        return f"TEST_{hashlib.md5(timestamp.encode()).hexdigest()[:8].upper()}"


def main() -> None:
    """Demo Layer 4 infrastructure testing."""
    print("=" * 80)
    print("LAYER 4: INFRASTRUCTURE TESTING")
    print("=" * 80)

    # Create test suite
    suite = InfrastructureTestSuite()

    # Add SLOs
    suite.add_slo(
        SLOSpec(
            service_name="api",
            availability_target=99.9,
            latency_p99_ms=200,
            error_rate_max=0.1,
        )
    )

    # Run tests
    services = ["api", "worker", "cache"]
    results = suite.run_all_tests(services)

    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Pass rate: {results['pass_rate']:.1f}%")
    print("=" * 80)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
