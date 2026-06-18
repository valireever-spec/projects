# Getting Started with Design & Bug Tracker

## Overview

This tool helps you track architecture design progress and bugs/gaps across your portfolio projects. It integrates with the 8-pillar architecture validation framework in `/home/vali/projects/project-designer/`.

## Installation (One-Time)

### Option 1: Automated Setup
```bash
cd /home/vali/projects/tracker
./setup.sh
```

### Option 2: Manual Setup

**Backend**:
```bash
cd /home/vali/projects/tracker/backend
pip install -r requirements.txt
cp .env.example .env
```

**Frontend**:
```bash
cd /home/vali/projects/tracker/frontend
npm install
```

## Running the App

Start both servers in separate terminals:

**Terminal 1 — Backend**:
```bash
cd /home/vali/projects/tracker/backend
python main.py
```
- Runs at `http://localhost:8000`
- API docs at `http://localhost:8000/docs`
- Database: `./tracker.db`

**Terminal 2 — Frontend**:
```bash
cd /home/vali/projects/tracker/frontend
npm run dev
```
- Runs at `http://localhost:5173`
- Hot reload enabled for development

## Using the Tracker

### 1. Create a Project
1. Go to Dashboard (`http://localhost:5173`)
2. Click "+ New Project"
3. Fill in: Name, Tech Stack, Description
4. Click "Create"

**Example**:
- Name: `investing-platform`
- Stack: `Python, FastAPI, React`
- Description: `Portfolio investment platform with real-time analytics`

### 2. Score Pillars (Scorecard Tab)
1. Click on a project → "Scorecard" tab
2. For each of the 8 pillars, select a status:
   - **✅ Met** — Fully implements the pillar
   - **⚠️ Partial** — Partially implements the pillar
   - **❌ Gap** — Missing or broken
   - **N/A** — Not applicable
3. Add evidence/notes for each pillar
4. Click "Save Scorecard"

**Example Evidence**:
- "ADRs documented in `/docs/adr/`"
- "90% test coverage on critical paths"
- "OWASP Top 10 reviewed quarterly"

### 3. Log Gaps & Bugs (Gaps & Bugs Tab)
1. Click "+ New Gap/Bug"
2. Fill in:
   - **Pillar**: Which pillar this gap affects
   - **Title**: Short description (e.g., "No automated test gate before production")
   - **Description**: Detailed explanation
   - **Severity**: Low / Medium / High / Critical
   - **Effort**: 1-3 days / 1-2 weeks / 2-4 weeks / 1+ months
3. Click "Create"

The gap appears in the "Discovered" column of the Kanban board.

### 4. Track Remediation (Kanban Board)
Move gaps through status columns:
1. **Discovered** → Initial findings from review
2. **Prioritized** → Ranked by impact and effort
3. **In Remediation** → Currently being fixed
4. **Done** → Completed and verified

Click the status dropdown on a card to change it.

### 5. Reference Rules & Playbooks
1. Click "Rules & Playbooks" tab
2. The framework data loads from:
   - `/home/vali/projects/project-designer/FRAMEWORK.md` (48 rules)
   - `/home/vali/projects/project-designer/PLAYBOOKS.md` (remediation guides)
   - `/home/vali/projects/project-designer/CHECKLIST.md` (scoring rubric)

Use these to guide remediation work.

## Key Concepts

### Maturity Score
Calculated as: (# Met Pillars / 8) × 100

**Example**:
- 3 pillars Met, 5 others = 37% maturity
- 6 pillars Met, 2 others = 75% maturity

### Dashboard View
Each project card shows:
- **Name & Tech Stack**
- **Maturity %** (large number, centered)
- **Gap Count** (number of open issues)
- **Pillar Status Pills** (8 colored dots showing ✅/⚠️/❌/•)

### Project Home
Four tabs provide a complete workspace:
1. **Scorecard** — Document pillar scores with evidence
2. **Gaps & Bugs** — Kanban board for tracking remediation
3. **Rules & Playbooks** — Framework reference
4. **Review History** — (Future) Dated snapshots of reviews

## Database

SQLite database at `/home/vali/projects/tracker/backend/tracker.db`

**Schema**:
- `projects` — Portfolio projects
- `reviews` — Dated review snapshots
- `scorecard_entries` — Pillar scores and evidence
- `gaps` — Discovered gaps with status and effort

To reset the database:
```bash
rm backend/tracker.db
python main.py  # Auto-creates fresh database
```

## API Quick Reference

```bash
# List all projects
curl http://localhost:8000/api/projects

# Get project detail
curl http://localhost:8000/api/projects/1

# Create project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "my-project", "tech_stack": "Python", "description": "..."}'

# Update scorecard
curl -X PUT http://localhost:8000/api/projects/1/scorecard \
  -H "Content-Type: application/json" \
  -d '[{"pillar": "Architecture Discipline", "status": "✅", "evidence": "..."}]'

# Create gap
curl -X POST http://localhost:8000/api/projects/1/gaps \
  -H "Content-Type: application/json" \
  -d '{"pillar": "CI & Safe Delivery", "title": "...", "description": "...", "severity": "High"}'

# Get framework rules
curl http://localhost:8000/api/rules

# Get playbooks
curl http://localhost:8000/api/playbooks
```

Full docs at `http://localhost:8000/docs`

## Common Tasks

### Add all 10 portfolio projects
Import from `/home/vali/projects/`:
```bash
# (Future feature) Import projects from directory
python -c "
import os
# Scan /home/vali/projects/ for project directories
# Create project records via API
"
```

### Export review report
```bash
# (Future feature) Generate PDF/JSON report
GET /api/projects/{id}/export-review
```

### Compare projects
```bash
# (Future feature) Side-by-side scorecard comparison
GET /api/compare?projects=1,2,3
```

## Troubleshooting

### Backend won't start
```bash
# Kill any process on port 8000
lsof -ti:8000 | xargs kill -9

# Try again
python main.py
```

### Frontend won't connect to API
- Check backend is running: `curl http://localhost:8000/api/projects`
- Check firewall/proxy settings
- Browser console (F12) shows CORS or connection errors

### Database locked
```bash
# Reset database
rm backend/tracker.db
python main.py
```

## Next Steps

1. **Create your first project** and score all 8 pillars
2. **Log discovered gaps** from your portfolio reviews
3. **Use Kanban board** to prioritize and track remediation
4. **Reference playbooks** to guide implementation
5. **Re-score pillars** as gaps are resolved

## Support

See `/home/vali/projects/tracker/README.md` for full documentation.

Check `/home/vali/projects/project-designer/` for framework docs:
- `FRAMEWORK.md` — 48 rules with verification methods
- `PLAYBOOKS.md` — Step-by-step remediation guides
- `CHECKLIST.md` — Scoring rubric
