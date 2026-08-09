# Phase 2: Final Implementation Spec

## Design Decisions (Locked)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Skill Cleanup** | **Yes** — Unload after use | Memory efficiency; support unlimited skills |
| **Skill Caching** | **No** — Always recompute | Fresh results; simple implementation; no stale data |
| **Partial Failures** | **Log+continue** | Resilient; optional skills don't block progress |
| **Skill Discovery** | **Auto-discovery** | Flexible; automatically pick up new skills from skill-library |

---

## Architecture (Final)

```
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR COORDINATOR                       │
│         (State machine, resource monitoring)                │
└──────────────┬──────────────────┬──────────────────┬────────┘
               ↓                  ↓                  ↓
        ┌────────────┐    ┌─────────────┐    ┌──────────────┐
        │  DESIGNER  │    │ IMPLEMENTER │    │  VERIFIER    │
        │ (Phase 1)  │    │ (Phase 2)   │    │ (Phase 2)    │
        └────────────┘    └─────────────┘    └──────────────┘
               ↓                  ↓                  ↓
             Claude          SkillPool          SkillPool
                         (Implementer         (Verifier
                          Skills)              Skills)
                                  ↓
                      ┌───────────────────────┐
                      │ SMART SKILL POOL      │
                      ├───────────────────────┤
                      │ Auto-discovery        │
                      │ Lazy-load on demand   │
                      │ Unload after use      │
                      │ Config-gated          │
                      │ Resource-aware        │
                      └───────────────────────┘
                             ↓
            ┌────────────────────────────────────┐
            │  SKILL LIBRARY (40+ skills)        │
            │  /home/vali/projects/skill-library │
            └────────────────────────────────────┘
                             ↓
          ┌──────────────────────────────────────┐
          │ TESTING-VALIDATION-PLATFORM         │
          │ (V-Model Validator)                 │
          │ /home/vali/projects/              │
          │  testing-validation-platform       │
          └──────────────────────────────────────┘
                             ↓
          ┌──────────────────────────────────────┐
          │ TRACKER (Central project state)     │
          │ http://localhost:8000               │
          └──────────────────────────────────────┘
```

---

## Skill Cleanup: Memory Management

### How It Works

```python
class SmartSkillPool:
    def __init__(self, skill_library_path, config):
        self._loaded_skills = {}      # Active skills in memory
        self._skill_registry = {}     # All skills (not loaded)
    
    async def run_if_needed(self, skill_name: str, input: Any):
        """Load → Execute → Cleanup (memory efficient)."""
        
        try:
            # Load skill into memory
            skill = await self._load_skill(skill_name)
            
            # Execute with timeout
            result = await asyncio.wait_for(
                skill.execute(input),
                timeout=skill.timeout_seconds
            )
            
            return result
        
        finally:
            # CLEANUP: Always unload after use (even on error)
            await self._cleanup_skill(skill_name)
    
    async def _cleanup_skill(self, skill_name: str):
        """Unload skill from memory."""
        if skill_name in self._loaded_skills:
            skill = self._loaded_skills[skill_name]
            
            # Call skill's cleanup method (if exists)
            if hasattr(skill, 'cleanup'):
                try:
                    await skill.cleanup()
                except Exception as e:
                    logger.warning(f"Skill {skill_name} cleanup failed: {e}")
            
            # Remove from memory
            del self._loaded_skills[skill_name]
            logger.debug(f"Unloaded skill: {skill_name}")
```

### Memory Timeline

```
Time    Memory Usage              Event
────────────────────────────────────────────────────────────
00:00   100MB (orchestrator base)
00:05   120MB (+20MB)             Load skill: best-practices-applier
00:10   120MB (same)              Execute skill
00:15   100MB (-20MB)             Cleanup: unload skill
00:20   110MB (+10MB)             Load skill: test-suite-builder
00:25   110MB (same)              Execute skill
00:30   100MB (-10MB)             Cleanup: unload skill
────────────────────────────────────────────────────────────
Result: Bounded memory (100-120MB), unlimited skills
```

### Cleanup Guarantees

- **Always cleanup** — even if skill times out or fails
- **No memory leaks** — skills unloaded after use
- **No blocking** — cleanup is async
- **Observable** — logs every unload

---

## Skill Caching: No Caching

### Decision Rationale

**Why no caching?**
1. **Simplicity** — No cache invalidation logic
2. **Fresh results** — Always get current data (no stale results)
3. **Deterministic** — Same input → same output (always)
4. **Low overhead** — Skill-library skills are fast enough

**Trade-off:**
- Con: Slight recomputation overhead
- Pro: Guaranteed correctness; no stale data bugs

### Implementation

```python
async def run_if_needed(self, skill_name: str, input: Any):
    """Never check cache; always execute."""
    
    skill = await self._load_skill(skill_name)
    
    # No cache lookup
    # Always execute
    result = await skill.execute(input)
    
    # No cache storage
    # Just return result
    
    await self._cleanup_skill(skill_name)
    return result
```

---

## Partial Failures: Log+Continue

### Non-Blocking Optional Skills

```python
async def run_if_needed(self, skill_name: str, input: Any) -> Optional[Any]:
    """Run optional skill. Log failures; don't block orchestrator."""
    
    if not self._is_skill_enabled(skill_name):
        logger.info(f"Skill disabled: {skill_name}")
        return None
    
    try:
        skill = await self._load_skill(skill_name)
        result = await asyncio.wait_for(
            skill.execute(input),
            timeout=skill.timeout_seconds
        )
        return result
    
    except asyncio.TimeoutError:
        logger.warning(f"Skill timeout: {skill_name} (>{skill.timeout_seconds}s)")
        return None
    
    except Exception as e:
        logger.warning(f"Skill failed: {skill_name}: {e}")
        return None
    
    finally:
        await self._cleanup_skill(skill_name)
```

### Required Skills Block

```python
async def run_required(self, skill_name: str, input: Any) -> Any:
    """Run required skill. Raise exception if fails (blocks orchestrator)."""
    
    try:
        skill = await self._load_skill(skill_name)
        result = await asyncio.wait_for(
            skill.execute(input),
            timeout=skill.timeout_seconds
        )
        return result
    
    except Exception as e:
        logger.error(f"Required skill failed: {skill_name}: {e}")
        raise  # Block orchestrator
    
    finally:
        await self._cleanup_skill(skill_name)
```

### Implementer Error Handling

```python
async def _implement_requirement(self, requirement: Requirement):
    """Implement requirement with optional + required skills."""
    
    code_change = CodeChange(...)
    gaps = []
    
    # OPTIONAL: Best practices (if fails, continue)
    try:
        approach = await self.skill_pool.run_if_needed(
            "best-practices-applier-v2", requirement
        )
        logger.info(f"Best practices applied")
    except Exception as e:
        logger.warning(f"Best practices skipped: {e}")
    
    # REQUIRED: Tests (if fails, block)
    try:
        test_plan = await self.skill_pool.run_required(
            "test-suite-builder", requirement
        )
        logger.info(f"Test suite generated")
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        gaps.append(Gap(
            pillar="Verification & Validation",
            title="Test Generation Failed",
            description=str(e),
            severity=SeverityLevel.CRITICAL
        ))
        return None  # Block this requirement
    
    return code_change
```

### Verifier Error Handling

```python
async def _validate_security(self, verifier_input: VerifierInput):
    """Validate security with optional + required skills."""
    
    findings = []
    
    # REQUIRED: API consistency (must pass)
    try:
        api_validation = await self.skill_pool.run_required(
            "api-consistency-validator-v2", verifier_input
        )
        findings.extend(api_validation.findings)
    except Exception as e:
        logger.error(f"API validation failed (required): {e}")
        raise  # Block orchestrator
    
    # OPTIONAL: Chaos testing (log+continue if fails)
    chaos_result = await self.skill_pool.run_if_needed(
        "chaos-testing-framework-v2", verifier_input
    )
    if chaos_result:
        findings.extend(chaos_result.findings)
    else:
        logger.warning(f"Chaos testing skipped (optional)")
    
    # OPTIONAL: Security audit (log+continue if fails)
    security_result = await self.skill_pool.run_if_needed(
        "security-checker-v2", verifier_input
    )
    if security_result:
        findings.extend(security_result.findings)
    else:
        logger.warning(f"Security audit skipped (optional)")
    
    return findings
```

### Result: Resilient Workflow

```
Verifying implementation:
├─ ✓ api-consistency-validator (REQUIRED) → passed
├─ ⊘ chaos-testing-framework (OPTIONAL) → timed out, skipped
├─ ✓ security-checker-v2 (OPTIONAL) → passed
└─ ✓ Verification complete (optional failures didn't block)
```

---

## Skill Discovery: Auto-Discovery

### How It Works

```python
class SmartSkillPool:
    def __init__(self, skill_library_path: Path):
        self.skill_library_path = skill_library_path
        self._skill_registry = {}     # Name → Path
        self._loaded_skills = {}      # Name → SkillDefinition
        
        # Auto-discovery on init
        self._discover_skills()
    
    def _discover_skills(self):
        """Scan skill-library and register all *-v2 skills."""
        
        logger.info(f"Discovering skills in {self.skill_library_path}")
        count = 0
        
        for skill_dir in self.skill_library_path.glob("*-v2"):
            if not skill_dir.is_dir():
                continue
            
            skill_name = skill_dir.name
            self._skill_registry[skill_name] = skill_dir
            count += 1
        
        logger.info(f"Discovered {count} skills")
        return count
    
    def get_available_skills(self) -> List[str]:
        """List all discovered skills."""
        return list(self._skill_registry.keys())
    
    def get_skills_by_pattern(self, pattern: str) -> List[str]:
        """Find skills matching pattern (e.g., '*validator*', '*security*')."""
        import fnmatch
        return [
            name for name in self._skill_registry.keys()
            if fnmatch.fnmatch(name, pattern)
        ]
```

### Auto-Discovery Example

```python
# Initialize orchestrator
coordinator = OrchestratorCoordinator(config)

# Auto-discovers all skills from skill-library
# Logs:
# INFO: Discovering skills in /home/vali/projects/skill-library
# INFO: Discovered 43 skills:
#   - analytics-engine-v2
#   - api-consistency-validator-v2
#   - api-integration-pattern-v2
#   - architecture-auditor-v2
#   - backtesting-simulator-v2
#   - best-practices-applier-v2
#   - brainstorming-v2
#   - business-safety-assessor-v1
#   - ... (34 more)

# Use discovered skills
implementer_skills = coordinator.skill_pool.get_skills_by_pattern("*applier*")
# → ["best-practices-applier-v2"]

security_skills = coordinator.skill_pool.get_skills_by_pattern("*security*")
# → ["security-checker-v2", "security-hardener"]

validator_skills = coordinator.skill_pool.get_skills_by_pattern("*validator*")
# → ["api-consistency-validator-v2", "requirement-validator", ...]
```

### Dynamic Skill Discovery

```python
class DynamicSkillPool(SmartSkillPool):
    """Watch skill-library for new skills and hot-load them."""
    
    def __init__(self, skill_library_path: Path):
        super().__init__(skill_library_path)
        self._last_discovery = time.time()
    
    async def run_if_needed(self, skill_name: str, input: Any):
        """Re-discover skills if any new ones added."""
        
        # Re-discover every 5 minutes (cheap operation)
        if time.time() - self._last_discovery > 300:
            self._discover_skills()  # Will log if new skills found
            self._last_discovery = time.time()
        
        # Run skill (may be newly discovered)
        return await super().run_if_needed(skill_name, input)
```

### Skill Registry Output

```json
{
  "discovered_at": "2026-07-11T19:00:00Z",
  "skill_library_path": "/home/vali/projects/skill-library",
  "total_skills": 43,
  "skills": [
    {
      "name": "best-practices-applier-v2",
      "path": "/home/vali/projects/skill-library/best-practices-applier-v2",
      "category": "implementation",
      "timeout_ms": 300000
    },
    {
      "name": "api-consistency-validator-v2",
      "path": "/home/vali/projects/skill-library/api-consistency-validator-v2",
      "category": "verification",
      "timeout_ms": 600000
    },
    ...
  ]
}
```

---

## Phase 2 Implementation Timeline

### Week 3: Smart Foundation
**Files to create:**
- `orchestrator/skill_pool.py` — SmartSkillPool (auto-discovery, lazy-load, cleanup)
- `orchestrator/skill_loader.py` — SkillDefinition parser
- `orchestrator/skills/__init__.py` — Skill interface/base class
- `tests/orchestrator/test_skill_pool.py` — Unit tests (auto-discovery, cleanup, failures)

**Deliverable:** SmartSkillPool working with auto-discovered skills

### Week 4: Implementer Agent
**Files to create:**
- `orchestrator/agents/implementer_agent.py` — Full implementation
- `orchestrator/adapters/implementer_adapter.py` — Phase 1 wrapper
- `tests/orchestrator/test_implementer_agent.py` — Full coverage

**Integration points:**
- ImplementerAgent uses SmartSkillPool
- Config-driven skill selection
- Parallel requirement handling
- Cleanup after each skill

**Deliverable:** Implementer agent + 5 skills integrated and tested

### Week 5–6: Verifier Agent + V-Model
**Files to create:**
- `orchestrator/agents/verifier_agent.py` — Full verification
- `orchestrator/clients/testing_platform_client.py` — V-Model integration
- `orchestrator/adapters/verifier_adapter.py` — Phase 1 wrapper
- `tests/orchestrator/test_verifier_agent.py` — Full coverage

**Integration points:**
- VerifierAgent uses SmartSkillPool
- Optional + required skill handling
- Testing-validation-platform sync
- V-Model requirement validation

**Deliverable:** Verifier agent + 5+ skills + V-Model working

### Week 7: Polish + E2E
**Files to modify:**
- `orchestrator/coordinator.py` — Wire up all phases
- `tests/orchestrator/test_integration_e2e.py` — Full workflow test

**Deliverable:** Full Designer → Implementer → Verifier workflow

---

## Phase 2 Deliverables Checklist

- [ ] SmartSkillPool (auto-discovery, lazy-load, cleanup, no-caching)
- [ ] ImplementerAgent with skill orchestration
- [ ] VerifierAgent with skill orchestration
- [ ] Testing-validation-platform integration
- [ ] 40+ skills available (auto-discovered)
- [ ] Config-driven skill enable/disable
- [ ] Partial failure handling (log+continue)
- [ ] Resource cleanup after each skill
- [ ] Full E2E test (Designer → Implementer → Verifier)
- [ ] Documentation + examples
- [ ] 85%+ test coverage

---

## Success Criteria

| Metric | Target |
|--------|--------|
| SmartSkillPool ready | Week 3 end |
| Implementer agent ready | Week 4 end |
| Verifier agent ready | Week 6 end |
| All skills discoverable | Week 6 end |
| Full E2E workflow tested | Week 7 end |
| Test coverage | 85%+ |
| Memory bounded | <500MB with unlimited skills |
| Zero skill cache | All recomputed (no stale data) |
| Documentation | Complete with examples |

---

## Phase 2 Configuration (Example)

```yaml
orchestrator:
  project_name: "investing-platform"
  project_path: "/home/vali/projects/investing-platform"
  framework: "CSF-21"
  
  # Global skill settings
  skills_enabled: true
  skill_library_path: "/home/vali/projects/skill-library"
  auto_discover_skills: true
  
  # Implementer phase
  implementation:
    skills:
      enabled: true
      required_skills:
        - "test-suite-builder"
      optional_skills:
        - "best-practices-applier-v2"
        - "documentation-generator"
        - "security-hardener"
      excluded_skills:
        - "backtesting-simulator-v2"  # Too slow for this project
  
  # Verifier phase
  verification:
    skills:
      enabled: true
      required_skills:
        - "api-consistency-validator-v2"
      optional_skills:
        - "chaos-testing-framework-v2"
        - "security-checker-v2"
        - "compliance-auditor"
  
  # V-Model validation
  testing_validation_platform:
    enabled: true
    url: "http://localhost:8004"
    auto_sync: true
  
  # Per-skill tuning
  skills:
    "test-suite-builder":
      enabled: true
      required: true
      timeout_seconds: 600
      config:
        coverage_target: 85
    
    "security-hardener":
      enabled: true
      required: false
      timeout_seconds: 300
    
    "chaos-testing-framework-v2":
      enabled: true
      required: false
      timeout_seconds: 900
```

---

## Phase 2: Ready to Go

**Decisions locked:**
- ✅ Skill Cleanup: Yes (unload after use)
- ✅ Skill Caching: No (always recompute)
- ✅ Partial Failures: Log+continue (resilient)
- ✅ Skill Discovery: Auto-discovery (flexible)

**Next steps:**
1. Create Phase 2 initial tasks
2. Start Week 3: SmartSkillPool
3. Progress through Implementer → Verifier
4. Full E2E test by Week 7

**Phase 2 is ready to implement immediately after Phase 1 stabilizes.**
