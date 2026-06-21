# ADR-002: Centralized V-Model Tracker Architecture

**Status:** Accepted  
**Date:** 2026-06-21  
**Deciders:** V-Model team

## Context

The investing-platform and other portfolio projects need a unified way to track:
- Functional and non-functional requirements
- Known gaps, bugs, and design decisions
- Traceability between requirements → design → tests
- Project maturity and health metrics

Initially, each project maintained scattered requirements documents. No unified view existed across the portfolio, making it hard to:
- Track which requirements were validated in production
- Correlate gaps across projects
- Assess portfolio-wide maturity

## Decision

We built a **centralized Tracker service** (separate infrastructure) that acts as a single source of truth for all V-Model data across projects.

**Architecture:**
```
Project A (requirements files)  \
Project B (requirements files)   → testing-validation-platform (sync engine)
Project C (requirements files)  /          ↓
                             Central Tracker (DB + API)
                                   ↓
                        V_MODEL_BOARD.md (for each project)
                        vmodel-status.html (dashboard)
```

**Data flows:**
1. **Inbound**: testing-validation-platform pulls requirements from each project and POSTs to Tracker
2. **Outbound**: Tracker exports gaps/bugs to V_MODEL_BOARD.md (git-friendly format)
3. **Dashboard**: FastAPI server queries Tracker and renders real-time status

## Consequences

### Benefits
- **Portfolio visibility**: Single source of truth for all project requirements across investing-platform, etc.
- **Traceability**: Central DB enables linking requirements → tests → bugs → design decisions
- **Automation**: Can auto-detect coverage gaps and missing tests
- **Extensibility**: Easy to add new metrics (test coverage %, design doc links, etc.) without forking projects

### Trade-offs
- **Operational burden**: Must maintain Tracker service (DB, API, backups)
- **Network dependency**: Projects depend on Tracker availability for sync to work
- **Schema evolution**: Changes to requirement format require coordinated migrations
- **Data consistency**: Risk of stale data if sync fails silently

### Mitigations
- Graceful degradation: If Tracker is down, testing-validation-platform retries with exponential backoff
- Git-friendly outputs: V_MODEL_BOARD.md is human-readable and version-controlled
- Observability: All sync operations logged and auto-reported to Tracker on error

## Alternatives Considered

### 1. Decentralized (No Tracker)
**Rejected because:**
- No cross-project visibility
- No unified dashboard
- Can't detect gaps at portfolio level
- Duplicate tooling across projects

### 2. Centralized File Store (Shared Git Repo)
**Rejected because:**
- Still no structured query capability (can't ask "which requirements are unvalidated?")
- Harder to maintain consistency across projects
- No single source of truth for gaps/bugs

### 3. Each Project Owns Its Own Tracker
**Rejected because:**
- Defeats purpose of portfolio-level visibility
- Maintenance burden per project
- Can't correlate cross-project dependencies

## Implementation Notes

- Tracker runs on `http://127.0.0.1:8001` (development)
- testing-validation-platform uses `tracker_client.py` to abstract API calls
- All requirements synced every 5 minutes (see ADR-001)
- Errors auto-reported back to Tracker (see: `backend/core/tracker_integration.py`)

## Related Decisions

- ADR-001: Pull-based sync model (how data flows to Tracker)
- ADR-003: FastAPI for dashboard API
