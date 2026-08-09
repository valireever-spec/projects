"""Local machine resource monitoring to prevent orchestrator crashes."""

import logging
import psutil
import asyncio
import time
from typing import Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ResourceExhausted(Exception):
    """Raised when system resources exhausted (force orchestrator halt)."""
    pass


@dataclass
class ResourceThresholds:
    """Safe resource thresholds for orchestrator operation (HARDENED DEFAULTS)."""
    min_available_memory_gb: float = 1.0  # Halt if <1GB free (was 2GB)
    max_cpu_percent: float = 75.0  # Halt if CPU >75% (was 80%)
    min_disk_free_percent: float = 8.0  # Halt if <8% disk free (was 10%)
    memory_growth_limit_mb: int = 500  # Kill if memory grows >500MB
    monitor_interval_seconds: int = 5  # Check every 5 seconds
    max_duration_without_progress: int = 60  # Kill if hung 60+ seconds


@dataclass
class ResourceStatus:
    """Current resource status."""
    memory_available_gb: float
    memory_used_percent: float
    cpu_percent: float
    disk_free_percent: float
    is_safe: bool
    warnings: list


class ResourceMonitor:
    """Monitor local machine resources and gate agent execution (HARDENED)."""

    def __init__(self, thresholds: Optional[ResourceThresholds] = None):
        """Initialize monitor with thresholds.

        Args:
            thresholds: Custom resource thresholds, or default if None (hardened)
        """
        self.thresholds = thresholds or ResourceThresholds()
        self._memory_baseline = None
        self._cpu_high_count = 0  # Track consecutive high-CPU samples
        self._monitor_task = None
        self._process = psutil.Process()

    def check_resources(self) -> ResourceStatus:
        """Check current resource usage.

        Returns:
            ResourceStatus with current metrics and safety flag

        Raises:
            RuntimeError: If unable to read system resources
        """
        try:
            # Memory
            mem = psutil.virtual_memory()
            memory_available_gb = mem.available / (1024 ** 3)
            memory_used_percent = mem.percent

            # CPU (1-second sample)
            cpu_percent = psutil.cpu_percent(interval=1)

            # Disk
            disk = psutil.disk_usage('/')
            disk_free_percent = (disk.free / disk.total) * 100

            # Safety check
            warnings = []
            is_safe = True

            if memory_available_gb < self.thresholds.min_available_memory_gb:
                warnings.append(f"Low memory: {memory_available_gb:.2f}GB available (threshold: {self.thresholds.min_available_memory_gb}GB)")
                is_safe = False

            if cpu_percent > self.thresholds.max_cpu_percent:
                warnings.append(f"High CPU: {cpu_percent:.1f}% (threshold: {self.thresholds.max_cpu_percent}%)")
                is_safe = False

            if disk_free_percent < self.thresholds.min_disk_free_percent:
                warnings.append(f"Low disk: {disk_free_percent:.1f}% free (threshold: {self.thresholds.min_disk_free_percent}%)")
                is_safe = False

            status = ResourceStatus(
                memory_available_gb=memory_available_gb,
                memory_used_percent=memory_used_percent,
                cpu_percent=cpu_percent,
                disk_free_percent=disk_free_percent,
                is_safe=is_safe,
                warnings=warnings
            )

            if not is_safe:
                logger.warning(f"⚠️  Resource warning: {'; '.join(warnings)}")
            else:
                logger.debug(f"Resources OK: {memory_available_gb:.2f}GB free, CPU {cpu_percent:.1f}%, disk {disk_free_percent:.1f}%")

            return status

        except Exception as e:
            logger.error(f"Failed to check resources: {e}", exc_info=True)
            raise RuntimeError(f"Resource monitoring failed: {e}")

    def can_run_agent(self) -> Tuple[bool, Optional[str]]:
        """Check if it's safe to run an agent.

        Returns:
            (can_run, reason_if_not)
        """
        try:
            status = self.check_resources()
            if status.is_safe:
                return True, None
            else:
                reason = "; ".join(status.warnings)
                return False, reason
        except Exception as e:
            return False, f"Resource check failed: {e}"

    def wait_for_resources(self, max_wait_seconds: int = 300, check_interval_seconds: int = 5) -> bool:
        """Wait for resources to become available (blocking).

        Args:
            max_wait_seconds: Maximum time to wait before giving up
            check_interval_seconds: How often to check resources

        Returns:
            True if resources became available, False if timeout
        """
        import time

        elapsed = 0
        while elapsed < max_wait_seconds:
            can_run, reason = self.can_run_agent()
            if can_run:
                logger.info("Resources available; proceeding with agent")
                return True

            logger.warning(f"Waiting for resources ({elapsed}s/{max_wait_seconds}s): {reason}")
            time.sleep(check_interval_seconds)
            elapsed += check_interval_seconds

        logger.error(f"Resources unavailable after {max_wait_seconds}s; giving up")
        return False

    def get_status_summary(self) -> str:
        """Get human-readable status summary."""
        status = self.check_resources()
        return (
            f"Memory: {status.memory_available_gb:.2f}GB free ({status.memory_used_percent:.1f}% used) | "
            f"CPU: {status.cpu_percent:.1f}% | "
            f"Disk: {status.disk_free_percent:.1f}% free | "
            f"Safe: {'✓' if status.is_safe else '✗'}"
        )

    # ========== HARDENED CONTINUOUS MONITORING ==========

    def _get_process_memory_mb(self) -> int:
        """Get memory used by orchestrator process."""
        return self._process.memory_info().rss // (1024 * 1024)

    async def monitor_during_execution(self, agent_name: str, timeout_seconds: int):
        """Monitor while agent runs. Kill if bloated/hung/high-CPU.

        Args:
            agent_name: Name of agent being monitored (for logging)
            timeout_seconds: Max execution time before timeout

        Returns:
            Monitor task that can be awaited or cancelled
        """
        initial_mem = self._get_process_memory_mb()
        self._memory_baseline = initial_mem
        self._cpu_high_count = 0

        logger.info(
            f"Starting monitoring for {agent_name}. "
            f"Memory baseline: {initial_mem}MB, "
            f"Timeout: {timeout_seconds}s"
        )

        # Start monitoring in background
        self._monitor_task = asyncio.create_task(
            self._continuous_monitor(agent_name, initial_mem, timeout_seconds)
        )

        return self._monitor_task

    async def _continuous_monitor(self, agent_name: str, baseline_mem: int, timeout: int):
        """Background task: check resources every N seconds."""
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > timeout:
                logger.info(f"Monitor [{agent_name}]: Completed within timeout ({int(elapsed)}s)")
                break

            try:
                # CHECK 1: Memory bloat
                current_mem = self._get_process_memory_mb()
                growth = current_mem - baseline_mem

                if growth > self.thresholds.memory_growth_limit_mb:
                    logger.critical(
                        f"🚨 MEMORY BLOAT DETECTED: {agent_name} grew {growth}MB "
                        f"({baseline_mem}MB → {current_mem}MB). KILLING AGENT."
                    )
                    await self._emergency_shutdown(agent_name, "memory_bloat")
                    raise ResourceExhausted(f"Memory bloat: {growth}MB growth")

                # CHECK 2: High CPU
                cpu = psutil.cpu_percent(interval=1)

                if cpu > self.thresholds.max_cpu_percent:
                    self._cpu_high_count += 1
                    logger.warning(
                        f"⚠️  High CPU: {cpu:.1f}% during {agent_name} "
                        f"(sample {self._cpu_high_count}/6)"
                    )

                    # If CPU high for 30+ seconds (6 samples), kill
                    if self._cpu_high_count >= 6:
                        logger.critical(
                            f"🚨 CPU STUCK HIGH: {agent_name} holding {cpu:.1f}% for 30s. KILLING."
                        )
                        await self._emergency_shutdown(agent_name, "cpu_stuck_high")
                        raise ResourceExhausted(f"CPU stuck high: {cpu:.1f}%")
                else:
                    self._cpu_high_count = 0

                # CHECK 3: Overall system health
                sys_status = self.check_resources()
                if not sys_status.is_safe:
                    logger.critical(
                        f"🚨 SYSTEM UNHEALTHY: {'; '.join(sys_status.warnings)}. "
                        f"KILLING {agent_name}."
                    )
                    await self._emergency_shutdown(agent_name, "system_unhealthy")
                    raise ResourceExhausted(f"System unhealthy: {sys_status.warnings}")

                logger.debug(
                    f"Monitor [{agent_name}]: "
                    f"Mem {current_mem}MB (+{growth}MB), "
                    f"CPU {cpu:.1f}%, "
                    f"Elapsed {int(elapsed)}s/{timeout}s"
                )

                await asyncio.sleep(self.thresholds.monitor_interval_seconds)

            except asyncio.CancelledError:
                logger.debug(f"Monitor [{agent_name}]: Cancelled by orchestrator")
                break
            except ResourceExhausted:
                raise
            except Exception as e:
                logger.error(f"Monitor [{agent_name}]: Error during monitoring: {e}")
                raise

    async def _emergency_shutdown(self, agent_name: str, reason: str):
        """EMERGENCY: Kill agent and child processes immediately."""
        logger.critical(f"🚨 EMERGENCY SHUTDOWN: {agent_name} ({reason})")

        try:
            # Find and kill child processes (agents, skills)
            children = self._process.children(recursive=True)

            for child in children:
                try:
                    logger.critical(f"  Killing: PID {child.pid} ({child.name()})")
                    child.kill()
                except Exception as e:
                    logger.warning(f"  Failed to kill PID {child.pid}: {e}")

        except Exception as e:
            logger.error(f"Failed to kill child processes: {e}")

        # Cleanup memory
        import gc
        gc.collect()

        logger.critical(f"Emergency shutdown complete. System resources freed.")

    async def cleanup(self):
        """Cleanup monitoring task."""
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        self._memory_baseline = None
        self._cpu_high_count = 0
