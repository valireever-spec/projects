# Orchestrator Systems Integrator: Command Interface & Workflow

## Overview

Use the orchestrator to coordinate design, implement, troubleshoot, verify, and validate OTHER PROJECTS as a systems integrator.

---

## Core Command Structure

```bash
orchestrator <action> <project> [--phase <phase>] [--config <config>] [--verify] [--rollback]
```

### Actions
- `design` - Analyze and design project improvements
- `implement` - Apply design changes and fixes
- `troubleshoot` - Diagnose and fix issues
- `verify` - Confirm solutions work
- `validate` - Validate against requirements/framework
- `coordinate` - Manage multiple projects
- `report` - Generate status reports

---

## 1. DESIGN PROJECT

### Command: Analyze & Design

```bash
# Analyze a project and generate design recommendations
orchestrator design <project-path> \
  --framework 8-pillar \
  --output design-report.md \
  --depth detailed
```

**What it does:**
- Scans project structure
- Analyzes architecture against 8-pillar framework
- Identifies gaps, risks, improvement opportunities
- Generates design recommendations
- Creates before-state snapshot

**Example:**
```bash
orchestrator design /home/vali/projects/lotto-sh \
  --framework 8-pillar \
  --output reports/lotto-design.md \
  --depth detailed

# Output:
# ✓ Project scanned (47 files, 12K LOC)
# ✓ Architecture analyzed
# ✓ Gaps identified (3 critical, 5 medium, 2 low)
# ✓ Design report generated: reports/lotto-design.md
```

### Command: Generate Improvement Plan

```bash
# Create implementation plan with phases and effort estimates
orchestrator design <project-path> \
  --generate-plan \
  --effort-estimation \
  --risk-assessment \
  --output improvement-plan.yaml
```

**Example:**
```bash
orchestrator design /home/vali/projects/crypto-daytrading \
  --generate-plan \
  --effort-estimation \
  --risk-assessment \
  --output improvement-plan.yaml

# Output generates improvement-plan.yaml:
# phases:
#   - name: "Fix exception handling"
#     effort_hours: 4
#     risk: low
#     files_affected: 23
#   - name: "Add type hints"
#     effort_hours: 8
#     risk: low
#     files_affected: 45
```

### Command: Compare Against Framework

```bash
# Score project against architecture framework
orchestrator design <project-path> \
  --score 8-pillar \
  --detailed \
  --gaps-only
```

**Example:**
```bash
orchestrator design /home/vali/projects/skill-creator \
  --score 8-pillar \
  --detailed

# Output:
# Pillar 1 (Architecture):        6/10 [====.....]  Gaps: No ADRs, circular deps
# Pillar 2 (Build Quality):       7/10 [====......]  Gaps: Missing type hints
# Pillar 3 (Verification):        5/10 [===.......]  Gaps: No integration tests
# Pillar 4 (CI/CD):               8/10 [=====.....]  Gaps: No rollback plan
# ...
# Overall Score: 6.5/10
```

---

## 2. IMPLEMENT PROJECT

### Command: Apply Fixes

```bash
# Execute implementation plan atomically
orchestrator implement <project-path> \
  --plan improvement-plan.yaml \
  --verify \
  --rollback-on-failure \
  --dry-run
```

**Workflow:**
1. Reads improvement plan
2. Creates backup
3. Executes changes atomically
4. Runs verification tests
5. Creates after-state snapshot
6. Reports results

**Example:**
```bash
# Preview changes first
orchestrator implement /home/vali/projects/lotto-sh \
  --plan improvement-plan.yaml \
  --dry-run

# Then execute
orchestrator implement /home/vali/projects/lotto-sh \
  --plan improvement-plan.yaml \
  --verify \
  --rollback-on-failure

# Output:
# ✓ Backup created: backups/lotto-sh_2026-07-13.tar.gz
# ✓ Phase 1: Exception handling (23 files)
#   - Replaced except Exception: patterns
#   - All tests passing
# ✓ Phase 2: Type hints (45 files)
#   - Added hints to critical functions
#   - MyPy score: 65% → 82%
# ✓ All changes applied successfully
# ✓ Backup: backups/lotto-sh_2026-07-13.tar.gz (retained)
```

### Command: Apply Specific Fix

```bash
# Apply single improvement without full plan
orchestrator implement <project-path> \
  --fix <fix-name> \
  --verify \
  --commit
```

**Example:**
```bash
orchestrator implement /home/vali/projects/network-automation \
  --fix "add-exception-handling" \
  --verify \
  --commit

# Output:
# ✓ Fix: add-exception-handling
# ✓ Applied to: 18 files
# ✓ Tests passing: 234/234
# ✓ Committed: abcd1234 "Fix: Add exception handling to network automation"
```

### Command: Refactor Code

```bash
# Perform complex refactoring (consolidate files, improve structure)
orchestrator implement <project-path> \
  --refactor <refactor-plan> \
  --analyze-dependencies \
  --verify \
  --rollback-on-failure
```

**Example:**
```bash
orchestrator implement /home/vali/projects/youtube-scraper \
  --refactor "consolidate-scraper-modules" \
  --analyze-dependencies \
  --verify \
  --rollback-on-failure

# Output:
# ✓ Dependency analysis: 12 files, 34 imports
# ✓ Consolidation plan:
#   - Merge scraper.py + scraper_core.py → scraper_unified.py
#   - Update 8 importers
#   - Verify 45 tests
# ✓ Executing consolidation...
# ✓ All tests passing (45/45)
# ✓ Refactoring complete
# ✓ Code metrics improved: Complexity 8.2 → 6.1
```

---

## 3. TROUBLESHOOT PROJECT

### Command: Diagnose Issues

```bash
# Scan project for issues and problems
orchestrator troubleshoot <project-path> \
  --deep-scan \
  --identify-root-causes \
  --suggest-fixes
```

**Identifies:**
- Build failures and compilation errors
- Test failures and flaky tests
- Performance issues and bottlenecks
- Security vulnerabilities
- Code quality issues
- Architecture problems

**Example:**
```bash
orchestrator troubleshoot /home/vali/projects/crypto-daytrading \
  --deep-scan \
  --identify-root-causes \
  --suggest-fixes

# Output:
# ISSUES FOUND:
# 
# 🔴 CRITICAL (3):
#   1. Circular import: market_data → analyzer → market_data
#      Root cause: Missing abstraction layer
#      Fix: Create data_interface.py
#   
#   2. Memory leak in WebSocket handler
#      Root cause: Unclosed connections on error
#      Fix: Add finally block to close connections
#   
#   3. Test data in production database
#      Root cause: Migration script didn't clean up
#      Fix: Run cleanup migration
#
# 🟡 WARNING (5):
#   4. Type hints only 42% coverage
#   5. No error handling in signal processor
#   ...
```

### Command: Root Cause Analysis

```bash
# Deep dive into specific issue
orchestrator troubleshoot <project-path> \
  --issue <issue-id> \
  --trace-dependencies \
  --show-impact
```

**Example:**
```bash
orchestrator troubleshoot /home/vali/projects/investing-platform \
  --issue "data-staleness" \
  --trace-dependencies \
  --show-impact

# Output:
# ISSUE: Data Staleness
# 
# ROOT CAUSE:
#   backend/core/data_refresh_scheduler.py:_trigger_refresh()
#   - Line 45: Function body is empty
#   - Never calls fallback data provider chain
#   - Symbols stuck at old data
#
# IMPACT:
#   - 90% of trades blocked by data quality gate
#   - Affects: 63 symbols in portfolio
#   - Severity: CRITICAL
#
# DEPENDENCIES:
#   Callers: bot_runner.py, signal_manager.py
#   Callees: data_provider.py, yfinance.py
#
# SUGGESTED FIX:
#   Implement _trigger_refresh() to call get_candles()
#   with fallback: Polygon → AlphaVantage → Twelve Data → yfinance
```

### Command: Fix Issues Automatically

```bash
# Automatically fix identified issues
orchestrator troubleshoot <project-path> \
  --auto-fix \
  --severity <critical|warning|all> \
  --verify
```

**Example:**
```bash
orchestrator troubleshoot /home/vali/projects/lotto-sh \
  --auto-fix \
  --severity critical \
  --verify

# Output:
# ✓ Found 3 critical issues
# ✓ Auto-fixing...
#   [1/3] Circular import: market_data → analyzer
#         → Created abstraction layer
#         → Updated imports
#   [2/3] Memory leak in WebSocket handler
#         → Added finally block
#         → Connection cleanup verified
#   [3/3] Test data in database
#         → Ran cleanup migration
#         → Verified removal
# ✓ All critical issues fixed
# ✓ Tests: 234/234 passing
```

---

## 4. VERIFY PROJECT

### Command: Run Verification Tests

```bash
# Verify solutions work and don't cause regressions
orchestrator verify <project-path> \
  --tests <unit|integration|e2e|all> \
  --coverage-threshold 80 \
  --regression-detection
```

**Tests:**
- Unit tests (fast, isolated)
- Integration tests (real dependencies)
- E2E tests (full workflows)
- Performance tests (latency, throughput)
- Architecture tests (structure, coupling)

**Example:**
```bash
orchestrator verify /home/vali/projects/investing-platform \
  --tests all \
  --coverage-threshold 80 \
  --regression-detection

# Output:
# UNIT TESTS:              234/234 passing ✓ (100%)
# INTEGRATION TESTS:        89/89 passing  ✓ (100%)
# E2E TESTS:               45/45 passing   ✓ (100%)
# PERFORMANCE TESTS:       All within threshold ✓
#   - Signal latency:      95ms (target: <100ms)
#   - Trade execution:     850ms (target: <1s)
#   - Failover detection:  8s (target: <10s)
#
# CODE COVERAGE:           82% ✓ (target: 80%)
#   - backend/trading:     89%
#   - backend/signals:     76%
#   - backend/core:        81%
#
# REGRESSION DETECTION:
#   - Before state: 234 tests passing
#   - After state:  234 tests passing
#   - Regressions:  NONE ✓
#
# RESULT: ✅ ALL VERIFICATIONS PASSED
```

### Command: Specific Component Verification

```bash
# Verify specific component works
orchestrator verify <project-path> \
  --component <component-path> \
  --test-scenarios <scenario-file>
```

**Example:**
```bash
orchestrator verify /home/vali/projects/investing-platform \
  --component backend/trading/bot_runner.py \
  --test-scenarios test-scenarios/bot_runner.yaml

# Output:
# Testing: backend/trading/bot_runner.py
# 
# Scenario 1: Initialize bot with paper trading
#   ✓ Bot instantiation: 25ms
#   ✓ All components initialized
#   ✓ HA monitoring armed
#
# Scenario 2: Execute trade with validation
#   ✓ Signal validation: 120ms
#   ✓ Risk checks: 380ms
#   ✓ Trade execution: 850ms
#   ✓ Fill tracking: 200ms
#
# Scenario 3: Failover detection
#   ✓ Primary health check: 10s
#   ✓ Backup promotion: <2s
#   ✓ State synchronization: <1s
#
# RESULT: ✅ ALL SCENARIOS PASSED
```

### Command: Before/After Comparison

```bash
# Compare state before/after changes
orchestrator verify <project-path> \
  --compare-snapshots \
  --before snapshot_before.json \
  --after snapshot_after.json \
  --show-diffs
```

**Example:**
```bash
orchestrator verify /home/vali/projects/network-automation \
  --compare-snapshots \
  --before checkpoints/before.json \
  --after checkpoints/after.json \
  --show-diffs

# Output:
# BEFORE/AFTER COMPARISON
# 
# Code Metrics:
#   Lines of Code:         2340 → 2180 (↓ 6.8%)
#   Cyclomatic Complexity: 8.2 → 6.1 (↓ 25.6%)
#   File count:            47 → 42 (↓ 10.6%, consolidation)
#
# Test Results:
#   Tests passing:         198/198 → 234/234 (↑ 18%)
#   Coverage:              71% → 82% (↑ 15.5%)
#   Failures:              2 → 0 (✓ fixed)
#
# Performance:
#   API response time:     450ms → 320ms (↓ 28.9%)
#   Test suite runtime:    8.2s → 5.1s (↓ 37.8%)
#
# Architecture:
#   Circular deps:         3 → 0 (✓ fixed)
#   High coupling:         8 modules → 2 modules (↓ 75%)
#   Architecture score:    6.5/10 → 8.2/10
#
# RESULT: ✅ ALL METRICS IMPROVED
```

---

## 5. VALIDATE PROJECT

### Command: Validate Against Framework

```bash
# Validate project meets 8-pillar framework requirements
orchestrator validate <project-path> \
  --framework 8-pillar \
  --strict \
  --generate-report
```

**All 8 Pillars:**
1. Architecture Discipline & Traceability
2. Build Quality In / Error-Proofing
3. Verification & Validation
4. CI/CD & Safe Delivery
5. Root-Cause Driven Improvement
6. Security & Privacy by Design
7. Observability & Telemetry
8. Maintainability & Sustainable Pace

**Example:**
```bash
orchestrator validate /home/vali/projects/investing-platform \
  --framework 8-pillar \
  --strict \
  --generate-report

# Output:
# VALIDATING AGAINST 8-PILLAR FRAMEWORK
# ═══════════════════════════════════════════════════════════════
#
# ✅ Pillar 1: Architecture Discipline & Traceability    8.2/10
#    ✓ Design documented (ADRs)
#    ✓ Module boundaries clear
#    ✓ No circular dependencies
#    ⚠ Missing: Deployment architecture docs
#
# ✅ Pillar 2: Build Quality In                          8.5/10
#    ✓ Type hints: 85% coverage
#    ✓ No secrets in code
#    ✓ Linting: All passing
#    ✓ Dependencies pinned
#
# ✅ Pillar 3: Verification & Validation                 8.0/10
#    ✓ Unit tests: 234/234 passing (100%)
#    ✓ Integration tests: 89/89 passing (100%)
#    ✓ Coverage: 82% (target: 80%)
#    ✓ No flaky tests
#
# ✅ Pillar 4: CI/CD & Safe Delivery                     8.5/10
#    ✓ Automated gates working
#    ✓ Reversible migrations
#    ✓ Health checks on deployment
#    ⚠ Rollback procedure needs documentation
#
# ✅ Pillar 5: Root-Cause Driven Improvement             7.5/10
#    ✓ Post-mortems documented
#    ✓ Patterns extracted
#    ⚠ Tech debt tracking incomplete
#
# ✅ Pillar 6: Security & Privacy by Design              8.0/10
#    ✓ No hardcoded secrets
#    ✓ Input validation: 95%
#    ✓ CVE scanning: Active
#    ⚠ Permission model incomplete
#
# ✅ Pillar 7: Observability & Telemetry                 7.5/10
#    ✓ Structured logging
#    ✓ SLOs defined
#    ⚠ Dashboards: Partial
#    ⚠ Runbooks: Incomplete
#
# ✅ Pillar 8: Maintainability & Sustainable Pace        8.0/10
#    ✓ Domain naming consistent
#    ✓ No files >500 lines
#    ✓ Dead code: 0%
#    ⚠ Some justified dependencies missing docs
#
# ═══════════════════════════════════════════════════════════════
# OVERALL SCORE: 8.1/10 ✅ PRODUCTION READY
# 
# Report generated: validation-report.html
```

### Command: Validate Against Custom Requirements

```bash
# Validate against custom requirements file
orchestrator validate <project-path> \
  --requirements requirements.yaml \
  --strict
```

**Example requirements.yaml:**
```yaml
requirements:
  code_quality:
    type_hints_coverage: ">= 80%"
    test_coverage: ">= 80%"
    linting: "must_pass"
  architecture:
    circular_dependencies: "== 0"
    high_coupling_modules: "< 3"
  performance:
    signal_latency: "< 100ms"
    trade_execution: "< 1s"
  security:
    secrets_in_code: "== 0"
    vulnerable_dependencies: "== 0"
```

---

## 6. COORDINATE MULTIPLE PROJECTS

### Command: Monitor Multiple Projects

```bash
# Track status of multiple projects simultaneously
orchestrator coordinate \
  --projects project1,project2,project3,project4 \
  --parallel 4 \
  --report-interval 5m
```

**Example:**
```bash
orchestrator coordinate \
  --projects lotto-sh,crypto-daytrading,skill-creator,network-automation,youtube-scraper \
  --parallel 5 \
  --report-interval 5m

# Real-time status:
# lotto-sh:              [Design] ████████░░ 85% (2h remaining)
# crypto-daytrading:     [Implement] ██████░░░░ 60% (4h remaining)
# skill-creator:         [Verify] ███░░░░░░░ 30% (1h remaining)
# network-automation:    [Validate] ████████░░ 80% (30m remaining)
# youtube-scraper:       [Complete] ██████████ 100% ✓
```

### Command: Orchestrate Workflow Across Projects

```bash
# Execute coordinated workflow across projects
orchestrator coordinate \
  --workflow project-improvement.yaml \
  --parallel 3 \
  --dependencies respect
```

**Example workflow.yaml:**
```yaml
projects:
  - name: lotto-sh
    actions:
      - design --output reports/lotto-design.md
      - implement --plan improvement-plan.yaml
      - verify --tests all
      - validate --framework 8-pillar
  
  - name: crypto-daytrading
    depends_on: [lotto-sh]  # Wait for lotto-sh to complete
    actions:
      - design
      - implement
      - verify
      - validate
  
  - name: skill-creator
    actions:
      - design
      - implement
      - verify
      - validate
```

**Example execution:**
```bash
orchestrator coordinate \
  --workflow improvement-workflow.yaml \
  --parallel 3 \
  --dependencies respect \
  --report-dir reports/

# Output:
# ORCHESTRATING WORKFLOW: project-improvement.yaml
# ═══════════════════════════════════════════════════════════════
#
# [1/5] lotto-sh: Design
#   ✓ Architecture analyzed
#   ✓ Design report: reports/lotto-design.md
#
# [2/5] lotto-sh: Implement
#   ✓ Changes applied (23 files)
#   ✓ Backup created
#
# [3/5] lotto-sh: Verify
#   ✓ All tests passing (198/198)
#
# [4/5] lotto-sh: Validate
#   ✓ Architecture score: 8.2/10
#
# [5/5] crypto-daytrading: Design (starting, depends on lotto-sh)
#   ✓ Architecture analyzed
#
# [Parallel: skill-creator, network-automation] Running...
#
# PROGRESS: 5/20 actions complete (25%)
# ETA: 2h 15m
```

---

## 7. GENERATE REPORTS

### Command: Status Report

```bash
# Generate status report for project(s)
orchestrator report \
  --project <project-path> \
  --type status|detailed|executive \
  --output report.html
```

**Example:**
```bash
orchestrator report \
  --project /home/vali/projects/investing-platform \
  --type executive \
  --output reports/investing-platform-status.html

# Generates:
# - Executive Summary
# - Architecture Score Card
# - Test Coverage Analysis
# - Performance Metrics
# - Risk Assessment
# - Recommendations
```

### Command: Comparison Report

```bash
# Compare multiple projects
orchestrator report \
  --compare lotto-sh,crypto-daytrading,skill-creator \
  --metric architecture-score,test-coverage,code-quality \
  --output comparison-report.html
```

---

## 8. COMPLETE WORKFLOW EXAMPLE

### Full Systems Integration Cycle

```bash
# Step 1: Design all projects
orchestrator design /home/vali/projects/lotto-sh --output design1.md
orchestrator design /home/vali/projects/crypto-daytrading --output design2.md
orchestrator design /home/vali/projects/skill-creator --output design3.md

# Step 2: Review designs
# (Human review: analyze reports, prioritize improvements)

# Step 3: Implement improvements
orchestrator implement /home/vali/projects/lotto-sh \
  --plan improvement-plan.yaml \
  --verify \
  --rollback-on-failure

# Step 4: Troubleshoot any issues
orchestrator troubleshoot /home/vali/projects/lotto-sh \
  --deep-scan \
  --auto-fix critical

# Step 5: Verify solutions
orchestrator verify /home/vali/projects/lotto-sh \
  --tests all \
  --regression-detection

# Step 6: Validate against framework
orchestrator validate /home/vali/projects/lotto-sh \
  --framework 8-pillar \
  --strict

# Step 7: Generate final report
orchestrator report \
  --project /home/vali/projects/lotto-sh \
  --type detailed \
  --output final-report.html

# Step 8: Deploy improvements
orchestrator deploy \
  --project /home/vali/projects/lotto-sh \
  --strategy canary
```

---

## Command Quick Reference

```bash
# DESIGN
orchestrator design <path> [--output report.md] [--framework 8-pillar]
orchestrator design <path> --generate-plan [--effort-estimation]
orchestrator design <path> --score 8-pillar [--detailed]

# IMPLEMENT
orchestrator implement <path> --plan plan.yaml [--dry-run] [--verify]
orchestrator implement <path> --fix <fix-name> [--commit]
orchestrator implement <path> --refactor <plan> [--verify]

# TROUBLESHOOT
orchestrator troubleshoot <path> [--deep-scan] [--suggest-fixes]
orchestrator troubleshoot <path> --issue <issue-id> [--trace-dependencies]
orchestrator troubleshoot <path> --auto-fix [--severity critical]

# VERIFY
orchestrator verify <path> --tests <unit|integration|e2e|all>
orchestrator verify <path> --component <path> --test-scenarios <file>
orchestrator verify <path> --compare-snapshots --before <b> --after <a>

# VALIDATE
orchestrator validate <path> --framework 8-pillar [--strict]
orchestrator validate <path> --requirements requirements.yaml

# COORDINATE
orchestrator coordinate --projects proj1,proj2,proj3 [--parallel 3]
orchestrator coordinate --workflow workflow.yaml [--parallel 3]

# REPORT
orchestrator report --project <path> --type <status|detailed|executive>
orchestrator report --compare proj1,proj2 --metric <metrics>
```

---

## Configuration Files

### Improvement Plan (YAML)
```yaml
phases:
  - name: Phase 1
    effort_hours: 4
    files_affected: 23
    acceptance_criteria:
      - All tests passing
      - No regressions
```

### Test Scenarios (YAML)
```yaml
scenarios:
  - name: "Scenario 1"
    setup: "Initialize bot"
    steps:
      - action: "create_bot"
      - action: "verify_initialization"
    expected_result: "Bot ready to trade"
```

### Workflow (YAML)
```yaml
projects:
  - name: project1
    actions:
      - design
      - implement
      - verify
      - validate
```

---

## Usage Examples by Role

### Project Manager
```bash
# Track multiple projects
orchestrator coordinate --projects proj1,proj2,proj3 \
  --report-interval 30m
```

### Systems Architect
```bash
# Design improvements
orchestrator design /path/to/project \
  --framework 8-pillar \
  --generate-plan \
  --effort-estimation
```

### DevOps Engineer
```bash
# Implement and verify
orchestrator implement /path/to/project \
  --plan plan.yaml \
  --verify

orchestrator verify /path/to/project --tests all
```

### QA Engineer
```bash
# Comprehensive testing
orchestrator verify /path/to/project \
  --tests all \
  --regression-detection \
  --coverage-threshold 80
```

### Compliance Officer
```bash
# Validate against requirements
orchestrator validate /path/to/project \
  --requirements compliance.yaml \
  --strict \
  --generate-report
```

