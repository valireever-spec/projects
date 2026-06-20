# Archive Manifest

This document describes archived files that were moved to `.archive/` directories to save tokens and reduce cognitive load.

## Archive Locations

### 1. `/projects/.archive/assessments/` (152 KB)

**What's archived**: Assessment reports, V-Model status, bug reports, verification results from June 20.

**Why**: These are snapshots from a specific date. New sessions generate fresh assessments.

**How to access**: `cd .archive/assessments && ls -lh`

**Keep because**: Historical record of project status. Reference if you need to compare against past state.

### 2. `/projects/investing-platform/.archive/` (2.5 MB, 171 files)

#### Subcategories:

**phase-reports/** — PHASE_*, CYCLE_* development phase summaries
- Old development iterations (Phases 174–301)
- Development cycle reports
- **Keep because**: Architecture evolution history; useful for understanding decisions

**test-questions/** — GUARDIAN_*_TEST_QUESTIONS.md
- Guardian integration and practical test specifications
- **Keep because**: Reference for Guardian bot testing if reactivating

**old-assessments/** — Status reports, deployment logs, old guides
- FINAL_*, DEPLOYMENT_*, WEEK_*, REFACTOR_* progress reports
- Multiple variants of the same spec (FEATURE_USAGE_COMPLETE variants)
- **Keep because**: Deployment history; useful for recovery/audit

**duplicate-specs/** — Old test harness specifications
- Multiple versions of comprehensive test harness specs
- Backup files (*_BROKEN_BACKUP.md, *_FULL_CORRECTED.md)
- **Keep because**: Testing artifacts; reference for understanding harness evolution

## What Remains at Root

### Essential Operating Docs (keep in root)
- `CLAUDE.md` — Project setup & workflow
- `README.md` — Project overview
- `FUNCTIONAL_REQUIREMENTS.md` / `NONFUNCTIONAL_REQUIREMENTS.md` — Current requirements
- `V_MODEL_BOARD.md` — Auto-generated status (do not edit)
- `ALEMBIC_GUIDE.md` — Database migration guide
- `ARCHITECTURE_DECISION_LOG.md` — Decision history
- `DEPLOYMENT_CHECKLIST.md` — Deployment process
- `INCIDENT_RUNBOOKS.md` — On-call procedures
- `OPERATIONAL_RUNBOOK.md` — Day-to-day operations

### Still-Active Feature Docs (224 files)
- Implementation guides, strategies, playbooks
- API specs, test harnesses, deployment guides
- Guardian integration and testing docs
- Backtest, analytics, risk management specs

These remain because they document active features or are referenced during development.

## Accessing Archived Content

```bash
# View archive structure
cd investing-platform/.archive
find . -type f | head -20

# Search within archive
grep -r "Guardian" investing-platform/.archive/test-questions/

# Restore a file if needed
mv investing-platform/.archive/phase-reports/PHASE_174_SUMMARY.md investing-platform/
```

## Why Archive?

1. **Token savings**: 171 files (2.5 MB) = ~10K tokens removed from session context
2. **Reduced noise**: Claude doesn't scan archived files during conversation
3. **Historical record**: Information preserved, just not active
4. **Clean workflow**: Root only contains documents actively used or referenced

## Notes

- Archives are gitignored (`.archive/` in `.gitignore`) so they don't bloat the repo
- Modification dates are preserved, so you can find files by date if needed
- Use `ls -lt .archive/**/*.md | head` to see recently archived files

---

**Last cleaned**: June 20, 2026
**Archived**: 171 files from investing-platform + 14 from projects root
**Freed**: ~2.6 MB ≈ 10K tokens per session
