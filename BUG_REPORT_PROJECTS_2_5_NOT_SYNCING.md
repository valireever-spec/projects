# Bug Report: Projects 2-5 Requirements Not Syncing

**Date:** 2026-06-20  
**Severity:** 🔴 CRITICAL  
**Status:** ⚠️ IDENTIFIED - NEEDS FIX  
**Impact:** 4 projects (business-dev-platform, network-automation, skill-creator, testing-validation-platform) have unsync'd requirements

---

## ISSUE SUMMARY

Projects 2-5 have requirement files with content but **ZERO requirements are synced to the tracker**.

---

## EVIDENCE

### Project Status
```
Project 1: investing-platform
  ✅ SYNCED: 22 requirements in tracker
  ✅ Source: 12 FR + 10 NFR files
  ✅ Status: WORKING CORRECTLY

Project 2: business-dev-platform
  ❌ NOT SYNCED: 0 requirements in tracker
  ⚠️ Source: 19 NFR in file
  ❌ Status: BROKEN - data exists but not synced

Project 3: network-automation
  ❌ NOT SYNCED: 0 requirements in tracker
  ⚠️ Source: 19 NFR in file
  ❌ Status: BROKEN - data exists but not synced

Project 4: skill-creator
  ❌ NOT SYNCED: 0 requirements in tracker
  ⚠️ Source: 19 NFR in file
  ❌ Status: BROKEN - data exists but not synced

Project 5: testing-validation-platform
  ❌ NOT SYNCED: 0 requirements in tracker
  ⚠️ Source: 19 NFR in file
  ❌ Status: BROKEN - data exists but not synced
```

### Total Impact
- **Requirements in source files:** 4 × 19 = **76 requirements**
- **Requirements in tracker:** 0
- **Gap:** **76 unsync'd requirements** (all projects except investing-platform)

---

## ROOT CAUSE ANALYSIS

### Problem 1: vmodel_sync.py is hardcoded for investing-platform
- **File:** `investing-platform/backend/core/vmodel_sync.py`
- **Issue:** Script only works for investing-platform, not other projects
- **Code:** 
  ```python
  TRACKER_URL = "http://127.0.0.1:8001"
  PROJECT_NAME = "investing-platform"  # ← HARDCODED
  PROJECT_ID = 1  # ← HARDCODED
  ```

### Problem 2: sync_all_projects.py doesn't sync requirements
- **File:** `/home/vali/projects/sync_all_projects.py` (created in Iteration 2)
- **Issue:** Script only syncs gaps/bugs, not requirements
- **Missing:** No requirement file parsing or syncing logic

### Problem 3: No background sync configured for other projects
- **Issue:** Only investing-platform has automated sync
- **Missing:** Cron jobs or background tasks for projects 2-5

---

## WHAT SHOULD HAPPEN

### Expected Behavior
1. Each project has its own sync script OR
2. Single multi-project sync that handles all 5 projects OR
3. Tracker's auto-import discovers and syncs requirements automatically

### Current Behavior
- investing-platform: Manual sync works (hardcoded)
- Projects 2-5: No sync exists, requirements stuck in files

---

## RECOMMENDED FIXES

### Option 1: Create Multi-Project Sync Script (RECOMMENDED)
Modify `sync_all_projects.py` to sync **requirements** in addition to gaps:

```python
def sync_requirements_for_project(project_id: int, project_path: Path) -> int:
    """Sync requirements from project files"""
    fr_file = project_path / "FUNCTIONAL_REQUIREMENTS.md"
    nfr_file = project_path / "NONFUNCTIONAL_REQUIREMENTS.md"
    
    all_requirements = []
    if fr_file.exists():
        all_requirements.extend(parse_markdown_requirements(fr_file))
    if nfr_file.exists():
        all_requirements.extend(parse_markdown_requirements(nfr_file))
    
    return push_requirements_to_tracker(project_id, all_requirements)
```

### Option 2: Refactor vmodel_sync.py to be parametric
Make it work for any project by passing project name as argument:

```python
def main(project_name: str):
    project_id = get_or_create_project(project_name)
    project_root = Path(f"/home/vali/projects/{project_name}")
    # ... rest of sync logic
```

Then call for each project:
```bash
python vmodel_sync.py investing-platform
python vmodel_sync.py business-dev-platform
python vmodel_sync.py network-automation
# etc.
```

### Option 3: Use Tracker's Auto-Import Feature
If tracker has auto-import capability, enable it to discover and import requirements automatically.

---

## TESTING PLAN

Once fixed, verify:

```
Test 1: Run sync for project 2
  GET /api/projects/2/requirements
  Expected: 19 requirements (from NONFUNCTIONAL_REQUIREMENTS.md)
  
Test 2: Run sync for all 4 projects
  GET /api/projects/2 → /api/projects/5
  Expected: Each shows their synced requirements
  
Test 3: Verify idempotency
  Run sync twice for each project
  Expected: Same counts, no duplicates
  
Test 4: Verify data integrity
  Check all requirements have:
    - req_id
    - description
    - status
    - req_type
    - category
  Expected: 100% populated
```

---

## PRIORITY & EFFORT

**Priority:** 🔴 CRITICAL (76 requirements unsync'd)

**Effort Estimate:**
- Option 1 (extend sync_all_projects.py): 1-2 hours
- Option 2 (refactor vmodel_sync.py): 2-3 hours
- Option 3 (tracker auto-import): 1-2 hours (if available)

**Recommended:** Start with Option 1 (simplest, lowest risk)

---

## QUESTIONS FOR INVESTIGATION

1. Why do projects 2-5 have NONFUNCTIONAL_REQUIREMENTS.md but no FUNCTIONAL_REQUIREMENTS.md?
2. Are those 19 NFR entries in each file actually valid requirements?
3. Should we sync those immediately or wait for project teams to review first?
4. Do projects 2-5 also have gaps/bugs in V_MODEL_BOARD.md that need syncing?

---

## NEXT STEPS

1. **Immediate:** Create comprehensive sync for projects 2-5 requirements
2. **Short-term:** Test and verify all 76 requirements sync correctly
3. **Medium-term:** Set up background sync for all projects
4. **Long-term:** Implement tracker auto-import if not already available

---

**Bug ID:** T-2024-002  
**Severity:** CRITICAL (data not syncing)  
**Discovered:** Iteration 2, Final Verification  
**Status:** OPEN - NEEDS IMPLEMENTATION
