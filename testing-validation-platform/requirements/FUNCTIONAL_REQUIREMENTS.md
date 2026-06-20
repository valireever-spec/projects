# Functional Requirements: testing-validation-platform

Complete specification of all features and use cases for the V-Model Requirements Tracker.

---

## Overview

**Project:** testing-validation-platform  
**Tech Stack:** Python FastAPI  
**Purpose:** Central V-Model tracking tool that syncs requirements and bugs between project files and a tracker system  
**Scope:** Bidirectional sync, REST API dashboard, requirement/bug lifecycle management

---

## FR-001: Sync Requirements from Project Files to Tracker

**ID:** FR-001  
**Category:** Data Integration  
**Priority:** Critical  
**Actor:** System (automated via vmodel_sync.py)

### Use Case Flow

**Main Flow:**
1. Project owner maintains FUNCTIONAL_REQUIREMENTS.md and NONFUNCTIONAL_REQUIREMENTS.md
2. vmodel_sync.py reads both files every 5 minutes (or on-demand)
3. Parses markdown to extract requirement IDs, titles, descriptions, priority
4. Syncs to tracker: POST new requirements, UPDATE existing ones
5. Tracker validates and stores; may return conflicts
6. System logs success/failure; reports errors

**Preconditions:**
- Tracker API is accessible at configured URL
- FUNCTIONAL_REQUIREMENTS.md and NONFUNCTIONAL_REQUIREMENTS.md exist
- Requirements follow markdown format: `- **FR-001** — Description`

**Postconditions:**
- All requirements in files are present in tracker
- Requirement status (Proposed/Implemented/Validated) matches tracker
- Any parsing errors are logged

### Acceptance Criteria

- **CR-001**: Parser reads all FR-* and NFR-* lines from markdown files
- **CR-002**: Extracts: ID, description, status (optional)
- **CR-003**: New requirements are created in tracker via POST
- **CR-004**: Existing requirements are updated via PATCH (status changes, etc.)
- **CR-005**: Sync completes in <30 seconds (for typical projects with <100 reqs)
- **CR-006**: If tracker unavailable, errors are logged with retry logic
- **CR-007**: Sync can be triggered manually: `python vmodel_sync.py sync`
- **CR-008**: Sync can run on schedule: `python vmodel_sync.py --daemon`

### Test Case

- **Unit**: `tests/unit/test_vmodel_sync.py::test_parse_markdown_requirements`
- **Integration**: `tests/integration/test_sync_workflow.py::test_sync_requirements_to_tracker`
- **E2E**: `tests/e2e/test_sync_e2e.py::test_full_sync_cycle`

### Related Components

- `backend/core/vmodel_sync.py` — Main sync logic
- `requirements/FUNCTIONAL_REQUIREMENTS.md` — Source data
- `NONFUNCTIONAL_REQUIREMENTS.md` — Source data
- `tracker_client.py` — Tracker API abstraction

---

## FR-002: Import Bugs/Gaps from Tracker to V-Model Board

**ID:** FR-002  
**Category:** Data Integration  
**Priority:** Critical  
**Actor:** System (automated)

### Use Case Flow

**Main Flow:**
1. System queries tracker for all gaps/bugs in project
2. Groups gaps by status (Discovered, Prioritized, In Remediation, Done)
3. Generates V_MODEL_BOARD.md with:
   - Summary: total gaps, status breakdown, health metrics
   - Requirements section: all FR/NFR with status
   - Gaps section: all bugs with description and linked requirements
   - Traceability matrix
4. Overwrites V_MODEL_BOARD.md (read-only, auto-generated)
5. Sync runs every 5 minutes automatically

**Preconditions:**
- Tracker API is accessible
- Project exists in tracker

**Postconditions:**
- V_MODEL_BOARD.md is updated with latest tracker data
- Timestamp in file reflects sync time

### Acceptance Criteria

- **CR-001**: Queries tracker API for all gaps: GET /api/projects/{id}/gaps
- **CR-002**: Parses response; groups by status
- **CR-003**: Generates markdown V_MODEL_BOARD.md with standard sections:
  - Summary (Coverage %, Maturity %)
  - V-Model left leg (Requirements by type)
  - V-Model right leg (Bugs by status)
  - Traceability matrix (Req → Gaps mapping)
- **CR-004**: File is marked as read-only with comment: "Auto-generated; do not edit"
- **CR-005**: Sync completes in <20 seconds (typical project)
- **CR-006**: Timestamp updated to last sync time
- **CR-007**: Health metrics calculated:
  - Coverage % = (Validated requirements) / (Total requirements) × 100
  - Maturity % = (Done gaps) / (Total gaps) × 100

### Test Case

- **Unit**: `tests/unit/test_vmodel_sync.py::test_generate_vmodel_board`
- **Integration**: `tests/integration/test_sync_workflow.py::test_import_gaps_from_tracker`

### Related Components

- `backend/core/vmodel_sync.py` — Generation logic
- `V_MODEL_BOARD.md` — Output (auto-generated)
- `tracker_client.py` — API access

---

## FR-003: Provide V-Model Dashboard REST API

**ID:** FR-003  
**Category:** User Interface / API  
**Priority:** High  
**Actor:** User (web browser or API client)

### Use Case Flow

**Main Flow:**
1. User visits http://localhost:8004/
2. FastAPI server (api_server.py) serves vmodel-status.html
3. Dashboard displays:
   - Project health snapshot (Coverage %, Maturity %)
   - Requirements grid (FR/NFR with status)
   - Gaps/Bugs grid (open issues with severity)
   - Traceability matrix
4. Data is read from V_MODEL_BOARD.md (cached)
5. Dashboard auto-refreshes every 30 seconds

**Preconditions:**
- API server is running on port 8004
- V_MODEL_BOARD.md exists and is current

**Postconditions:**
- Browser displays live V-Model status
- Can navigate requirements and gaps

### Acceptance Criteria

- **CR-001**: GET / serves HTML dashboard
- **CR-002**: GET /api/vmodel/board returns JSON with structure:
  ```json
  {
    "summary": {
      "total_requirements": 22,
      "total_gaps": 8,
      "coverage_pct": 45.5,
      "maturity_pct": 50
    },
    "requirements": [...],
    "gaps": [...]
  }
  ```
- **CR-003**: Dashboard displays:
  - Summary card: Coverage %, Maturity %, Total metrics
  - Requirements table: ID, Title, Type (FR/NFR), Status
  - Gaps table: ID, Title, Severity, Status, Effort
  - Traceability matrix
- **CR-004**: Auto-refresh every 30 seconds (configurable)
- **CR-005**: Responsive design (works on mobile, tablet, desktop)
- **CR-006**: Response time: <500ms for API, <2s for page load

### Test Case

- **Unit**: `tests/unit/test_api_server.py::test_vmodel_endpoint`
- **Integration**: `tests/e2e/test_dashboard.py::test_dashboard_loads`

### Related Components

- `backend/api_server.py` — FastAPI server
- `vmodel-status.html` — Dashboard UI
- `V_MODEL_BOARD.md` — Data source

---

## FR-004: Report Bugs to Tracker (Auto-Reporting)

**ID:** FR-004  
**Category:** Bug Tracking / Integration  
**Priority:** High  
**Actor:** System (tracker_integration.py auto-reports on errors)

### Use Case Flow

**Main Flow:**
1. System encounters error (API call fails, test fails, etc.)
2. Error handler calls `report_api_error()` or `report_test_failure()`
3. Bug is created in tracker with:
   - Title: Error type + endpoint/test name
   - Description: Full error message, context, stack trace
   - Severity: High (API), Medium (test)
   - Pillar: Related 8-pillar (e.g., "Verification & Validation")
   - Status: "Discovered"
4. Tracker returns gap ID; system logs it
5. Developer is notified via tracker dashboard

**Preconditions:**
- Tracker API accessible
- Error occurs in system

**Postconditions:**
- Bug is in tracker under "Discovered" status
- Error message includes enough context for diagnosis

### Acceptance Criteria

- **CR-001**: `report_api_error(endpoint, error_message, error_type, severity)` creates gap in tracker
- **CR-002**: `report_test_failure(test_name, failure_reason, requirement_id)` creates gap in tracker
- **CR-003**: Gap includes:
  - Title: Type + identifier (e.g., "API Error: /api/signals/timeout")
  - Description: Full error message, additional context
  - Severity: Critical/High/Medium/Low
  - Pillar: Relevant 8-pillar
  - Requirement link (if applicable)
- **CR-004**: Errors don't block system; fail gracefully if tracker down
- **CR-005**: Gap ID returned and logged
- **CR-006**: Deduplication: Don't create duplicate bugs for same error within 5 minutes

### Test Case

- **Unit**: `tests/unit/test_tracker_integration.py::test_report_api_error`
- **Integration**: `tests/integration/test_auto_reporting.py::test_error_creates_gap`

### Related Components

- `backend/core/tracker_integration.py` — Main reporting logic
- `tracker_client.py` — API calls
- Error handlers in various modules

---

## FR-005: Requirement Status Lifecycle Management

**ID:** FR-005  
**Category:** Workflow / Lifecycle  
**Priority:** High  
**Actor:** Developer, QA, Product Manager

### Use Case Flow

**Main Flow:**
1. Requirement starts as "Proposed"
2. Developer implements feature; marks as "Implemented"
3. QA tests; if passes, marks as "Validated"
4. If fails, reverts to "Implemented" with notes
5. Product can accept/reject requirement: marks "Accepted" or rejects

**Preconditions:**
- Requirement exists in tracker

**Postconditions:**
- Requirement status reflects current lifecycle state
- Status history is traceable

### Acceptance Criteria

- **CR-001**: Requirement status can transition: Proposed → Implemented → Validated → Accepted
- **CR-002**: Status changes include optional notes/comments
- **CR-003**: Status changes can be made via tracker API: PATCH /requirements/{id}
- **CR-004**: Status changes trigger tracker notifications (optional)
- **CR-005**: Status history is preserved in tracker (read-only audit trail)

### Test Case

- **Integration**: `tests/integration/test_requirement_lifecycle.py::test_status_transitions`

---

## FR-006: Bug Status Lifecycle & Resolution Tracking

**ID:** FR-006  
**Category:** Workflow / Lifecycle  
**Priority:** High  
**Actor:** Developer, QA, Project Manager

### Use Case Flow

**Main Flow:**
1. Bug discovered: status = "Discovered"
2. Triaged: status = "Prioritized" (with priority/effort)
3. Assigned & worked: status = "In Remediation"
4. Fixed: developer updates status = "Done" with solution notes
5. QA re-tests; if passes, remains "Done"
6. Bug closed and archived

**Preconditions:**
- Bug exists in tracker

**Postconditions:**
- Bug status reflects resolution progress
- Solution details captured for future reference

### Acceptance Criteria

- **CR-001**: Bug lifecycle: Discovered → Prioritized → In Remediation → Done
- **CR-002**: Status changes: PATCH /gaps/{id} with status + notes
- **CR-003**: "Done" status requires solution_summary and code_file
- **CR-004**: Solution details persist in tracker
- **CR-005**: "Done" bugs can be reopened if issue recurs

### Test Case

- **Integration**: `tests/integration/test_bug_lifecycle.py::test_bug_resolution_flow`

---

## Summary

| ID | Title | Priority | Status |
|----|-------|----------|--------|
| FR-001 | Sync requirements to tracker | Critical | Implemented |
| FR-002 | Import bugs from tracker | Critical | Implemented |
| FR-003 | V-Model dashboard REST API | High | Partial |
| FR-004 | Auto-report errors to tracker | High | Partial |
| FR-005 | Requirement status lifecycle | High | Proposed |
| FR-006 | Bug status lifecycle | High | Proposed |

**Total Functional Requirements: 6**  
**Implemented: 2**  
**Partial: 2**  
**Proposed: 2**  
**Total Acceptance Criteria: 40+**
