# Design & Bug Tracker

A web-based tool for tracking architecture design progress and bugs/gaps across your portfolio projects using the 8-pillar architecture validation framework.

## Features

- **Project Dashboard** — View all projects with maturity scores, 8-pillar status, and gap counts
- **Project Homes** — Dedicated workspace per project with 4 tabs:
  - **Scorecard** — Score each pillar (✅ Met / ⚠️ Partial / ❌ Gap / N/A) with evidence
  - **Gaps & Bugs Board** — Kanban-style tracking (Discovered → Prioritized → In Remediation → Done)
  - **Rules & Playbooks** — Reference framework rules and remediation guides
  - **Review History** — Track dated review snapshots
- **Framework Integration** — Links to FRAMEWORK.md, PLAYBOOKS.md, and CHECKLIST.md from project-designer/
- **SQLite Persistence** — Simple file-based database for projects, reviews, and gaps

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: React + React Router + Axios
- **Dev Server**: Vite

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Setup

1. **Install backend dependencies**:
   ```bash
   cd /home/vali/projects/tracker/backend
   pip install -r requirements.txt
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Install frontend dependencies**:
   ```bash
   cd /home/vali/projects/tracker/frontend
   npm install
   ```

### Run Locally

**Terminal 1 — Backend (FastAPI)**:
```bash
cd /home/vali/projects/tracker/backend
python main.py
```
Backend runs at `http://localhost:8000`  
API docs available at `http://localhost:8000/docs`

**Terminal 2 — Frontend (React)**:
```bash
cd /home/vali/projects/tracker/frontend
npm run dev
```
Frontend runs at `http://localhost:5173`

### Usage

1. **Dashboard** (`/`)
   - See all portfolio projects with maturity scores
   - Click to open a project or create a new one

2. **Project Home** (`/project/:id`)
   - **Scorecard Tab**: Score each of the 8 pillars with status and evidence
   - **Gaps & Bugs Tab**: Log gaps/bugs discovered during review, track remediation
   - **Rules & Playbooks Tab**: Search framework rules and playbooks for remediation guidance

3. **Kanban Board** — Move gaps/bugs through status columns:
   - **Discovered** — Initial findings from review
   - **Prioritized** — Ranked by impact and effort
   - **In Remediation** — Currently being fixed
   - **Done** — Completed and verified

## API Endpoints

- `GET /api/projects` — List all projects
- `POST /api/projects` — Create new project
- `GET /api/projects/{id}` — Get project detail with scorecard and gaps
- `PUT /api/projects/{id}/scorecard` — Update pillar scores
- `POST /api/projects/{id}/gaps` — Create new gap/bug
- `PUT /api/projects/{id}/gaps/{gap_id}` — Update gap status
- `DELETE /api/projects/{id}/gaps/{gap_id}` — Delete gap
- `GET /api/rules` — Get 48 framework rules by pillar
- `GET /api/playbooks` — Get remediation playbooks

## Database

SQLite database at `/home/vali/projects/tracker/backend/tracker.db` (auto-created on first run)

**Tables**:
- `projects` — Portfolio projects
- `reviews` — Dated review snapshots
- `scorecard_entries` — Pillar scores and evidence
- `gaps` — Discovered gaps/bugs with status, severity, effort

## Framework Integration

The tool integrates with `/home/vali/projects/project-designer/`:
- **FRAMEWORK.md** — 48 rules (6 per pillar) with verification methods
- **PLAYBOOKS.md** — Step-by-step remediation guides (FastAPI + Python)
- **CHECKLIST.md** — Scoring rubric for manual assessment

## Next Steps

- Auto-import existing projects from `/home/vali/projects/`
- Link discovered gaps to specific rules
- Generate remediation roadmaps
- Export review reports
- Multi-user collaboration

## License

Private project.
