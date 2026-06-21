# CLAUDE.md

## Portfolio Standards & Frameworks

This project follows **three complementary frameworks** from `project-designer/` for engineering excellence:

### 1️⃣ Architecture Validation: 8-Pillar Framework

**Purpose:** Assess and improve architecture across 8 dimensions (NASA/Tesla/Apple/Toyota standards).

**Core documents:**
- **[FRAMEWORK.md](../project-designer/FRAMEWORK.md)** — 48 rules (6 per pillar) with examples
- **[CHECKLIST.md](../project-designer/CHECKLIST.md)** — Scoreable rubric (0–5 per pillar, target 4+/5)
- **[PLAYBOOKS.md](../project-designer/PLAYBOOKS.md)** — Step-by-step fixes for common gaps by pillar

**The 8 Pillars:**
1. Architecture Discipline & Traceability — Documented design, ADRs, explicit boundaries
2. Build Quality In / Error-Proofing — Type hints, linting, pinned dependencies, no secrets
3. Verification & Validation — Test gates, coverage, chaos tests, bounded complexity
4. Continuous Integration & Safe Delivery — Automated gates, reversible migrations, rollback
5. Root-Cause Driven Improvement — Post-mortems, refactor patterns, tech-debt cadence
6. Security & Privacy by Design — Least-privilege, secrets, input validation, CVE scanning
7. Observability & Telemetry — Structured logging, SLOs, dashboards, runbooks
8. Maintainability & Sustainable Pace — Domain naming, bounded file size, justified deps

**How to use:**
- Before reviews: Read [FRAMEWORK.md](../project-designer/FRAMEWORK.md) + [CHECKLIST.md](../project-designer/CHECKLIST.md)
- When fixing gaps: Link to pillar + rule, consult [PLAYBOOKS.md](../project-designer/PLAYBOOKS.md)
- Score target: 4+/5 per pillar (80%+ overall)

---

### 2️⃣ Engineering Standards: 11 Core Practices

**Purpose:** Ensure all projects follow consistent engineering practices (observability, error handling, testing, deployment, etc.).

**Core document:**
- **[ENGINEERING_STANDARDS_BASE.md](../project-designer/ENGINEERING_STANDARDS_BASE.md)** — 11 mandatory practices for all projects

**The 11 Standards:**
1. Observability — Structured logging (JSON), metrics (Prometheus), health checks
2. Error Handling — Specific exceptions, standard error responses, logging
3. Configuration — No hardcoding; all config via environment variables
4. Type Hints — All functions must have type annotations
5. Testing — ≥85% coverage; test error paths and edge cases
6. Code Organization — Files <1500 lines, single responsibility principle
7. Deployment — Health checks, graceful shutdown, readiness probes
8. Incident Response — Runbooks, SLOs, post-mortems for failures
9. Code Review — Checklist-based, minimum 2 reviewers
10. Documentation — Docstrings, README, architecture diagrams
11. Git Standards — Conventional commits, GPG signing recommended

**How to use:**
- New code: Follow the 11 standards from day one
- Reviews: Check against standards as part of code review
- Refactoring: Prioritize gaps in standards (especially observability, testing, error handling)

---

### 3️⃣ Requirements-Driven V-Model

**Purpose:** Trace requirements → design → implementation → validation (tests). Every feature is testable and linked to requirements.

**Core document:**
- **[V_MODEL_REQUIREMENTS.md](../project-designer/V_MODEL_REQUIREMENTS.md)** — Full V-Model framework with templates

**The V-Model Structure:**
```
REQUIREMENTS (Left)          VALIDATION (Right)
├─ Functional Specs          ├─ System Tests
├─ Non-Functional Specs      ├─ Integration Tests
├─ Use Cases                 ├─ Unit Tests
├─ Acceptance Criteria       └─ Acceptance Tests
└─ Traceability Matrix       └─ Bugs linked to requirements
```

**How to use:**
- Document: Maintain `FUNCTIONAL_REQUIREMENTS.md` and `NONFUNCTIONAL_REQUIREMENTS.md` in project root
- Track: Use tracker's V-Model dashboard to monitor requirements status (if applicable)
- Validate: Link tests to requirements (test IDs match requirement IDs)

---

### 4️⃣ Maturity Roadmap

**Purpose:** Understand project maturity level and progression path (Prototype → Viable → Production-Ready → Mature → Exemplary).

**Core document:**
- **[MATURITY_ROADMAP.md](../project-designer/MATURITY_ROADMAP.md)** — Progression levels and next-step guidance per pillar

**Maturity Levels:**
| Level | Score | Timeline | Focus |
|-------|-------|----------|-------|
| Prototype | <40% | Weeks | Test core idea; minimal tooling |
| Viable | 40–60% | Months 1–3 | Feature-complete; basic CI/CD |
| Production-Ready | 60–80% | Months 3–6 | Defensible architecture; monitoring |
| Mature | 80–95% | Months 6–12 | Comprehensive practices; secure |
| Exemplary | 95%+ | 12+ months | Industry-leading; continuous improvement |

**How to use:**
- Assessment: Determine this project's current level
- Planning: Use roadmap to identify quick wins for next level
- Priorities: Focus on pillar gaps that block progression


This file provides guidance to Claude Code (claude.ai/code) when working 
with code in this repository.

## Tracker Integration: V-Model & Requirements ✅

This project is **fully integrated with the central tracker** for bidirectional requirements and bug tracking.

### Dashboard & Visibility (NEW)
- **V-Model Dashboard:** http://localhost:PORT/vmodel-status.html (standalone) or API endpoint
- Shows: Requirements status, linked bugs, coverage %, last sync time
- Real-time sync every 30 seconds
- Filterable by type (FR/NFR), status, severity

### Your Responsibility
**As the team maintaining this project, you are responsible for:**
1. Keeping `FUNCTIONAL_REQUIREMENTS.md` and `NONFUNCTIONAL_REQUIREMENTS.md` current
2. Updating requirement status in tracker UI as features ship (Proposed → Validated)
3. Marking bugs/gaps as discovered, and updating status as they're fixed
4. Verifying V_MODEL_BOARD.md matches reality (syncs every 5 minutes)

### How It Works
- **Every 5 minutes:** Tracker reads your requirements files → imports to DB
- **Every 5 minutes:** Tracker exports V_MODEL_BOARD.md with updated health metrics
- **Every 30 seconds:** Dashboard auto-refreshes to show live status
- **On error:** Auto-report to tracker via tracker_integration module

### Key Files
- `./V_MODEL_BOARD.md` — Auto-generated; **READ-ONLY** (synced from tracker)
- `./FUNCTIONAL_REQUIREMENTS.md` — **YOU MAINTAIN THIS**
- `./NONFUNCTIONAL_REQUIREMENTS.md` — **YOU MAINTAIN THIS**
- `./backend/core/tracker_integration.py` — Bidirectional sync client

