# Design Goal, Roadmap & Current Status

**Date**: 2026-06-20  
**Status**: Phase 4 Complete — Bidirectional Sync & Bug-Requirement Traceability Operational

---

## Design Goal (The Why)

**Build a requirement-driven portfolio architecture validation system where:**

1. **Requirements drive design** — Every architectural decision traces back to a functional or non-functional requirement
2. **Design is validated by tests** — The V-Model: left leg (requirements) ↔ right leg (tests/validation)
3. **Bugs trace to unmet requirements** — Not just "there's a bug" but "requirement X is violated"
4. **Each project owns its state** — Bidirectional sync between central tracker and project files
5. **8-pillar framework enables requirements** — The pillars ensure requirements are met (discipline, quality, verification, CI/CD, etc.)
6. **Coverage is visible** — Dashboard shows % of requirements validated, which are at-risk, which need work

**Underlying principle**: *"Who else is more aware of the data than the project itself?"* — Each project maintains its own requirements files; the tracker syncs and aggregates.

---

## Roadmap (The Phases)

### Phase 1: Core Framework ✅ DONE
- Set up 8-pillar architecture validation framework (FRAMEWORK.md, CHECKLIST.md, PLAYBOOKS.md)
- Create tracker web app with scorecard (FastAPI + React)
- Manual project import and gap tracking

### Phase 2: V-Model Requirements Framework ✅ DONE
- Add FUNCTIONAL_REQUIREMENTS.md and NONFUNCTIONAL_REQUIREMENTS.md to projects
- Create Requirement model (req_id, type, status: Proposed → Validated)
- Add requirement import endpoint
- Link gaps/bugs to requirements
- Requirement status workflow

### Phase 3: Customer-to-System Requirements Translation ✅ DONE
- Document customer requirement → system requirement translation
- Map each customer ask to FR/NFR
- Create CUSTOMER_TO_SYSTEM_REQUIREMENTS.md guide
- Enable projects to define requirements in terms of what customers need

### Phase 4: Bidirectional Sync & Bug-Requirement Traceability ✅ DONE
- Auto-import requirements from projects (every 5 min)
- Auto-export V-Model boards back to projects (every 5 min)
- Bug solution tracking (solution_summary, fixed_code_file, commit_hash, fixed_by)
- Traceability endpoint: Gap → Requirement → Solution
- Real requirements + bugs for investing-platform (proof of concept)

### Phase 5: Requirement-Driven Design Enforcement (NEXT)
- CI/CD gates: Block merge if requirement tests don't pass
- Requirement coverage gates: Cannot deploy with < 80% coverage
- Automatic requirement status updates based on test results
- SLO monitoring for NFR requirements

### Phase 6: Advanced Analytics & Roadmapping (Future)
- Requirement dependency graph (FR-001 depends on NFR-003)
- Risk prediction: which requirements likely to fail based on pattern
- Roadmap generation: auto-suggest phases based on requirement dependencies
- Compliance reporting: audit trail of requirement validation

---

## Current Status (Where We Are Now)

### ✅ What's Working

**Backend Infrastructure:**
- FastAPI + SQLAlchemy + SQLite running on port 8001
- Models: Project, Requirement, Gap, Review, ScorecardEntry
- Auto-sync scheduler running every 5 minutes
- Requirement parser for FR/NFR markdown files
- Traceability endpoint: `GET /api/projects/{id}/gaps/{gap_id}/traceability`

**Data Flow:**
- Projects define requirements in markdown (FUNCTIONAL_REQUIREMENTS.md, NONFUNCTIONAL_REQUIREMENTS.md)
- Tracker auto-imports requirements every 5 minutes via RequirementsAutoImporter
- Tracker auto-exports V-Model boards back to projects every 5 minutes
- Bugs/gaps linked to requirements they violate
- Solutions documented with code location and commit hash

**Frontend UI:**
- Dashboard showing 19 projects (http://localhost:5173)
- Portfolio dashboard with analytics
- Requirements tab per project
- V-Model board rendering with FR/NFR status

**Live Data:**
- investing-platform: 22 requirements (12 FR + 10 NFR)
- 5 real bugs tracked and linked to requirements
- 3 bugs marked FIXED with solutions documented
- 1 bug IN REMEDIATION
- 1 bug DISCOVERED

**Documentation:**
- REQUIREMENTS_DRIVEN_DESIGN.md (complete framework)
- CUSTOMER_TO_SYSTEM_REQUIREMENTS.md (translation guide)
- GETTING_STARTED.md (quick start)
- CLAUDE.md in all 19 projects (integration instructions)

### 🔄 Partially Complete

**Multi-Project Population:**
- investing-platform fully populated with real requirements and bugs
- 18 other projects have CLAUDE.md documentation explaining the system
- Auto-sync running for all 19 projects (requirements/boards update every 5 min)
- V_MODEL_BOARD.md files generated in 19 projects (showing requirements + bugs + solutions)

### ❌ Not Yet Started

**Phase 5 (CI/CD Enforcement):**
- Requirement test gates in CI/CD pipeline
- Block merges/deploys if requirement tests fail
- Automatic status updates based on test results
- SLO monitoring dashboard

**Phase 6 (Advanced Analytics):**
- Requirement dependency graphs
- Risk prediction models
- Auto-generated roadmaps
- Compliance audit trails

---

## Key Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Requirements imported | 19 projects | 1 (investing-platform demo) | 🟡 Partial |
| Bugs tracked | All discovered | 5 (investing-platform) | 🟡 Partial |
| Bug-Requirement linkage | 100% | 100% | ✅ Done |
| Solution documentation | All fixed bugs | 3/4 fixed bugs | 🟡 Partial |
| Auto-sync cycle | Every 5 min | Every 5 min | ✅ Done |
| V-Model board export | All 19 projects | 19 projects | ✅ Done |
| Traceability visible | All projects | Yes (via API + board) | ✅ Done |

---

## What's Unique About This Approach

1. **Requirements-First Architecture**: Design maturity measured by requirement coverage %, not just pillar compliance
2. **Bidirectional Sync**: Not just tracker importing from projects — tracker also exports back so projects own their state
3. **Bug Traceability**: Every bug tied to violated requirement + solution documented + code change tracked
4. **Portfolio Visibility**: Central dashboard shows which requirements at-risk across ALL 19 projects
5. **Integration with 8-Pillars**: Each pillar now explicitly supports requirement fulfillment

---

## Next Actions (If Continuing)

1. **Complete data population**: Define FR/NFR for all 18 remaining projects (templates exist)
2. **Build Phase 5**: Implement CI/CD gates that block merge if requirement tests fail
3. **Live monitoring**: Add SLO dashboard for NFR validation in production
4. **Compliance reporting**: Enable audit trail of requirement sign-offs

---

## Architecture Diagram

```
Project Files                    Central Tracker                 Dashboard
─────────────────────────────────────────────────────────────────────────

FUNCTIONAL_REQUIREMENTS.md    FR-001, FR-002, ...             📊 Portfolio View
        ↓ (auto-import)                ↓
NONFUNCTIONAL_REQUIREMENTS.md ← NFR-001, NFR-002, ...       ├─ Project Health
        ↓                             ↓                        ├─ At-Risk Reqs
        ├─ V_MODEL_BOARD.md ← Gaps/Bugs ← BUG-001, BUG-002   └─ Coverage %
        │                             ↓
        └─ Solutions documented ← Solution tracking (code file, commit)

⚙️ Bidirectional Sync Every 5 Minutes:
  • Step 1: Import requirements FROM projects TO tracker
  • Step 2: Export V-Model boards TO projects FROM tracker
  • Result: Each project has current board; tracker has all data
```

