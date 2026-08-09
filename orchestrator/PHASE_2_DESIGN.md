# Phase 2 Design: Full Integration (Implementer + Verifier + Skills + V-Model)

## Overview

Phase 2 transforms the orchestrator into a **full multi-agent skill-based system** that:
- Implements Implementer + Verifier agents
- Integrates **40+ skills from skill-library** into agent workflows
- Integrates **testing-validation-platform** for requirement validation
- Optionally uses **skill-creator framework** for agent definitions
- Supports parallel Implementer execution across requirements

---

## Architecture: Phase 2 Full Integration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR COORDINATOR                            │
│  (Central state machine, resource monitoring, agent coordination)            │
└─────────────────────────────────────────────────────────────────────────────┘
          ↓                          ↓                          ↓
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ DESIGNER AGENT   │    │IMPLEMENTER AGENT │    │ VERIFIER AGENT   │
│ (Phase 1)        │    │ (NEW Phase 2)    │    │ (NEW Phase 2)    │
└──────────────────┘    └──────────────────┘    └──────────────────┘
       ↓                       ↓                       ↓
  Claude +            Skills Pool (10–15):     Skills Pool (10–15):
  Design Rules    • best-practices-applier     • api-consistency-validator
                  • architecture-auditor       • chaos-testing-framework
                  • analytics-engine           • business-safety-assessor
                  • backtesting-simulator      • security-checker-v2
                  • codebase-refactorer        • performance-profiler
                  • documentation-generator    • compliance-auditor
                  • test-suite-builder         • deployment-validator
                  • performance-optimizer      • resilience-tester
                  • security-hardener          • (5+ more)
                  • (5+ more)

          ↓                       ↓                       ↓
          ├───────────────────────┼───────────────────────┤
                                  ↓
                    ┌──────────────────────────────────┐
                    │  TESTING-VALIDATION-PLATFORM    │
                    │  (V-Model Validator)             │
                    ├──────────────────────────────────┤
                    │ • Sync requirements markdown     │
                    │ • Validate implementation        │
                    │ • Track V-Model traceability     │
                    │ • Report gaps to tracker         │
                    └──────────────────────────────────┘
                                  ↓
                    ┌──────────────────────────────────┐
                    │      TRACKER ADAPTER             │
                    │  (Central Project State)         │
                    └──────────────────────────────────┘
```

---

## Component Breakdown

### 1. Implementer Agent (New)

**Purpose:** Generate code, tests, and documentation based on designer findings.

**Architecture:**
```python
class ImplementerAgent:
    def __init__(self, config: AgentConfig, skills: SkillPool):
        self.config = config
        self.skills = skills  # Access to 10-15 implementation skills
        
    async def run(self, impl_input: ImplementerInput) -> ImplementerOutput:
        # Parallel execution across requirements
        tasks = []
        for requirement in impl_input.target_requirements:
            task = self._implement_requirement(requirement)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return self._merge_outputs(results)
    
    async def _implement_requirement(self, req: Requirement):
        # Workflow:
        # 1. best-practices-applier → architecture-auditor → Decide approach
        # 2. codebase-refactorer → Refactor if needed
        # 3. test-suite-builder → Generate tests
        # 4. documentation-generator → Create docs
        # 5. performance-optimizer → Optimize if needed
        # 6. security-hardener → Apply security hardening
        
        # Each skill is async; can run in series or parallel
        approach = await self.skills.run('best-practices-applier', req)
        code_change = await self.skills.run('codebase-refactorer', approach)
        test_plan = await self.skills.run('test-suite-builder', code_change)
        docs = await self.skills.run('documentation-generator', code_change)
        
        return ImplementerOutput(code_changes=[code_change], test_plan=test_plan, ...)
```

**Skills Used:**
| Skill | Input | Output | Purpose |
|-------|-------|--------|---------|
| `best-practices-applier-v2` | Requirement | Architecture approach | Decide implementation strategy |
| `architecture-auditor-v2` | Code design | Audit report | Validate design quality |
| `codebase-refactorer` | Old code | Refactored code | Improve existing code |
| `test-suite-builder` | Code | Test plan + tests | Generate tests |
| `documentation-generator` | Code | Docs | Auto-generate docs |
| `performance-optimizer` | Code | Optimized code | Improve performance |
| `security-hardener` | Code | Hardened code | Apply security practices |
| `backtesting-simulator-v2` | Algo code | Results | Test trading algorithms |
| `analytics-engine-v2` | Code + metrics | Analysis | Analyze code metrics |
| `(5+ more)` | Various | Various | Domain-specific tasks |

### 2. Verifier Agent (New)

**Purpose:** Validate implementation against requirements, security, performance, compliance.

**Architecture:**
```python
class VerifierAgent:
    def __init__(self, config: AgentConfig, skills: SkillPool):
        self.config = config
        self.skills = skills
        self.testing_platform = TestingValidationPlatformClient()  # V-Model validator
        
    async def run(self, verifier_input: VerifierInput) -> VerifierOutput:
        # Parallel skill execution
        tasks = [
            self._validate_requirements(verifier_input),
            self._validate_security(verifier_input),
            self._validate_performance(verifier_input),
            self._validate_compliance(verifier_input),
            self._validate_vmodel(verifier_input),  # testing-validation-platform
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self._merge_verification_results(results)
    
    async def _validate_requirements(self, input):
        # Use testing-validation-platform to check V-Model traceability
        vmodel_result = await self.testing_platform.validate_requirements(
            project_id=input.project_id,
            implementation=input.code_changes,
            requirements=input.original_requirements
        )
        return vmodel_result
    
    async def _validate_security(self, input):
        # Run security skills in parallel
        tasks = [
            self.skills.run('api-consistency-validator-v2', input),
            self.skills.run('security-checker-v2', input),
        ]
        return await asyncio.gather(*tasks)
    
    async def _validate_performance(self, input):
        # Run performance skills
        return await self.skills.run('performance-profiler', input)
    
    async def _validate_compliance(self, input):
        # Run compliance skills
        return await self.skills.run('compliance-auditor', input)
    
    async def _validate_vmodel(self, input):
        # New: Use testing-validation-platform for V-Model validation
        return await self.testing_platform.validate_vmodel(input)
```

**Skills Used:**
| Skill | Purpose |
|-------|---------|
| `api-consistency-validator-v2` | Check API contracts + compatibility |
| `chaos-testing-framework-v2` | Resilience testing |
| `business-safety-assessor-v1` | Business logic validation |
| `security-checker-v2` | Security audit (CVE, injection, etc.) |
| `performance-profiler` | Performance analysis |
| `compliance-auditor` | Compliance checking |
| `deployment-validator` | Deployment readiness |
| `resilience-tester` | Failure scenario testing |
| `(5+ more)` | Domain-specific validation |

### 3. Skill Pool Manager (New)

**Purpose:** Load, manage, and execute skills from skill-library.

```python
class SkillPool:
    """Manages access to 40+ skills from skill-library."""
    
    def __init__(self, skill_library_path: Path):
        self.skills = self._load_skills(skill_library_path)
        self.cache = {}  # Cache skill results
    
    def _load_skills(self, path: Path) -> Dict[str, SkillDefinition]:
        """Load skill definitions from skill-library directories."""
        skills = {}
        for skill_dir in path.glob("*-v2"):  # Load v2 versions
            skill_def = self._parse_skill(skill_dir)
            skills[skill_def.name] = skill_def
        return skills
    
    async def run(self, skill_name: str, input: Any, timeout: int = 300) -> Any:
        """Execute a skill with timeout and error handling."""
        if skill_name not in self.skills:
            raise ValueError(f"Skill not found: {skill_name}")
        
        skill = self.skills[skill_name]
        
        # Execute skill (could be subprocess, HTTP, direct Python, etc.)
        try:
            result = await self._execute_skill(skill, input, timeout)
            return result
        except TimeoutError:
            logger.error(f"Skill {skill_name} timed out after {timeout}s")
            raise
        except Exception as e:
            logger.error(f"Skill {skill_name} failed: {e}")
            raise
    
    async def run_parallel(self, skills: List[str], input: Any) -> List[Any]:
        """Execute multiple skills in parallel."""
        tasks = [self.run(skill, input) for skill in skills]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_skills_by_category(self, category: str) -> List[str]:
        """Get all skills in a category (e.g., 'security', 'testing')."""
        return [name for name, skill in self.skills.items() 
                if skill.category == category]
```

### 4. Testing-Validation-Platform Integration (New)

**Purpose:** Validate implementation against V-Model requirements.

```python
class TestingValidationPlatformClient:
    """Client for testing-validation-platform V-Model validation."""
    
    def __init__(self, api_url: str = "http://localhost:8004"):
        self.api_url = api_url
        self.client = httpx.AsyncClient()
    
    async def validate_requirements(
        self,
        project_id: int,
        implementation: List[CodeChange],
        requirements: List[Requirement]
    ) -> RequirementValidation:
        """Validate implementation against requirements using V-Model."""
        
        # POST to testing-validation-platform
        response = await self.client.post(
            f"{self.api_url}/api/vmodel/validate",
            json={
                "project_id": project_id,
                "implementation": [c.dict() for c in implementation],
                "requirements": [r.dict() for r in requirements],
            }
        )
        
        return RequirementValidation(**response.json())
    
    async def sync_vmodel(self, project_id: int) -> bool:
        """Sync V-Model board with tracker before verification."""
        response = await self.client.post(
            f"{self.api_url}/api/vmodel/sync",
            json={"project_id": project_id}
        )
        return response.status_code == 200
    
    async def get_vmodel_board(self, project_id: int) -> Dict:
        """Get current V-Model board state."""
        response = await self.client.get(
            f"{self.api_url}/api/vmodel/board/{project_id}"
        )
        return response.json()
    
    async def report_gaps(self, project_id: int, gaps: List[Gap]) -> bool:
        """Report discovered gaps back to testing-validation-platform."""
        response = await self.client.post(
            f"{self.api_url}/api/vmodel/gaps",
            json={"project_id": project_id, "gaps": [g.dict() for g in gaps]}
        )
        return response.status_code == 200
```

### 5. Skill Integration in Coordinator (Updated)

```python
class OrchestratorCoordinator:
    def __init__(
        self,
        config: OrchestratorConfig,
        skill_library_path: Path = Path("/home/vali/projects/skill-library")
    ):
        self.config = config
        self.skill_pool = SkillPool(skill_library_path)
        self.testing_platform = TestingValidationPlatformClient()
        self.resource_monitor = ResourceMonitor()
        
        # Initialize agents with skill pool
        self.designer = DesignerAdapter(config.agents["designer"])
        self.implementer = ImplementerAgent(
            config.agents["implementer"],
            self.skill_pool
        )
        self.verifier = VerifierAgent(
            config.agents["verifier"],
            self.skill_pool,
            self.testing_platform
        )
        self.tracker = TrackerAdapter(config.tracker)
    
    async def run_workflow(self) -> ProjectState:
        # Phase 1: Design (unchanged from Phase 1)
        design_output = await self._execute_design_phase()
        if not design_output or not self._check_design_gate():
            return self.state_machine.get_current_state()
        
        # Phase 2: Implementation (NEW - with skills)
        implementer_output = await self._execute_implementation_phase(design_output)
        if not implementer_output or not self._check_implementation_gate():
            return self.state_machine.get_current_state()
        
        # Phase 3: V-Model Sync (NEW)
        await self.testing_platform.sync_vmodel(self.state_machine.state.project_id)
        
        # Phase 4: Verification (NEW - with skills + V-Model)
        verifier_output = await self._execute_verification_phase(
            design_output, implementer_output
        )
        if not verifier_output or not self._check_verification_gate(verifier_output):
            return self.state_machine.get_current_state()
        
        # Complete
        self.state_machine.pass_verification_gate(verifier_output)
        return self.state_machine.get_current_state()
    
    async def _execute_implementation_phase(self, design_output):
        logger.info("Starting implementation phase with skill pool")
        
        # Resource check
        can_run, reason = self.resource_monitor.can_run_agent()
        if not can_run:
            logger.error(f"Cannot run implementer: {reason}")
            return None
        
        # Create input with parallel requirements
        impl_input = ImplementerInput(
            project_id=self.state_machine.state.project_id,
            project_path=self.config.project_path,
            design_findings=design_output,
            target_requirements=design_output.proposed_requirements,
            available_skills=self.skill_pool.get_available_skills(),
        )
        
        # Run implementer (now using skills)
        impl_output = await self.implementer.run(impl_input)
        
        # File to tracker
        await self.tracker.file_implementation_findings(
            self.state_machine.state.project_id,
            impl_output
        )
        
        return impl_output
    
    async def _execute_verification_phase(self, design_output, impl_output):
        logger.info("Starting verification phase with skills + V-Model")
        
        # Resource check
        can_run, reason = self.resource_monitor.can_run_agent()
        if not can_run:
            logger.error(f"Cannot run verifier: {reason}")
            return None
        
        # Create input
        verifier_input = VerifierInput(
            project_id=self.state_machine.state.project_id,
            project_path=self.config.project_path,
            code_changes=impl_output.code_changes,
            original_requirements=design_output.proposed_requirements,
            available_skills=self.skill_pool.get_available_skills(),
        )
        
        # Run verifier (now using skills + V-Model validation)
        verifier_output = await self.verifier.run(verifier_input)
        
        # File to tracker + testing-validation-platform
        await self.tracker.file_verification_findings(
            self.state_machine.state.project_id,
            verifier_output
        )
        
        return verifier_output
```

---

## Skill Library Integration Strategy

### Loading Skills

```python
# Load all skills from skill-library
skill_library_path = Path("/home/vali/projects/skill-library")

# Find all *-v2 skill directories (40+ skills)
for skill_dir in skill_library_path.glob("*-v2"):
    skill_def = SkillDefinition.from_directory(skill_dir)
    # skill_def.name: "best-practices-applier"
    # skill_def.category: "implementation"
    # skill_def.execute(): async callable
    skill_pool.register(skill_def)
```

### Skill Discovery

```python
# Get skills for a phase
implementer_skills = skill_pool.get_skills_by_category("implementation")
# → ["best-practices-applier", "codebase-refactorer", "test-suite-builder", ...]

verifier_skills = skill_pool.get_skills_by_category("verification")
# → ["api-consistency-validator", "chaos-testing-framework", "security-checker", ...]

# Get skill metadata
skill = skill_pool.get_skill("best-practices-applier")
print(skill.description)  # "Apply software engineering best practices"
print(skill.inputs)       # ["requirement", "codebase"]
print(skill.outputs)      # ["code_changes", "design_rationale"]
print(skill.timeout_ms)   # 300000
```

### Skill Execution Model

**Option A: Direct Python (preferred)**
```python
# Skill is a Python async function
from skill_library.best_practices_applier_v2 import apply_best_practices
result = await apply_best_practices(requirement)
```

**Option B: CLI Subprocess**
```python
# Skill is a CLI tool
process = subprocess.run(
    ["python3", "skill.py", "--input", json.dumps(input)],
    capture_output=True
)
result = json.loads(process.stdout)
```

**Option C: HTTP Service**
```python
# Skill is a microservice
response = await httpx.get(
    "http://skill-service:8080/execute",
    json={"skill": "best-practices-applier", "input": input}
)
result = response.json()
```

**Recommendation:** Use **Option A** (direct Python) for Phase 2. Allows:
- Direct `await` on async skills
- No subprocess overhead
- Easy debugging
- Full error propagation

---

## Testing-Validation-Platform Integration

### What testing-validation-platform provides

1. **V-Model Sync** → parses FUNCTIONAL_REQUIREMENTS.md + NONFUNCTIONAL_REQUIREMENTS.md
2. **Requirement Validation** → checks if implementation satisfies each requirement
3. **Gap Tracking** → reports which requirements are unmet
4. **Traceability** → links requirements → code → tests
5. **Dashboard** → real-time V-Model board at http://localhost:8004

### Integration Points

**1. Before Verifier Runs**
```python
# Sync V-Model to ensure requirements are up-to-date
await testing_platform.sync_vmodel(project_id)
```

**2. During Verification**
```python
# Check each requirement against implementation
validation = await testing_platform.validate_requirements(
    project_id,
    implementation=impl_output.code_changes,
    requirements=design_output.proposed_requirements
)

# Results include per-requirement pass/fail
for req_validation in validation.requirement_validations:
    if not req_validation.passed:
        blockers.append(req_validation.gap_description)
```

**3. After Verification**
```python
# Report verified requirements back
for req_id, status in implementation_status.items():
    await testing_platform.mark_requirement(req_id, status)
```

---

## Phase 2 Implementation Plan

### Week 3–4: Implementer Agent + Skills

**Tasks:**
1. Create `ImplementerAgent` class with skill pool support
2. Implement `SkillPool` manager (load + execute skills)
3. Create `ImplementerAdapter` (Claude or skill-orchestrated)
4. Integrate 10–15 implementation skills
5. Unit tests for skill execution
6. Integration test: Designer → Implementer → Tracker

**Files to Create:**
- `orchestrator/agents/implementer_agent.py`
- `orchestrator/skill_pool.py`
- `orchestrator/adapters/implementer_adapter.py`
- `orchestrator/skill_loader.py`
- `tests/orchestrator/test_implementer_agent.py`
- `tests/orchestrator/test_skill_pool.py`

**Success Criteria:**
- Implementer runs 5+ skills in sequence
- Parallel requirement handling works
- All skills timeout gracefully
- Tests pass (100% coverage of skill execution)

---

### Week 5–6: Verifier Agent + V-Model + Skills

**Tasks:**
1. Create `VerifierAgent` class
2. Integrate `TestingValidationPlatformClient`
3. Integrate 10–15 verification skills
4. Implement parallel skill execution in verifier
5. V-Model sync before + after verification
6. Unit tests + integration tests

**Files to Create:**
- `orchestrator/agents/verifier_agent.py`
- `orchestrator/clients/testing_platform_client.py`
- `orchestrator/adapters/verifier_adapter.py`
- `tests/orchestrator/test_verifier_agent.py`
- `tests/orchestrator/test_testing_platform_integration.py`

**Success Criteria:**
- Verifier runs 10+ skills in parallel
- V-Model validation works
- Requirements marked pass/fail
- All integration tests pass

---

### Week 7: Polish + Multi-Project Support

**Tasks:**
1. Full end-to-end test (Designer → Implementer → Verifier)
2. Parallel project execution (multi-project coordinator)
3. Dashboard for orchestrator status
4. Error recovery + retry logic
5. Observability (logging + metrics)
6. Documentation + examples

**Files to Create:**
- `orchestrator/api/main.py` (FastAPI dashboard)
- `orchestrator/pool.py` (multi-project support)
- `docs/phase_2_guide.md`
- Integration test suite

---

## Design Decisions for Phase 2

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Skill execution model | Direct Python (Option A) | Fastest, easiest debugging, no subprocess overhead |
| Parallel implementer | Yes, per-requirement | Throughput; can implement FR-001, FR-002 in parallel |
| Parallel verifier | Yes, per-skill | Run security + performance checks in parallel |
| V-Model sync timing | Before verification | Ensures requirements current before validation |
| Blocker escalation | Halt orchestrator | Safety: don't auto-merge broken changes |
| Skill timeout | Configurable (default 300s) | Prevent hanging; operator can tune per-skill |
| Resource monitoring | Keep Phase 1 implementation | Prevents orchestrator crashes |

---

## Known Challenges & Mitigations

| Challenge | Mitigation |
|-----------|-----------|
| **40+ skills to integrate** | Load lazily; cache results; only load skills needed for phase |
| **Skill API variations** | Create `SkillAdapter` interface; normalize inputs/outputs |
| **Long execution time** | Parallel skill execution; progress logging; operator dashboards |
| **Skill failures** | Retry logic; fallback skills; clear error messages to blocker list |
| **Memory usage** | Resource monitoring; skill result caching; cleanup after each phase |
| **Testing complexity** | Mock skills; fixture library; parallel test execution |

---

## Files to Create/Modify in Phase 2

### New Files
```
orchestrator/
├── agents/
│   ├── __init__.py
│   ├── implementer_agent.py      ← NEW
│   ├── verifier_agent.py         ← NEW
│   └── designer_agent.py         (moved from adapters)
├── clients/
│   ├── __init__.py
│   └── testing_platform_client.py ← NEW
├── skill_pool.py                 ← NEW
├── skill_loader.py               ← NEW
├── pool.py                       ← NEW (multi-project orchestrator)
├── api/
│   ├── __init__.py
│   └── main.py                   ← NEW (FastAPI dashboard)
└── config/
    └── phase_2_config.yaml       ← NEW (example config)

tests/orchestrator/
├── test_implementer_agent.py     ← NEW
├── test_verifier_agent.py        ← NEW
├── test_skill_pool.py            ← NEW
└── test_skill_integration.py     ← NEW

docs/
└── PHASE_2_IMPLEMENTATION.md     ← NEW (detailed guide)
```

### Modified Files
```
orchestrator/
├── coordinator.py                (add Implementer + Verifier phases)
├── schemas.py                    (add SkillDefinition, SkillResult)
├── adapters/
│   ├── tracker_adapter.py       (add skill tracking methods)
│   ├── designer_adapter.py      (already exists from Phase 1)
│   ├── implementer_adapter.py   ← NEW wrapper for ImplementerAgent
│   └── verifier_adapter.py      ← NEW wrapper for VerifierAgent
└── requirements.txt              (add dependencies)
```

---

## Open Questions for Phase 2

1. **Skill Input/Output Format** — How should skills receive inputs and return outputs?
   - Pydantic models? Raw dicts? Different per skill?

2. **Skill Execution Parallelism** — How many skills can run in parallel?
   - Per-requirement? Per-phase? Resource-limited?

3. **Skill Failure Handling** — If a skill fails, should we:
   - Halt orchestrator (fail-fast)?
   - Mark as blocker but continue (collect all failures)?
   - Retry with fallback skill?

4. **V-Model Frequency** — When to sync V-Model?
   - Before verification only?
   - Also before implementation?
   - After every skill execution?

5. **Testing-Validation-Platform Availability** — Should orchestrator:
   - Require it running (hard dependency)?
   - Gracefully degrade if unavailable (soft dependency)?
   - Skip V-Model validation if unavailable?

6. **Skill Library Versioning** — Use v1 or v2 skills?
   - Recommendation: v2 (newer, better tested)

7. **Agent Model Selection** — For Implementer + Verifier:
   - Use Claude like Designer?
   - Use local LLM?
   - Use skill orchestration (no LLM)?

---

## Success Metrics for Phase 2

| Metric | Target |
|--------|--------|
| Implementer agent ready | Week 4 |
| Verifier agent ready | Week 6 |
| 20+ skills integrated | Week 6 |
| V-Model validation working | Week 6 |
| Full E2E workflow tested | Week 7 |
| Test coverage | 85%+ |
| Documentation complete | Week 7 |
| Multi-project support | Week 7 |

---

## Next Phase Preview: Phase 3

Phase 3 (Weeks 8–9) will implement:
1. **CSF Framework Loading** — Load 21–23 CSF pillars into tracker
2. **Hybrid Scoring** — CSF + 8-pillar combined scoring
3. **CSF Validators** — Run CSF validators alongside orchestrator
4. **Designer Enhancement** — CSF-aware requirement generation
5. **Continuous Monitoring** — Real-time CSF compliance dashboards

---

## Conclusion

Phase 2 is **ambitious but achievable**:
- ✅ Implementer agent with skills
- ✅ Verifier agent with skills + V-Model
- ✅ 40+ skills integrated
- ✅ Full end-to-end orchestration
- ✅ Multi-project support

**Timeline:** 3–4 weeks (parallel skill integration)

**Ready to proceed?** Answer the 7 open questions above, then Phase 2 can start immediately after Phase 1 stabilizes.
