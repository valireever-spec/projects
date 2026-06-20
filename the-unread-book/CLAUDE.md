# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working 
with code in this repository.

## Tracker Integration: V-Model & Requirements

This project participates in a portfolio-wide **requirements tracking system**.
All requirements are synced bidirectionally with a central tracker.

**Your Project Files:**
- `./V_MODEL_BOARD.md` — Auto-generated board showing phase progress
  (coverage %, requirements status, linked bugs)
- `./FUNCTIONAL_REQUIREMENTS.md` — Feature specs you maintain
- `./NONFUNCTIONAL_REQUIREMENTS.md` — Performance/reliability specs you maintain

**Workflow:**
1. Edit FUNCTIONAL/NONFUNCTIONAL_REQUIREMENTS.md
2. Tracker auto-imports every 5 minutes
3. Update status in tracker UI as you implement (Proposed → Validated)
4. View your phase progress in V_MODEL_BOARD.md
5. Link bugs to requirements when issues found

**Tracker Dashboard:** http://localhost:5173

**Auto-Sync (every 5 minutes):**
- Requirements imported from your files → Tracker DB
- V_MODEL_BOARD.md exported to your project
- Requirement status updates flow back to your board

See V_MODEL_BOARD.md in your project root for current phase progress.

---

