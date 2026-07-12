#!/usr/bin/env python3
"""
Master Orchestrator: Comprehensive task execution with REAL task implementations.

Features:
1. Execute ACTUAL work, not mocks
2. 12 production-quality checks
3. Retry failed tasks (3 attempts)
4. Continue on error (doesn't stop)
5. Generate comprehensive audit report
"""

import subprocess
import time
import sys
import re
import json
import ast
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from orchestrator_progress import ProgressTracker
from commit_grouper import CommitGrouper
from rollback_manager import RollbackManager, CheckpointType
from result_cache import ResultCache


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    SKIPPED = "skipped"


@dataclass
class TaskResult:
    """Result of task execution."""

    task_id: str
    task_name: str
    status: TaskStatus
    attempts: int = 0
    max_attempts: int = 3
    error_message: str = ""
    output: str = ""
    duration_ms: int = 0
    retry_count: int = 0
    details: Dict = field(default_factory=dict)


class MasterOrchestrator:
    """Master orchestrator with comprehensive task handling."""

    def __init__(self):
        self.progress = ProgressTracker("Master Orchestrator", total_items=None)
        self.commit_grouper = CommitGrouper(auto_finalize_threshold=500)
        self.rollback_mgr = RollbackManager()
        self.cache = ResultCache(ttl_seconds=3600)
        self.tasks: List[TaskResult] = []
        self.task_queue: List[Dict] = []
        self.results: Dict[str, TaskResult] = {}
        self.max_retries = 3
        self.use_parallel = True  # Enable Phase 2 parallel execution
        self.num_agents = 3  # Use 3 parallel agents

    def get_task_dependencies(self, task_id: str) -> Set[str]:
        """
        Get task IDs that must complete before this task.

        Returns:
            Set of task IDs this task depends on (empty = no dependencies)
        """
        # Format check should run first (all tasks depend on it)
        # Other tasks have no inter-dependencies
        dependencies = {
            "task_01_import_validation": {"task_00_format_check"},
            "task_05_resource_audit": {"task_00_format_check"},
            "task_10_error_handling": {"task_00_format_check"},
            "task_15_logging_check": {"task_00_format_check"},
            "task_16_guardian_e2e": {"task_00_format_check"},
            "task_20_api_endpoints": {"task_00_format_check"},
            "task_21_production_readiness": {"task_00_format_check"},
            "task_30_type_hints": {"task_00_format_check"},
            "task_40_test_coverage": {"task_00_format_check"},
            "task_50_documentation": {"task_00_format_check"},
            "task_60_security_scan": {"task_00_format_check"},
        }
        return dependencies.get(task_id, set())

    def find_independent_groups(self) -> List[Set[str]]:
        """
        Find groups of tasks that can run in parallel.

        Returns:
            List of sets, where each set contains task IDs that can run simultaneously
        """
        # Build dependency map
        task_ids = {t["id"] for t in self.task_queue}
        dependencies = {}
        for task_id in task_ids:
            dependencies[task_id] = self.get_task_dependencies(task_id)

        # Find independent groups using topological analysis
        processed = set()
        groups = []

        while len(processed) < len(task_ids):
            # Find all tasks with no unprocessed dependencies
            current_group = set()

            for task_id in task_ids:
                if task_id in processed:
                    continue

                # Check if all dependencies are processed
                deps = dependencies[task_id]
                if deps.issubset(processed):
                    current_group.add(task_id)

            if not current_group:
                # Circular dependency or error
                break

            groups.append(current_group)
            processed.update(current_group)

        return groups

    def can_parallelize(self) -> bool:
        """Check if there are enough independent tasks to benefit from parallelization."""
        groups = self.find_independent_groups()
        # Parallelization beneficial if >1 group and first group has >1 task
        return len(groups) > 1 or any(len(g) > 1 for g in groups)

    def estimate_speedup(self) -> Tuple[float, str]:
        """
        Estimate speedup from parallelization.

        Returns:
            (speedup_factor, explanation)
        """
        groups = self.find_independent_groups()

        if len(groups) <= 1 and all(len(g) == 1 for g in groups):
            return 1.0, "No parallelizable tasks"

        # Speedup formula: total_tasks / (num_groups + merge_overhead)
        total_tasks = len(self.task_queue)
        merge_overhead = (self.num_agents - 1) * 0.15  # 15% per agent merge cost
        theoretical_speedup = total_tasks / (len(groups) + merge_overhead)

        # Cap at practical limit (diminishing returns beyond 3x)
        practical_speedup = min(theoretical_speedup, 2.8)

        explanation = f"{self.num_agents} agents, {len(groups)} independent phases"

        return practical_speedup, explanation

    def register_tasks(self):
        """Register ALL tasks to be executed."""
        # Task definitions with comprehensive coverage
        task_definitions = [
            {
                "id": "task_00_format_check",
                "name": "Format & Syntax Validation",
                "description": "Check all Python files for format errors",
                "executor": self.execute_format_check,
            },
            {
                "id": "task_01_import_validation",
                "name": "Import Dependencies Validation",
                "description": "Verify all imports are available",
                "executor": self.execute_import_validation,
            },
            {
                "id": "task_05_resource_audit",
                "name": "Resource Leak Audit",
                "description": "Audit backend for resource leaks",
                "executor": self.execute_resource_audit,
            },
            {
                "id": "task_10_error_handling",
                "name": "Error Handling Verification",
                "description": "Verify error handling patterns",
                "executor": self.execute_error_handling,
            },
            {
                "id": "task_15_logging_check",
                "name": "Logging Completeness Check",
                "description": "Verify logging in critical paths",
                "executor": self.execute_logging_check,
            },
            {
                "id": "task_16_guardian_e2e",
                "name": "Guardian E2E Tests",
                "description": "Run Guardian system end-to-end tests",
                "executor": self.execute_guardian_e2e,
            },
            {
                "id": "task_20_api_endpoints",
                "name": "API Endpoint Validation",
                "description": "Validate all API endpoints",
                "executor": self.execute_api_validation,
            },
            {
                "id": "task_21_production_readiness",
                "name": "Production Module Readiness",
                "description": "Check top modules for production readiness",
                "executor": self.execute_production_readiness,
            },
            {
                "id": "task_30_type_hints",
                "name": "Type Hints Coverage",
                "description": "Verify type hints in critical modules",
                "executor": self.execute_type_hints,
            },
            {
                "id": "task_40_test_coverage",
                "name": "Test Coverage Check",
                "description": "Verify test coverage for critical paths",
                "executor": self.execute_test_coverage,
            },
            {
                "id": "task_50_documentation",
                "name": "Documentation Completeness",
                "description": "Check documentation coverage",
                "executor": self.execute_documentation,
            },
            {
                "id": "task_60_security_scan",
                "name": "Security Scan",
                "description": "Security analysis of codebase",
                "executor": self.execute_security_scan,
            },
        ]

        self.task_queue = task_definitions
        self.progress.log_status(f"Registered {len(self.task_queue)} tasks")

    def execute_format_check(self) -> TaskResult:
        """Task: Format and syntax validation (check ALL Python files)."""
        result = TaskResult("task_00_format_check", "Format & Syntax Validation", TaskStatus.PENDING)
        try:
            import py_compile
            import ast

            py_files = sorted(Path("backend").rglob("*.py"))
            errors = []
            syntax_ok = 0

            for py_file in py_files:
                try:
                    py_compile.compile(str(py_file), doraise=True)
                    syntax_ok += 1
                except SyntaxError as e:
                    errors.append(f"{py_file.name}:{e.lineno} - {e.msg}")
                except Exception as e:
                    errors.append(f"{py_file.name} - {str(e)}")

            result.details = {
                "files_checked": len(py_files),
                "syntax_ok": syntax_ok,
                "errors": len(errors),
                "error_list": errors[:10],
            }

            if errors:
                result.status = TaskStatus.FAILED
                result.output = f"Format check: {len(errors)} syntax errors found"
                result.error_message = "\n".join(errors[:5])
            else:
                result.status = TaskStatus.SUCCESS
                result.output = f"Format check passed: {len(py_files)} files, 0 syntax errors"

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"Format check failed: {str(e)}"
        return result

    def execute_import_validation(self) -> TaskResult:
        """Task: Import dependencies validation (check backend module imports)."""
        result = TaskResult("task_01_import_validation", "Import Validation", TaskStatus.PENDING)
        try:
            # Check critical backend modules can be imported
            critical_modules = [
                "backend.core.config_manager",
                "backend.core.exceptions",
                "backend.db.database",
                "backend.api.main",
                "backend.trading.bot_runner",
                "backend.services.universe_service",
                "backend.analytics.composite_signal",
            ]

            failed = []
            for module in critical_modules:
                try:
                    __import__(module)
                except ImportError as e:
                    failed.append({"module": module, "error": str(e)})
                except Exception as e:
                    failed.append({"module": module, "error": f"Syntax/Runtime: {str(e)}"})

            result.details = {
                "modules_checked": len(critical_modules),
                "failed": len(failed),
                "failed_modules": failed,
            }

            if failed:
                result.status = TaskStatus.FAILED
                result.output = f"Import validation: {len(failed)} modules failed to import"
                result.error_message = "; ".join([f"{f['module']}: {f['error']}" for f in failed[:3]])
            else:
                result.status = TaskStatus.SUCCESS
                result.output = f"Import validation passed: {len(critical_modules)} critical modules ok"

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"Import validation failed: {str(e)}"
        return result

    def execute_resource_audit(self) -> TaskResult:
        """Task: Resource leak audit (check for unclosed files, subprocesses, etc)."""
        result = TaskResult("task_05_resource_audit", "Resource Audit", TaskStatus.PENDING)
        try:
            issues = []
            files_scanned = 0

            for py_file in Path("backend").rglob("*.py"):
                files_scanned += 1
                try:
                    content = py_file.read_text(encoding="utf-8")
                    lines = content.split("\n")

                    # Check for unclosed file opens
                    for i, line in enumerate(lines, 1):
                        # Pattern: open(...) without 'with'
                        if "open(" in line and "with" not in lines[max(0, i - 2) : i]:
                            if "=" in line and not line.strip().startswith("#"):
                                issues.append(
                                    {
                                        "file": py_file.name,
                                        "line": i,
                                        "type": "unclosed_file",
                                        "code": line.strip()[:60],
                                    }
                                )

                        # Check for subprocess without context manager
                        if "subprocess." in line and "Popen(" in line:
                            if "with" not in lines[max(0, i - 2) : i] and "context" not in line.lower():
                                issues.append(
                                    {
                                        "file": py_file.name,
                                        "line": i,
                                        "type": "unclosed_subprocess",
                                        "code": line.strip()[:60],
                                    }
                                )

                except Exception as e:
                    pass

            result.details = {
                "files_scanned": files_scanned,
                "issues_found": len(issues),
                "issues": issues[:10],
            }

            if issues:
                result.status = TaskStatus.FAILED
                result.output = f"Resource audit: {len(issues)} potential leaks found"
                result.error_message = f"Issues in {len(set(i['file'] for i in issues))} files"
            else:
                result.status = TaskStatus.SUCCESS
                result.output = f"Resource audit: {files_scanned} files scanned, 0 leaks detected"

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"Resource audit failed: {str(e)}"
        return result

    def execute_error_handling(self) -> TaskResult:
        """Task: Error handling verification (check except patterns)."""
        result = TaskResult("task_10_error_handling", "Error Handling", TaskStatus.PENDING)
        try:
            issues = []
            files_checked = 0

            for py_file in Path("backend").rglob("*.py"):
                files_checked += 1
                try:
                    content = py_file.read_text(encoding="utf-8")
                    lines = content.split("\n")

                    for i, line in enumerate(lines, 1):
                        stripped = line.strip()

                        # Bare except without logging/handling
                        if stripped == "except:" or stripped.startswith("except:"):
                            issues.append(
                                {
                                    "file": py_file.name,
                                    "line": i,
                                    "type": "bare_except",
                                    "code": stripped[:60],
                                }
                            )

                        # Generic Exception without specific types
                        if stripped.startswith("except Exception"):
                            # Check if there's proper logging/handling after
                            following = "\n".join(lines[i : min(i + 3, len(lines))])
                            if "logger" not in following and "print" not in following:
                                issues.append(
                                    {
                                        "file": py_file.name,
                                        "line": i,
                                        "type": "generic_exception_silent",
                                        "code": stripped[:60],
                                    }
                                )

                except Exception as e:
                    pass

            result.details = {
                "files_checked": files_checked,
                "issues_found": len(issues),
                "bare_excepts": len([i for i in issues if i["type"] == "bare_except"]),
                "silent_exceptions": len([i for i in issues if i["type"] == "generic_exception_silent"]),
                "issues": issues[:10],
            }

            if issues:
                result.status = TaskStatus.FAILED
                result.output = f"Error handling: {len(issues)} issues found"
                result.error_message = f"{result.details['bare_excepts']} bare excepts, {result.details['silent_exceptions']} silent exception handlers"
            else:
                result.status = TaskStatus.SUCCESS
                result.output = f"Error handling verified: {files_checked} files, no issues"

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"Error handling check failed: {str(e)}"
        return result

    def execute_logging_check(self) -> TaskResult:
        """Task: Logging completeness check (verify logging in critical paths)."""
        result = TaskResult("task_15_logging_check", "Logging Check", TaskStatus.PENDING)
        try:
            # Define critical files that MUST have logging
            critical_files = {
                "bot_runner.py": ["execute_cycle", "trade"],
                "main.py": ["startup", "shutdown", "error"],
                "failover_monitor.py": ["failover", "health"],
                "health_check.py": ["check", "alert"],
                "composite_signal.py": ["compute", "score"],
            }

            issues = []

            for py_file in Path("backend").rglob("*.py"):
                filename = py_file.name
                if filename in critical_files:
                    try:
                        content = py_file.read_text(encoding="utf-8")

                        # Check if any logger import exists
                        has_logger_import = "import logging" in content or "from" in content and "logger" in content

                        # Check for critical functions with logging
                        for critical_func in critical_files[filename]:
                            func_pattern = f"def {critical_func}"
                            if func_pattern in content:
                                # Extract function body
                                lines = content.split("\n")
                                func_start = next(
                                    (i for i, l in enumerate(lines) if func_pattern in l),
                                    None,
                                )
                                if func_start:
                                    func_body = "\n".join(lines[func_start : min(func_start + 20, len(lines))])
                                    # Check for logging statements
                                    if "logger." not in func_body and "logging." not in func_body:
                                        issues.append(
                                            {
                                                "file": filename,
                                                "function": critical_func,
                                                "type": "missing_logging",
                                            }
                                        )

                    except Exception as e:
                        pass

            result.details = {
                "critical_files_checked": len(critical_files),
                "missing_logging": len(issues),
                "issues": issues,
            }

            if issues:
                result.status = TaskStatus.FAILED
                result.output = f"Logging: {len(issues)} critical functions lack logging"
                result.error_message = f"Missing logging in: {', '.join([i['function'] for i in issues[:3]])}"
            else:
                result.status = TaskStatus.SUCCESS
                result.output = f"Logging verified: all {len(critical_files)} critical files have proper logging"

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"Logging check failed: {str(e)}"
        return result

    def execute_guardian_e2e(self) -> TaskResult:
        """Task: Guardian E2E tests (run actual pytest tests)."""
        result = TaskResult("task_16_guardian_e2e", "Guardian E2E", TaskStatus.PENDING)
        try:
            # Look for Guardian tests
            test_files = [
                Path("tests/integration/test_guardian*.py"),
                Path("tests/test_guardian*.py"),
            ]

            found_tests = []
            for pattern in test_files:
                found_tests.extend(Path(".").glob(str(pattern)))

            if not found_tests:
                result.status = TaskStatus.FAILED
                result.output = "Guardian E2E: No test files found"
                result.error_message = "Expected to find test_guardian*.py files in tests/"
                result.details = {"tests_found": 0}
                return result

            # Run pytest on Guardian tests
            cmd = [
                "python",
                "-m",
                "pytest",
                *[str(f) for f in found_tests],
                "-v",
                "--tb=short",
                "-x",
            ]

            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            # Parse output
            output = proc.stdout + proc.stderr
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")
            errors = output.count(" ERROR")

            result.details = {
                "test_files": len(found_tests),
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "return_code": proc.returncode,
            }

            if proc.returncode == 0:
                result.status = TaskStatus.SUCCESS
                result.output = f"Guardian E2E: {passed} tests passed"
            else:
                result.status = TaskStatus.FAILED
                result.output = f"Guardian E2E: {failed} failed, {errors} errors"
                result.error_message = output[-500:] if len(output) > 500 else output

        except subprocess.TimeoutExpired:
            result.status = TaskStatus.FAILED
            result.error_message = "Guardian E2E tests timed out (>2 minutes)"
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"Guardian E2E failed: {str(e)}"
        return result

    def execute_api_validation(self) -> TaskResult:
        """Task: API endpoint validation (check endpoint definitions)."""
        result = TaskResult("task_20_api_endpoints", "API Validation", TaskStatus.PENDING)
        try:
            # Check main.py for FastAPI routes
            main_file = Path("backend/api/main.py")
            if not main_file.exists():
                result.status = TaskStatus.FAILED
                result.output = "API validation: main.py not found"
                result.details = {"endpoints_found": 0}
                return result

            content = main_file.read_text()

            # Count route decorators
            endpoints = {
                "GET": len(re.findall(r"@app\.get", content)),
                "POST": len(re.findall(r"@app\.post", content)),
                "PUT": len(re.findall(r"@app\.put", content)),
                "DELETE": len(re.findall(r"@app\.delete", content)),
                "PATCH": len(re.findall(r"@app\.patch", content)),
            }

            total_endpoints = sum(endpoints.values())

            # Check for common issues
            issues = []

            # Check if endpoints have proper response codes
            if "@responses" not in content:
                issues.append("Missing @responses decorators for status codes")

            # Check for missing error handling
            if "HTTPException" not in content:
                issues.append("Missing HTTPException imports/usage")

            # Look for common anti-patterns
            for bad_pattern in ["print(", "time.sleep(", "eval(", "exec("]:
                if bad_pattern in content and "test" not in main_file.parent.name:
                    issues.append(f"Found {bad_pattern} in endpoints")

            result.details = {
                "endpoints": endpoints,
                "total_endpoints": total_endpoints,
                "issues": len(issues),
                "issue_list": issues,
            }

            if issues or total_endpoints == 0:
                result.status = TaskStatus.FAILED
                result.output = f"API validation: {total_endpoints} endpoints, {len(issues)} issues"
                result.error_message = "; ".join(issues[:3])
            else:
                result.status = TaskStatus.SUCCESS
                result.output = f"API validation: {total_endpoints} endpoints validated"

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"API validation failed: {str(e)}"
        return result

    def execute_production_readiness(self) -> TaskResult:
        """Task: Production module readiness (check critical modules)."""
        result = TaskResult("task_21_production_readiness", "Production Ready", TaskStatus.PENDING)
        try:
            critical_modules = [
                "backend/trading/bot_runner.py",
                "backend/api/main.py",
                "backend/trading/failover_monitor.py",
                "backend/trading/pre_trade_validator.py",
                "backend/monitoring/health_check.py",
                "backend/analytics/composite_signal.py",
            ]

            scores = {}
            for module_path in critical_modules:
                module = Path(module_path)
                if not module.exists():
                    scores[module.name] = 0
                    continue

                try:
                    content = module.read_text(encoding="utf-8")
                    lines = len(content.split("\n"))

                    score = 50  # Base score

                    # Check for logging
                    if "logger" in content or "logging" in content:
                        score += 10

                    # Check for error handling
                    if "except" in content:
                        score += 10

                    # Check for type hints
                    if "->" in content and "def " in content:
                        score += 10

                    # Check for docstrings
                    if '"""' in content:
                        score += 10

                    # Check for proper config usage
                    if "config" in content.lower():
                        score += 5

                    # Check file size (smaller is better for maintainability)
                    if lines < 500:
                        score += 5
                    elif lines > 1500:
                        score -= 5

                    scores[module.name] = min(100, score)

                except Exception as e:
                    scores[module.name] = 0

            avg_score = sum(scores.values()) // len(scores) if scores else 0
            low_scoring = [k for k, v in scores.items() if v < 70]

            result.details = {
                "modules_checked": len(critical_modules),
                "scores": scores,
                "average_score": avg_score,
                "low_scoring": low_scoring,
            }

            if low_scoring:
                result.status = TaskStatus.FAILED
                result.output = f"Production readiness: {avg_score}/100, {len(low_scoring)} modules need work"
                result.error_message = f"Low-scoring modules: {', '.join(low_scoring)}"
            else:
                result.status = TaskStatus.SUCCESS
                result.output = f"Production readiness: {avg_score}/100 average score"

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"Production readiness check failed: {str(e)}"
        return result

    def execute_type_hints(self) -> TaskResult:
        """Task: Type hints coverage (check function annotations)."""
        result = TaskResult("task_30_type_hints", "Type Hints", TaskStatus.PENDING)
        try:
            total_functions = 0
            functions_with_hints = 0
            files_without_hints = []

            for py_file in sorted(Path("backend").rglob("*.py"))[:50]:  # Sample first 50 files
                try:
                    content = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            total_functions += 1

                            # Check if function has return type hint
                            has_return_hint = node.returns is not None

                            # Check if all args have type hints
                            has_arg_hints = all(
                                arg.annotation is not None for arg in node.args.args if arg.arg != "self"
                            )

                            if has_return_hint and has_arg_hints:
                                functions_with_hints += 1
                            elif not has_return_hint and len(node.args.args) > 1:
                                if py_file.name not in files_without_hints:
                                    files_without_hints.append(py_file.name)

                except Exception as e:
                    pass

            coverage_pct = (functions_with_hints / total_functions * 100) if total_functions > 0 else 0

            result.details = {
                "total_functions": total_functions,
                "with_hints": functions_with_hints,
                "coverage_pct": round(coverage_pct, 1),
                "files_lacking_hints": files_without_hints[:10],
            }

            if coverage_pct < 70:
                result.status = TaskStatus.FAILED
                result.output = f"Type hints: {coverage_pct:.1f}% coverage (target: ≥70%)"
                result.error_message = f"{len(files_without_hints)} files lack type hints"
            else:
                result.status = TaskStatus.SUCCESS
                result.output = f"Type hints: {coverage_pct:.1f}% coverage"

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"Type hints check failed: {str(e)}"
        return result

    def execute_test_coverage(self) -> TaskResult:
        """Task: Test coverage check (run pytest with coverage)."""
        result = TaskResult("task_40_test_coverage", "Test Coverage", TaskStatus.PENDING)
        try:
            # Run pytest with coverage on critical paths
            cmd = [
                "python",
                "-m",
                "pytest",
                "tests/",
                "--cov=backend",
                "--cov-report=term-missing",
                "--quiet",
                "-x",
            ]

            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            output = proc.stdout + proc.stderr

            # Parse coverage percentage from output
            # Look for patterns like "TOTAL ... 85%"
            coverage_match = re.search(r"TOTAL\s+.*?(\d+)%", output)
            coverage_pct = int(coverage_match.group(1)) if coverage_match else 0

            # Count pass/fail
            passed = output.count(" passed")
            failed = output.count(" failed")
            errors = output.count(" error")

            result.details = {
                "coverage_pct": coverage_pct,
                "tests_passed": passed,
                "tests_failed": failed,
                "tests_error": errors,
                "return_code": proc.returncode,
            }

            if coverage_pct >= 75 and proc.returncode == 0:
                result.status = TaskStatus.SUCCESS
                result.output = f"Test coverage: {coverage_pct}%"
            elif coverage_pct >= 60:
                result.status = TaskStatus.FAILED
                result.output = f"Test coverage: {coverage_pct}% (target: ≥75%)"
                result.error_message = f"Coverage below target"
            else:
                result.status = TaskStatus.FAILED
                result.output = f"Test coverage: {coverage_pct}% (critical: <60%)"
                result.error_message = f"{failed} tests failed"

        except subprocess.TimeoutExpired:
            result.status = TaskStatus.FAILED
            result.error_message = "Test coverage check timed out (>3 minutes)"
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"Test coverage check failed: {str(e)}"
        return result

    def execute_documentation(self) -> TaskResult:
        """Task: Documentation completeness (check docstrings)."""
        result = TaskResult("task_50_documentation", "Documentation", TaskStatus.PENDING)
        try:
            files_with_docs = 0
            total_files = 0
            missing_docs = []

            for py_file in sorted(Path("backend").rglob("*.py"))[:100]:  # Sample 100 files
                total_files += 1
                try:
                    content = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(content)

                    # Check module docstring
                    module_has_doc = ast.get_docstring(tree) is not None

                    # Check class and function docstrings
                    docs_count = 0
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            if ast.get_docstring(node):
                                docs_count += 1

                    if module_has_doc or docs_count > 0:
                        files_with_docs += 1
                    else:
                        missing_docs.append(py_file.name)

                except Exception as e:
                    pass

            coverage_pct = (files_with_docs / total_files * 100) if total_files > 0 else 0

            result.details = {
                "files_checked": total_files,
                "files_documented": files_with_docs,
                "coverage_pct": round(coverage_pct, 1),
                "files_lacking_docs": missing_docs[:10],
            }

            if coverage_pct < 60:
                result.status = TaskStatus.FAILED
                result.output = f"Documentation: {coverage_pct:.1f}% files documented"
                result.error_message = f"{len(missing_docs)} files lack documentation"
            else:
                result.status = TaskStatus.SUCCESS
                result.output = f"Documentation: {coverage_pct:.1f}% complete"

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"Documentation check failed: {str(e)}"
        return result

    def execute_security_scan(self) -> TaskResult:
        """Task: Security scan (check for common vulnerabilities)."""
        result = TaskResult("task_60_security_scan", "Security Scan", TaskStatus.PENDING)
        try:
            issues = []

            # Security patterns to look for
            security_patterns = {
                "hardcoded_password": (r'password\s*=\s*["\']', "Hardcoded password"),
                "hardcoded_api_key": (r'api[_-]?key\s*=\s*["\']', "Hardcoded API key"),
                "sql_injection": (r"\.format\s*\(.*query", "Potential SQL injection"),
                "eval_usage": (r"\beval\s*\(", "Use of eval()"),
                "exec_usage": (r"\bexec\s*\(", "Use of exec()"),
                "hardcoded_secret": (r'secret\s*=\s*["\']', "Hardcoded secret"),
            }

            files_scanned = 0

            for py_file in Path("backend").rglob("*.py"):
                files_scanned += 1
                try:
                    content = py_file.read_text(encoding="utf-8")
                    lines = content.split("\n")

                    for i, line in enumerate(lines, 1):
                        # Skip comments
                        if line.strip().startswith("#"):
                            continue

                        for pattern_name, (
                            pattern,
                            description,
                        ) in security_patterns.items():
                            if re.search(pattern, line, re.IGNORECASE):
                                # Check if it's in a comment or string
                                if not line.strip().startswith("#"):
                                    issues.append(
                                        {
                                            "file": py_file.name,
                                            "line": i,
                                            "type": pattern_name,
                                            "description": description,
                                            "code": line.strip()[:60],
                                        }
                                    )

                except Exception as e:
                    pass

            # Check for requirements.txt for known vulnerable versions
            req_file = Path("requirements.txt")
            if req_file.exists():
                try:
                    reqs = req_file.read_text().split("\n")
                    # Basic check for pinning
                    unpinned = [r for r in reqs if r and not ("==" in r or ">=" in r)]
                    if len(unpinned) > 5:
                        issues.append(
                            {
                                "type": "unpinned_dependencies",
                                "description": f"{len(unpinned)} unpinned dependencies",
                                "count": len(unpinned),
                            }
                        )
                except Exception as e:
                    pass

            result.details = {
                "files_scanned": files_scanned,
                "issues_found": len(issues),
                "issues": issues[:10],
            }

            if issues:
                result.status = TaskStatus.FAILED
                result.output = f"Security: {len(issues)} issues found"
                result.error_message = f"Issues: {', '.join(set(i['type'] for i in issues))}"
            else:
                result.status = TaskStatus.SUCCESS
                result.output = f"Security scan: {files_scanned} files, 0 vulnerabilities"

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"Security scan failed: {str(e)}"
        return result

    def execute_task_group_parallel(self, task_group: Set[str], task_map: Dict[str, Dict]) -> Dict[str, TaskResult]:
        """
        Execute a group of independent tasks in parallel using threads.

        Args:
            task_group: Set of task IDs to execute in parallel
            task_map: Dict mapping task_id -> task definition

        Returns:
            Dict mapping task_id -> TaskResult
        """
        group_results = {}
        threads = []
        lock = threading.Lock()

        def execute_with_lock(task_id: str, task_def: Dict):
            """Execute task and store result with lock."""
            result = self.execute_task(task_def)
            with lock:
                group_results[task_id] = result

        # Spawn threads for each task in group
        for task_id in task_group:
            task_def = task_map[task_id]
            thread = threading.Thread(target=execute_with_lock, args=(task_id, task_def), daemon=False)
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=300)  # 5-minute timeout per task

        return group_results

    def execute_task(self, task_def: Dict) -> TaskResult:
        """Execute a single task with retry logic."""
        task_id = task_def["id"]
        task_name = task_def["name"]
        executor = task_def["executor"]

        for attempt in range(1, self.max_retries + 1):
            try:
                self.progress.log_status(f"Executing {task_name} (attempt {attempt}/{self.max_retries})")
                result = executor()
                result.attempts = attempt

                if result.status == TaskStatus.SUCCESS:
                    self.progress.log_status(f"✅ {task_name} PASSED")
                    return result
                elif result.status == TaskStatus.FAILED and attempt < self.max_retries:
                    self.progress.log_status(f"⚠️  {task_name} failed, retrying...")
                    time.sleep(0.1)
                    continue
                else:
                    return result

            except Exception as e:
                if attempt < self.max_retries:
                    self.progress.log_status(f"⚠️  Exception, retrying...")
                    time.sleep(0.1)
                    continue
                else:
                    result = TaskResult(task_id, task_name, TaskStatus.FAILED)
                    result.error_message = str(e)
                    result.attempts = attempt
                    return result

        result = TaskResult(task_id, task_name, TaskStatus.FAILED)
        result.error_message = "Max retries exceeded"
        return result

    def run(self) -> bool:
        """Run ALL tasks with parallel execution (Phase 2)."""
        print("\n" + "=" * 70)
        print("🚀 MASTER ORCHESTRATOR: Phase 1+2 Parallel Execution")
        print("=" * 70)

        start_time = time.time()
        self.register_tasks()

        # Phase 1: Create checkpoint
        print("\n[Phase 1] Creating execution checkpoint...")
        ckpt = self.rollback_mgr.create_checkpoint(
            CheckpointType.PRE_EXECUTION, "Master orchestrator parallel execution"
        )
        print(f"✅ Checkpoint created: {ckpt.checkpoint_id[:40]}")

        # Analyze parallelizability
        print("\n[Phase 2] Analyzing task dependencies...")
        groups = self.find_independent_groups()
        speedup, speedup_explain = self.estimate_speedup()
        print(f"   Found {len(groups)} independent phase(s)")
        print(f"   Estimated speedup: {speedup:.2f}x ({speedup_explain})")

        # Create task map for quick lookup
        task_map = {t["id"]: t for t in self.task_queue}

        # Execute each group in sequence, but tasks within groups in parallel
        total_executed = 0
        print(f"\n[Phase 2] Executing {len(self.task_queue)} tasks in parallel...\n")

        for phase_idx, task_group in enumerate(groups, 1):
            print(f"⏱️  Phase {phase_idx}: Executing {len(task_group)} parallel task(s)")
            print(f"   Tasks: {', '.join(sorted(task_group)[:3])}" + (f", ..." if len(task_group) > 3 else ""))

            # Execute group in parallel
            group_results = self.execute_task_group_parallel(task_group, task_map)

            # Store results
            for task_id, result in group_results.items():
                self.results[task_id] = result
                total_executed += 1

                status_icon = "✅" if result.status == TaskStatus.SUCCESS else "⚠️"
                print(f"   {status_icon} {result.task_name:40s}")

        print(f"\n✅ Executed {total_executed}/{len(self.task_queue)} tasks")

        # Final summary
        success_count = sum(1 for r in self.results.values() if r.status == TaskStatus.SUCCESS)
        failed_count = sum(1 for r in self.results.values() if r.status == TaskStatus.FAILED)
        elapsed = time.time() - start_time

        print("\n" + "=" * 70)
        print("📊 ORCHESTRATOR COMPLETE (Phase 1+2)")
        print("=" * 70)
        print(f"Total tasks:        {len(self.results)}")
        print(f"✅ Success:          {success_count}")
        print(f"⚠️  Failed:           {failed_count}")
        print(f"Success rate:       {success_count/len(self.results)*100:.1f}%")
        print(f"Execution time:     {elapsed:.1f}s")
        print(f"Parallel phases:    {len(groups)}")
        print(f"Estimated speedup:  {speedup:.2f}x")
        print("=" * 70)

        return True


def main():
    """Main entry point."""
    try:
        orchestrator = MasterOrchestrator()
        success = orchestrator.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
