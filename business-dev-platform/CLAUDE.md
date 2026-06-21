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


## Tracker Integration: V-Model & Requirements ✅

This project is **fully integrated with the central tracker** for bidirectional requirements and bug tracking.

### Dashboard & Visibility (NEW)
- **UI Dashboard:** http://localhost:8000/api/vmodel/board (or embedded in frontend)
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
- **On error:** Auto-report to tracker via tracker_integration middleware

### Key Files
- `./V_MODEL_BOARD.md` — Auto-generated; **READ-ONLY** (synced from tracker)
- `./FUNCTIONAL_REQUIREMENTS.md` — **YOU MAINTAIN THIS**
- `./NONFUNCTIONAL_REQUIREMENTS.md` — **YOU MAINTAIN THIS**
- `./backend/core/tracker_integration.py` — Bidirectional sync client

### Quick Commands
```bash
# View requirements and bugs in UI
open http://localhost:8000

# Push requirements to tracker (or edit files, waits 5 min for auto-sync)
curl http://127.0.0.1:5173/sync/business-dev-platform

# Check current V-Model coverage
curl http://localhost:8000/api/vmodel/coverage
```

### When Requirements Change
1. Edit `FUNCTIONAL_REQUIREMENTS.md` or `NONFUNCTIONAL_REQUIREMENTS.md`
2. Commit the change
3. **Wait 5 minutes** for tracker to sync (or manually trigger via curl above)
4. Check `V_MODEL_BOARD.md` to verify import was successful
5. Update requirement status in tracker UI: http://localhost:5173

See V_MODEL_BOARD.md in your project root for current phase progress.

---

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: Business Dev Platform

A wizard-driven web application that helps users discover trending business domains in Germany with low competition, then guides them through a comprehensive 6-step business plan: market analysis, financial projections, risk assessment, and German regulatory compliance.

**Status:** MVP-Grade (Production Ready) ⭐⭐⭐⭐  
**Latest Phase:** Phase 5 Complete (2026-05-18)

---

## Architecture at a Glance

**Backend Stack:** Python 3.12+ + FastAPI + Pydantic v2  
**Frontend:** Single-file HTML SPA with Chart.js, no build tooling  
**Storage:** File-backed sessions (JSON) + file-backed API cache with TTL  
**APIs:** 7 free external sources (Google Trends, Eurostat, Destatis, ECB, World Bank, NewsAPI, Wikipedia)

**Key Pattern:** Data layer → Analytics layer → Services layer → API routers  
- **data/**: Pure API clients with graceful degradation
- **analytics/**: Pure functions (domain scoring, financial modeling, risk assessment)
- **services/**: Orchestration (combines data + analytics)
- **api/routers/**: HTTP endpoints

**No database, no authentication, no external dependencies beyond requests/pytrends.**

---

## Common Development Commands

### Initial Setup
```bash
cd /home/vali/projects/business-dev-platform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Development Server
```bash
source venv/bin/activate
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
# Open http://localhost:8000
```

### Run Tests
```bash
# All tests with validation framework (RECOMMENDED)
./run_validation.sh

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_domain_scorer.py -v

# Single test
pytest tests/unit/test_domain_scorer.py::test_total_score_composition -v

# With code coverage
pytest tests/ --cov=backend --cov-report=html
# Open htmlcov/index.html in browser
```

### Service Management (Production)
```bash
# First time: Install as systemd service
sudo /home/vali/projects/business-dev-platform/manage_service.sh install

# Start/stop
sudo /home/vali/projects/business-dev-platform/manage_service.sh start
sudo /home/vali/projects/business-dev-platform/manage_service.sh stop

# Check status and get port
sudo /home/vali/projects/business-dev-platform/manage_service.sh status

# View real-time logs
sudo /home/vali/projects/business-dev-platform/manage_service.sh logs

# Enable auto-start at boot
sudo /home/vali/projects/business-dev-platform/manage_service.sh enable
```

---

## Data Flow: The 6-Step Wizard

**Frontend → Session → Services → Routers → Response**

### Step 1: Domain Discovery
- `GET /domains/trending` → domain_service.py → Returns 10 scored domains
- Source: google_trends.py, eurostat.py, german_domains.json (seed data)
- Stored in session["profile"]["domain_slug"]

### Step 2: Business Profile
- `PATCH /sessions/{id}` with profile data → Saved to sessions/{id}.json
- Required fields: business_name, legal_form, city, unique_value_proposition, founder_background, startup_budget

### Step 3: Market Analysis
- `GET /market/analysis?domain=X&city=Y` → market_service.py
- Returns: market size, growth rate, competition level, news, barriers
- Analytics: market_sizer.py, competitor_analyzer.py

### Step 4: Financial Projections
- `POST /financials/project` with revenue_model → financial_service.py → financial_model.py
- Returns: 36-month P&L, break-even month, 3 scenarios (conservative/base/optimistic)
- Stored in session["financial_projection"]

### Step 5: Risk & Regulatory
- `GET /risk/assess?session_id=X&domain=Y` → risk_scorer.py (8-dimension matrix)
- `GET /risk/regulatory?domain=Y&legal_form=Z` → regulatory.py (hardcoded German law)
- Stored in session["risk_assessment"]

### Step 6: Plan Review & Export
- `GET /export/{session_id}/summary` → plan_service.py (assembles 8-section plan)
- `GET /export/plan/{session_id}/markdown` → markdown_generator.py (downloadable .md)
- `GET /export/plan/{session_id}/html` → html_generator.py + jinja2 template (printable HTML)

---

## Key Design Decisions

### Why File-Backed Sessions?
Sessions are small (<50KB), no concurrent writes, portable. Trade-off: scales to ~1000 concurrent users max. For production scale, use PostgreSQL.

### Why Hardcoded Regulatory Data?
German law in `regulatory.py` doesn't change frequently. Hardcoded with `gesetze-im-internet.de` links = no scraping failures, auditable, easy to version-control updates.

### Why TTL File Cache?
API rate limits are strict. File cache with TTL (google_trends: 6h, eurostat: 24h) avoids duplicate calls. No background job needed—cache checked on read.

### Why Graceful Degradation?
APIs fail. All data/ modules return cached/fallback values. `german_domains.json` provides seed data if APIs unavailable. Platform never crashes due to external API failures.

### Why Pure Analytics Functions?
domain_scorer.py, financial_model.py, risk_scorer.py take inputs → return outputs, no I/O. Testable (130+ unit tests), composable, no hidden state.

---

## Critical Data Structures

### Domain Score (0-100)
```
trend_momentum (0-30): Google Trends YoY growth
+ market_growth (0-25): Eurostat sector CAGR vs GDP
+ competition_density (0-25, inverted): businesses per 1000 residents
+ registration_momentum (0-20): new business delta YoY
= Total (0-100)

Grades: Excellent ≥80, Good ≥60, Moderate ≥40, Saturated <40
```

### Financial Projections
```
Inputs: revenue_model, monthly_revenue_estimate, startup_costs, legal_form, city, sector
Outputs: 36-month P&L array with:
  - Revenue ramp (M1: 30%, M2: 50%, M3-5: 70%→90%, M6+: 100%)
  - Fixed costs (salary + city index, office, software, insurance)
  - Variable costs (COGS % of revenue, depends on model)
  - Tax (0% for M1-12, then 25% on positive EBITDA)
  - Break-even month (fixed costs ÷ contribution margin ratio)

Scenarios: conservative (0.6x), base (1.0x), optimistic (1.5x)
```

### Risk Matrix (8 Dimensions)
```
1. Market saturation (domain-specific)
2. Regulatory risk (domain + legal form specific)
3. Funding/cash flow risk (based on break-even month)
4. Labor market risk (sector + city specific)
5. Technology disruption risk (AI/ML vulnerability)
6. Macroeconomic risk (inflation, default 2%)
7. Operational risk (legal form specific)
8. Competition risk (domain-specific)

Each: likelihood (1-5) × impact (1-5) = score (0-20)
Total: 0-160, normalized to 0-100
```

---

## Testing Framework: 130+ Tests

### Unit Tests (90 tests)
Located in `tests/unit/`:
- **test_domain_scorer.py** (25 tests): Algorithm correctness, bounds, monotonicity, grading
- **test_financial_model.py** (35 tests): Break-even formula, revenue ramp, tax, scenarios, plausibility
- **test_risk_scorer.py** (30 tests): 8-dimension structure, color mapping, break-even influence

Each test validates both **correctness** (formula works) and **plausibility** (result makes business sense).

### Integration Tests (40 tests)
Located in `tests/integration/`:
- **test_export.py** (12 tests): Markdown/HTML export, session not found errors, file headers
- **test_system_validation.py** (15+ tests): End-to-end workflow, data plausibility, consistency

### Run Tests
```bash
./run_validation.sh                                # All tests + coverage
pytest tests/unit/test_domain_scorer.py -v        # Single module
pytest tests/unit/test_domain_scorer.py::test_total_score_composition -v  # Single test
```

**Expected:** 130 tests pass, 82% coverage. Code quality is validated before any merge.

---

## External API Integration

All APIs in `backend/data/` with graceful degradation:

| API | Module | Cache TTL | Fallback |
|-----|--------|-----------|----------|
| Google Trends | google_trends.py | 6h | Keywords from german_domains.json |
| Eurostat REST | eurostat.py | 24h | Last cached value |
| Destatis GENESIS | destatis.py | 24h | Eurostat as substitute |
| ECB Data | ecb.py | 1h | Hardcoded: inflation 2.8%, Euribor 3.2% |
| World Bank | world_bank.py | 24h | ECB data for macro |
| NewsAPI | news.py | 2h | Empty list (optional feature) |
| Wikipedia MediaWiki | wikipedia.py | 48h | german_domains.json description |

**Cache file format:** `cache/{source}_{hash(key)}.json` with `{ts, ttl, data}` structure.

---

## Frontend Conventions

**Single HTML file** (`frontend/index.html`) with 6 steps, Chart.js, no build process.

### Auto-Save Pattern
Form inputs → debounced PATCH request (800ms) → updates `sessions/{id}.json` → localStorage keeps session_id

### Responsive Design
Sidebar + main content. On mobile, sidebar collapses. All forms stack vertically. Uses CSS Grid.

### Session Persistence
`localStorage.getItem("session_id")` + `localStorage.getItem("current_step")` ensures wizard state survives page reloads.

---

## Validation & Plausibility

See **VALIDATION_GUIDE.md** (30 pages) and **TESTING_SUMMARY.md** for:
- What each test validates (algorithm vs. business logic vs. integration)
- Confidence levels for each component (100% algorithm, 85% accuracy needs backtesting)
- Reference data (Stripe SaaS benchmarks, Eurostat sector data, etc.)
- How to extend testing with your own domains

**Quick answer:** Are the scores correct?
- ✅ Algorithm: 100% correct (25 unit tests)
- ⚠️ Accuracy: 85% (needs real business backtesting in Phase 6)

---

## Deployment

### Development
```bash
source venv/bin/activate
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production (Systemd Service)
```bash
sudo /home/vali/projects/business-dev-platform/manage_service.sh install
sudo systemctl start business-dev-platform
sudo systemctl enable business-dev-platform
```

Auto-detects available port (tries 8000-8010). Logs to `/home/vali/projects/business-dev-platform/logs/app.log`.

### Environment Variables
```bash
# .env (optional)
DEBUG=True
PORT=8000
NEWSAPI_KEY=<optional, for news integration>
ANTHROPIC_API_KEY=<optional, for future AI features>
```

---

## What to Focus On When Editing

### Adding a New Analytics Algorithm
1. Add pure function to `backend/analytics/new_module.py`
2. Add 10+ unit tests in `tests/unit/test_new_module.py` covering:
   - Algorithm correctness (inputs → expected outputs)
   - Boundary conditions (0, max, negative)
   - Plausibility (does result make business sense?)
3. Call from `backend/services/service_name.py`
4. Expose via `backend/api/routers/router_name.py`
5. Test end-to-end: add integration test in `tests/integration/test_system_validation.py`

### Modifying API Response
1. Update Pydantic model in `backend/models/`
2. Update corresponding router in `backend/api/routers/`
3. Update frontend HTML to handle new fields
4. Update tests if logic changed

### Changing Financial Model Assumptions
1. Edit `backend/analytics/financial_model.py`
2. Update unit tests if formula changed
3. Run validation: `./run_validation.sh`
4. Check if results still plausible (Year 3 > Year 1, break-even < 36 months)

### Extending German Regulatory Data
1. Update `backend/analytics/regulatory.py` with reference to `gesetze-im-internet.de`
2. Don't add without link to official source
3. Update integration tests in `tests/integration/test_system_validation.py`

---

## Common Issues & Solutions

### "mkd: command not found" when starting service
Service runs in minimal environment. Use `/bin/mkdir` in scripts. Already fixed in `start_service.sh`.

### Google Trends API slow/failing
Expected. `pytrends` is unofficial. Falls back to `german_domains.json` keywords. For production, upgrade to Similarweb or SerpAPI.

### Session file not found
Check `SESSIONS_DIR` in `backend/core/config.py`. Default: `./sessions/`. Ensure directory exists and is writable.

### Tests fail with "fixture not found"
Ensure `tests/unit/` and `tests/integration/` have `__init__.py`. Already present.

---

## Next Phases (Post-MVP)

**Phase 6 (Validation)** — 2 weeks
- Confidence intervals (±20% on projections)
- Sensitivity analysis ("what if" scenarios)
- Historical backtesting (100 real businesses)
- User feedback loop

**Phase 7 (Monetization)** — 4 weeks
- JWT authentication
- PostgreSQL for sessions + audit log
- PDF export with branding
- Premium features (advanced scenarios, API)

**Phase 8 (Scale)** — 8 weeks
- Multi-country (Austria, Switzerland)
- B2B API for accountants
- ML model fine-tuning on 10K+ businesses

---

## Key Files Reference

| File | Purpose | When to Edit |
|------|---------|--------------|
| `backend/analytics/domain_scorer.py` | Domain scoring algorithm | Adjust weights (trend, market, competition, registration) |
| `backend/analytics/financial_model.py` | 36-month P&L engine | Change revenue ramp, tax %, startup cost assumptions |
| `backend/analytics/risk_scorer.py` | 8-dimension risk matrix | Add/remove dimensions, change scoring |
| `backend/analytics/regulatory.py` | German compliance checklist | Update requirements, costs, timelines |
| `data/german_domains.json` | 40 seed domains | Add sectors, adjust margins, wage indices |
| `frontend/index.html` | 6-step wizard | UI changes, form validation, Chart.js settings |
| `tests/unit/test_*.py` | Algorithm validation | When algorithms change, update tests first |
| `tests/integration/test_system_validation.py` | End-to-end validation | After major changes, add plausibility checks |

---

## End-of-Phase Workflow

**At the end of each phase, follow this checklist:**

1. ✅ Run all validation tests
   ```bash
   ./run_validation.sh  # Expect: 130+ tests, 82%+ coverage
   ```

2. ✅ Generate phase completion report
   - Use `PHASE_COMPLETION_TEMPLATE.md` as template
   - Name it `PHASE_X_COMPLETION_REPORT.md`
   - Include: milestone reached, tests passing, path forward

3. ✅ Display in console:
   ```
   ════════════════════════════════════════
   Phase X: [Name] ✅ COMPLETE
   ════════════════════════════════════════
   ✅ Tests: 130/130 passing
   ✅ Coverage: 82%
   ✅ Status: [MVP/Credible MVP/Enterprise]
   
   📈 Path to High-Maturity:
   Phase X → MVP ⭐⭐⭐⭐
   Phase X+1 → Credible MVP ⭐⭐⭐⭐⭐
   Phase X+2 → Enterprise ⭐⭐⭐⭐⭐
   
   Next: [Phase X+1 goals]
   ════════════════════════════════════════
   ```

4. ✅ Update CLAUDE.md with new patterns/commands added

**See:** `PHASE_5_COMPLETION_REPORT.md` for example

---

## For Your Reference

- **Project Start:** May 17, 2026
- **Phase 5 Completion:** May 18, 2026
- **Current Status:** MVP-Grade (⭐⭐⭐⭐)
- **Codebase Size:** ~4,000 lines (backend) + 1,500 lines (frontend) + 2,000 lines (tests)
- **Test Count:** 130+ (82% coverage)
- **API Endpoints:** 25+
- **External APIs:** 7 (all with graceful fallback)
- **Wizard Steps:** 6 (all complete)
- **Path to Enterprise:** 2-3 more phases (6-14 weeks)
