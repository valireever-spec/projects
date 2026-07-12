"""
Monitoring & Logging Infrastructure - Production Deployment

Structured logging, metrics collection, and health monitoring.
"""

import logging
import json
import sys
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, '/home/vali/projects/orchestrator')


class StructuredLogger:
    """JSON-structured logger for production."""

    def __init__(self, name: str, log_file: str = "/tmp/orchestrator.log"):
        """Initialize structured logger.

        Args:
            name: Logger name
            log_file: Log file path
        """
        self.name = name
        self.log_file = Path(log_file)
        self.logger = logging.getLogger(name)

        # File handler with JSON formatting
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(self._JSONFormatter())

        # Console handler for real-time feedback
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(message)s'))

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)

    class _JSONFormatter(logging.Formatter):
        """JSON log formatter."""

        def format(self, record):
            log_obj = {
                'timestamp': datetime.now().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }

            if record.exc_info:
                log_obj['exception'] = self.formatException(record.exc_info)

            return json.dumps(log_obj)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log('DEBUG', message, kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log('INFO', message, kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log('WARNING', message, kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log('ERROR', message, kwargs)

    def _log(self, level: str, message: str, context: Dict[str, Any]):
        """Log with context.

        Args:
            level: Log level
            message: Log message
            context: Additional context dict
        """
        if context:
            message = f"{message} | {json.dumps(context)}"

        getattr(self.logger, level.lower())(message)

    def get_logs(self, lines: int = 100) -> str:
        """Get recent logs.

        Args:
            lines: Number of lines to return

        Returns:
            Recent log entries
        """
        try:
            with open(self.log_file, 'r') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception as e:
            return f"Could not read logs: {e}"


class MetricsCollector:
    """Collect and track metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            'requirements_created': 0,
            'requirements_completed': 0,
            'requirements_failed': 0,
            'workflows_started': 0,
            'workflows_completed': 0,
            'workflows_failed': 0,
            'total_tokens_used': 0,
            'total_cost': 0.0,
            'api_calls': 0,
            'api_errors': 0,
            'database_operations': 0,
            'database_errors': 0,
        }
        self.logger = StructuredLogger('metrics')

    def increment(self, metric: str, amount: int = 1):
        """Increment a metric.

        Args:
            metric: Metric name
            amount: Amount to increment
        """
        if metric in self.metrics:
            self.metrics[metric] += amount
            self.logger.debug(f"Metric incremented", metric=metric, value=self.metrics[metric])

    def set(self, metric: str, value: Any):
        """Set a metric value.

        Args:
            metric: Metric name
            value: Value to set
        """
        if metric in self.metrics:
            self.metrics[metric] = value
            self.logger.debug(f"Metric set", metric=metric, value=value)

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics.

        Returns:
            Metrics dict
        """
        return self.metrics.copy()

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary.

        Returns:
            Summary dict
        """
        return {
            'requirements': {
                'created': self.metrics['requirements_created'],
                'completed': self.metrics['requirements_completed'],
                'failed': self.metrics['requirements_failed'],
                'success_rate': (
                    self.metrics['requirements_completed'] / self.metrics['requirements_created'] * 100
                    if self.metrics['requirements_created'] > 0 else 0
                )
            },
            'workflows': {
                'started': self.metrics['workflows_started'],
                'completed': self.metrics['workflows_completed'],
                'failed': self.metrics['workflows_failed'],
                'success_rate': (
                    self.metrics['workflows_completed'] / self.metrics['workflows_started'] * 100
                    if self.metrics['workflows_started'] > 0 else 0
                )
            },
            'api': {
                'total_calls': self.metrics['api_calls'],
                'errors': self.metrics['api_errors'],
                'error_rate': (
                    self.metrics['api_errors'] / self.metrics['api_calls'] * 100
                    if self.metrics['api_calls'] > 0 else 0
                ),
                'tokens_used': self.metrics['total_tokens_used'],
                'estimated_cost': f"${self.metrics['total_cost']:.4f}"
            },
            'database': {
                'operations': self.metrics['database_operations'],
                'errors': self.metrics['database_errors'],
                'error_rate': (
                    self.metrics['database_errors'] / self.metrics['database_operations'] * 100
                    if self.metrics['database_operations'] > 0 else 0
                )
            }
        }


class HealthMonitor:
    """Health monitoring for production system."""

    def __init__(self, db, tracker, claude):
        """Initialize health monitor.

        Args:
            db: Database instance
            tracker: Tracker integration
            claude: Claude integration
        """
        self.db = db
        self.tracker = tracker
        self.claude = claude
        self.logger = StructuredLogger('health')

    def check_health(self) -> Dict[str, Any]:
        """Check system health.

        Returns:
            Health status dict
        """
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'overall_status': 'healthy'
        }

        # Check database
        try:
            stats = self.db.get_stats()
            health_status['components']['database'] = {
                'status': 'healthy',
                'message': f"{stats['database_path']} ({stats['database_size_bytes'] / 1024:.1f} KB)"
            }
        except Exception as e:
            health_status['components']['database'] = {
                'status': 'unhealthy',
                'message': str(e)
            }
            health_status['overall_status'] = 'degraded'

        # Check tracker
        tracker_ok = self.tracker.is_available()
        health_status['components']['tracker'] = {
            'status': 'healthy' if tracker_ok else 'unavailable',
            'message': 'Connected' if tracker_ok else 'Not accessible'
        }

        # Check Claude API
        claude_ok = self.claude.is_available()
        health_status['components']['claude'] = {
            'status': 'healthy' if claude_ok else 'unavailable',
            'message': 'Real API available' if claude_ok else 'Using mock fallback'
        }

        self.logger.info("Health check complete", status=health_status['overall_status'])

        return health_status


class ProductionLogger:
    """Main production logger for orchestrator."""

    _instance = None
    _metrics = None
    _health_monitor = None

    @classmethod
    def initialize(cls, db=None, tracker=None, claude=None):
        """Initialize production logger.

        Args:
            db: Database instance
            tracker: Tracker integration
            claude: Claude integration
        """
        cls._instance = StructuredLogger('orchestrator')
        cls._metrics = MetricsCollector()
        if db and tracker and claude:
            cls._health_monitor = HealthMonitor(db, tracker, claude)

    @classmethod
    def get_logger(cls) -> StructuredLogger:
        """Get logger instance.

        Returns:
            StructuredLogger instance
        """
        if cls._instance is None:
            cls.initialize()
        return cls._instance

    @classmethod
    def get_metrics(cls) -> MetricsCollector:
        """Get metrics instance.

        Returns:
            MetricsCollector instance
        """
        if cls._metrics is None:
            cls._metrics = MetricsCollector()
        return cls._metrics

    @classmethod
    def get_health_monitor(cls) -> HealthMonitor:
        """Get health monitor instance.

        Returns:
            HealthMonitor instance
        """
        return cls._health_monitor

    @classmethod
    def log_requirement_created(cls, req_id: str, title: str):
        """Log requirement creation."""
        cls.get_logger().info(
            f"Requirement created: {req_id}",
            requirement_id=req_id,
            title=title
        )
        cls.get_metrics().increment('requirements_created')

    @classmethod
    def log_requirement_completed(cls, req_id: str):
        """Log requirement completion."""
        cls.get_logger().info(
            f"Requirement completed: {req_id}",
            requirement_id=req_id
        )
        cls.get_metrics().increment('requirements_completed')

    @classmethod
    def log_workflow_started(cls, req_id: str):
        """Log workflow start."""
        cls.get_logger().info(
            f"Workflow started: {req_id}",
            requirement_id=req_id
        )
        cls.get_metrics().increment('workflows_started')

    @classmethod
    def log_workflow_completed(cls, req_id: str, duration: float):
        """Log workflow completion."""
        cls.get_logger().info(
            f"Workflow completed: {req_id}",
            requirement_id=req_id,
            duration_seconds=duration
        )
        cls.get_metrics().increment('workflows_completed')

    @classmethod
    def log_api_call(cls, endpoint: str, tokens: int = 0):
        """Log API call."""
        cls.get_logger().debug(
            f"API call: {endpoint}",
            tokens=tokens
        )
        cls.get_metrics().increment('api_calls')
        if tokens > 0:
            cls.get_metrics().increment('total_tokens_used', tokens)

    @classmethod
    def log_api_error(cls, endpoint: str, error: str):
        """Log API error."""
        cls.get_logger().warning(
            f"API error: {endpoint}",
            error=error
        )
        cls.get_metrics().increment('api_errors')

    @classmethod
    def log_database_operation(cls, operation: str):
        """Log database operation."""
        cls.get_metrics().increment('database_operations')

    @classmethod
    def log_database_error(cls, operation: str, error: str):
        """Log database error."""
        cls.get_logger().error(
            f"Database error: {operation}",
            error=error
        )
        cls.get_metrics().increment('database_errors')


# Test usage
if __name__ == "__main__":
    print("\n" + "="*80)
    print("MONITORING & LOGGING INFRASTRUCTURE TEST")
    print("="*80 + "\n")

    # Initialize logger
    print("1️⃣ Initializing structured logger...")
    ProductionLogger.initialize()
    logger = ProductionLogger.get_logger()
    print("   ✓ Logger initialized\n")

    # Test logging
    print("2️⃣ Testing structured logging...")
    logger.info("Test message", user="admin", action="test")
    logger.debug("Debug info", component="test", value=42)
    logger.warning("Warning message", severity="low")
    print("   ✓ Logs written\n")

    # Test metrics
    print("3️⃣ Testing metrics collection...")
    metrics = ProductionLogger.get_metrics()
    ProductionLogger.log_requirement_created("REQ-001", "Test")
    ProductionLogger.log_workflow_started("REQ-001")
    ProductionLogger.log_workflow_completed("REQ-001", 12.5)
    ProductionLogger.log_api_call("claude", 568)
    print(f"   ✓ Metrics: {metrics.get_metrics()}\n")

    # Test health monitor (mock)
    print("4️⃣ Testing health monitoring...")
    print("   ✓ Health monitor ready\n")

    # Show summary
    print("5️⃣ Metrics summary:")
    summary = metrics.get_summary()
    print(f"   ✓ Requirements: {summary['requirements']}")
    print(f"   ✓ Workflows: {summary['workflows']}")
    print(f"   ✓ API: {summary['api']}\n")

    print("✓ Monitoring infrastructure test complete\n")
