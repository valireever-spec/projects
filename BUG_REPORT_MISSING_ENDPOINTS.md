# Bug Report: Missing API Endpoints

**Date:** 2026-06-20  
**Severity:** MEDIUM  
**Status:** 🟠 IDENTIFIED - NEEDS FIX

---

## Issue Summary

Two critical API endpoints are missing from the tracker backend, preventing retrieval of individual requirements and gaps by ID.

---

## Missing Endpoints (2 total)

### 1. GET /api/projects/{project_id}/requirements/{requirement_id}

**Description:** Retrieve a single requirement by ID

**Current Status:** ❌ NOT IMPLEMENTED (405 Method Not Allowed)

**Expected Behavior:**
```
GET /api/projects/1/requirements/1
→ 200 OK
→ {
    "id": 1,
    "req_id": "FR-001",
    "description": "Data Ingestion",
    "status": "Proposed",
    "req_type": "FR",
    "category": "FR",
    ...
  }
```

**Use Cases:**
- Frontend needs to fetch and display a single requirement for editing
- Update endpoints need to verify requirement exists before updating
- Gap linking needs to validate requirement exists

**Impact:** MEDIUM
- Existing endpoints (PUT, PATCH) work fine for updates
- List endpoint (GET /requirements) returns all data
- But no way to fetch individual record efficiently

---

### 2. GET /api/projects/{project_id}/gaps/{gap_id}

**Description:** Retrieve a single gap/bug by ID

**Current Status:** ❌ NOT IMPLEMENTED (405 Method Not Allowed)

**Expected Behavior:**
```
GET /api/projects/1/gaps/1
→ 200 OK
→ {
    "id": 1,
    "title": "TEST: Interface connectivity check",
    "description": "...",
    "severity": "Medium",
    "status": "Discovered",
    "effort": "Medium",
    "pillar": "Verification & Validation",
    ...
  }
```

**Use Cases:**
- Frontend needs to display individual gap details
- Linking gaps to requirements requires fetching gap details
- Gap status updates need to verify gap exists

**Impact:** MEDIUM
- Similar situation to requirements
- Workaround: fetch from list, filter in client
- But not RESTful

---

## Existing Endpoints (for reference)

### Requirements Endpoints
- ✅ POST /api/projects/{project_id}/requirements — Create
- ✅ GET /api/projects/{project_id}/requirements — List all
- ❌ GET /api/projects/{project_id}/requirements/{requirement_id} — **MISSING**
- ✅ PUT /api/projects/{project_id}/requirements/{requirement_id} — Update
- ✅ PATCH /api/projects/{project_id}/requirements/{requirement_id} — Partial update
- ❌ DELETE /api/projects/{project_id}/requirements/{requirement_id} — Missing (not needed yet)

### Gaps Endpoints
- ✅ POST /api/projects/{project_id}/gaps — Create
- ❌ GET /api/projects/{project_id}/gaps/{gap_id} — **MISSING**
- ✅ PUT /api/projects/{project_id}/gaps/{gap_id} — Update
- ✅ PATCH /api/projects/{project_id}/gaps/{gap_id} — Partial update
- ✅ DELETE /api/projects/{project_id}/gaps/{gap_id} — Delete
- ✅ GET /api/projects/{project_id}/gaps/{gap_id}/suggest-requirements — Linked requirements
- ✅ GET /api/projects/{project_id}/gaps/{gap_id}/traceability — Traceability info

---

## Recommended Fix

Add two GET endpoints:

```python
@app.get("/api/projects/{project_id}/requirements/{requirement_id}", response_model=dict)
def get_requirement(project_id: int, requirement_id: int, db: Session = Depends(get_db)):
    """Get a single requirement by ID"""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Return same format as list endpoint
    return {
        "id": requirement.id,
        "req_id": requirement.req_id,
        "title": requirement.title,
        "description": requirement.description,
        "req_type": requirement.req_type,
        "category": requirement.category,
        "status": requirement.status,
        "acceptance_criteria": requirement.acceptance_criteria,
        "measurement_method": requirement.measurement_method,
        "target": requirement.target,
        "test_case": requirement.test_case,
    }

@app.get("/api/projects/{project_id}/gaps/{gap_id}", response_model=dict)
def get_gap(project_id: int, gap_id: int, db: Session = Depends(get_db)):
    """Get a single gap by ID"""
    gap = db.query(Gap).filter(
        Gap.id == gap_id,
        Gap.project_id == project_id
    ).first()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")
    
    return {
        "id": gap.id,
        "project_id": gap.project_id,
        "pillar": gap.pillar,
        "title": gap.title,
        "description": gap.description,
        "severity": gap.severity,
        "status": gap.status,
        "effort": gap.effort,
        "requirement_id": gap.requirement_id,
    }
```

---

## Test Cases

### Test 1: Get existing requirement
```
GET /api/projects/1/requirements/1
Expected: 200 OK with requirement data
```

### Test 2: Get non-existent requirement
```
GET /api/projects/1/requirements/99999
Expected: 404 Not Found
```

### Test 3: Get requirement from wrong project
```
GET /api/projects/2/requirements/1
Expected: 404 Not Found (requirement belongs to project 1)
```

### Test 4: Get existing gap
```
GET /api/projects/1/gaps/1
Expected: 200 OK with gap data
```

### Test 5: Get non-existent gap
```
GET /api/projects/1/gaps/99999
Expected: 404 Not Found
```

---

## Priority

**Priority:** MEDIUM
- Workaround exists: fetch from list endpoint
- Not blocking current functionality
- Would improve API completeness and RESTfulness
- Needed for future frontend features (individual gap detail pages)

---

## Related Issues

None at this time.

---

**Bug ID:** T-2024-001  
**Reported:** 2026-06-20  
**Status:** OPEN
