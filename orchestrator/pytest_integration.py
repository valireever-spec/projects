"""
Pytest Integration Module for Production Orchestrator - Phase 1

Provides real test execution and result collection.
"""

import logging
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    logger.warning("pytest not installed")


@dataclass
class TestResult:
    """Result of a single test."""
    test_name: str
    passed: bool
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    stdout: str = ""
    stderr: str = ""


@dataclass
class TestSuiteResult:
    """Results of test suite execution."""
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    tests_error: int = 0
    total_duration: float = 0.0
    test_results: List[TestResult] = field(default_factory=list)
    coverage_percent: float = 0.0
    errors: List[str] = field(default_factory=list)

    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.tests_run == 0:
            return 0.0
        return (self.tests_passed / self.tests_run) * 100

    def summary(self) -> Dict:
        """Get summary dictionary."""
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_failed,
            'tests_skipped': self.tests_skipped,
            'tests_error': self.tests_error,
            'success_rate': self.success_rate(),
            'total_duration': self.total_duration,
            'coverage_percent': self.coverage_percent,
        }


class PytestRunner:
    """Runs pytest tests and collects results."""

    def __init__(self, project_root: str, timeout_seconds: int = 300):
        """Initialize pytest runner.

        Args:
            project_root: Path to project root
            timeout_seconds: Timeout for test execution (default 5 min)
        """
        self.project_root = Path(project_root)
        self.timeout_seconds = timeout_seconds

        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {project_root}")

        logger.info(f"Initialized PytestRunner for {project_root}")

    def discover_tests(self, test_dir: str = "tests") -> List[str]:
        """Discover all tests in project.

        Args:
            test_dir: Directory to search for tests (relative to project root)

        Returns:
            List of test file paths
        """
        test_path = self.project_root / test_dir

        if not test_path.exists():
            logger.warning(f"Test directory not found: {test_dir}")
            return []

        test_files = []

        for test_file in test_path.glob("**/test_*.py"):
            try:
                rel_path = test_file.relative_to(self.project_root)
                test_files.append(str(rel_path))
            except ValueError:
                pass

        logger.info(f"Discovered {len(test_files)} test files")
        return sorted(test_files)

    def run_tests(self, test_pattern: Optional[str] = None, verbose: bool = False) -> TestSuiteResult:
        """Run tests and collect results.

        Args:
            test_pattern: Pattern to filter tests (e.g., "test_unit.py", "test_*integration*")
            verbose: Enable verbose output

        Returns:
            TestSuiteResult with all metrics
        """
        result = TestSuiteResult()

        try:
            # Build pytest arguments
            args = [
                str(self.project_root / "tests") if (self.project_root / "tests").exists() else str(self.project_root),
                "-v" if verbose else "-q",
                "--tb=short",
                "--junit-xml=/tmp/pytest_results.xml",
                "-x" if not verbose else "",  # Stop on first failure in quiet mode
            ]

            # Add pattern filter if provided
            if test_pattern:
                args.extend(["-k", test_pattern])

            # Run via subprocess for safety (timeout protection)
            try:
                proc_result = subprocess.run(
                    [sys.executable, "-m", "pytest"] + [a for a in args if a],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds
                )

                # Parse results from XML report
                return self._parse_junit_xml(proc_result.stdout, proc_result.stderr)

            except subprocess.TimeoutExpired:
                result.errors.append(f"Tests timed out after {self.timeout_seconds}s")
                logger.error(f"Test execution timed out")
                return result

        except Exception as e:
            result.errors.append(str(e))
            logger.error(f"Error running tests: {e}")
            return result

    def run_single_test(self, test_file: str) -> TestResult:
        """Run a single test file.

        Args:
            test_file: Path to test file (relative to project root)

        Returns:
            TestResult for that test
        """
        full_path = self.project_root / test_file

        if not full_path.exists():
            return TestResult(
                test_name=test_file,
                passed=False,
                error_message=f"Test file not found: {test_file}"
            )

        try:
            proc_result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse simple pass/fail
            passed = proc_result.returncode == 0

            return TestResult(
                test_name=test_file,
                passed=passed,
                error_message=proc_result.stderr if not passed else None,
                stdout=proc_result.stdout,
                stderr=proc_result.stderr
            )

        except subprocess.TimeoutExpired:
            return TestResult(
                test_name=test_file,
                passed=False,
                error_message="Test timed out"
            )
        except Exception as e:
            return TestResult(
                test_name=test_file,
                passed=False,
                error_message=str(e)
            )

    def _parse_junit_xml(self, stdout: str, stderr: str) -> TestSuiteResult:
        """Parse pytest JUnit XML output.

        Args:
            stdout: pytest stdout
            stderr: pytest stderr

        Returns:
            TestSuiteResult parsed from XML
        """
        result = TestSuiteResult()

        try:
            # Try to parse XML report
            xml_file = Path("/tmp/pytest_results.xml")

            if xml_file.exists():
                tree = ET.parse(xml_file)
                root = tree.getroot()

                # Extract stats from testsuite element
                if root.tag == "testsuites":
                    for testsuite in root.findall("testsuite"):
                        result._parse_testsuite_element(testsuite)
                elif root.tag == "testsuite":
                    result._parse_testsuite_element(root)

            # If XML parsing didn't work, try to parse text output
            if result.tests_run == 0:
                result = self._parse_text_output(stdout, stderr)

            return result

        except Exception as e:
            logger.warning(f"Could not parse test results: {e}")
            return self._parse_text_output(stdout, stderr)

    def _parse_text_output(self, stdout: str, stderr: str) -> TestSuiteResult:
        """Parse pytest text output as fallback.

        Args:
            stdout: pytest stdout
            stderr: pytest stderr

        Returns:
            TestSuiteResult parsed from text
        """
        result = TestSuiteResult()

        # Look for pytest summary line
        for line in (stdout + stderr).split('\n'):
            if 'passed' in line or 'failed' in line:
                # Parse lines like: "10 passed, 2 failed in 0.50s"
                parts = line.split()

                for i, part in enumerate(parts):
                    if part == 'passed':
                        try:
                            result.tests_passed = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'failed':
                        try:
                            result.tests_failed = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'skipped':
                        try:
                            result.tests_skipped = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'error' or part == 'errors':
                        try:
                            result.tests_error = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass

        result.tests_run = result.tests_passed + result.tests_failed + result.tests_skipped + result.tests_error

        return result


# Extend TestSuiteResult for parsing
def _parse_testsuite_element(self, testsuite):
    """Parse a testsuite XML element."""
    try:
        self.tests_run = int(testsuite.get('tests', 0))
        failures = int(testsuite.get('failures', 0))
        errors = int(testsuite.get('errors', 0))
        skipped = int(testsuite.get('skipped', 0))

        self.tests_failed = failures
        self.tests_error = errors
        self.tests_skipped = skipped
        self.tests_passed = self.tests_run - failures - errors - skipped

        # Try to get duration
        try:
            self.total_duration = float(testsuite.get('time', 0))
        except (ValueError, TypeError):
            self.total_duration = 0.0

    except Exception as e:
        logger.warning(f"Could not parse testsuite element: {e}")


TestSuiteResult._parse_testsuite_element = _parse_testsuite_element


# Test module usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "/home/vali/projects/investing-platform"

    logging.basicConfig(level=logging.INFO)

    try:
        runner = PytestRunner(project_path, timeout_seconds=60)

        print(f"✓ Project: {project_path}")

        # Discover tests
        tests = runner.discover_tests()
        print(f"✓ Discovered {len(tests)} test files")

        # Run a sample of tests
        if len(tests) > 0:
            print(f"✓ Running test: {tests[0]}")
            single_result = runner.run_single_test(tests[0])
            print(f"  - Passed: {single_result.passed}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
