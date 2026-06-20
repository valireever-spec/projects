# Non-Functional Requirements: testing-validation-platform

Specification of system qualities: performance, reliability, security, maintainability for the V-Model tracker.

---

## Overview

**Project:** testing-validation-platform  
**Tech Stack:** Python FastAPI, Requests HTTP client  
**Tier:** Internal tool (low criticality vs production systems)

---

## Performance Requirements

### NFR-001: Requirement Sync Performance

**ID:** NFR-001  
**Category:** Performance  
**Related Requirement:** FR-001, FR-002

### Specification

**Requirement:** Requirement sync from files to tracker must complete quickly to enable frequent updates.

**Measurement Method:**
```bash
time python vmodel_sync.py sync
# Or monitor /api/vmodel/board endpoint response time
```

**Target:**
- Typical sync (50–100 requirements): <30 seconds
- Sync for 200+ requirements: <60 seconds
- API response time (GET /api/vmodel/board): <500ms (p99)

**Alert Threshold:**
- Warning: Sync takes >45 seconds
- Critical: Sync takes >90 seconds

**Test Case:**
```python
def test_sync_performance():
    import time
    start = time.time()
    vmodel_sync.sync_requirements()
    elapsed = time.time() - start
    assert elapsed < 30  # 30 second target
```

### Rationale

Developers run sync frequently to keep tracker current. <30s keeps feedback loop tight.

### Related Pillar

- **Pillar 4 — Continuous Integration**: Fast feedback enables safe iteration
- **Pillar 7 — Observability**: Monitor sync latency as system health metric

---

### NFR-002: API Response Time

**ID:** NFR-002  
**Category:** Performance  
**Related Requirement:** FR-003

**Target:**
- Dashboard page load: <2 seconds
- /api/vmodel/board endpoint: <500ms (p99)
- /health check: <100ms

**Alert Threshold:**
- Warning: API response >750ms
- Critical: API response >2 seconds

**Measurement:**
```bash
time curl http://localhost:8004/api/vmodel/board
```

---

## Reliability Requirements

### NFR-003: Tracker Availability Tolerance

**ID:** NFR-003  
**Category:** Reliability  
**Related Requirement:** FR-001, FR-002, FR-004

### Specification

**Requirement:** System must degrade gracefully when tracker is unavailable; retries are automatic.

**Target:**
- Sync retries on failure: 3 attempts with exponential backoff
- Retry delay: 2s, 4s, 8s (exponential)
- If all retries fail: log error, skip this sync cycle, try again next cycle
- Dashboard shows "last sync: [time]" so user knows staleness

**Test Case:**
```python
def test_sync_resilience_tracker_down():
    # Mock tracker as unavailable
    with patch('requests.post') as mock_post:
        mock_post.side_effect = ConnectionError("Tracker down")
        
        # Should retry 3x, then fail gracefully
        vmodel_sync.sync_requirements()
        
        assert mock_post.call_count >= 3  # At least 3 retries
        assert log_contains("Failed to sync after 3 attempts")
```

**Alert Threshold:**
- Warning: Sync fails 2x in a row
- Critical: Sync fails 5x in a row (>25 minutes without sync)

---

### NFR-004: Data Consistency

**ID:** NFR-004  
**Category:** Reliability  
**Related Requirement:** FR-002

**Target:**
- V_MODEL_BOARD.md matches tracker data within 5 minutes
- No data loss when syncing
- All requirement IDs unique (no duplicates in tracker)

**Measurement:**
```python
def test_data_consistency():
    # Sync data to tracker
    # Wait 5 minutes
    # Query tracker
    # Verify: all requirements present, no duplicates
```

---

## Maintainability Requirements

### NFR-005: Type Hint Coverage

**ID:** NFR-005  
**Category:** Maintainability  
**Related Requirement:** All

**Target:**
- ≥90% of functions have complete type hints
- mypy --strict passes with zero errors
- Type hints verified in CI

**Measurement:**
```bash
mypy backend/ --strict
# Should exit with 0 errors
```

**Test Case:**
```bash
# In CI:
mypy backend/ --strict || exit 1
```

---

### NFR-006: Test Coverage

**ID:** NFR-006  
**Category:** Maintainability / Verification  
**Related Requirement:** All

**Target:**
- ≥80% code coverage (measured by pytest-cov)
- 100% coverage on critical paths:
  - tracker_client.py: report_bug(), update_bug_status(), mark_bug_fixed()
  - vmodel_sync.py: sync_requirements(), generate_vmodel_board()
- All critical code paths have integration tests

**Measurement:**
```bash
pytest tests/ --cov=backend --cov-report=html
# Open htmlcov/index.html to view coverage
```

**Alert Threshold:**
- Warning: Coverage drops below 80%
- Critical: Coverage drops below 75%

---

### NFR-007: Code Complexity Bounds

**ID:** NFR-007  
**Category:** Maintainability  
**Related Requirement:** All

**Target:**
- Cyclomatic complexity: <15 per function
- File size: <500 lines (soft limit)
- No function >50 lines

**Measurement:**
```bash
radon cc backend/ -s -a
# Should show all functions with CC <15
```

---

### NFR-008: Documentation Completeness

**ID:** NFR-008  
**Category:** Maintainability  
**Related Requirement:** All

**Target:**
- README.md: Explains purpose, architecture, quick start
- Every public function has docstring (mandatory)
- Docstrings explain intent, parameters, return value
- Complex logic has inline comments explaining "why" not "what"

**Measurement:**
```bash
pydocstyle backend/ --match-dir='backend'
# Should have 0 missing docstrings
```

---

## Security Requirements

### NFR-009: No Secrets in Code

**ID:** NFR-009  
**Category:** Security  
**Related Requirement:** All

**Target:**
- Zero API keys, passwords, tokens in git history
- All configuration via environment variables or .env (gitignored)
- Pre-commit hook checks for secrets

**Measurement:**
```bash
git log -p | grep -E "api.?key|password|token" || echo "✅ No secrets"
```

**Test Case:**
```bash
# In CI:
pip install git-secrets
git secrets --scan || exit 1
```

---

### NFR-010: Dependency Vulnerability Scanning

**ID:** NFR-010  
**Category:** Security  
**Related Requirement:** All

**Target:**
- Zero high/critical CVEs in dependencies
- Automated scanning on every dependency update
- Vulnerable deps are upgraded or replaced within 7 days

**Measurement:**
```bash
pip install safety
safety check
# Should show 0 vulnerabilities
```

---

### NFR-011: Input Validation

**ID:** NFR-011  
**Category:** Security  
**Related Requirement:** FR-001, FR-002, FR-004

**Target:**
- All tracker API responses validated with Pydantic models
- All markdown parsing guards against malformed input
- No crashes from unexpected data shapes

**Measurement:**
- Unit tests verify Pydantic validation
- Fuzzing tests with malformed inputs

---

## Correctness Requirements

### NFR-012: Requirement Sync Accuracy

**ID:** NFR-012  
**Category:** Correctness  
**Related Requirement:** FR-001, FR-002

**Target:**
- 100% of requirements in markdown files appear in tracker (no data loss)
- No duplicate requirements created
- Requirement properties (ID, title, status) preserved correctly

**Measurement:**
```python
def test_sync_accuracy():
    # Create 50 requirements in markdown
    # Run sync
    # Query tracker
    # Verify: exactly 50 requirements, all have correct IDs/titles
```

---

### NFR-013: Gap Deduplication

**ID:** NFR-013  
**Category:** Correctness  
**Related Requirement:** FR-004 (auto-reporting)

**Target:**
- Same error reported multiple times: create only ONE gap, with count
- Within 5-minute window: treat as duplicate
- Track error frequency for trend analysis

**Test Case:**
```python
def test_deduplication():
    # Report same error 3x
    # Should create 1 gap with count=3
```

---

## Operational Requirements

### NFR-014: Observability & Diagnostics

**ID:** NFR-014  
**Category:** Observability  
**Related Requirement:** All

**Target:**
- Structured logging (JSON format) for all operations
- Every log entry includes: timestamp, level, message, context (function, line)
- Error logs include full stack traces
- Sync operations logged: start, end, duration, count of synced requirements

**Measurement:**
```python
def test_logging():
    # Perform sync
    # Verify logs contain: operation start, end, duration, error context if failed
```

---

### NFR-015: Operational Documentation

**ID:** NFR-015  
**Category:** Maintainability  
**Related Requirement:** All

**Target:**
- Runbooks for common failures:
  - "Tracker is unavailable" → check tracker health, manual retry, escalate
  - "Sync stuck" → check logs, kill process, restart
  - "Dashboard shows stale data" → trigger manual sync, check last sync time
- Runbooks stored in RUNBOOKS.md, linked from README

---

## Deployment & Operations

### NFR-016: Deployment Repeatability

**ID:** NFR-016  
**Category:** Reliability  
**Related Requirement:** All

**Target:**
- Docker image builds reproducibly: Dockerfile documents all steps
- Environment setup <30 minutes for new developer
- All dependencies pinned (requirements.txt with exact versions)
- CI/CD pipeline documented (see: .github/workflows/)

**Measurement:**
```bash
# New developer follows README:
1. git clone
2. pip install -r requirements.txt
3. python -m pytest  # All tests pass
4. python -m uvicorn backend.api_server:app  # Server starts
```

---

### NFR-017: Monitoring & Alerting

**ID:** NFR-017  
**Category:** Observability  
**Related Requirement:** All

**Target:**
- Metrics exported: sync_duration_seconds, api_response_time_ms, sync_success_count, sync_failure_count
- Dashboard shows: last sync time, last sync status, recent errors
- Alerts configured for:
  - Sync hasn't completed in >90 seconds
  - Sync failures 5+ times in a row
  - API response time >2 seconds consistently

---

## Summary

| ID | Category | Title | Target | Current | Status |
|----|----------|-------|--------|---------|--------|
| NFR-001 | Performance | Sync completes in <30s | <30s | TBD | To Test |
| NFR-002 | Performance | API response time <500ms | <500ms | TBD | To Test |
| NFR-003 | Reliability | Tracker unavailability tolerance | 3 retries, exponential backoff | Not implemented | Gap |
| NFR-004 | Reliability | Data consistency within 5min | 100% consistency | TBD | To Test |
| NFR-005 | Maintainability | Type hint coverage ≥90% | ≥90% | ~30% | Gap |
| NFR-006 | Maintainability | Test coverage ≥80% | ≥80% | 0% | Gap |
| NFR-007 | Maintainability | Complexity <15 CC per function | <15 | TBD | To Measure |
| NFR-008 | Maintainability | All public functions documented | 100% docstrings | ~60% | Partial |
| NFR-009 | Security | No secrets in git | 0 secrets | Met | Met ✅ |
| NFR-010 | Security | No CVE high/critical deps | 0 CVEs | Unknown | To Scan |
| NFR-011 | Security | Input validation with Pydantic | 100% APIs validated | Not implemented | Gap |
| NFR-012 | Correctness | Sync accuracy 100% | 100% | TBD | To Test |
| NFR-013 | Correctness | Gap deduplication | 1 per error/5min | Not implemented | Gap |
| NFR-014 | Observability | Structured logging | JSON logs + context | Print statements | Partial |
| NFR-015 | Observability | Runbooks for common failures | Documented | Not documented | Gap |
| NFR-016 | Deployment | Deployment repeatability | <30min setup | Unknown | To Test |
| NFR-017 | Operations | Monitoring & alerting | Metrics + alerts | Not configured | Gap |

**Total Non-Functional Requirements: 17**  
**Met: 1**  
**Partial: 2**  
**Gap: 14**  

**Summary Score: 6% (1/17 Met) — Significant work needed on quality attributes**
