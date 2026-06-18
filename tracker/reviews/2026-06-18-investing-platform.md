# Architecture Review: investing-platform

**Date**: 2026-06-18  
**Reviewer**: Claude Code (8-Pillar Framework)  
**Status**: Early-stage, feature-complete, production-ready architecture under development

---

## Snapshot

**Project**: investing-platform — Full-stack trading research and paper trading platform  
**Tech Stack**: Python (FastAPI, SQLAlchemy), PostgreSQL, vanilla JavaScript (34K lines)  
**Team Size**: Solo/small  
**Deployment**: Systemd service (production), local development on FastAPI dev server  
**Current Phase**: Phase 301 (Production Hardening)

**Key Capabilities**:
- Market data ingestion (yfinance, Alpaca)
- Composite trading signals (6-factor: technical, ML, sentiment, options, fear/greed, news)
- Backtesting engine with execution costs and slippage modeling
- Paper trading (real-time portfolio simulation)
- Risk analytics (Sharpe, CAGR, max drawdown, walk-forward validation)
- LLM Guardian (Ollama-based two-pass market analysis)
- 64 API routers; 2200+ tests across 80 test files

---

## Score: 37% Professional-Grade (3 of 8 pillars Met)

| Pillar | Status | Evidence |
|--------|--------|----------|
| **Architecture Discipline & Traceability** | ✅ Met | ADRs, layered design, 64 organized routers, explicit module boundaries |
| **Build Quality In / Error-Proofing** | ⚠️ Partial | Type hints 43% (target 90%+), pinned deps, linting; secrets in git, 57 bare excepts |
| **Verification & Validation** | ✅ Met | 2200+ tests, comprehensive suites (unit/integration/plausibility), walk-forward validation |
| **CI & Safe Delivery** | ✅ Met | .github CI, Alembic migrations (5), systemd service, health checks, reversible deploys |
| **Root-Cause Driven Improvement** | ❌ Gap | No post-mortems, incident reports, or formal root-cause process |
| **Security & Privacy by Design** | ❌ Gap | **Critical**: 4 secrets in git, CORS wildcard, bare excepts mask errors, no CVE scanning |
| **Observability & Telemetry** | ⚠️ Partial | Logging, monitor_system.sh, journalctl, signal_log.jsonl; missing SLOs and alert thresholds |
| **Maintainability & Sustainable Pace** | ⚠️ Partial | 40 directories, domain-driven design; 2 god files >1500 lines, 34K JS frontend, phase-driven debt |

---

## Strengths (What's Working Well)

### 1. **Exceptional Test Coverage**
- 2200+ tests across 80 test files
- Three-tiered strategy: unit (no DB), integration (TestClient), plausibility (real data)
- Covers all major features: analytics, strategies, backtesting, API endpoints
- Load testing and regression test suites
- **Impact**: Enables confident refactoring and regression detection

### 2. **Well-Documented Architecture**
- Clear layered design: ingestion → analytics → strategies → API → frontend
- README with data flow diagrams
- ARCHITECTURE_DECISION_LOG.md with ADRs
- CLAUDE.md with operational runbooks (systemd, cron, monitoring)
- **Impact**: Onboarding is smooth; design intent is clear

### 3. **Thoughtful Technical Decisions**
- Composite signals blend 6 independent factors (0–100 score), not single indicator
- Walk-forward validation prevents overfitting in backtesting
- ML model caching keyed by last candle date (auto-retrain on new data)
- Symbol validation before analysis (prevents hallucination in Ollama)
- **Impact**: Reduced risk of spurious signals and hallucinated market data

### 4. **Production-Ready DevOps**
- Systemd service with resource limits (MemoryMax, CPUQuota) — prevents runaway Ollama/ML
- Cron jobs with Persistent=true timers (catches missed jobs on boot)
- Database backups with compression and retention
- Health check endpoints; journalctl monitoring
- **Impact**: Stable operation; recovery from failures automatic

### 5. **Clean Module Boundaries**
- 40 focused directories (analytics, strategies, backtesting, ML, risk, broker, etc.)
- Domain-driven structure (domains/ folder)
- No circular dependencies
- Pure functions in analytics/ (no DB, no I/O) — testable, cacheable
- **Impact**: Isolated development; minimal coupling

---

## Top Gaps (Ranked by Impact × Effort)

### 🔴 Critical (Block production hardening)

#### **1. Security & Privacy: Secrets Exposed in Git History**
- **Evidence**: Auto-checker found 4 secrets (API keys, credentials) in git history
- **Risk**: Exposed credentials enable unauthorized API access; legacy commits may persist in backups
- **Effort**: 2–4 weeks (clean history, rotate credentials, add scanning)
- **Recommendation**: Use `git-filter-repo` to purge secrets; add `pip-audit` and `git-secrets` to CI

#### **2. Build Quality: 57 Bare Exception Handlers**
- **Evidence**: `except:` statements throughout codebase (no specific exception types)
- **Risk**: Silently swallows errors (network failures, disk full, permission denied), makes debugging hard
- **Effort**: 1–2 weeks (convert to `except (ValueError, TypeError, ...):`)
- **Recommendation**: Add linting rule (flake8 plugin) to fail on bare excepts

#### **3. Security: No CVE Scanning in CI/CD**
- **Evidence**: No automated dependency vulnerability scanning
- **Risk**: Known vulnerabilities in transitive deps go undetected until exploit hits production
- **Effort**: 1–3 days (add `pip-audit` or `safety` to .github)
- **Recommendation**: Run `pip-audit` on every PR; block if vulnerabilities found

### 🟠 High (Impact: medium, Effort: low)

#### **4. Build Quality: Type Hints Coverage (43%)**
- **Evidence**: Only 43% of Python files have type hints; target >90%
- **Risk**: IDE autocomplete unreliable; refactoring blind; subtle runtime bugs missed
- **Effort**: 1–2 weeks
- **Recommendation**: Use `pyright` in strict mode; gradual adoption per module

#### **5. Maintainability: Two God Files (>1500 lines)**
- **Evidence**: `check_alerts.py` (1725 lines), `send_digest.py` (1569 lines)
- **Risk**: Hard to test, reuse, or reason about; difficult to parallelize
- **Effort**: 1 week (split into focused modules: alert_checker.py, email_builder.py, etc.)
- **Recommendation**: Split by responsibility; each module <500 lines

### 🟡 Medium (Impact: medium, Effort: medium)

#### **6. Root-Cause Improvement: No Incident/Learning Capture**
- **Evidence**: No post-mortems, incident reports, or root-cause analysis process
- **Risk**: Bugs recur; lessons from production failures are lost; continuous improvement stalls
- **Effort**: 1 week (template + wiki + monthly retrospective cadence)
- **Recommendation**: Adopt blameless post-mortem template; log to incident_log.jsonl

#### **7. Observability: Missing SLOs and Alert Thresholds**
- **Evidence**: Logging and scripts exist; no formal SLOs, alert rules, or escalation playbooks
- **Risk**: Outages not detected until user reports; on-call response is reactive
- **Effort**: 2–3 weeks (define SLOs, configure alerts in journalctl/systemd, write runbooks)
- **Recommendation**: SLOs: API availability >99%, composite signal latency <500ms; set alert thresholds

---

## Roadmap to 80% Professional-Grade

| Phase | Goal | Effort | Blockers |
|-------|------|--------|----------|
| **Phase 262** | Fix critical security gaps (secrets, CVE scanning, bare excepts) | 2–4 weeks | None (can start now) |
| **Phase 263** | Increase type hints to >90% | 1–2 weeks | Depends on Phase 262 linting setup |
| **Phase 264** | Split god files; refactor check_alerts.py, send_digest.py | 1 week | Depends on type hints working |
| **Phase 265** | Implement SLOs, alert thresholds, on-call runbooks | 2–3 weeks | Depends on monitoring baseline |
| **Phase 266** | Post-mortem process + root-cause training | 1 week | None |
| **Phase 267** | Production hardening: load testing, chaos engineering | 2–3 weeks | Depends on all above |

**Target**: 80% by end of Phase 267 (6–8 weeks)

---

## Playbooks (How to Fix)

### Fix Secrets in Git
```bash
# 1. Install git-filter-repo
pip install git-filter-repo

# 2. Identify files with secrets (grep for API keys, tokens)
git log --all -S "sk_" --oneline | head -10

# 3. Purge from history
git filter-repo --invert-paths --path "scripts/auto_check.py"  # or specific files

# 4. Rotate all exposed credentials (API keys, DB passwords, tokens)
# Update .env and re-deploy

# 5. Add scanning to CI (.github/workflows/security.yml)
pip-audit --desc
```

### Add CVE Scanning
```bash
# .github/workflows/security.yml
- name: Run pip-audit
  run: pip-audit
  
# Or use safety
- name: Check dependencies
  run: safety check
```

### Convert Bare Excepts
**Before**:
```python
try:
    response = requests.get(url)
except:
    logger.error("Request failed")
```

**After**:
```python
try:
    response = requests.get(url)
except (requests.RequestException, TimeoutError) as e:
    logger.error(f"Request failed: {e}")
```

See `project-designer/PLAYBOOKS.md` for full step-by-step guides.

---

## Related Framework Rules

This review references the 8-pillar framework:

- **Pillar 1** (Architecture): Rule 1.1 (documented design), 1.2 (ADRs) ✅
- **Pillar 2** (Build Quality): Rule 2.1 (type hints), 2.4 (secrets), 2.5 (no bare excepts) ⚠️
- **Pillar 3** (Verification): Rule 3.1 (tests), 3.4 (coverage), 3.6 (no broad excepts) ✅
- **Pillar 4** (CI/CD): Rule 4.1 (CI config), 4.2 (automation), 4.3 (migrations) ✅
- **Pillar 5** (Root-Cause): Rule 5.3 (incident logs), 5.4 (retros) ❌
- **Pillar 6** (Security): Rule 6.1 (no CORS wildcard), 6.3 (secrets not in git), 6.4 (CVE scanning) ❌
- **Pillar 7** (Observability): Rule 7.2 (SLOs), 7.3 (alert thresholds) ⚠️
- **Pillar 8** (Maintainability): Rule 8.1 (file size <1000 lines), 8.2 (naming) ⚠️

See `project-designer/FRAMEWORK.md` for detailed rule definitions.

---

## Summary

**investing-platform** is a well-engineered, test-rich system with strong fundamentals (architecture, testing, CI/CD) but critical gaps in security and processes. The three **critical security gaps** (secrets in git, bare excepts, no CVE scanning) must be addressed before production use. Once fixed, the project reaches 60% and is on a clear path to 80%+ with 2–3 months of focused hardening.

**Next step**: Start Phase 262 (critical security fixes). Effort: 2–4 weeks. No blockers.

---

**Generated by Design & Bug Tracker** — logged in `/tracker` with scorecard and gaps visible in the UI.
