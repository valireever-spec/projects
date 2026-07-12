#!/usr/bin/env python3
"""
Phase 1 Integration Test

Tests that all real integrations work together with Layer 1.
"""

import sys
import logging
from pathlib import Path
from orchestrator_layer1_state import ProjectAnalyzer, StateSnapshot, StateDiff, TaskType

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_phase1_integration():
    """End-to-end test of Phase 1 integration."""
    print("\n" + "=" * 80)
    print("PHASE 1 INTEGRATION TEST")
    print("=" * 80 + "\n")

    project = "/home/vali/projects/investing-platform"

    try:
        # Initialize analyzer
        print("1️⃣  Initializing ProjectAnalyzer...")
        analyzer = ProjectAnalyzer(project)
        print("   ✓ ProjectAnalyzer initialized\n")

        # Capture initial state
        print("2️⃣  Capturing initial project state...")
        state1 = analyzer.capture_state()
        print(f"   ✓ Files: {state1.total_files}")
        print(f"   ✓ Python files: {state1.metrics.get('python_files', 0)}")
        print(f"   ✓ Test files: {state1.metrics.get('test_files', 0)}")
        print(f"   ✓ Lines of code: {state1.total_lines:,}")
        print(f"   ✓ Tests passing: {state1.tests_passing}")
        print(f"   ✓ Tests failing: {state1.tests_failing}")
        print(f"   ✓ Coverage: {state1.coverage_percent:.1f}%")
        print(f"   ✓ File hashes computed: {len(state1.file_hashes)}")
        print(f"   ✓ Timestamp: {state1.timestamp}\n")

        # Verify state is valid
        assert state1.total_files > 0, "Should have files"
        assert len(state1.file_hashes) > 0, "Should have file hashes"
        assert state1.coverage_percent >= 0, "Coverage should be >= 0"
        print("   ✓ All assertions passed\n")

        # Print snapshot summary
        print("   📋 State Snapshot Summary:")
        summary = state1.summary()
        for key, value in summary.items():
            print(f"      {key}: {value}")
        print()

        # Simulate a file change (for testing - we won't actually change anything yet)
        print("3️⃣  Capturing state for comparison...")
        state2 = analyzer.capture_state()
        print(f"   ✓ Second state captured\n")

        # Compare states
        print("4️⃣  Comparing states...")
        diff = analyzer.compare_states(state1, state2)
        print(f"   ✓ Files changed: {len(diff.files_changed)}")
        print(f"   ✓ Files added: {len(diff.files_added)}")
        print(f"   ✓ Files deleted: {len(diff.files_deleted)}")
        print(f"   ✓ Coverage delta: {diff.coverage_delta:+.2f}%")
        print(f"   ✓ New passing tests: {len(diff.tests_new_passing)}")
        print(f"   ✓ New failing tests: {len(diff.tests_new_failing)}\n")

        # Check diff
        diff_summary = diff.summary()
        print("   📊 Diff Summary:")
        for key, value in diff_summary.items():
            print(f"      {key}: {value}")
        print()

        # Classify task
        print("5️⃣  Classifying task...")
        if diff.any_changes():
            task_type = TaskType.FIXED
            reason = "Code changes detected"
        else:
            task_type = TaskType.ANALYZED
            reason = "No code changes (state is stable)"

        print(f"   ✓ Task type: {task_type.value.upper()}")
        print(f"   ✓ Reason: {reason}\n")

        # Summary
        print("6️⃣  Verification Summary")
        print("   " + "=" * 76)
        print(f"   Before:  {state1.summary()['files']} files, "
              f"{state1.tests_passing} passing tests, "
              f"{state1.coverage_percent:.1f}% coverage")
        print(f"   After:   {state2.summary()['files']} files, "
              f"{state2.tests_passing} passing tests, "
              f"{state2.coverage_percent:.1f}% coverage")
        print(f"   Status:  {task_type.value.upper()}")
        print("   " + "=" * 76 + "\n")

        # Return success
        return True, "Phase 1 integration test PASSED ✓"

    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        return False, f"Phase 1 integration test FAILED: {e}"


if __name__ == "__main__":
    success, message = test_phase1_integration()
    print(f"\n{'✓' if success else '✗'} {message}\n")
    sys.exit(0 if success else 1)
