# UI Navigation Guide - Where to Find Everything

Access the tracker dashboard at: **http://localhost:5173**

---

## 📊 **Main Dashboard** (Home Page)

**URL**: `http://localhost:5173`

Shows all 19 projects in a table:

| Column | Shows |
|--------|-------|
| Project Name | Name with link to project details |
| Gaps | 🔴 Number of open bugs/gaps |
| Maturity | 📈 % score (0-100%) |
| Description | Tech stack info |

**What you can do**:
- ✅ Click project name → view project details page
- ✅ See at-a-glance gap count for each project
- ✅ Identify which projects have the most issues

**What's missing**:
- ❌ Requirement count per project
- ❌ Quick filter by gap severity
- ❌ Portfolio-wide metrics

---

## 🎯 **Portfolio Dashboard** (Cross-Project View)

**URL**: `http://localhost:5173/portfolio`

Shows aggregate metrics across all 19 projects:

| Section | Shows |
|---------|-------|
| Health Card | Overall maturity score (A-F grade) |
| Coverage % | Requirements covered per project |
| FR/NFR Breakdown | Count of functional vs non-functional requirements |
| Project Table | All projects with health status |
| Requirements At-Risk | Which requirements have bugs |

**What you can do**:
- ✅ See portfolio-wide health score
- ✅ Identify which projects are most mature
- ✅ View which requirements are most at-risk (have bugs)
- ✅ Compare project status side-by-side

**What's missing**:
- ❌ Roadmap timeline
- ❌ Solution tracking (which bugs are fixed)
- ❌ Project trends over time

---

## 📁 **Project Details Page** (Individual Project)

**URL**: `http://localhost:5173/project/1` (replacing "1" with project ID)

For **investing-platform**, the project detail page has 5 main tabs:

### **Tab 1: Scorecard** (8-Pillar Framework)

Shows the 8 pillars of architecture excellence:

```
┌─────────────────────────────────┐
│ Architecture Discipline         │ ✅ Met / ⚠️ Partial / ❌ Gap
├─────────────────────────────────┤
│ Build Quality In                │ ⚠️ Partial
├─────────────────────────────────┤
│ Verification & Validation       │ ❌ Gap (has bugs)
├─────────────────────────────────┤
│ Continuous Integration & CD     │ ✅ Met
├─────────────────────────────────┤
│ Root-Cause Driven Improvement   │ ❌ Gap
├─────────────────────────────────┤
│ Security & Privacy by Design    │ ✅ Met
├─────────────────────────────────┤
│ Observability & Telemetry       │ ⚠️ Partial
├─────────────────────────────────┤
│ Maintainability & Sustainable   │ ⚠️ Partial
└─────────────────────────────────┘
```

**Shows**:
- Status of each pillar (Met/Partial/Gap)
- Evidence notes for each pillar
- Last updated timestamp

**What you can do**:
- ✅ Click to edit pillar status and add evidence
- ✅ Identify architecture weaknesses by pillar
- ✅ Track which pillars have gaps

---

### **Tab 2: Gaps & Bugs** (Bug Tracker Board)

Shows all bugs/gaps tracked for the project (the 5 critical bugs for investing-platform):

**Current Display**:
```
Gap ID | Title                              | Status      | Severity
───────┼────────────────────────────────────┼─────────────┼──────────
  #1   | Watchlist Add doesn't persist      | Discovered  | Critical
  #2   | Chart data returns 0 bars          | Discovered  | Critical
  #3   | Backtest metrics don't calculate   | Discovered  | Critical
  #4   | Signals tab shows no data          | Discovered  | Critical
  #5   | Risk metrics don't populate        | Discovered  | Critical
```

**What you can do**:
- ✅ View all bugs with title, status, severity
- ✅ Click bug to see full description
- ✅ Create new bug (button at top)
- ✅ Edit bug status and details
- ✅ Delete bugs (archive)

**What's shown for each bug**:
- Title
- Description
- Status (Discovered, In Remediation, Done)
- Severity (Critical, High, Medium, Low)
- Pillar category
- Effort estimate
- Linked requirement (if any)

**What's missing**:
- ❌ Solution details (when fixed)
- ❌ Code file and commit hash
- ❌ Requirement linkage display in table
- ❌ Bug age / time to fix

---

### **Tab 3: Requirements** (FR & NFR List)

Shows all requirements (22 total: 12 FR + 10 NFR):

**Display Format**:
```
Requirement | Type | Status    | Linked Gaps | Tests
────────────┼──────┼───────────┼─────────────┼──────
FR-001      | FR   | Proposed  | 0           | ✅
FR-002      | FR   | Proposed  | 1           | ✅
FR-003      | FR   | Proposed  | 1           | ✅
FR-004      | FR   | Proposed  | 1           | ✅
FR-005      | FR   | Proposed  | 1           | ✅
NFR-001     | NFR  | Proposed  | 1           | ❌
...
```

**What you can do**:
- ✅ View all requirements with ID, type, status
- ✅ See how many bugs are linked to each requirement
- ✅ Check if requirement has test cases defined

**What's shown for each requirement**:
- Requirement ID (FR-001, NFR-005, etc.)
- Type (Functional or Non-Functional)
- Status (Proposed, Accepted, Implemented, Validated)
- Linked gap count
- Test case indicator

**What's missing**:
- ❌ Full requirement details (acceptance criteria, targets)
- ❌ Actor / Use Case description
- ❌ Measurement method for NFR
- ❌ Edit requirement status via UI

---

### **Tab 4: Health & At-Risk** (Requirement Health Dashboard)

Shows which requirements are healthy vs at-risk:

**Healthy**: Requirements with no linked bugs
```
✅ HEALTHY (11 requirements)
  - FR-001: Data Ingestion (0 bugs)
  - FR-006: Discovery Screener (0 bugs)
  - FR-007: Watchlist & Task Management (0 bugs)
  - ... (8 more)
```

**At-Risk**: Requirements with bugs that need fixing
```
⚠️ AT-RISK (5 requirements)
  - FR-002: Technical Analysis (1 bug: "Chart data returns 0 bars")
  - FR-003: Strategy Backtesting (1 bug: "Backtest metrics don't calculate")
  - FR-004: Composite Signal (1 bug: "Signals tab shows no data")
  - FR-005: Portfolio Management (1 bug: "Watchlist doesn't persist")
  - NFR-001: API Latency (1 bug: "Risk metrics don't populate")
```

**Unvalidated**: Requirements not yet tested/validated
```
📝 UNVALIDATED (22 requirements)
  All 22 are in "Proposed" status - none validated yet
```

**What you can do**:
- ✅ Identify which features are most at-risk
- ✅ See which bugs block which features
- ✅ Prioritize fix work based on impact

---

### **Tab 5: Rules & Playbooks** (Reference)

Shows the architecture framework rules and remediation playbooks:

**What it displays**:
- 48 detailed rules (6 per pillar)
- Principles behind each rule
- Verification methods
- Acceptable equivalents

**What you can do**:
- ✅ Read framework guidance
- ✅ Understand what each pillar measures
- ✅ Find remediation steps for gaps

**What's missing**:
- ❌ Playbook implementation guides
- ❌ Estimated effort to fix each rule
- ❌ Best practices for specific tech stack

---

## 📄 **V-Model Board File** (Local File)

**Location**: `/home/vali/projects/investing-platform/V_MODEL_BOARD.md`

This is the **most comprehensive view** showing everything:

**Sections in the board**:

### 1. Summary
```
Total Requirements: 22 (12 FR + 10 NFR)
Total Bugs/Gaps: 5
Coverage: 0% (0/18 validated)
```

### 2. Health Status
```
Coverage: 0.0% (0/22 validated)
├─ ✅ Validated: 0
├─ ✔️ Implemented: 0
├─ 📋 Accepted: 0
└─ 📝 Proposed: 22
```

### 3. V-Model: Left Leg (Requirements)
Shows all FR and NFR with:
- Requirement ID and title
- Status icon
- Category
- Target (for NFR)
- Linked gaps count

### 4. V-Model: Right Leg (Validation & Bug Tracking)
Shows all bugs with:
- Title
- Status
- Severity
- **Violates: Which requirement**
- **Full description**
- **Solution details (when fixed)**:
  - Summary of what was changed
  - Code file location
  - Commit hash
  - Who fixed it
  - When it was fixed

### 5. Traceability Matrix
```
Requirement | Type | Status    | Gaps | Tests
────────────┼──────┼───────────┼──────┼──────
FR-001      | F    | Proposed  | 0    | ✅
FR-002      | F    | Proposed  | 1    | ✅
NFR-001     | N    | Proposed  | 1    | ❌
...
```

**How to view**: 
```bash
cat /home/vali/projects/investing-platform/V_MODEL_BOARD.md
# or
code /home/vali/projects/investing-platform/V_MODEL_BOARD.md
```

---

## 📖 **Documentation Files** (Local)

### **Design Goal & Roadmap**
**Location**: `/home/vali/projects/tracker/DESIGN_GOAL_ROADMAP_STATUS.md`

Shows:
- Design goal: "requirement-driven portfolio architecture validation"
- Complete roadmap with 6 phases
- Current status: Phase 4 Complete
- What's working vs. not yet started
- Key metrics

### **Requirement Files**
**Location**: 
- `/home/vali/projects/investing-platform/FUNCTIONAL_REQUIREMENTS.md` (12 FR)
- `/home/vali/projects/investing-platform/NONFUNCTIONAL_REQUIREMENTS.md` (10 NFR)

Shows:
- Each requirement with full details:
  - Actor (who uses it)
  - Use case (what problem it solves)
  - Acceptance criteria (how to test it)
  - Test cases (specific test names)
  - Target SLO (for NFR)
  - Measurement method

### **Bug Diagnostic Checklist**
**Location**: `/home/vali/projects/investing-platform/BUG_DIAGNOSTIC_CHECKLIST.md`

Shows step-by-step instructions to investigate each of the 5 bugs.

### **Tracker Integration Guide**
**Location**: `/home/vali/projects/investing-platform/TRACKER_INTEGRATION.md`

Shows:
- How to report bugs from code
- How to update requirement status
- Real example workflow

---

## 🔍 **Information Matrix: Where to Find What**

| What You Want | Where to Find It | Format |
|---------------|------------------|--------|
| **List of all bugs** | Gaps & Bugs tab OR V_MODEL_BOARD.md | UI table or markdown |
| **Bug description & severity** | Click bug in Gaps tab OR read V_MODEL_BOARD.md | UI modal or markdown |
| **Bug solution** | V_MODEL_BOARD.md (when fixed) | Markdown (code file + commit) |
| **All requirements** | Requirements tab OR FUNCTIONAL_REQUIREMENTS.md | UI list or markdown |
| **Requirement details (acceptance criteria)** | FUNCTIONAL_REQUIREMENTS.md | Markdown |
| **Which bugs block which features** | Health & At-Risk tab | UI summary |
| **Design goal & phases** | DESIGN_GOAL_ROADMAP_STATUS.md | Markdown |
| **Architecture standards (8 pillars)** | Scorecard tab OR Rules & Playbooks tab | UI or reference |
| **Project maturity score** | Dashboard home page OR project header | UI (%) |
| **Portfolio health** | /portfolio page | UI (A-F grade) |
| **Traceability (requirement → bug → solution)** | V_MODEL_BOARD.md OR click bug in Gaps tab | Markdown or UI |
| **How to report a bug from code** | TRACKER_INTEGRATION.md | Markdown |
| **How to fix bugs** | BUG_DIAGNOSTIC_CHECKLIST.md | Markdown |

---

## 🚀 **Quick Navigation Shortcuts**

```
Dashboard (All Projects)
    http://localhost:5173
    └─→ See all 19 projects and gap count

Portfolio Dashboard
    http://localhost:5173/portfolio
    └─→ See cross-project health, coverage %, at-risk requirements

investing-platform Project
    http://localhost:5173/project/1
    ├─→ Scorecard tab: 8-pillar framework status
    ├─→ Gaps & Bugs tab: All 5 critical bugs
    ├─→ Requirements tab: All 22 requirements
    ├─→ Health & At-Risk tab: Which reqs have bugs
    └─→ Rules & Playbooks tab: Framework reference

V-Model Board File (Complete View)
    /home/vali/projects/investing-platform/V_MODEL_BOARD.md
    └─→ Everything: requirements, bugs, solutions, traceability
```

---

## ✨ **What's Currently Visible on UI vs. What's Missing**

### ✅ **Currently Visible**
- Project list with gap count
- 8-pillar scorecard
- Bug list with status/severity
- Requirement list with linked gap count
- At-risk requirements
- Portfolio-wide health score

### ❌ **Currently NOT on UI (But in Local Files)**
- Bug solution details (code file, commit hash)
- Full requirement descriptions (acceptance criteria, targets)
- Design goal & roadmap
- Diagnostic checklists
- Traceability details
- How to integrate tracker into your code

### 🔧 **Easy Wins to Add to UI**
1. **Bug Details Modal** - Show full description, linked requirement, solution (if fixed)
2. **Requirement Details Modal** - Show acceptance criteria, actor, use case, target
3. **Traceability View** - Show requirement → bugs → solutions chain
4. **Solution Panel** - Show which bugs have been fixed with code location & commit
5. **Roadmap Timeline** - Show phases and progress
6. **Diagnostic Guide** - Link to checklist for each bug

---

## 💡 **Recommended Reading Order**

**For Project Managers / Stakeholders**:
1. Dashboard (http://localhost:5173) - see project status
2. Portfolio page (/portfolio) - see cross-project health
3. DESIGN_GOAL_ROADMAP_STATUS.md - understand the system
4. Health & At-Risk tab - see what's broken

**For Developers / QA**:
1. Gaps & Bugs tab - see what needs fixing
2. BUG_DIAGNOSTIC_CHECKLIST.md - understand each bug
3. FUNCTIONAL_REQUIREMENTS.md & NONFUNCTIONAL_REQUIREMENTS.md - see targets
4. TRACKER_INTEGRATION.md - learn how to report/update bugs

**For Architects**:
1. Scorecard tab - see pillar compliance
2. Rules & Playbooks tab - see standards
3. DESIGN_GOAL_ROADMAP_STATUS.md - see vision
4. V_MODEL_BOARD.md - see traceability

