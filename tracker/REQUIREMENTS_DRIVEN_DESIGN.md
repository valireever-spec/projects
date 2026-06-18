# Requirements-Driven Design & Bug Tracking

Complete integration of V-Model requirements framework with 8-pillar architecture validation and bug tracker.

---

## The Complete Model: V-Model + 8-Pillars + Bug Tracker

```
┌─────────────────────────────────────────────────────────────────┐
│                    REQUIREMENTS SPECIFICATION                    │
│  (What the system must do + how well + measurable success)       │
├─────────────────────────────────────────────────────────────────┤
│ • Functional Requirements (FR-001, FR-002, ...)                  │
│   - Use cases, actors, flows, acceptance criteria                │
│ • Non-Functional Requirements (NFR-001, NFR-002, ...)            │
│   - Performance, security, reliability, maintainability          │
│ • Acceptance Criteria (CR-001, CR-002, ...)                      │
│   - Measurable, testable, verifiable                             │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   DESIGN SPECIFICATION                           │
│  (How requirements are decomposed into components)               │
├─────────────────────────────────────────────────────────────────┤
│ • Architecture Decisions (mapped to requirements)                │
│ • Component Design (modules, interfaces, databases)              │
│ • Traceability Matrix (requirement → design component)           │
│                                                                  │
│ 8-PILLAR FRAMEWORK checks design quality:                       │
│  ✓ Pillar 1: Architecture Discipline (ADRs trace requirements)  │
│  ✓ Pillar 2: Build Quality (validation rules for specs)         │
│  ✓ Pillar 3: Verification (test strategy per requirement)       │
│  ✓ Pillar 4: CI/CD (gates ensure specs are met)                │
│  ✓ Pillar 5: Root-Cause (link bugs to unmet specs)             │
│  ✓ Pillar 6: Security (NFR validation for secrets, auth, etc.)  │
│  ✓ Pillar 7: Observability (monitor NFR metrics)               │
│  ✓ Pillar 8: Maintainability (traceability enables safe changes)│
└─────────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION                                │
│  (Code, tests, configuration)                                   │
├─────────────────────────────────────────────────────────────────┤
│ • Backend code (implements design)                               │
│ • Frontend code (implements design)                              │
│ • Tests (validate implementation against requirements)           │
│ • Configuration (CI/CD, monitoring, security)                    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   VALIDATION & TESTING                           │
│  (Right leg of V-Model: tests validate requirements)             │
├─────────────────────────────────────────────────────────────────┤
│ • Unit Tests → Validate implementation (code correctness)        │
│ • Integration Tests → Validate design (modules work together)    │
│ • System Tests → Validate requirements (end-to-end features)     │
│ • Acceptance Tests → Validate use cases (user-facing behavior)   │
│ • Non-Functional Tests → Validate NFRs (performance, security)   │
│                                                                  │
│ Gap/Bug Tracker:                                                │
│  • Links every bug to unmet requirement                          │
│  • Tracks acceptance criterion failures                          │
│  • Measures: requirement coverage, at-risk requirements          │
│  • Status flow: Discovered → Prioritized → Remediation → Done    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  REQUIREMENT COVERAGE REPORT                     │
│  (Is the system meeting its requirements?)                       │
├─────────────────────────────────────────────────────────────────┤
│ Functional Requirements: 15/15 met (100%) ✅                     │
│ Non-Functional Requirements: 18/20 met (90%) ⚠️                  │
│   - At risk: NFR-003 (Security patch SLA), NFR-004 (Type hints)  │
│ Acceptance Criteria: 58/60 met (96.7%)                          │
│                                                                  │
│ Open Bugs by Requirement:                                       │
│   FR-001: 1 bug (allocation rounding)                           │
│   NFR-003: 2 bugs (patch response, CVE scanning)                │
│   NFR-004: 3 bugs (type hints)                                  │
│                                                                  │
│ Overall: 37/40 requirements met (92.5%)                         │
│ Trend: ↑ 5% improvement last month                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## How Each Component Works

### 1. Requirements Specification (Left Leg of V)

**Functional Requirements** (what the system does):
```yaml
ID: FR-001
Title: User can create investment portfolio
Actor: Investor
Acceptance Criteria:
  - Portfolio name must be non-empty and unique (CR-001)
  - Asset allocation percentages must sum to 100% ±0.1% (CR-002)
  - Creation must complete within 2 seconds (links to NFR-003)
Test Case: tests/functional/test_portfolio_creation.py::test_create_portfolio_valid
Status: Implemented ✅ (but CR-002 has open bug BUG-042)
```

**Non-Functional Requirements** (how well the system does it):
```yaml
ID: NFR-001
Category: Performance
Title: Portfolio fetch API responds in < 500ms (p99)
Measurement Method: Monitor journalctl for response_time_ms metric
Target: < 500ms for 99% of requests
Test Case: tests/nonfunctional/test_performance.py::test_portfolio_fetch_latency
Status: Validated ✅ (current p99 = 450ms)
```

### 2. Design Traceability (Bridge Between Specs & Code)

**Traceability Matrix** maps requirements to implementation:
```
Requirement | Design Component | Code File | Test | Status
FR-001      | PortfolioAPI     | backend/api/routers/portfolio.py | test_create | ✅
FR-002      | PortfolioService | backend/services/portfolio.py | test_fetch | ✅
NFR-001     | APIGateway       | backend/api/main.py | test_perf | ✅
NFR-002     | DatabasePool     | backend/db/pool.py | test_latency | ⚠️ (p99=450)
```

**Architecture Decisions** link design choices to requirements:
```
Decision ID: AD-042
Requirement: NFR-001 (Portfolio fetch < 500ms)
Decision: Use PostgreSQL query caching + in-memory LRU cache
Rationale: Reduces DB load, speeds up repeated queries
Trade-off: Adds complexity, must invalidate cache on updates
Test: Integration test verifies cache invalidation (IT-125)
```

### 3. Tests Validate Requirements

Each test maps back to a requirement:

```python
# tests/functional/test_portfolio_creation.py
def test_create_portfolio_valid():
    """Validates FR-001 acceptance criteria CR-001 and CR-002"""
    response = client.post("/api/portfolio", json={
        "name": "My Portfolio",
        "allocation": {"AAPL": 30, "GOOGL": 30, "BND": 40}
    })
    assert response.status_code == 201
    assert response.json()["name"] == "My Portfolio"
    # Validates CR-001: name not empty
    # Validates CR-002: sum == 100%
    
def test_portfolio_fetch_latency():
    """Validates NFR-001: Portfolio fetch < 500ms p99"""
    start = time.time()
    response = client.get("/api/portfolio/1")
    latency_ms = (time.time() - start) * 1000
    assert latency_ms < 500  # Validates NFR target
    assert response.status_code == 200
```

### 4. Bugs Link to Requirements (Not Just Pillars)

**Bug in Tracker**:
```
ID: BUG-042
Title: Asset allocation sums to 100.2% instead of 100%
Related Requirement: FR-001
Acceptance Criterion: CR-002 (sum to 100% ±0.1%)
Related Pillar: Build Quality In (validation logic)
Measurement: Test case test_portfolio_creation.py::test_allocation_rounding fails
Current State: Allocation [30%, 30%, 40.2%] is rejected
Expected State: Should accept (within ±0.1%)
Severity: Medium
Effort: 1 day
Status: Discovered → In Remediation
```

This shows:
- **What's broken**: Requirement CR-002 not met
- **Why it's broken**: Validation logic too strict (rounding error)
- **Which pillar**: Build Quality In (error-proofing issue)
- **How to verify it's fixed**: Acceptance test passes

### 5. Requirement Coverage Report

Dashboard shows:

```
Requirement Coverage for investing-platform
═════════════════════════════════════════

Functional Requirements: 15/15 met (100%) ✅
├─ FR-001: Create Portfolio (1 bug: CR-002 rounding)
├─ FR-002: Fetch Portfolio (0 bugs) ✅
├─ FR-003: Backtest (0 bugs) ✅
└─ ... (12 more)

Non-Functional Requirements: 18/20 met (90%) ⚠️
├─ NFR-001: API latency < 500ms (p99=450ms) ✅
├─ NFR-002: 99.5% availability (current=99.8%) ✅
├─ ❌ NFR-003: Security patch SLA 7 days (current=12 days) — 2 bugs
└─ ❌ NFR-004: Type hints >= 90% (current=43%) — 3 bugs

Acceptance Criteria: 58/60 met (96.7%)
└─ At Risk: CR-002 (Asset allocation rounding), CR-047 (Import CSV format)

Overall Requirement Coverage: 91/100 (91%)
Trend: +5% improvement last month
```

---

## Integration with 8-Pillar Framework

Each pillar now explicitly supports requirement fulfillment:

### **Pillar 1: Architecture Discipline & Traceability**
- **Requirement**: ADRs trace requirements to design decisions
- **Measurement**: Every ADR references ≥1 requirement ID
- **Test**: ARCHITECTURE_DECISION_LOG.md validated against FUNCTIONAL_REQUIREMENTS.md
- **Tracker**: Design tab shows which requirements each component addresses

### **Pillar 2: Build Quality In / Error-Proofing**
- **Requirement**: Acceptance criteria have validation rules
- **Measurement**: Type hints >90%, linting rules >80%, secrets scanning
- **Test**: Unit tests validate acceptance criteria (CR-*)
- **Tracker**: Bug severity links to which acceptance criterion failed

### **Pillar 3: Verification & Validation**
- **Requirement**: Test coverage for each requirement (FR and NFR)
- **Measurement**: ≥1 test case per requirement, 100% critical requirement coverage
- **Test**: tests/functional/, tests/nonfunctional/, tests/integration/
- **Tracker**: Requirements coverage report (% requirements validated)

### **Pillar 4: CI & Safe Delivery**
- **Requirement**: Automated gates ensure requirements before merge/deploy
- **Measurement**: No code deploys unless requirement tests pass
- **Test**: .github CI/CD blocks merge if any critical requirement test fails
- **Tracker**: Requirement status updated automatically when tests pass

### **Pillar 5: Root-Cause Driven Improvement**
- **Requirement**: Every bug links to unmet requirement
- **Measurement**: 100% of bugs have requirement_id, root cause analysis
- **Test**: Incident reports trace back to which requirement was violated
- **Tracker**: Post-mortems linked to requirement ID; prevent recurrence

### **Pillar 6: Security & Privacy by Design**
- **Requirement**: Security requirements (NFRs) explicit and measured
- **Measurement**: NFR-XXX for each security property (encryption, secrets, auth, etc.)
- **Test**: Security-specific tests per NFR (test_no_secrets.py, test_encryption.py)
- **Tracker**: Security bugs linked to NFR-XXX; SLA tracked

### **Pillar 7: Observability & Telemetry**
- **Requirement**: NFRs for performance/availability/reliability measured in production
- **Measurement**: SLO definitions (latency, availability, error rate) per NFR
- **Test**: Non-functional tests validate NFR targets in staging
- **Tracker**: Live SLO dashboard; alerts when NFR at risk

### **Pillar 8: Maintainability & Sustainable Pace**
- **Requirement**: Traceability enables safe refactoring
- **Measurement**: Every code change links to requirement or bug
- **Test**: Refactoring must not break any requirement validation tests
- **Tracker**: Change log shows which requirement each change addresses

---

## Practical Example: investing-platform

### Step 1: Define Requirements

**FUNCTIONAL_REQUIREMENTS.md**:
```yaml
ID: FR-002
Title: Compute composite trading signal
Actor: Portfolio manager
Acceptance Criteria:
  - Signal score is always 0–100 (CR-015)
  - All 6 factors weighted equally (CR-016)
  - Can override weights via API (CR-017)
  - Result returned within 1 second (links to NFR-002)
Test: tests/functional/test_composite_signal.py
```

**NONFUNCTIONAL_REQUIREMENTS.md**:
```yaml
ID: NFR-002
Category: Performance
Title: Composite signal API responds in < 1 second
Measurement: Monitor signal_compute_time_ms in journalctl
Target: < 1000ms for 99% of requests
Test: tests/nonfunctional/test_signal_latency.py
Alert: If p99 > 1200ms, page on-call engineer
```

### Step 2: Design & Trace

**ARCHITECTURE_DECISION_LOG.md**:
```
Decision: Cache composite signals for 1 hour
Related Requirement: NFR-002 (signal < 1 second)
Rationale: Recomputing all 6 factors takes 800–900ms; 1hr cache keeps p99 < 500ms
```

**TRACEABILITY_MATRIX.md**:
```
Requirement | Component | File | Test | Status
FR-002      | CompositeSignal | backend/analytics/composite_signal.py | test_composite_signal | ✅
CR-015      | SignalValidator | backend/analytics/validators.py | test_signal_range | ✅
NFR-002     | SignalCache + API | backend/api/main.py | test_signal_latency | ✅ (p99=450ms)
```

### Step 3: Test

**tests/functional/test_composite_signal.py**:
```python
def test_cr015_signal_in_range():
    """Validates FR-002 acceptance criterion CR-015: score 0–100"""
    for symbol in ["AAPL", "GOOGL", "BND"]:
        score = compute_composite(symbol)
        assert 0 <= score <= 100, f"Signal {score} out of range"
        
def test_cr016_equal_weights():
    """Validates FR-002 acceptance criterion CR-016: all 6 factors equal"""
    # With equal weights, all factors should contribute 1/6 each
    score = compute_composite("AAPL", weights=[1/6]*6)
    assert 0 <= score <= 100
```

**tests/nonfunctional/test_signal_latency.py**:
```python
def test_nfr002_signal_latency():
    """Validates NFR-002: signal computed in < 1 second p99"""
    latencies = []
    for _ in range(100):
        start = time.time()
        compute_composite("AAPL")
        latencies.append((time.time() - start) * 1000)
    
    p99 = np.percentile(latencies, 99)
    assert p99 < 1000, f"p99 latency {p99}ms > 1000ms target"
```

### Step 4: Track & Report

**Requirement Coverage Report**:
```
FR-002: Composite Signal
├─ CR-015 (score 0–100): ✅ Met
├─ CR-016 (equal weights): ✅ Met
├─ CR-017 (weight override): ⚠️ Partial (API exists, doesn't validate overrides)
│  └─ Open Bug: BUG-089 (weight validation missing)
└─ NFR-002 (< 1 second): ✅ Met (p99=450ms)

Overall: 3/4 criteria met (75%)
Bugs blocking completion: BUG-089 (effort: 3 days)
```

### Step 5: Fix & Close

**Bug BUG-089**:
```
Title: Weight override doesn't validate that sum = 1.0
Requirement: FR-002 CR-017
Status: In Remediation
PR: #342 (adds validation_signal_weights() function)
Test: Commits with test passing before merge
Once merged & tested: Requirement FR-002 CR-017 marked ✅
```

---

## How the Tracker Supports This

### Database Schema
```
Project
├─ Requirement (FR-001, NFR-002, etc.)
│  ├─ req_id: "FR-001"
│  ├─ req_type: "Functional" | "Non-Functional"
│  ├─ title: "User can create portfolio"
│  ├─ acceptance_criteria: "Portfolio name required..."
│  ├─ measurement_method: "Automated test suite"
│  ├─ target: "100% of criteria met"
│  ├─ test_case: "tests/functional/test_portfolio.py"
│  ├─ status: "Proposed" → "Accepted" → "Implemented" → "Validated"
│  └─ Gap (bug linked to this requirement)
│
├─ Gap (bug)
│  ├─ requirement_id: 42 (links to Requirement)
│  ├─ pillar: "Build Quality In"
│  ├─ title: "Allocation validation too strict"
│  ├─ status: "Discovered" → "In Remediation" → "Done"
│  └─ severity/effort

└─ ScorecardEntry (pillar score)
   └─ (unchanged—still tracks 8-pillar assessment)
```

### API Endpoints
```
POST   /api/projects/{id}/requirements             # Create requirement
GET    /api/projects/{id}/requirements             # List all requirements
GET    /api/projects/{id}/requirements/{req_id}    # Get one requirement
PUT    /api/projects/{id}/requirements/{req_id}    # Update status
GET    /api/projects/{id}/requirements-coverage    # Coverage report
```

### Tracker UI Views
```
Dashboard:
├─ Projects Grid
│  └─ Requirement Coverage % (alongside maturity score)

Project Home (New Tab):
├─ Requirements Tab
│  ├─ Functional: [FR-001] [FR-002] [FR-003]
│  │  └─ Click to see: description, acceptance criteria, test, status, linked bugs
│  ├─ Non-Functional: [NFR-001] [NFR-002]
│  └─ Coverage Report: 91% (18/20 met)
│
├─ Scorecard Tab (8 pillars)
│  └─ (unchanged)
│
├─ Gaps & Bugs Tab
│  └─ Now shows: Requirement linked to each bug
│
└─ Traceability Tab (new)
   └─ Matrix view: Requirement → Design → Code → Test
```

---

## Getting Started

For **each project**, create:

1. **`requirements/FUNCTIONAL_REQUIREMENTS.md`**
   - List all features (FR-001, FR-002, ...)
   - Include: use case, actors, acceptance criteria, test case

2. **`requirements/NONFUNCTIONAL_REQUIREMENTS.md`**
   - List all qualities (NFR-001, NFR-002, ...)
   - Include: measurement method, target, test case, alert threshold

3. **`TRACEABILITY_MATRIX.md`**
   - Map: Requirement → Design Component → Code File → Test Case

4. **Link bugs in tracker to requirements**
   - Every bug answers: "Which requirement does this violate?"
   - Include the acceptance criterion (CR-XXX) that's failing

5. **Requirement Coverage Report** (generated monthly)
   - % functional requirements met
   - % non-functional requirements validated
   - Which requirements are at risk (have open bugs)
   - Trend (improving or declining)

---

## Success Criteria

✅ **Requirements-Driven Design is working when**:
- Every bug links back to unmet requirement
- New features start with written requirement (not vague ideas)
- Requirements coverage % is the primary success metric (not just test %)
- Root-cause analysis always identifies which requirement or design flaw caused the bug
- Refactoring is guided by traceability (don't change untraceable code)
- On-call knows: "System is currently meeting 92% of requirements, at risk: NFR-003"

---

## References

- `project-designer/V_MODEL_REQUIREMENTS.md` — Full V-Model specification framework
- `project-designer/FRAMEWORK.md` — 8-pillar rules (updated to reference V-Model)
- Each project: `requirements/`, `TRACEABILITY_MATRIX.md`, tracker UI

