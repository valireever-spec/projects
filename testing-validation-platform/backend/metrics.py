"""
Metrics and SLO tracking for investing-platform V-Model tracker.

Tracks:
- API endpoint latency (p50, p95, p99)
- Error rates by endpoint
- Success rates
- Database operation timing
"""

import logging
import time
from typing import Dict, List, Optional, Callable, Any, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class LatencyMetric:
    """Latency metric for an operation."""

    operation: str
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "success"  # success, error, timeout
    error_type: Optional[str] = None


@dataclass
class SLOTarget:
    """SLO (Service Level Objective) target."""

    name: str
    metric: str  # "latency", "error_rate", "availability"
    target_value: float
    unit: str  # "ms", "percent", "count"
    window_minutes: int = 5


class MetricsCollector:
    """Collect and report metrics for SLO tracking."""

    def __init__(self) -> None:
        self.metrics: List[LatencyMetric] = []
        self.slos: Dict[str, SLOTarget] = {}
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.request_counts: Dict[str, int] = defaultdict(int)

    def record_operation(
        self,
        operation: str,
        duration_ms: float,
        status: str = "success",
        error_type: Optional[str] = None
    ) -> None:
        """Record an operation metric.

        Args:
            operation: Operation name (e.g., "tracker.report_bug", "vmodel.sync")
            duration_ms: Duration in milliseconds
            status: success, error, timeout
            error_type: Type of error if status is error
        """
        metric = LatencyMetric(
            operation=operation,
            duration_ms=duration_ms,
            status=status,
            error_type=error_type
        )
        self.metrics.append(metric)
        self.request_counts[operation] += 1

        if status != "success":
            self.error_counts[operation] += 1

        logger.debug(
            "Metric recorded",
            extra={
                "operation": operation,
                "duration_ms": duration_ms,
                "status": status,
            }
        )

    def register_slo(
        self,
        name: str,
        metric: str,
        target_value: float,
        unit: str,
        window_minutes: int = 5
    ) -> None:
        """Register an SLO target.

        Args:
            name: SLO name (e.g., "tracker_api_latency_p95")
            metric: Metric type (latency, error_rate, availability)
            target_value: Target value (e.g., 500 for 500ms latency)
            unit: Unit of measurement (ms, percent, count)
            window_minutes: Time window for measurement
        """
        slo = SLOTarget(
            name=name,
            metric=metric,
            target_value=target_value,
            unit=unit,
            window_minutes=window_minutes
        )
        self.slos[name] = slo
        logger.info(f"SLO registered: {name}")

    def get_latency_percentile(
        self,
        operation: str,
        percentile: int = 95,
        minutes: int = 5
    ) -> Optional[float]:
        """Get latency percentile for an operation.

        Args:
            operation: Operation name to query
            percentile: Percentile to calculate (50, 95, 99)
            minutes: Time window in minutes

        Returns:
            Latency in milliseconds, or None if no data
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        durations = [
            m.duration_ms
            for m in self.metrics
            if m.operation == operation
            and m.timestamp > cutoff_time
            and m.status == "success"
        ]

        if not durations:
            return None

        durations.sort()
        index = int((percentile / 100) * len(durations))
        return durations[min(index, len(durations) - 1)]

    def get_error_rate(
        self,
        operation: str,
        minutes: int = 5
    ) -> float:
        """Get error rate for an operation.

        Args:
            operation: Operation name to query
            minutes: Time window in minutes

        Returns:
            Error rate as percentage (0-100)
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics
            if m.operation == operation and m.timestamp > cutoff_time
        ]

        if not recent_metrics:
            return 0.0

        error_count = sum(1 for m in recent_metrics if m.status != "success")
        return (error_count / len(recent_metrics)) * 100

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status.

        Returns:
            Health dict with metrics for each operation
        """
        health: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "operations": {}
        }

        # Collect unique operations
        operations = set(m.operation for m in self.metrics)

        for operation in operations:
            p95_latency = self.get_latency_percentile(operation, 95)
            error_rate = self.get_error_rate(operation)
            request_count = self.request_counts.get(operation, 0)
            error_count = self.error_counts.get(operation, 0)

            health["operations"][operation] = {
                "request_count": request_count,
                "error_count": error_count,
                "error_rate_percent": error_rate,
                "p95_latency_ms": p95_latency,
                "slo_status": "pass" if (p95_latency or 0) < 1000 else "warn",
            }

        return health

    def cleanup_old_metrics(self, hours: int = 24) -> int:
        """Remove metrics older than specified hours.

        Args:
            hours: Hours to keep (default 24)

        Returns:
            Number of metrics removed
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        old_count = len(self.metrics)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        removed = old_count - len(self.metrics)
        logger.info(f"Cleaned up {removed} old metrics")
        return removed


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or initialize the global metrics collector.

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
        # Register default SLOs
        _metrics_collector.register_slo(
            "tracker_api_latency_p95",
            "latency",
            500,
            "ms"
        )
        _metrics_collector.register_slo(
            "tracker_error_rate",
            "error_rate",
            5.0,
            "percent"
        )
    return _metrics_collector


def track_operation(operation: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to track operation metrics.

    Usage:
        @track_operation("my_operation")
        def my_function():
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                get_metrics_collector().record_operation(
                    operation,
                    duration_ms,
                    status="success"
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                get_metrics_collector().record_operation(
                    operation,
                    duration_ms,
                    status="error",
                    error_type=type(e).__name__
                )
                raise
        return wrapper  # type: ignore
    return decorator
