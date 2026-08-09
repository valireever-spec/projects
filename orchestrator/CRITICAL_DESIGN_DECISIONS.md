# Critical Design Decisions: Complete Reference

**This document captures all significant architectural and operational decisions made during Phase 1 design and implementation.**

---

## Phase 1 Decisions (Locked)

### 1. Agent Execution Model
**Decision:** Sequential (synchronous), not parallel  
**Rationale:**
- Simpler debugging and tracing
- Clear causality (designer → implementer → verifier)
- Easier error recovery
- Less complex state management

**Trade-off:** Slower than parallel, but more predictable and maintainable.

---

### 2. Workflow Gates
**Decision:** Auto-proceed if no blockers (no manual approval gates)  
**Rationale:**
- Faster iteration
- All blockers logged for review
- No friction from manual reviews
- Operator can always inspect state after

**Trade-off:** Less human oversight; mitigated by comprehensive logging.

---

### 3. State Progression
**Decision:** Proposed → Design → Implementation → Verification → Complete  
**Rationale:**
- Clear, logical progression
- Matches V-Model requirements framework
- Allows rollback at any stage
- Easy to implement in state machine

**Trade-off:** Can't restart from arbitrary stage; must flow through in order.

---

### 4. Requirement Status Flow
**Decision:** Proposed → Accepted → Implemented → Validated  
**Rationale:**
- Clear ownership at each stage
- Matches tracker's existing status model
- Easy to query "what's implemented?"
- Aligns with CSF-21 framework

**Trade-off:** Fixed 4-stage flow; no custom statuses.

---

### 5. Tracker Integration
**Decision:** Auto-file findings; no manual sync  
**Rationale:**
- Eliminates manual tracking overhead
- Single source of truth in tracker
- Real-time visibility
- Prevents data inconsistency

**Trade-off:** If orchestrator crashes mid-file, data may be partial; mitigated by idempotent operations.

---

### 6. Framework Support
**Decision:** CSF-21 first; 8-pillar as fallback  
**Rationale:**
- User explicitly chose CSF-21 as superset
- 21–23 pillars more comprehensive than 8
- Can support both (hybrid scoring in Phase 3)
- CSF-21 is future direction

**Trade-off:** CSF rules not yet loaded into tracker; Phase 3 task.

---

### 7. Claude Integration
**Decision:** Claude (paid) as default; Ollama as alternative  
**Rationale:**
- Claude more mature and reliable
- Better structured output parsing
- Consistent quality across runs
- Config allows override

**Trade-off:** Cost for each agent run; justified by ROI on automation.

---

## Phase 1 Hardening Decisions (Locked)

### 8. Resource Monitoring Strategy
**Decision:** Three-level defense (pre-flight, continuous, emergency)  
**Rationale:**
- User concern: "Prevent machine freeze"
- Level 1 catches obvious problems early
- Level 2 catches runtime bloat
- Level 3 force-kills runaway processes
- Graduated response = more resilient

**Trade-off:** Continuous monitoring adds 5s check overhead; worth it for safety.

---

### 9. Resource Thresholds (Hardened)
**Decision:** 1GB RAM, 75% CPU, 8% disk, 500MB growth limit  
**Rationale:**
- Aggressive (but safe) defaults
- Catches problems before cascade
- 500MB growth = clear bloat indicator
- 5-second checks = fast response

**Trade-off:** May kill agents prematurely on constrained systems; config allows tuning.

---

### 10. Memory Cleanup Strategy
**Decision:** Unload skills after execution (Phase 2)  
**Rationale:**
- Bounded memory usage
- Supports unlimited skills (40+)
- No memory leaks
- Can run many phases without restart

**Trade-off:** Reload overhead if same skill runs again; acceptable given laziness.

---

### 11. Skill Caching Strategy
**Decision:** No caching; always recompute  
**Rationale:**
- Fresh results guaranteed
- No stale-data bugs
- Simple implementation
- Skills are fast enough

**Trade-off:** Slight recomputation overhead; worth it for correctness.

---

### 12. Partial Failure Handling
**Decision:** Log+continue for optional skills; block for required  
**Rationale:**
- Resilient to transient failures
- Optional skills never block orchestrator
- Required skills fail fast
- Clear semantics (optional vs required)

**Trade-off:** Partial success possible; mitigated by clear logging of what failed.

---

### 13. Skill Discovery Strategy
**Decision:** Auto-discovery (scan skill-library on startup)  
**Rationale:**
- Flexible (picks up new skills automatically)
- No config maintenance
- Scales to 40+ skills without bloat
- Dynamic (re-scan every 5 min if needed)

**Trade-off:** Startup cost to scan directories; one-time only.

---

### 14. Configuration Approach
**Decision:** YAML-based per-project config (not code-driven)  
**Rationale:**
- Non-technical operators can tune
- Easy to version control
- Different configs per project
- No code changes needed

**Trade-off:** YAML parsing; mitigated by Pydantic validation.

---

### 15. Error Propagation
**Decision:** ResourceExhausted halts orchestrator; other exceptions logged  
**Rationale:**
- Resource problems are critical → fail fast
- Other errors are recoverable
- Clear distinction in logs
- Prevents cascading resource exhaustion

**Trade-off:** May halt prematurely if false positive; mitigated by aggressive tuning.

---

## Phase 2 Decisions (Locked)

### 16. Implementer Agent Pattern
**Decision:** Skill-orchestrated (not pure Claude)  
**Rationale:**
- Better code quality (skills proven)
- Parallel requirement handling
- Skill re-use across projects
- Composable architecture

**Trade-off:** More moving parts; mitigated by SkillPool abstraction.

---

### 17. Verifier Agent Pattern
**Decision:** Skill-orchestrated + V-Model validation  
**Rationale:**
- Skills for specialized checks (security, performance)
- V-Model ensures requirements met
- Parallel skill execution
- Comprehensive validation

**Trade-off:** Many moving parts; mitigated by clear interfaces.

---

### 18. Testing-Validation-Platform Integration
**Decision:** Optional (can disable in config)  
**Rationale:**
- V-Model traceability important
- But not mandatory for all projects
- Graceful degradation if unavailable
- Can be added incrementally

**Trade-off:** Partial validation possible; acceptable if V-Model disabled.

---

## Phase 3 Decisions (Planned)

### 19. CSF Framework Loading
**Decision:** Load 21–23 pillars into tracker on-demand  
**Rationale:**
- Phase 1/2 works fine with designer's assessments
- CSF loading is mechanical (no complexity)
- Can defer to Phase 3 without blocking
- Cleaner separation of concerns

**Trade-off:** CSF validators not available until Phase 3; Designer output still includes CSF.

---

### 20. Hybrid Scoring
**Decision:** Weighted average (70% CSF, 30% 8-pillar) starting; tunable  
**Rationale:**
- CSF is superset, gets higher weight
- 8-pillar provides stability
- Tunable per-project
- Can evolve to 100% CSF later

**Trade-off:** Complexity; mitigated by config-driven approach.

---

## Phase 4 Decisions (Planned)

### 21. Multi-Project Orchestrator
**Decision:** Single orchestrator handles N projects (pooled agents)  
**Rationale:**
- Resource efficiency (shared agent pool)
- Scalability (N projects without N orchestrators)
- Better resource utilization

**Trade-off:** More complex state management; Phase 4 only.

---

### 22. CLI Tool
**Decision:** Create for project initialization and status  
**Rationale:**
- Non-technical users can initialize projects
- Easy status checks
- Consistent UX

**Trade-off:** Additional maintenance; Phase 4 only.

---

### 23. FastAPI Dashboard
**Decision:** Real-time orchestrator status UI  
**Rationale:**
- Operator visibility into running phases
- Live resource monitoring
- Project status at a glance

**Trade-off:** Frontend code; Phase 4 only.

---

## Decisions NOT Made (Left Flexible)

### Per-Project Customization
**Decision:** Config-driven (YAML per project)  
**Rationale:** Different projects have different needs  
**Flexibility:** Can override any threshold, enable/disable skills, choose framework  

### Skill Execution Model
**Decision:** Deferred to Phase 2 (could be subprocess, HTTP, direct Python)  
**Rationale:** Need to understand skill-library structure first  
**Current design:** Direct Python (Phase 2 assumption)  

### Parallelism Within Phases
**Decision:** Sequential by default; Implementer can do parallel requirements  
**Rationale:** Balances complexity and performance  
**Could evolve:** More parallelism in Phase 4 if needed  

---

## Decision Record: When to Revisit

| Decision | Review Trigger | Trigger Condition |
|----------|---|---|
| Agent execution model | Complexity grows | If sequential becomes bottleneck |
| Resource thresholds | False positives | If >10% of runs killed prematurely |
| Memory cleanup | Fragmentation | If memory doesn't stay bounded |
| Skill caching | Performance | If repeated skills are 50%+ of runtime |
| Framework choice | CSF stability | If CSF-21 proves problematic |
| Manual gates | Operator feedback | If blockers not caught by automation |

---

## Summary: Locked vs Flexible

| Aspect | Status | Flexibility |
|--------|--------|------------|
| **Execution model** | Locked (sequential) | Low (architectural) |
| **Workflow gates** | Locked (auto-proceed) | Low (fundamental) |
| **Resource protection** | Locked (hardened 3-level) | Medium (tunable thresholds) |
| **Framework** | Locked (CSF-21 default) | High (config per-project) |
| **Agent models** | Locked (Claude default) | Medium (config override) |
| **Skill pool** | Locked (lazy-load) | Medium (can disable skills) |
| **V-Model** | Locked (optional) | High (can disable in config) |
| **Parallelism** | Locked (sequential) | Medium (can tune per-phase) |

---

## Conclusion

**Phase 1 is locked on critical architectural decisions:**
- Sequential agents (simple, predictable)
- Auto-proceed gates (fast, logged)
- Hardened resource protection (safe, observable)
- Config-driven flexibility (adaptive per-project)

**Phase 2 can proceed with confidence** knowing Phase 1 foundation is solid and well-documented.

**Future phases (3–4) have clear decision framework** to revisit if needed.
