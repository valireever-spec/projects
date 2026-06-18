# Traceability Matrix: claude_helper

Maps: Requirements → Design Components → Code Files → Tests

---

## Functional Requirements Traceability

| Req ID | Title | Design Component | Code Files | Test Case | Status |
|--------|-------|------------------|-----------|-----------|--------|
| FR-001 | [Feature] | [Component] | `code/file.py` | `test_file.py` | TBD |
| | **CR-001** | [Sub-component] | `code/file.py` | `test_criterion.py` | TBD |
| | **CR-002** | [Sub-component] | `code/file.py` | `test_criterion.py` | TBD |

**Instructions:**
1. For each FR, fill in the design component that implements it
2. List actual code files (backend, frontend, etc.)
3. Reference test case files that validate it
4. Mark status: ✅ Met / ⚠️ Partial / ❌ Gap

---

## Non-Functional Requirements Traceability

| Req ID | Category | Title | Design Component | Code Files | Test Case | Target | Current | Status |
|--------|----------|-------|------------------|-----------|-----------|--------|---------|--------|
| NFR-001 | [Category] | [Metric] | [Component] | `code/file.py` | `test_nfr.py` | [Target] | [TBD] | TBD |

---

## Component-to-Requirement Mapping

**Backend Layer:**
- [Component]: Implements FR-001, FR-002, NFR-001

**Frontend Layer:**
- [Component]: Implements FR-003, FR-004

**Data Layer:**
- [Component]: Implements FR-005, NFR-002

**Integration Layer:**
- [Component]: Implements FR-006, NFR-003

---

## Test Coverage by Requirement

- Total Requirements: [TBD]
- Total Test Cases: [TBD]
- Coverage: [TBD]%

**By Type:**
- Unit tests: [TBD]
- Integration tests: [TBD]
- End-to-end tests: [TBD]

---

## Requirement Coverage Summary

| Status | Count | % |
|--------|-------|---|
| ✅ **Met** | [TBD] | [TBD]% |
| ⚠️ **Partial** | [TBD] | [TBD]% |
| ❌ **Gap** | [TBD] | [TBD]% |
| **Total** | [TBD] | 100% |

---

## At-Risk Requirements

[List requirements that have partial coverage or gaps]

1. [Requirement]: [Why at risk]
2. [Requirement]: [Why at risk]

---

## Using This Matrix

- **Developers**: Find FR-X to see what to implement
- **QA**: Find NFR-Y to see what to measure
- **Architecture**: Identify which components implement which requirements
- **Root-cause**: Trace bugs back to which requirement they violate
