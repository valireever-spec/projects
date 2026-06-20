# investing-platform — V-Model & Requirements Tracker

**A centralized V-Model tracking system that syncs requirements and bugs between project files and a tracker service.**

![Maturity](https://img.shields.io/badge/Maturity-Prototype-yellow) ![Tests](https://img.shields.io/badge/Tests-Planned-red) ![License](https://img.shields.io/badge/License-Internal-blue)

---

## 🎯 Purpose

The **testing-validation-platform** is a support tool for the investing-platform project that:

1. **Syncs requirements** from markdown files (FUNCTIONAL_REQUIREMENTS.md, NONFUNCTIONAL_REQUIREMENTS.md) → Central Tracker
2. **Imports bugs/gaps** from Tracker → V_MODEL_BOARD.md (auto-generated)
3. **Provides a dashboard** showing project health: requirements coverage, bug status, maturity metrics
4. **Auto-reports errors** to tracker when issues occur in production
5. **Maintains V-Model traceability** (Requirements → Design → Code → Tests)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ INVESTING-PLATFORM (main project)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  FUNCTIONAL_REQUIREMENTS.md                                 │
│  NONFUNCTIONAL_REQUIREMENTS.md                              │
│                                                              │
│  (Project owner maintains these)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ Reads (pull model)
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ TESTING-VALIDATION-PLATFORM                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  backend/core/vmodel_sync.py                                │
│  └─ Parses markdown → Syncs to Tracker (every 5 min)       │
│  └─ Imports gaps from Tracker → Writes V_MODEL_BOARD.md    │
│                                                              │
│  tracker_client.py                                          │
│  └─ Abstraction for Tracker API (report bugs, update status)│
│                                                              │
│  backend/core/tracker_integration.py                        │
│  └─ Auto-reports errors to Tracker when they occur         │
│                                                              │
│  backend/api_server.py (FastAPI)                            │
│  └─ REST API: GET /api/vmodel/board (JSON)                 │
│  └─ Serves: http://localhost:8004 (dashboard)              │
│                                                              │
│  vmodel-status.html                                         │
│  └─ Dashboard UI (auto-refreshes every 30 sec)             │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP requests
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ CENTRAL TRACKER                                              │
│ (http://127.0.0.1:8001)                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /api/projects/{id}                                         │
│  ├─ Requirements (FR-001, FR-002, ... FR-NNN)             │
│  ├─ Gaps/Bugs (automatically tracked)                      │
│  └─ Project health metrics (coverage %, maturity %)        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow

### Sync Cycle (Every 5 Minutes)

```
1. vmodel_sync.py reads FUNCTIONAL_REQUIREMENTS.md
   └─ Extracts: FR-001, FR-002, ... with descriptions, status
   
2. POST new requirements to Tracker API
   └─ Tracker stores or updates each requirement
   
3. Query Tracker for all gaps/bugs in project
   └─ Gets: ID, title, severity, status, linked requirement
   
4. Generate V_MODEL_BOARD.md
   └─ Creates: Summary, Requirements table, Gaps table, Traceability matrix
   
5. Dashboard (http://localhost:8004) displays live data
   └─ Auto-refreshes every 30 seconds
```

### Error Reporting (On-Demand)

```
1. System encounters error (API fails, test fails, etc.)
2. tracker_integration.report_api_error() called
3. Bug created in Tracker with context:
   - Title: "API Error: /api/signals"
   - Description: Full error message, stack trace
   - Severity: Critical/High/Medium/Low
   - Pillar: Related 8-pillar (e.g., "Verification & Validation")
4. Dashboard shows new gap under "Discovered"
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Central Tracker running on http://127.0.0.1:8001
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/vali/investing-platform.git
cd investing-platform

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify environment
python -c "import fastapi, requests; print('✅ Dependencies OK')"
```

### Running the Tracker System

#### Option 1: Manual Sync (One-Time)
```bash
# Sync requirements to tracker and generate V_MODEL_BOARD.md
python backend/core/vmodel_sync.py sync

# Output:
# ✅ Found project 'investing-platform' in tracker (ID: 1)
# 📋 Parsed 22 requirements from FUNCTIONAL_REQUIREMENTS.md
# 📋 Parsed 17 requirements from NONFUNCTIONAL_REQUIREMENTS.md
# ✅ Synced 39 requirements to tracker
# ✅ Generated V_MODEL_BOARD.md
```

#### Option 2: Daemon Mode (Continuous Sync)
```bash
# Run sync every 5 minutes in background
python backend/core/vmodel_sync.py --daemon

# Output:
# 🔄 Starting V-Model sync daemon (5-minute interval)
# [2026-06-20 14:30:00] ✅ Sync cycle completed
# [2026-06-20 14:35:00] ✅ Sync cycle completed
# [Ctrl+C to stop]
```

#### Option 3: Start Dashboard API
```bash
# Start FastAPI server on http://localhost:8004
python -m uvicorn backend.api_server:app --reload --port 8004

# Output:
# INFO:     Uvicorn running on http://127.0.0.1:8004 (Press CTRL+C to quit)
# INFO:     Application startup complete
```

Then open in browser:
```
http://localhost:8004/
```

### API Endpoints

```bash
# Get V-Model board as JSON
curl http://localhost:8004/api/vmodel/board

# Health check
curl http://localhost:8004/health
```

---

## 📋 Key Files

### Source Files
| File | Purpose |
|------|---------|
| `tracker_client.py` | Tracker API abstraction (report bugs, update status) |
| `backend/core/vmodel_sync.py` | Parse markdown + sync to tracker + generate board |
| `backend/core/tracker_integration.py` | Auto-report errors on exceptions |
| `backend/api_server.py` | FastAPI server for dashboard |
| `vmodel-status.html` | Dashboard UI (auto-generated) |

### Configuration Files
| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |
| `.pre-commit-config.yaml` | Git hooks (planned) |

### Requirements Files
| File | Purpose |
|------|---------|
| `requirements/FUNCTIONAL_REQUIREMENTS.md` | Feature specifications (FR-001 to FR-NNN) |
| `NONFUNCTIONAL_REQUIREMENTS.md` | Quality targets (NFR-001 to NFR-NNN) |
| `TRACEABILITY_MATRIX.md` | Requirements → Design → Code → Tests mapping |

### Auto-Generated Files
| File | Purpose |
|------|---------|
| `V_MODEL_BOARD.md` | V-Model dashboard (auto-synced from tracker, read-only) |

---

## 🧪 Testing (Planned)

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# Type checking
mypy backend/ --strict

# Linting
ruff check backend/

# Security scan
safety check
```

---

## 🔄 Workflow

### For Project Owner (investing-platform)

1. **Update requirements** in `FUNCTIONAL_REQUIREMENTS.md`:
   ```markdown
   ## FR-001: Data Ingestion
   **Status:** Proposed | Implemented | Validated
   
   Description and acceptance criteria...
   ```

2. **Run sync** to push changes to tracker:
   ```bash
   python backend/core/vmodel_sync.py sync
   ```

3. **View dashboard** to see project health:
   - Coverage: How many requirements are validated?
   - Maturity: How many bugs are fixed?
   - Traceability: Which requirements have gaps?

### For QA/Developers (when issues occur)

1. **System encounters error** → `tracker_integration.report_api_error()` auto-reports
2. **Error appears in tracker** under "Discovered" gaps
3. **Dashboard updates** automatically
4. **Developer fixes** and marks gap as "Done"

### For Dashboard Users

1. **Open** http://localhost:8004/
2. **View** requirements status (Proposed / Implemented / Validated)
3. **View** bugs/gaps by severity and status
4. **Click** on requirement to see acceptance criteria
5. **Click** on gap to see error details and recommended fix

---

## 📈 Maturity & Metrics

### Current Status
```
Architecture Maturity: 25% (Prototype)
Test Coverage: 0% (Planned)
Type Hints: 30% (Partial)
Documentation: 40% (Partial)
```

### Target Status (Phase 1 — After 1 week)
```
Architecture Maturity: 40% (Production-Safe)
Test Coverage: TBD
Type Hints: TBD
Documentation: 90%
```

See **ARCHITECTURE_ANALYSIS_20260620.md** for detailed pillar scores and remediation roadmap.

---

## 🛠️ Development

### Project Structure
```
testing-validation-platform/
├── backend/
│   ├── api_server.py              # FastAPI dashboard
│   └── core/
│       ├── vmodel_sync.py         # Sync engine
│       └── tracker_integration.py # Error reporting
├── requirements/
│   └── FUNCTIONAL_REQUIREMENTS.md # Feature specs
├── NONFUNCTIONAL_REQUIREMENTS.md  # Quality targets
├── TRACEABILITY_MATRIX.md         # Requirements mapping
├── V_MODEL_BOARD.md               # Auto-generated dashboard
├── vmodel-status.html             # Dashboard UI
├── tracker_client.py              # Tracker API client
└── requirements.txt               # Dependencies
```

### Key Modules

**tracker_client.py**
```python
from tracker_client import TrackerClient

client = TrackerClient(
    tracker_url="http://127.0.0.1:8001",
    project_name="investing-platform"
)

# Report a bug
client.report_bug(
    title="API Error: /api/signals",
    description="Endpoint times out after 60 seconds",
    pillar="Verification & Validation",
    severity="High"
)

# Update bug status
client.update_bug_status(gap_id=123, status="Done")
```

**vmodel_sync.py**
```python
from backend.core.vmodel_sync import sync_requirements, import_gaps

# Sync requirements to tracker
sync_requirements()

# Import gaps and generate board
import_gaps()
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
TRACKER_URL=http://127.0.0.1:8001
PROJECT_NAME=investing-platform
SYNC_INTERVAL=300  # 5 minutes
DASHBOARD_AUTO_REFRESH=30  # seconds
```

### Tracker Integration

The tool connects to tracker at `http://127.0.0.1:8001/api/` and:
- Creates/updates requirements
- Reports bugs automatically
- Reads gaps and health metrics
- Syncs V-Model board

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **README.md** | This file — quick start & overview |
| **CLAUDE.md** | Guidance for Claude Code (this AI) |
| **ARCHITECTURE_ANALYSIS_20260620.md** | 8-pillar assessment + 3-phase roadmap |
| **FUNCTIONAL_REQUIREMENTS.md** | 6 features with acceptance criteria |
| **NONFUNCTIONAL_REQUIREMENTS.md** | 17 quality targets with metrics |
| **TRACEABILITY_MATRIX.md** | Requirements → Code → Tests mapping |
| **V_MODEL_BOARD.md** | Live project health (auto-generated) |

---

## 🐛 Troubleshooting

### "Tracker not found" Error
```
❌ Failed to connect to tracker
```
**Solution:** Ensure tracker is running on http://127.0.0.1:8001
```bash
curl http://127.0.0.1:8001/health
# Should return: {"status": "ok"}
```

### "vmodel-status.html not found"
```
❌ vmodel-status.html not found
```
**Solution:** File should exist in project root. Verify:
```bash
ls -la vmodel-status.html
```

### Sync Stuck or Hanging
```bash
# Check logs
tail -f sync.log

# Kill process and retry
pkill -f vmodel_sync.py
python backend/core/vmodel_sync.py sync
```

---

## 📞 Support

- **Issues?** Update gap in tracker or check logs
- **Questions?** Review ARCHITECTURE_ANALYSIS_20260620.md
- **Contributing?** See FUNCTIONAL_REQUIREMENTS.md for current work

---

## 📝 Next Steps

1. **Phase 1** ✅ (Just completed):
   - ✅ Fixed project name (investing-platform)
   - ✅ Created requirements.txt
   - ✅ Created README.md
   - ⏳ Add error recovery + centralize config

2. **Phase 2** (Next week):
   - [ ] Create test suite (80% coverage)
   - [ ] Add type hints (mypy strict)
   - [ ] Add Pydantic validation

3. **Phase 3** (2–3 weeks):
   - [ ] GitHub Actions CI pipeline
   - [ ] Pre-commit hooks
   - [ ] Dependency scanning

See **ARCHITECTURE_ANALYSIS_20260620.md** for detailed roadmap.

---

## 📄 License

Internal project. See organization policies.

---

**Last Updated:** 2026-06-20  
**Maturity:** Prototype (25%) → Target: Production-Ready (80%)  
**Owner:** investing-platform team
