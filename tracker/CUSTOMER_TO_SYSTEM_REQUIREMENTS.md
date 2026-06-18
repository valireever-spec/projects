# Customer Requirements → System Requirements Translation

Framework for converting customer requests into traceable system requirements.

---

## The Translation Pipeline

```
CUSTOMER REQUEST (Conversation)
    ↓
EXTRACT BUSINESS NEED (What problem are they solving?)
    ↓
TRANSLATE TO FUNCTIONAL REQUIREMENT (What must the system do?)
    ↓
TRANSLATE TO NON-FUNCTIONAL REQUIREMENT (How well must it work?)
    ↓
ADD ACCEPTANCE CRITERIA (How do we know it's done?)
    ↓
LINK TO TEST CASE (How do we validate it?)
    ↓
TRACK IN SYSTEM (Design → Implementation → Validation)
```

---

## Translation Framework

### Example 1: Dashboard Auto-Refresh

**CUSTOMER REQUEST:**
> "I need the dashboard to show fresh data without me reloading the page. The data shouldn't be stale."

**EXTRACT BUSINESS NEED:**
- User wants real-time visibility into portfolio state
- Manual refresh is friction and misses updates
- Stale data leads to bad decisions

**TRANSLATE TO FUNCTIONAL REQUIREMENT:**
```yaml
ID: FR-005
Title: Dashboard Auto-Refresh
Category: User Interface
Priority: High
Acceptance Criteria:
  - CR-050: Dashboard refreshes automatically every 5 minutes
  - CR-051: User can disable auto-refresh if needed
  - CR-052: Refresh doesn't lose scroll position or form input
  - CR-053: Shows "last updated" timestamp
Test Case: tests/integration/test_dashboard_refresh.py
Related Components: 
  - frontend/dashboard.js (auto-refresh logic)
  - backend/api/dashboard.py (fresh data endpoint)
```

**TRANSLATE TO NON-FUNCTIONAL REQUIREMENT:**
```yaml
ID: NFR-005
Title: Dashboard Refresh Latency
Category: Performance
Priority: High
Specification:
  - Dashboard should update within 3 seconds of refresh trigger
  - Refresh should not cause visible jank or flicker
Measurement: Monitor refresh_latency_ms in journalctl
Target: p99 < 3000ms
Alert Threshold: > 5000ms
Test Case: tests/nonfunctional/test_dashboard_latency.py
```

**LINK BACK TO CUSTOMER REQUEST:**
```
Date: 2026-06-18
Customer: User (portfolio manager)
Request: "Fresh data without manual reload"
Trace: FR-005 (Dashboard Auto-Refresh)
      → CR-050, CR-051, CR-052, CR-053 (acceptance criteria)
      → NFR-005 (3-second latency SLO)
      → tests/integration/test_dashboard_refresh.py (validation)
Status: Implemented ✅
```

---

## Example 2: Bug Tracker Integration

**CUSTOMER REQUEST:**
> "I believe that in order to track the design is by knowing the requirements so that the target design is defined. The requirements must be covered by system description and measures. The V model. The bug tracker is also a part of each project. This shall be part of the pillars model used by all."

**EXTRACT BUSINESS NEED:**
- Requirements drive design (not vice versa)
- Every requirement needs acceptance criteria (measurable)
- Bug tracker should link to requirements, not just pillars
- V-Model structure (left leg: requirements, right leg: validation)
- Apply to all projects systematically

**TRANSLATE TO FUNCTIONAL REQUIREMENTS:**
```yaml
ID: FR-X01
Title: V-Model Requirements Framework
Category: Architecture / Process
Priority: Critical
Acceptance Criteria:
  - CR-X01: Every project has FUNCTIONAL_REQUIREMENTS.md
  - CR-X02: Every project has NONFUNCTIONAL_REQUIREMENTS.md
  - CR-X03: Every project has TRACEABILITY_MATRIX.md
  - CR-X04: Requirements use V-Model structure (left leg: specs, right leg: tests)
  - CR-X05: Bug tracker links bugs to requirements (not just pillars)
  - CR-X06: Framework applies to all 19 portfolio projects
  - CR-X07: Each requirement has acceptance criteria (measurable)
Test Case: Verify structure exists in each project
Related Components:
  - project-designer/V_MODEL_REQUIREMENTS.md (framework)
  - project-designer/scripts/generate_requirements.py (automation)
  - tracker/ (bug tracker integration)
  - All 19 projects

ID: FR-X02
Title: Design & Bug Tracker Integration with Requirements
Category: Tools / Process
Priority: Critical
Acceptance Criteria:
  - CR-X08: Tracker supports requirement as first-class object
  - CR-X09: Bugs can be linked to requirements (which requirement violated?)
  - CR-X10: Dashboard shows requirement coverage % per project
  - CR-X11: Bugs show which acceptance criterion is failing
Test Case: Tracker shows requirement-bug linkage
Related Components:
  - tracker/backend/models.py (Requirement model)
  - tracker/backend/main.py (API endpoints)
  - tracker/frontend (UI for requirements)
```

**TRANSLATE TO NON-FUNCTIONAL REQUIREMENTS:**
```yaml
ID: NFR-X01
Title: Requirements Framework Adoption (Coverage)
Category: Correctness / Completeness
Priority: High
Specification:
  - 100% of projects have requirements framework applied
  - >= 80% of requirements have acceptance criteria
  - >= 90% of bugs link to requirements
Measurement: Count projects/requirements/bugs in tracker
Target: 100% projects, 80% criteria, 90% linkage
Current: 100% projects (19/19), 60% criteria, 0% linkage
Alert Threshold: < 80% projects, < 70% criteria, < 80% linkage
Test Case: Automated audit of requirements coverage
Timeline: 
  - Framework rollout: ✅ Complete (2026-06-18)
  - Fill in requirements: In progress (2-4 weeks per project)
  - Link bugs: Next phase (starting with investing-platform)
```

**LINK BACK TO CUSTOMER REQUEST:**
```
Date: 2026-06-18
Customer: Architecture lead
Request: "V-Model + requirements + bug tracker integration for all projects"
Trace: FR-X01 (Framework structure)
      FR-X02 (Tracker integration)
      NFR-X01 (Coverage SLO)
      → CR-X01 through CR-X11 (19 acceptance criteria)
      → tests/integration/test_requirements_framework.py (validation)
Status: Framework deployed ✅, requirements filling in progress, tracker integration next
```

---

## Process: From Customer Request to System Requirement

**When you receive a customer request:**

### **Step 1: Parse the Request**
```
What are they asking for?
What problem are they solving?
What pain point exists?
What outcome do they want?
```

### **Step 2: Extract Business Need**
```
Problem statement (1-2 sentences)
User/stakeholder name
Timeline/urgency
Related existing requirements
```

### **Step 3: Translate to Functional Requirement**
```
What must the system DO?
  → FR-XXX: [Feature name]
  → Category: [Data Processing / UI / Integration / Architecture / etc.]
  → Priority: [Critical / High / Medium / Low]
  
What does success look like?
  → CR-001: [Measurable acceptance criterion]
  → CR-002: [Another criterion]
  → CR-003: [etc.]
  
How do we test it?
  → tests/unit/test_xxx.py
  → tests/integration/test_xxx.py
  → tests/e2e/test_xxx.py
```

### **Step 4: Translate to Non-Functional Requirement**
```
What quality properties matter?
  → Performance: latency, throughput, batch duration?
  → Reliability: availability %, uptime?
  → Security: encryption, secrets, CVE scanning?
  → Maintainability: type hints %, test coverage %?
  → Correctness: accuracy ±%, completeness?
  
How do we measure success?
  → NFR-XXX: [Quality requirement]
  → Measurement method: [how to monitor]
  → Target/SLO: [what's acceptable]
  → Alert threshold: [when to escalate]
  
How do we validate it?
  → tests/nonfunctional/test_xxx.py
```

### **Step 5: Document Traceability**
```
Link customer request → FR → CR → NFR → Tests
Create entry in TRACEABILITY_MATRIX.md
Track status: Proposed → Accepted → Implemented → Validated
```

### **Step 6: Implement & Validate**
```
Code implements FR acceptance criteria
Tests validate CR-XXX
Monitor NFR metrics in production
Update tracker status: ✅ Met / ⚠️ Partial / ❌ Gap
```

---

## Template: Customer Request Form

**For each request, capture:**

```markdown
---
Date: YYYY-MM-DD
Customer: [Name/Role]
Request Title: [Short description]
Priority: [Critical / High / Medium / Low]
Timeline: [ASAP / This week / This month / etc.]

## The Ask
[Quote or paraphrase of exactly what they asked for]

## Business Need
[Why do they need this? What problem solves?]

## Functional Requirement
- ID: FR-XXX
- Title: [Feature name]
- Use Case: [Actor, trigger, main flow]
- Acceptance Criteria: [CR-001, CR-002, ...]

## Non-Functional Requirement
- ID: NFR-XXX
- Category: [Performance / Reliability / Security / Maintainability]
- Specification: [Measurable target]
- Measurement: [How to monitor]

## Test Cases
- [tests/unit/test_xxx.py]
- [tests/integration/test_xxx.py]

## Implementation
- PR: [GitHub PR URL]
- Status: [Proposed / In Progress / Done / Blocked]

## Validation
- Acceptance criteria met: [Y/N]
- Tests passing: [Y/N]
- Deployed: [Y/N]
---
```

---

## Real-World Examples from This Session

### Request 1: Design & Bug Tracker
**Customer Asked:** "I want a tool to track design progress and bugs"
**Translated To:**
- FR-001: Create project dashboard
- FR-002: Score 8 pillars (scorecard)
- FR-003: Log gaps on Kanban board
- FR-004: Reference rules & playbooks
- NFR-001: Dashboard loads in < 3 seconds
- NFR-002: 99.5% availability
- Tests: 80+ test cases across unit/integration/e2e

### Request 2: V-Model Requirements Framework
**Customer Asked:** "Requirements must drive design. Use V-Model. Bug tracker must link to requirements."
**Translated To:**
- FR-X01: V-Model requirements framework for all projects
- FR-X02: Tracker integration (bugs → requirements)
- FR-X03: Requirements scorecard (% met, % partial, % gap)
- NFR-X01: 100% of projects have framework
- NFR-X02: >= 80% of requirements have acceptance criteria
- Test Case: Automated audit of requirements coverage

### Request 3: Apply Framework to All 19 Projects
**Customer Asked:** "Apply requirements framework to all projects"
**Translated To:**
- FR-X04: Generate requirements templates for each project
- CR-X12: Each project has FUNCTIONAL_REQUIREMENTS.md
- CR-X13: Each project has NONFUNCTIONAL_REQUIREMENTS.md
- CR-X14: Each project has TRACEABILITY_MATRIX.md
- NFR-X03: Framework can be applied to any project in 10 minutes
- Test Case: Verify files exist in all 19 projects ✅

---

## Benefits of This Approach

✅ **Traceability** — Every customer request → FR → test → code → production  
✅ **Accountability** — Track what was promised vs. what was delivered  
✅ **Requirements Completeness** — Avoid implicit requirements (they're explicit)  
✅ **Measurability** — Every requirement has acceptance criteria and SLOs  
✅ **Communication** — Customer sees exactly how their request becomes a system  
✅ **Roadmap** — Prioritize by customer impact + effort  
✅ **Root-Cause** — Bug violates which customer request?  

---

## Integration with Tracker

**In the Design & Bug Tracker:**

Each requirement shows:
```
FR-001: Dashboard Auto-Refresh
├─ Customer Request: "Fresh data without reload"
├─ Date Added: 2026-06-18
├─ Acceptance Criteria:
│  ├─ CR-050: Refresh every 5 minutes
│  ├─ CR-051: Can disable auto-refresh
│  ├─ CR-052: Preserves scroll position
│  └─ CR-053: Shows timestamp
├─ Related NFR: NFR-005 (< 3 sec latency)
├─ Tests: [test_dashboard_refresh.py]
├─ Status: ✅ Met
└─ Notes: Deployed in v1.2, live in production
```

Each bug shows:
```
BUG-042: Dashboard refreshes too slowly
├─ Related Requirement: FR-001 (Dashboard Auto-Refresh)
├─ Violates: NFR-005 (< 3 sec latency) → Current: 5.2 sec
├─ Status: In Remediation
├─ Root-Cause: Database query N+1 problem
└─ Acceptance Test: tests/nonfunctional/test_dashboard_latency.py
```

---

## Workflow

**For Every Customer Request:**

1. **Capture:** Record the exact request (quote)
2. **Extract:** Identify business need + use case
3. **Translate:** Create FR (what) + NFR (how well)
4. **Define:** Write acceptance criteria (CR-001, CR-002, ...)
5. **Commit:** Add to requirements document + tracker
6. **Implement:** Code implements FR, tests validate CR
7. **Track:** Update status in tracker (Proposed → Done)
8. **Validate:** Monitor NFR metrics in production
9. **Link:** Bug report references this FR/CR/NFR
10. **Report:** Monthly review of requirement fulfillment

---

## Summary

Every customer interaction is a **customer requirement**. The framework translates it into:
- **FR**: Functional Requirement (what the system must do)
- **CR**: Acceptance Criterion (measurable, testable)
- **NFR**: Non-Functional Requirement (how well)
- **Test Cases**: How we validate it works
- **Tracker Entry**: Linked to code, bugs, deployment status

This closes the loop: **Customer → System → Code → Tests → Production → Monitoring → Customer Validation**.

