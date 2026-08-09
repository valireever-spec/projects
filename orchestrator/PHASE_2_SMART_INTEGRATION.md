# Phase 2: Smart Integration (Lazy Skills + Conditional Validation)

## Principle: Only Load What's Needed

Instead of loading all 40+ skills upfront, Phase 2 will:
- **Lazy-load skills** (load only when orchestrator decides to use them)
- **Conditional skill execution** (gate skills based on project config)
- **Conditional V-Model validation** (only validate when enabled)
- **Resource-aware** (check resources before launching each skill)

---

## Smart Skill Pool Architecture

```python
class SmartSkillPool:
    """Lazy-loading skill pool. Load skills only when needed."""
    
    def __init__(self, skill_library_path: Path, config: OrchestratorConfig):
        self.skill_library_path = skill_library_path
        self.config = config
        self._loaded_skills = {}  # Cache of loaded skills
        self._skill_registry = {}  # Registry: skill_name -> path
        self._register_all_skills()  # Scan directories, but don't load yet
    
    def _register_all_skills(self):
        """Register all skills (lightweight: just scan dirs, no loading)."""
        for skill_dir in self.skill_library_path.glob("*-v2"):
            skill_name = skill_dir.name
            self._skill_registry[skill_name] = skill_dir
    
    async def run_if_needed(self, skill_name: str, input: Any) -> Optional[Any]:
        """Run a skill ONLY if config enables it. Otherwise return None (skip)."""
        
        # Gate 1: Is this skill enabled in config?
        if not self._is_skill_enabled(skill_name):
            logger.info(f"Skill '{skill_name}' disabled in config; skipping")
            return None
        
        # Gate 2: Load skill lazily (only now, if enabled)
        skill = await self._load_skill(skill_name)
        if not skill:
            logger.warning(f"Skill '{skill_name}' failed to load; skipping")
            return None
        
        # Gate 3: Check resources before execution
        can_run, reason = self.resource_monitor.can_run_agent()
        if not can_run:
            logger.warning(f"Insufficient resources for skill '{skill_name}': {reason}")
            return None
        
        # Gate 4: Execute with timeout
        try:
            logger.info(f"Running skill: {skill_name}")
            result = await asyncio.wait_for(
                skill.execute(input),
                timeout=skill.timeout_seconds
            )
            logger.info(f"Skill '{skill_name}' completed successfully")
            return result
        
        except asyncio.TimeoutError:
            logger.warning(f"Skill '{skill_name}' timed out after {skill.timeout_seconds}s")
            return None
        except Exception as e:
            logger.error(f"Skill '{skill_name}' failed: {e}")
            return None
    
    async def run_required(self, skill_name: str, input: Any) -> Any:
        """Run a skill and FAIL if it's not available (required skill)."""
        
        if not self._is_skill_enabled(skill_name):
            raise ValueError(f"Required skill '{skill_name}' is disabled in config")
        
        skill = await self._load_skill(skill_name)
        if not skill:
            raise RuntimeError(f"Required skill '{skill_name}' failed to load")
        
        result = await asyncio.wait_for(
            skill.execute(input),
            timeout=skill.timeout_seconds
        )
        return result
    
    async def _load_skill(self, skill_name: str) -> Optional[SkillDefinition]:
        """Lazy-load a skill. Return cached if already loaded."""
        
        # Already loaded?
        if skill_name in self._loaded_skills:
            return self._loaded_skills[skill_name]
        
        # In registry but not loaded yet?
        if skill_name not in self._skill_registry:
            logger.warning(f"Skill not found: {skill_name}")
            return None
        
        # Load it now
        try:
            skill_path = self._skill_registry[skill_name]
            skill = SkillDefinition.from_directory(skill_path)
            self._loaded_skills[skill_name] = skill
            logger.debug(f"Loaded skill: {skill_name}")
            return skill
        except Exception as e:
            logger.error(f"Failed to load skill '{skill_name}': {e}")
            return None
    
    def _is_skill_enabled(self, skill_name: str) -> bool:
        """Check if skill is enabled in config."""
        
        # Global setting: skills_enabled?
        if not self.config.get("skills_enabled", True):
            return False
        
        # Per-phase settings
        phase = self.config.get("current_phase")  # "design", "implementation", "verification"
        if phase:
            phase_config = self.config.get(f"{phase}_skills", {})
            enabled = phase_config.get("enabled", True)
            excluded = phase_config.get("excluded_skills", [])
            
            if not enabled:
                return False
            if skill_name in excluded:
                return False
        
        # Skill-specific setting
        skill_config = self.config.get("skills", {}).get(skill_name, {})
        return skill_config.get("enabled", True)
```

---

## Smart Orchestrator: Conditional Skill Usage

```python
class SmartOrchestratorCoordinator(OrchestratorCoordinator):
    """Orchestrator that uses skills only when configured."""
    
    async def _execute_implementation_phase(self, design_output):
        logger.info("Implementation phase: checking which skills to use")
        
        # Decision tree:
        # - If config.use_skills = False → pure Claude
        # - If config.use_skills = True → use skills
        # - If resource-constrained → skip optional skills, keep required only
        
        if not self.config.get("use_skills", True):
            logger.info("Skills disabled; using pure Claude for implementation")
            impl_output = await self.implementer_via_claude(design_output)
        else:
            logger.info("Skills enabled; orchestrating skill execution")
            impl_output = await self.implementer_via_skills(design_output)
        
        return impl_output
    
    async def implementer_via_claude(self, design_output):
        """Pure Claude implementation (no skills)."""
        return await self.implementer_claude.run(
            ImplementerInput(..., use_skills=False)
        )
    
    async def implementer_via_skills(self, design_output):
        """Skill-orchestrated implementation."""
        
        impl_output = ImplementerOutput(project_id=...)
        
        for requirement in design_output.proposed_requirements:
            logger.info(f"Implementing requirement: {requirement.req_id}")
            
            # For each requirement, selectively run skills
            
            # OPTIONAL: Best practices?
            if self._should_run_skill("best-practices-applier"):
                approach = await self.skill_pool.run_if_needed(
                    "best-practices-applier", requirement
                )
            
            # REQUIRED: Test suite?
            if self._should_run_skill("test-suite-builder"):
                test_plan = await self.skill_pool.run_required(
                    "test-suite-builder", requirement
                )
            
            # OPTIONAL: Performance optimization?
            if self._should_run_skill("performance-optimizer"):
                optimized = await self.skill_pool.run_if_needed(
                    "performance-optimizer", code_change
                )
        
        return impl_output
    
    def _should_run_skill(self, skill_name: str) -> bool:
        """Decision: should we run this skill?"""
        
        # Check config
        skill_config = self.config.get("skills", {}).get(skill_name, {})
        if not skill_config.get("enabled", True):
            return False
        
        # Check resources
        can_run, _ = self.resource_monitor.can_run_agent()
        if not can_run:
            # Only skip OPTIONAL skills; run REQUIRED ones anyway
            if skill_config.get("required", False):
                logger.warning(f"Low resources but '{skill_name}' is required; running anyway")
                return True
            else:
                logger.info(f"Low resources; skipping optional skill '{skill_name}'")
                return False
        
        return True
    
    async def _execute_verification_phase(self, design_output, impl_output):
        logger.info("Verification phase: checking which validations to run")
        
        # Decision tree:
        # - If config.validate_vmodel = False → skip testing-validation-platform
        # - If config.validate_vmodel = True → use testing-validation-platform
        # - If config.security_audit = False → skip security skills
        # - etc.
        
        verifier_input = VerifierInput(...)
        
        # Run REQUIRED validation (always)
        requirement_validation = await self.skill_pool.run_required(
            "requirement-validator", verifier_input
        )
        
        # Run OPTIONAL validations (if config enabled + resources available)
        if self._should_run_skill("chaos-testing-framework"):
            chaos_results = await self.skill_pool.run_if_needed(
                "chaos-testing-framework", verifier_input
            )
        
        if self._should_run_skill("security-checker-v2"):
            security_results = await self.skill_pool.run_if_needed(
                "security-checker-v2", verifier_input
            )
        
        # Conditional: V-Model validation
        if self.config.get("validate_vmodel", True):
            logger.info("Running V-Model validation via testing-validation-platform")
            vmodel_validation = await self.testing_platform.validate_requirements(
                verifier_input.project_id,
                verifier_input.code_changes,
                verifier_input.original_requirements
            )
        else:
            logger.info("V-Model validation disabled in config")
            vmodel_validation = None
        
        return self._merge_verifications(...)
```

---

## Configuration: Smart Skill Gating

```yaml
orchestrator:
  project_name: "investing-platform"
  project_path: "/home/vali/projects/investing-platform"
  framework: "CSF-21"
  
  # Global skill enable/disable
  skills_enabled: true
  
  # Phase-specific skill configuration
  implementation:
    skills:
      enabled: true
      required_skills:
        - "test-suite-builder"        # Must run
        - "documentation-generator"   # Must run
      optional_skills:
        - "best-practices-applier"    # Run if resources available
        - "performance-optimizer"     # Run if resources available
        - "security-hardener"         # Run if resources available
      excluded_skills:                # Never run
        - "backtesting-simulator"     # Overkill for this project
      timeout_seconds: 300
  
  verification:
    skills:
      enabled: true
      required_skills:
        - "api-consistency-validator" # Must run
      optional_skills:
        - "chaos-testing-framework"   # Run if time/resources
        - "security-checker-v2"       # Run if enabled
        - "compliance-auditor"        # Run if enabled
      excluded_skills:
        - "business-safety-assessor"  # Not applicable
      timeout_seconds: 600
  
  # V-Model validation (conditional)
  testing_validation_platform:
    enabled: true                     # Set to false to skip V-Model validation
    url: "http://localhost:8004"
    auto_sync: true                   # Auto-sync before verification
    sync_timeout_seconds: 30
  
  # Skill-specific configuration
  skills:
    "best-practices-applier-v2":
      enabled: true
      required: false                 # Optional skill
      timeout_seconds: 300
    
    "test-suite-builder":
      enabled: true
      required: true                  # Must run
      timeout_seconds: 600
      config:
        coverage_target: 85
        generate_e2e: false           # Optional config per skill
    
    "chaos-testing-framework-v2":
      enabled: false                  # Disabled for this project
      required: false
      timeout_seconds: 900
```

---

## Smart Skill Execution Example

### Design Phase (Unchanged)
```python
# Designer always runs (Phase 1)
# No skills used
design_output = await coordinator._execute_design_phase()
```

### Implementation Phase (Smart Skill Usage)

**Scenario A: Resources plentiful, all skills enabled**
```
Implementing FR-001: User Authentication
├─ ✓ best-practices-applier (OPTIONAL, enabled) → approach
├─ ✓ test-suite-builder (REQUIRED) → test_plan
├─ ✓ documentation-generator (OPTIONAL, enabled) → docs
├─ ✓ security-hardener (OPTIONAL, enabled) → hardened_code
└─ ⏱️  All skills completed in 240s (under budget)
```

**Scenario B: Low memory, optional skills skipped**
```
Implementing FR-001: User Authentication
├─ ⊘ best-practices-applier (OPTIONAL, skipped due to memory)
├─ ✓ test-suite-builder (REQUIRED, runs anyway) → test_plan
├─ ⊘ documentation-generator (OPTIONAL, skipped due to memory)
├─ ⊘ security-hardener (OPTIONAL, skipped due to memory)
└─ ⏱️  Only required skills ran (60s)
```

**Scenario C: Skills disabled globally**
```
Implementing FR-001: User Authentication
⊘ All skills disabled in config; using pure Claude
└─ Claude generates code + tests directly (180s)
```

### Verification Phase (Smart Validation)

**Scenario A: Full validation enabled**
```
Verifying implementation
├─ ✓ api-consistency-validator (REQUIRED) → API check
├─ ✓ chaos-testing-framework (OPTIONAL, enabled) → resilience
├─ ✓ security-checker-v2 (OPTIONAL, enabled) → security audit
├─ ✓ V-Model validation (ENABLED) → requirement check
└─ ✓ Approved with evidence
```

**Scenario B: V-Model disabled, reduced security checks**
```
Verifying implementation
├─ ✓ api-consistency-validator (REQUIRED) → API check
├─ ⊘ chaos-testing-framework (disabled) → skipped
├─ ⊘ security-checker-v2 (disabled) → skipped
├─ ⊘ V-Model validation (DISABLED) → skipped
└─ ⏱️  Partial verification (quick path)
```

---

## Smart Skill Loading: Memory Efficiency

```python
# Only load skills as needed
total_memory_before = get_memory_usage()

# Run Designer (no skills loaded)
design_output = await coordinator._execute_design_phase()

# Load only implementation skills when needed
for skill_name in config.implementation_skills:
    skill = await skill_pool._load_skill(skill_name)  # Load only if needed
    result = await skill.execute(input)
    await skill.cleanup()  # Optional: unload after use to free memory

# Load only verification skills when needed
for skill_name in config.verification_skills:
    skill = await skill_pool._load_skill(skill_name)
    result = await skill.execute(input)
    await skill.cleanup()

total_memory_after = get_memory_usage()
# Memory delta should be small (lazy loading)
```

---

## Key Benefits of Smart Integration

| Benefit | How |
|---------|-----|
| **Memory efficient** | Lazy-load skills; unload after use |
| **Resource aware** | Check CPU/memory before running skills |
| **Flexible** | Enable/disable skills per-project in YAML config |
| **Fast path** | Skip optional skills when time/resources tight |
| **Failsafe** | Required skills run; optional skills gracefully skip |
| **Observable** | Clear logging of which skills run, why they're skipped |
| **Testable** | Easy to mock skills; test with/without skills |
| **Backward compatible** | Can run pure Claude if skills unavailable |

---

## Implementation Strategy

### Phase 2a: Smart Framework (Week 3)
1. Create `SmartSkillPool` with lazy loading
2. Update `OrchestratorCoordinator` with conditional gates
3. Create config schema for skill enable/disable
4. Unit tests for gating logic

### Phase 2b: Implementer + Skills (Week 4)
1. Implement `ImplementerAgent` with smart skill usage
2. Integrate 5–10 implementation skills (lazy-loaded)
3. Integration tests

### Phase 2c: Verifier + V-Model (Week 5–6)
1. Implement `VerifierAgent` with smart skill usage
2. Conditional V-Model validation
3. Integrate 5–10 verification skills
4. End-to-end tests

---

## Configuration Examples

### Example 1: Lightweight (Skills Disabled)
```yaml
orchestrator:
  skills_enabled: false                    # Pure Claude, no skills
  testing_validation_platform:
    enabled: false                         # Skip V-Model validation
```
**Use case:** Quick prototyping, limited resources

### Example 2: Balanced (Selective Skills)
```yaml
orchestrator:
  skills_enabled: true
  implementation:
    skills:
      enabled: true
      required_skills: ["test-suite-builder"]
      optional_skills: ["documentation-generator"]
  verification:
    skills:
      enabled: true
      required_skills: ["api-consistency-validator"]
      optional_skills: []
  testing_validation_platform:
    enabled: true
```
**Use case:** Production systems, balanced overhead

### Example 3: Comprehensive (All Skills)
```yaml
orchestrator:
  skills_enabled: true
  implementation:
    skills:
      enabled: true
      required_skills: ["test-suite-builder", "documentation-generator"]
      optional_skills: 
        - "best-practices-applier"
        - "performance-optimizer"
        - "security-hardener"
  verification:
    skills:
      enabled: true
      required_skills: ["api-consistency-validator"]
      optional_skills:
        - "chaos-testing-framework"
        - "security-checker-v2"
        - "compliance-auditor"
  testing_validation_platform:
    enabled: true
```
**Use case:** Production hardening, comprehensive validation

---

## Open Question for Smart Integration

1. **Skill Cleanup:** After a skill runs, should we unload it to free memory?
   - Pro: Memory efficient; can run many skills
   - Con: Reload overhead if same skill runs again

2. **Skill Caching:** Cache skill results across runs?
   - Pro: Fast re-runs; cheaper
   - Con: Stale results if inputs change slightly

3. **Partial Failures:** If optional skill fails, should orchestrator:
   - Log warning and continue?
   - Stop and report as blocker?
   - Retry once then skip?

4. **Skill Discovery:** Should orchestrator auto-discover skills, or use static config?
   - Auto-discovery: flexible, but requires scanning directories
   - Static config: explicit, requires maintenance

---

## Success Criteria for Smart Integration

- ✅ Skills only load when needed (lazy loading verified)
- ✅ Optional skills skip gracefully under resource constraints
- ✅ Required skills always run (or fail with clear error)
- ✅ Per-project skill config works (YAML-driven)
- ✅ V-Model validation is conditional
- ✅ Memory usage stays bounded
- ✅ All tests pass (mocked skills, real skills)
- ✅ Documentation clear on how to enable/disable skills

---

## Conclusion

**Smart integration** = full integration without the overhead.

- Load skills only when needed (lazy)
- Gate skills based on config + resources
- V-Model validation is conditional
- Required vs optional skills enforced
- Backward compatible (can run without skills)

**This allows:**
- Lightweight deployments (skills disabled)
- Production-grade deployments (all skills)
- Resource-constrained environments (optional skills skipped)
- Clean upgrade path (start simple, add skills as needed)

---

## Next: Ready for Phase 2?

Answer these 4 questions, then Phase 2 can start:

1. **Skill cleanup:** Yes (unload after use) or No (keep loaded)?
2. **Skill caching:** Yes (cache results) or No (always recompute)?
3. **Partial failure:** Log+continue, or Stop+blocker, or Retry?
4. **Skill discovery:** Auto-discovery or static config?
