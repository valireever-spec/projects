"""Tests for ResourceMonitor."""

import pytest
from orchestrator.resource_monitor import ResourceMonitor, ResourceThresholds, ResourceStatus


def test_resource_monitor_initialization():
    """Test ResourceMonitor initializes with thresholds."""
    monitor = ResourceMonitor()

    assert monitor.thresholds is not None
    assert monitor.thresholds.min_available_memory_gb == 2.0
    assert monitor.thresholds.max_cpu_percent == 80.0


def test_resource_monitor_custom_thresholds():
    """Test ResourceMonitor with custom thresholds."""
    thresholds = ResourceThresholds(
        min_available_memory_gb=1.0,
        max_cpu_percent=90.0,
        min_disk_free_percent=5.0
    )

    monitor = ResourceMonitor(thresholds)

    assert monitor.thresholds.min_available_memory_gb == 1.0
    assert monitor.thresholds.max_cpu_percent == 90.0
    assert monitor.thresholds.min_disk_free_percent == 5.0


def test_resource_monitor_check_resources():
    """Test checking resources returns status."""
    monitor = ResourceMonitor()

    status = monitor.check_resources()

    assert isinstance(status, ResourceStatus)
    assert status.memory_available_gb >= 0
    assert 0 <= status.memory_used_percent <= 100
    assert 0 <= status.cpu_percent <= 100
    assert 0 <= status.disk_free_percent <= 100
    assert isinstance(status.is_safe, bool)
    assert isinstance(status.warnings, list)


def test_resource_monitor_can_run_agent():
    """Test can_run_agent returns tuple."""
    monitor = ResourceMonitor()

    can_run, reason = monitor.can_run_agent()

    assert isinstance(can_run, bool)
    assert reason is None or isinstance(reason, str)


def test_resource_monitor_status_summary():
    """Test getting status summary string."""
    monitor = ResourceMonitor()

    summary = monitor.get_status_summary()

    assert isinstance(summary, str)
    assert "Memory" in summary
    assert "CPU" in summary
    assert "Disk" in summary
    assert "Safe" in summary


def test_resource_status_with_warnings():
    """Test ResourceStatus with warnings."""
    status = ResourceStatus(
        memory_available_gb=0.5,
        memory_used_percent=99,
        cpu_percent=50,
        disk_free_percent=8,
        is_safe=False,
        warnings=["Low memory", "Low disk"]
    )

    assert status.is_safe is False
    assert len(status.warnings) == 2
    assert "Low memory" in status.warnings


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
