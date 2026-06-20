# CLAUDE.md

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

