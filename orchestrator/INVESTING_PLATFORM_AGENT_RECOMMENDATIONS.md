# Investing-Platform: Specialized Agents & Skills Selection

**Document:** Recommended agent roles, specialized skills, and orchestration workflows for investing-platform

---

## SUMMARY: AGENT CONFIGURATION FOR INVESTING-PLATFORM

```
┌────────────────────────────────────────────────────────────────┐
│             INVESTING-PLATFORM ORCHESTRATOR                    │
│                  Agent + Skill Configuration                   │
└────────────────────────────────────────────────────────────────┘

DESIGNER AGENT
└─ Analyzes market data, trading strategies, risk profile
   └─ Skills: best-practices-applier, architecture-auditor
   └─ Output: Market assessment, signal recommendations, risk alerts

IMPLEMENTER AGENT
├─ Implements trading logic, signal improvements, model retraining
├─ Skills (Phase 2):
│  ├─ best-practices-applier-v2 (market best practices)
│  ├─ backtesting-simulator-v2 (validate strategy performance)
│  ├─ test-suite-builder (create trading tests)
│  ├─ performance-optimizer (optimize trade execution)
│  ├─ security-hardener (secure credential handling)
│  └─ ml_pipeline_orchestrator (retrain ML models)
└─ Output: Updated strategies, backtested signals, trained models

VERIFIER AGENT
├─ Validates trading decisions, audits risk compliance
├─ Skills (Phase 2):
│  ├─ api-consistency-validator-v2 (Alpaca API validation)
│  ├─ chaos-testing-framework-v2 (market disorder resilience)
│  ├─ security-checker-v2 (credential/secret scanning)
│  ├─ business-safety-assessor-v1 (compliance check)
│  ├─ performance-profiler (execution performance)
│  └─ compliance-auditor (regulatory rules)
└─ Output: Verified strategies, compliance sign-off, test results

ORCHESTRATOR COORDINATOR
├─ Coordinates daily/weekly/monthly workflows
├─ Integrations:
│  ├─ ResourceMonitor (CPU/memory/disk safety)
│  ├─ TestingValidationPlatform (V-Model traceability)
│  └─ Tracker (central requirement + bug tracking)
└─ Output: Scheduled workflows, automated alerts, incident escalation
```

---

## 1. DESIGNER AGENT FOR INVESTING-PLATFORM

### Purpose
Analyze market conditions, portfolio state, and signal quality to recommend improvements.

### Input
```python
DesignInput(
    project_id=investing_platform_id,
    project_path="/home/vali/projects/investing-platform",
    tech_stack="Python FastAPI + PostgreSQL + Ollama",
    framework="CSF-21",
    focus_area="Trading signal quality + risk management",
    context={
        "current_sharpe": 1.2,
        "current_max_drawdown": 8.5,
        "signal_accuracy_30d": 0.62,
        "data_freshness": "Grade A",
        "portfolio_size": "$250K",
    }
)
```

### Designer Tasks

1. **Market Analysis** — Assess current market regime (bull/bear/volatile/sideways)
   - Input: Last 30 days of market data
   - Output: Regime assessment + recommended strategy adjustments
   - Skill: N/A (Claude analysis)

2. **Signal Quality Audit** — Evaluate 6-factor composite signal effectiveness
   - Input: Signal accuracy (30/60/90-day rolling), factor correlations
   - Output: Weak factors identified, recommendations to improve
   - Skill: analytics-engine-v2

3. **Risk Assessment** — Assess current risk posture
   - Input: Current loss level, position sizing, volatility
   - Output: Risk level (GREEN/YELLOW/ORANGE/RED), recommendations
   - Skill: business-safety-assessor-v1

4. **Architecture Review** — Code quality assessment
   - Input: Recent commits, test coverage, silent failures count
   - Output: Code quality score, gaps identified
   - Skill: architecture-auditor-v2

5. **Model Performance Review** — ML model evaluation
   - Input: Model accuracy, feature importance, drift indicators
   - Output: Retraining recommendation (retrain or hold)
   - Skill: analytics-engine-v2

### Designer Output

```python
DesignOutput(
    findings=[
        "Signal accuracy declining: 0.65 (90d) → 0.62 (30d)",
        "Market in BULL regime: favor growth factor over value",
        "1,389 silent failures in error handlers: compliance risk",
        "ML model drift detected: retraining recommended",
    ],
    proposed_requirements=[
        Requirement(
            req_id="FR-051",
            title="Improve Signal Accuracy",
            description="Reduce false positives in composite signal (target: 0.70)",
            category="Trading",
            acceptance_criteria="30-day accuracy >= 0.70"
        ),
        Requirement(
            req_id="FR-052",
            title="Fix Silent Failures",
            description="Replace bare except handlers with proper logging",
            category="Reliability",
            acceptance_criteria="0 silent failures in error paths"
        ),
        Requirement(
            req_id="FR-053",
            title="Retrain ML Models",
            description="Retrain ensemble models on latest data",
            category="ML",
            acceptance_criteria="Model accuracy >= 0.58 on hold-out set"
        ),
    ],
    gaps_identified=[
        Gap(
            pillar="Build Quality In",
            title="1,389 Silent Exception Handlers",
            severity=SeverityLevel.CRITICAL,
            effort=EffortLevel.MEDIUM
        ),
        Gap(
            pillar="Verification & Validation",
            title="Phase 343 Integration Not End-to-End Tested",
            severity=SeverityLevel.HIGH,
            effort=EffortLevel.MEDIUM
        ),
    ],
    risk_assessment={
        "critical": ["Silent failures in error paths"],
        "high": ["HA failover untested", "Request timeouts missing"],
        "medium": ["ML model drift", "Signal accuracy declining"],
    },
    next_steps=[
        "Fix critical silent failures (1-2 hours)",
        "Add request timeouts to HTTP calls (15 min)",
        "End-to-end test Phase 343 Guardian integration (2 hours)",
        "Retrain ML models with latest data (30 min)",
    ],
)
```

### Designer Frequency
- **Daily:** Quick market assessment (10 min)
- **Weekly:** Full review (signal quality, architecture, ML models)
- **Monthly:** Deep analysis (trend assessment, strategy evolution)

---

## 2. IMPLEMENTER AGENT FOR INVESTING-PLATFORM

### Purpose
Implement improvements identified by Designer (fix bugs, retrain models, improve signals).

### Input
```python
ImplementerInput(
    project_id=investing_platform_id,
    project_path="/home/vali/projects/investing-platform",
    design_findings=design_output,  # From Designer
    target_requirements=[
        Requirement(req_id="FR-051", title="Improve Signal Accuracy", ...),
        Requirement(req_id="FR-052", title="Fix Silent Failures", ...),
        Requirement(req_id="FR-053", title="Retrain ML Models", ...),
    ],
    test_framework="pytest",
    ci_system="GitHub Actions",
)
```

### Implementer Tasks (Skill-Driven)

#### Task 1: Fix Silent Failures
- **Skill:** best-practices-applier-v2
- **Process:** 
  1. Scan for bare `except:` handlers
  2. Replace with specific exception types
  3. Add structured logging (JSON)
- **Time:** 1-2 hours
- **Validation:** Linting + type checking

#### Task 2: Add Request Timeouts
- **Skill:** security-hardener (timeout is security + reliability)
- **Process:**
  1. Identify all HTTP calls (httpx, requests, etc.)
  2. Add timeout=120s to each
  3. Add retry logic on timeout
- **Time:** 15 min
- **Validation:** Test with simulated network latency

#### Task 3: Retrain ML Models
- **Skill:** ml_pipeline_orchestrator (or custom ML skill)
- **Process:**
  1. Fetch latest data (last 90 days)
  2. Retrain LSTM, RandomForest, XGBoost
  3. Validate accuracy on hold-out set
  4. Save new model checkpoint
- **Time:** 30 min
- **Validation:** Model accuracy >= 0.58 on test set

#### Task 4: Improve Composite Signal
- **Skill:** best-practices-applier-v2 + backtesting-simulator-v2
- **Process:**
  1. Analyze factor correlations (technical, ML, sentiment, fear/greed, news)
  2. Adjust weighting to reduce false positives
  3. Backtest new weighting (2020-2026 data)
  4. Validate Sharpe ratio improvement
- **Time:** 1-2 hours
- **Validation:** Backtest results show improvement

#### Task 5: End-to-End Test Phase 343
- **Skill:** test-suite-builder + chaos-testing-framework-v2
- **Process:**
  1. Create integration tests for Guardian Guidance topics
  2. Test failover scenario (simulate primary down)
  3. Verify backup auto-promotion
  4. Validate data consistency after failover
- **Time:** 2-3 hours
- **Validation:** All tests pass; failover succeeds in <30s

### Implementer Parallel Execution

All tasks run in parallel (Implementer orchestrates):
```
├─ Fix silent failures (1-2 hours)
├─ Add request timeouts (15 min)
├─ Retrain ML models (30 min)
├─ Improve composite signal (1-2 hours)
└─ End-to-end test Phase 343 (2-3 hours)

Total time: MAX(2h, 0.25h, 0.5h, 2h, 3h) = 3 hours (parallel)
vs. 6.25 hours (serial)
```

### Implementer Output

```python
ImplementerOutput(
    code_changes=[
        CodeChange(
            file_path="backend/core/exceptions.py",
            description="Add specific exception types for error handling",
            rationale="Replace bare except handlers with typed exceptions"
        ),
        CodeChange(
            file_path="backend/ml/ensemble_model.py",
            description="Retrain ensemble with latest data",
            rationale="Reduce model drift; improve prediction accuracy"
        ),
        CodeChange(
            file_path="backend/signals/composite_signal.py",
            description="Adjust factor weighting to reduce false positives",
            rationale="Improve signal accuracy from 0.62 to 0.70"
        ),
    ],
    test_plan=TestPlan(
        unit_tests=["test_exception_handling.py", "test_ml_model_accuracy.py"],
        integration_tests=["test_failover.py", "test_guardian_topics.py"],
        e2e_tests=["test_end_to_end_workflow.py"],
        coverage_target=85
    ),
    gaps_created=[],  # Clean implementation
    blockers=[],  # No blockers
)
```

### Implementer Frequency
- **Daily:** Retrain ML models (nightly, automatic)
- **Weekly:** Major improvements (signal weighting, strategy updates)
- **As-needed:** Bug fixes, urgent improvements

---

## 3. VERIFIER AGENT FOR INVESTING-PLATFORM

### Purpose
Validate that implementations meet requirements, comply with regulations, and won't break trading.

### Input
```python
VerifierInput(
    project_id=investing_platform_id,
    project_path="/home/vali/projects/investing-platform",
    code_changes=implementer_output.code_changes,
    original_requirements=[
        Requirement(req_id="FR-051", ...),
        Requirement(req_id="FR-052", ...),
        Requirement(req_id="FR-053", ...),
    ],
    test_results={
        "unit_test_pass_rate": 0.99,
        "integration_test_pass_rate": 1.0,
        "coverage": 0.87,
    },
    audit_rules=[
        "No credentials in code",
        "All HTTP calls have timeout",
        "ML model accuracy >= 0.58",
        "Failover completes in < 30s",
    ],
)
```

### Verifier Tasks (Skill-Driven)

#### Task 1: API Consistency Validation
- **Skill:** api-consistency-validator-v2
- **Checks:**
  - All 810+ endpoints return consistent error format
  - Alpaca API integration doesn't break on changed contract
  - Version compatibility checked
- **Outcome:** ✓ All endpoints valid; Alpaca client still compatible

#### Task 2: Security & Compliance Audit
- **Skill:** security-checker-v2 + compliance-auditor
- **Checks:**
  - No hardcoded secrets/credentials
  - Request timeouts in place
  - Input validation on all endpoints
  - Regulatory rules (suitability, best execution)
- **Outcome:** ✓ Security checks pass; compliance verified

#### Task 3: Chaos Testing (Market Disorder)
- **Skill:** chaos-testing-framework-v2
- **Scenarios:**
  - Network timeout during order placement
  - Market data 5 minutes stale
  - Alpaca API rate-limited (100/min breach)
  - Failover happens mid-trade
- **Outcome:** ✓ All scenarios handled gracefully; no data loss

#### Task 4: Business Logic Validation
- **Skill:** business-safety-assessor-v1
- **Checks:**
  - Signal recommendations don't violate risk caps
  - Position sizing respects notional limits
  - Loss caps enforced correctly (5-zone system)
  - Failover doesn't lose order history
- **Outcome:** ✓ Business logic validated; risk constraints met

#### Task 5: Performance Profiling
- **Skill:** performance-profiler
- **Checks:**
  - Order execution latency < 5s (p95)
  - Signal generation < 30s for 100+ symbols
  - Daily ingest completes by 9:00 AM market open
  - HA failover completes in < 30s
- **Outcome:** ✓ Performance SLAs met

#### Task 6: Requirement Traceability (V-Model)
- **Integration:** testing-validation-platform
- **Checks:**
  - FR-051 (Signal Accuracy): 30-day accuracy >= 0.70 ✓
  - FR-052 (Fix Silent Failures): 0 bare exceptions in error paths ✓
  - FR-053 (Retrain Models): ML accuracy >= 0.58 ✓
- **Outcome:** ✓ All requirements validated; audit trail created

### Verifier Output

```python
VerifierOutput(
    project_id=investing_platform_id,
    requirement_validation=[
        RequirementValidation(
            req_id="FR-051",
            title="Improve Signal Accuracy",
            passed=True,
            evidence="30-day accuracy now 0.71 (target: 0.70)"
        ),
        RequirementValidation(
            req_id="FR-052",
            title="Fix Silent Failures",
            passed=True,
            evidence="0 bare except handlers; all errors logged"
        ),
        RequirementValidation(
            req_id="FR-053",
            title="Retrain ML Models",
            passed=True,
            evidence="Ensemble accuracy: 0.59 (target: >= 0.58)"
        ),
    ],
    security_findings=[],  # Clean
    quality_findings=[],   # Clean
    blockers=[],           # No blockers
    approved=True,         # Ready for production
)
```

### Verifier Frequency
- **After each Implementer run:** Full validation (1-2 hours)
- **Before trading pause/restart:** Quick validation (10 min)
- **Weekly:** Comprehensive audit (2-3 hours)

---

## 4. SPECIALIZED SKILL SELECTION FOR INVESTING-PLATFORM

### Tier 1: Essential Skills (Always Use)

| Skill | Purpose | Phase | ROI |
|-------|---------|-------|-----|
| **best-practices-applier-v2** | Apply trading best practices, fix code issues | All | High |
| **test-suite-builder** | Generate/validate test coverage | All | High |
| **backtesting-simulator-v2** | Validate strategy performance | Implementer | High |
| **security-checker-v2** | Credential/secret scanning | Verifier | Critical |
| **api-consistency-validator-v2** | Alpaca API compatibility | Verifier | High |
| **performance-profiler** | Latency SLA validation | Verifier | High |

### Tier 2: Recommended Skills (Use When Applicable)

| Skill | Purpose | When |
|-------|---------|------|
| **analytics-engine-v2** | Signal quality analysis | Weekly Designer run |
| **chaos-testing-framework-v2** | Market disorder resilience | Monthly Verifier run |
| **ml_pipeline_orchestrator** | ML model retraining | Daily (auto) or weekly (manual) |
| **business-safety-assessor-v1** | Compliance verification | Verifier gate |
| **compliance-auditor** | Regulatory rules checking | Verifier gate |

### Tier 3: Optional Skills (Use If Available)

| Skill | Purpose | Optional |
|-------|---------|----------|
| **architecture-auditor-v2** | Code architecture review | Yes (Designer quarterly) |
| **documentation-generator** | Auto-generate design docs | Yes (one-time) |
| **performance-optimizer** | Optimize trade execution | Yes (if latency SLA breached) |

---

## 5. ORCHESTRATOR WORKFLOW FOR INVESTING-PLATFORM

### Daily Workflow (Automatic)

```
08:00 Market Open
├─ Orchestrator: Check resource status (1 min)
├─ Designer: Quick market assessment (10 min)
│  └─ Output: Market regime, signal quality score
├─ Implementer: Retrain ML models with new day's data (30 min)
│  └─ Skill: ml_pipeline_orchestrator
├─ Verifier: Validate new models pass accuracy threshold (10 min)
│  └─ Skill: performance-profiler
├─ Orchestrator: Gate check (models approved? data fresh? resources OK?)
│  └─ If all pass: Enable trading
│  └─ If any fail: Alert operator, hold trading
└─ Output: Trading enabled, audit trail logged

09:00 - 16:00 Trading Active
├─ Continuous: Sentinel bot executes trades
├─ Every 1h: Signal accuracy check (Designer lightweight)
└─ Real-time: Resource monitoring + emergency shutdown on exhaustion

17:00 Market Close
├─ Orchestrator: Post-market review
├─ Designer: End-of-day portfolio assessment
├─ Orchestrator: Log daily results to tracker
└─ Output: Daily performance summary, any alerts logged
```

### Weekly Workflow (Designer + Verifier)

```
Monday 09:00
├─ Designer: Full signal quality audit (1-2 hours)
│  ├─ Analyze 30/60/90-day accuracy trends
│  ├─ Check factor correlations
│  ├─ Identify weaknesses
│  └─ Output: Recommendations filed in tracker
├─ Implementer: Implement improvements (2-3 hours, parallel)
│  ├─ Adjust signal weighting
│  ├─ Add new factors if needed
│  └─ Output: Updated signal generation
└─ Verifier: Validate improvements (1-2 hours)
   ├─ Backtest new weighting (2020-2026 data)
   ├─ Verify Sharpe ratio improvement
   ├─ Chaos test (market shocks)
   └─ Output: Approved or blocked with feedback

Friday 16:00
└─ Orchestrator: Weekly digest
   ├─ Wins: signal accuracy trend, Sharpe ratio, new models deployed
   ├─ Risks: any blockers, failed tests, resource issues
   └─ Output: Weekly report to stakeholder
```

### Monthly Workflow (Architecture Review)

```
First Monday of Month
├─ Designer: Deep architecture review (4-6 hours)
│  ├─ Skill: architecture-auditor-v2
│  ├─ Review all 26 modules
│  ├─ Check code quality, test coverage, dependencies
│  └─ Output: Gaps filed in tracker
├─ Implementer: Fix high-priority issues (8 hours, parallel)
│  └─ Output: Code changes + tests
└─ Verifier: Validate changes (4 hours)
   └─ Output: Approved for next sprint
```

---

## 6. EXPECTED OUTCOMES BY AGENT

### Designer Agent Outputs (Weekly)
- ✓ Market assessment + trading recommendations
- ✓ Signal quality audit + factor analysis
- ✓ ML model performance review + retraining trigger
- ✓ Code quality assessment + gaps identified
- ✓ Risk posture analysis + alert levels

### Implementer Agent Outputs (Weekly)
- ✓ Fixed bugs (silent failures, missing timeouts)
- ✓ Improved signals (higher accuracy)
- ✓ Retrained models (lower drift)
- ✓ New tests (coverage maintained)
- ✓ Performance optimizations (faster execution)

### Verifier Agent Outputs (Weekly)
- ✓ Requirement traceability (FR/NFR met)
- ✓ Security validation (no secrets, timeouts in place)
- ✓ Compliance sign-off (regulatory rules)
- ✓ Performance SLA validation (latency, throughput)
- ✓ Chaos test results (market disorder handled)

---

## 7. CONFIGURATION FOR INVESTING-PLATFORM

```yaml
orchestrator:
  project_name: "investing-platform"
  project_path: "/home/vali/projects/investing-platform"
  framework: "CSF-21"
  
  agents:
    designer:
      model: "claude-opus-4-8"
      timeout_seconds: 600  # 10 min for market analysis
      schedule: "daily@08:00, weekly@09:00"
    
    implementer:
      model: "claude-opus-4-8"
      timeout_seconds: 900  # 15 min for multi-task
      schedule: "daily@08:30, weekly@10:00"
    
    verifier:
      model: "claude-opus-4-8"
      timeout_seconds: 1200 # 20 min for full validation
      schedule: "daily@09:15, weekly@13:00"
  
  skills:
    # Tier 1: Essential
    required_skills:
      - "best-practices-applier-v2"
      - "test-suite-builder"
      - "backtesting-simulator-v2"
      - "security-checker-v2"
      - "api-consistency-validator-v2"
      - "performance-profiler"
    
    # Tier 2: Recommended
    recommended_skills:
      - "analytics-engine-v2"
      - "chaos-testing-framework-v2"
      - "ml_pipeline_orchestrator"
      - "business-safety-assessor-v1"
      - "compliance-auditor"
    
    # Tier 3: Optional
    optional_skills:
      - "architecture-auditor-v2"
      - "documentation-generator"
      - "performance-optimizer"
  
  integration:
    testing_validation_platform:
      enabled: true
      url: "http://localhost:8004"
      auto_sync: true
    
    tracker:
      url: "http://localhost:8000"
      project_id: 123  # investing-platform
      auto_file_requirements: true
      auto_file_gaps: true
  
  resource_protection:
    hardened: true
    min_available_memory_gb: 2.0  # Ollama + trading needs headroom
    max_cpu_percent: 75.0
    min_disk_free_percent: 10.0
    memory_growth_limit_mb: 800  # ML models can be large
```

---

## SUMMARY: AGENT RECOMMENDATIONS

| Agent | Purpose | Skills | Frequency | ROI |
|-------|---------|--------|-----------|-----|
| **Designer** | Market assessment + signal audit | best-practices-applier, analytics-engine | Daily + weekly | High (identifies improvements) |
| **Implementer** | Implement improvements + retrain | test-suite-builder, ml_pipeline, backtesting | Daily + weekly | High (fixes bugs, improves performance) |
| **Verifier** | Validate requirements + compliance | security-checker, api-validator, chaos-testing | Daily + weekly | Critical (prevents bad trades) |

**Total Weekly Time Investment:** ~15 hours (orchestrator + 3 agents)  
**Time Freed for Operator:** 4+ hours/week (manual overhead eliminated)  
**Net Benefit:** More systematic improvements, better quality, faster iteration
