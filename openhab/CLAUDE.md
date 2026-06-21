# CLAUDE.md

## Portfolio Standards & Frameworks

This project follows **three complementary frameworks** from `project-designer/` for engineering excellence:

### 1️⃣ Architecture Validation: 8-Pillar Framework

**Purpose:** Assess and improve architecture across 8 dimensions (NASA/Tesla/Apple/Toyota standards).

**Core documents:**
- **[FRAMEWORK.md](../project-designer/FRAMEWORK.md)** — 48 rules (6 per pillar) with examples
- **[CHECKLIST.md](../project-designer/CHECKLIST.md)** — Scoreable rubric (0–5 per pillar, target 4+/5)
- **[PLAYBOOKS.md](../project-designer/PLAYBOOKS.md)** — Step-by-step fixes for common gaps by pillar

**The 8 Pillars:**
1. Architecture Discipline & Traceability — Documented design, ADRs, explicit boundaries
2. Build Quality In / Error-Proofing — Type hints, linting, pinned dependencies, no secrets
3. Verification & Validation — Test gates, coverage, chaos tests, bounded complexity
4. Continuous Integration & Safe Delivery — Automated gates, reversible migrations, rollback
5. Root-Cause Driven Improvement — Post-mortems, refactor patterns, tech-debt cadence
6. Security & Privacy by Design — Least-privilege, secrets, input validation, CVE scanning
7. Observability & Telemetry — Structured logging, SLOs, dashboards, runbooks
8. Maintainability & Sustainable Pace — Domain naming, bounded file size, justified deps

**How to use:**
- Before reviews: Read [FRAMEWORK.md](../project-designer/FRAMEWORK.md) + [CHECKLIST.md](../project-designer/CHECKLIST.md)
- When fixing gaps: Link to pillar + rule, consult [PLAYBOOKS.md](../project-designer/PLAYBOOKS.md)
- Score target: 4+/5 per pillar (80%+ overall)

---

### 2️⃣ Engineering Standards: 11 Core Practices

**Purpose:** Ensure all projects follow consistent engineering practices (observability, error handling, testing, deployment, etc.).

**Core document:**
- **[ENGINEERING_STANDARDS_BASE.md](../project-designer/ENGINEERING_STANDARDS_BASE.md)** — 11 mandatory practices for all projects

**The 11 Standards:**
1. Observability — Structured logging (JSON), metrics (Prometheus), health checks
2. Error Handling — Specific exceptions, standard error responses, logging
3. Configuration — No hardcoding; all config via environment variables
4. Type Hints — All functions must have type annotations
5. Testing — ≥85% coverage; test error paths and edge cases
6. Code Organization — Files <1500 lines, single responsibility principle
7. Deployment — Health checks, graceful shutdown, readiness probes
8. Incident Response — Runbooks, SLOs, post-mortems for failures
9. Code Review — Checklist-based, minimum 2 reviewers
10. Documentation — Docstrings, README, architecture diagrams
11. Git Standards — Conventional commits, GPG signing recommended

**How to use:**
- New code: Follow the 11 standards from day one
- Reviews: Check against standards as part of code review
- Refactoring: Prioritize gaps in standards (especially observability, testing, error handling)

---

### 3️⃣ Requirements-Driven V-Model

**Purpose:** Trace requirements → design → implementation → validation (tests). Every feature is testable and linked to requirements.

**Core document:**
- **[V_MODEL_REQUIREMENTS.md](../project-designer/V_MODEL_REQUIREMENTS.md)** — Full V-Model framework with templates

**The V-Model Structure:**
```
REQUIREMENTS (Left)          VALIDATION (Right)
├─ Functional Specs          ├─ System Tests
├─ Non-Functional Specs      ├─ Integration Tests
├─ Use Cases                 ├─ Unit Tests
├─ Acceptance Criteria       └─ Acceptance Tests
└─ Traceability Matrix       └─ Bugs linked to requirements
```

**How to use:**
- Document: Maintain `FUNCTIONAL_REQUIREMENTS.md` and `NONFUNCTIONAL_REQUIREMENTS.md` in project root
- Track: Use tracker's V-Model dashboard to monitor requirements status (if applicable)
- Validate: Link tests to requirements (test IDs match requirement IDs)

---

### 4️⃣ Maturity Roadmap

**Purpose:** Understand project maturity level and progression path (Prototype → Viable → Production-Ready → Mature → Exemplary).

**Core document:**
- **[MATURITY_ROADMAP.md](../project-designer/MATURITY_ROADMAP.md)** — Progression levels and next-step guidance per pillar

**Maturity Levels:**
| Level | Score | Timeline | Focus |
|-------|-------|----------|-------|
| Prototype | <40% | Weeks | Test core idea; minimal tooling |
| Viable | 40–60% | Months 1–3 | Feature-complete; basic CI/CD |
| Production-Ready | 60–80% | Months 3–6 | Defensible architecture; monitoring |
| Mature | 80–95% | Months 6–12 | Comprehensive practices; secure |
| Exemplary | 95%+ | 12+ months | Industry-leading; continuous improvement |

**How to use:**
- Assessment: Determine this project's current level
- Planning: Use roadmap to identify quick wins for next level
- Priorities: Focus on pillar gaps that block progression

## Portfolio Standards & Frameworks

This project follows **three complementary frameworks** from `project-designer/` for engineering excellence:

### 1️⃣ Architecture Validation: 8-Pillar Framework

**Purpose:** Assess and improve architecture across 8 dimensions (NASA/Tesla/Apple/Toyota standards).

**Core documents:**
- **[FRAMEWORK.md](../project-designer/FRAMEWORK.md)** — 48 rules (6 per pillar) with examples
- **[CHECKLIST.md](../project-designer/CHECKLIST.md)** — Scoreable rubric (0–5 per pillar, target 4+/5)
- **[PLAYBOOKS.md](../project-designer/PLAYBOOKS.md)** — Step-by-step fixes for common gaps by pillar

**The 8 Pillars:**
1. Architecture Discipline & Traceability — Documented design, ADRs, explicit boundaries
2. Build Quality In / Error-Proofing — Type hints, linting, pinned dependencies, no secrets
3. Verification & Validation — Test gates, coverage, chaos tests, bounded complexity
4. Continuous Integration & Safe Delivery — Automated gates, reversible migrations, rollback
5. Root-Cause Driven Improvement — Post-mortems, refactor patterns, tech-debt cadence
6. Security & Privacy by Design — Least-privilege, secrets, input validation, CVE scanning
7. Observability & Telemetry — Structured logging, SLOs, dashboards, runbooks
8. Maintainability & Sustainable Pace — Domain naming, bounded file size, justified deps

**How to use:**
- Before reviews: Read [FRAMEWORK.md](../project-designer/FRAMEWORK.md) + [CHECKLIST.md](../project-designer/CHECKLIST.md)
- When fixing gaps: Link to pillar + rule, consult [PLAYBOOKS.md](../project-designer/PLAYBOOKS.md)
- Score target: 4+/5 per pillar (80%+ overall)

---

### 2️⃣ Engineering Standards: 11 Core Practices

**Purpose:** Ensure all projects follow consistent engineering practices (observability, error handling, testing, deployment, etc.).

**Core document:**
- **[ENGINEERING_STANDARDS_BASE.md](../project-designer/ENGINEERING_STANDARDS_BASE.md)** — 11 mandatory practices for all projects

**The 11 Standards:**
1. Observability — Structured logging (JSON), metrics (Prometheus), health checks
2. Error Handling — Specific exceptions, standard error responses, logging
3. Configuration — No hardcoding; all config via environment variables
4. Type Hints — All functions must have type annotations
5. Testing — ≥85% coverage; test error paths and edge cases
6. Code Organization — Files <1500 lines, single responsibility principle
7. Deployment — Health checks, graceful shutdown, readiness probes
8. Incident Response — Runbooks, SLOs, post-mortems for failures
9. Code Review — Checklist-based, minimum 2 reviewers
10. Documentation — Docstrings, README, architecture diagrams
11. Git Standards — Conventional commits, GPG signing recommended

**How to use:**
- New code: Follow the 11 standards from day one
- Reviews: Check against standards as part of code review
- Refactoring: Prioritize gaps in standards (especially observability, testing, error handling)

---

### 3️⃣ Requirements-Driven V-Model

**Purpose:** Trace requirements → design → implementation → validation (tests). Every feature is testable and linked to requirements.

**Core document:**
- **[V_MODEL_REQUIREMENTS.md](../project-designer/V_MODEL_REQUIREMENTS.md)** — Full V-Model framework with templates

**The V-Model Structure:**
```
REQUIREMENTS (Left)          VALIDATION (Right)
├─ Functional Specs          ├─ System Tests
├─ Non-Functional Specs      ├─ Integration Tests
├─ Use Cases                 ├─ Unit Tests
├─ Acceptance Criteria       └─ Acceptance Tests
└─ Traceability Matrix       └─ Bugs linked to requirements
```

**How to use:**
- Document: Maintain `FUNCTIONAL_REQUIREMENTS.md` and `NONFUNCTIONAL_REQUIREMENTS.md` in project root
- Track: Use tracker's V-Model dashboard to monitor requirements status (if applicable)
- Validate: Link tests to requirements (test IDs match requirement IDs)

---

### 4️⃣ Maturity Roadmap

**Purpose:** Understand project maturity level and progression path (Prototype → Viable → Production-Ready → Mature → Exemplary).

**Core document:**
- **[MATURITY_ROADMAP.md](../project-designer/MATURITY_ROADMAP.md)** — Progression levels and next-step guidance per pillar

**Maturity Levels:**
| Level | Score | Timeline | Focus |
|-------|-------|----------|-------|
| Prototype | <40% | Weeks | Test core idea; minimal tooling |
| Viable | 40–60% | Months 1–3 | Feature-complete; basic CI/CD |
| Production-Ready | 60–80% | Months 3–6 | Defensible architecture; monitoring |
| Mature | 80–95% | Months 6–12 | Comprehensive practices; secure |
| Exemplary | 95%+ | 12+ months | Industry-leading; continuous improvement |

**How to use:**
- Assessment: Determine this project's current level
- Planning: Use roadmap to identify quick wins for next level
- Priorities: Focus on pillar gaps that block progression

## Portfolio Standards & Frameworks

This project follows **three complementary frameworks** from `project-designer/` for engineering excellence:

### 1️⃣ Architecture Validation: 8-Pillar Framework

**Purpose:** Assess and improve architecture across 8 dimensions (NASA/Tesla/Apple/Toyota standards).

**Core documents:**
- **[FRAMEWORK.md](../project-designer/FRAMEWORK.md)** — 48 rules (6 per pillar) with examples
- **[CHECKLIST.md](../project-designer/CHECKLIST.md)** — Scoreable rubric (0–5 per pillar, target 4+/5)
- **[PLAYBOOKS.md](../project-designer/PLAYBOOKS.md)** — Step-by-step fixes for common gaps by pillar

**The 8 Pillars:**
1. Architecture Discipline & Traceability — Documented design, ADRs, explicit boundaries
2. Build Quality In / Error-Proofing — Type hints, linting, pinned dependencies, no secrets
3. Verification & Validation — Test gates, coverage, chaos tests, bounded complexity
4. Continuous Integration & Safe Delivery — Automated gates, reversible migrations, rollback
5. Root-Cause Driven Improvement — Post-mortems, refactor patterns, tech-debt cadence
6. Security & Privacy by Design — Least-privilege, secrets, input validation, CVE scanning
7. Observability & Telemetry — Structured logging, SLOs, dashboards, runbooks
8. Maintainability & Sustainable Pace — Domain naming, bounded file size, justified deps

**How to use:**
- Before reviews: Read [FRAMEWORK.md](../project-designer/FRAMEWORK.md) + [CHECKLIST.md](../project-designer/CHECKLIST.md)
- When fixing gaps: Link to pillar + rule, consult [PLAYBOOKS.md](../project-designer/PLAYBOOKS.md)
- Score target: 4+/5 per pillar (80%+ overall)

---

### 2️⃣ Engineering Standards: 11 Core Practices

**Purpose:** Ensure all projects follow consistent engineering practices (observability, error handling, testing, deployment, etc.).

**Core document:**
- **[ENGINEERING_STANDARDS_BASE.md](../project-designer/ENGINEERING_STANDARDS_BASE.md)** — 11 mandatory practices for all projects

**The 11 Standards:**
1. Observability — Structured logging (JSON), metrics (Prometheus), health checks
2. Error Handling — Specific exceptions, standard error responses, logging
3. Configuration — No hardcoding; all config via environment variables
4. Type Hints — All functions must have type annotations
5. Testing — ≥85% coverage; test error paths and edge cases
6. Code Organization — Files <1500 lines, single responsibility principle
7. Deployment — Health checks, graceful shutdown, readiness probes
8. Incident Response — Runbooks, SLOs, post-mortems for failures
9. Code Review — Checklist-based, minimum 2 reviewers
10. Documentation — Docstrings, README, architecture diagrams
11. Git Standards — Conventional commits, GPG signing recommended

**How to use:**
- New code: Follow the 11 standards from day one
- Reviews: Check against standards as part of code review
- Refactoring: Prioritize gaps in standards (especially observability, testing, error handling)

---

### 3️⃣ Requirements-Driven V-Model

**Purpose:** Trace requirements → design → implementation → validation (tests). Every feature is testable and linked to requirements.

**Core document:**
- **[V_MODEL_REQUIREMENTS.md](../project-designer/V_MODEL_REQUIREMENTS.md)** — Full V-Model framework with templates

**The V-Model Structure:**
```
REQUIREMENTS (Left)          VALIDATION (Right)
├─ Functional Specs          ├─ System Tests
├─ Non-Functional Specs      ├─ Integration Tests
├─ Use Cases                 ├─ Unit Tests
├─ Acceptance Criteria       └─ Acceptance Tests
└─ Traceability Matrix       └─ Bugs linked to requirements
```

**How to use:**
- Document: Maintain `FUNCTIONAL_REQUIREMENTS.md` and `NONFUNCTIONAL_REQUIREMENTS.md` in project root
- Track: Use tracker's V-Model dashboard to monitor requirements status (if applicable)
- Validate: Link tests to requirements (test IDs match requirement IDs)

---

### 4️⃣ Maturity Roadmap

**Purpose:** Understand project maturity level and progression path (Prototype → Viable → Production-Ready → Mature → Exemplary).

**Core document:**
- **[MATURITY_ROADMAP.md](../project-designer/MATURITY_ROADMAP.md)** — Progression levels and next-step guidance per pillar

**Maturity Levels:**
| Level | Score | Timeline | Focus |
|-------|-------|----------|-------|
| Prototype | <40% | Weeks | Test core idea; minimal tooling |
| Viable | 40–60% | Months 1–3 | Feature-complete; basic CI/CD |
| Production-Ready | 60–80% | Months 3–6 | Defensible architecture; monitoring |
| Mature | 80–95% | Months 6–12 | Comprehensive practices; secure |
| Exemplary | 95%+ | 12+ months | Industry-leading; continuous improvement |

**How to use:**
- Assessment: Determine this project's current level
- Planning: Use roadmap to identify quick wins for next level
- Priorities: Focus on pillar gaps that block progression

## Tracker Integration: V-Model & Requirements

This project participates in a portfolio-wide **requirements tracking system**.
All requirements are synced bidirectionally with a central tracker.

**Your Project Files:**
- `./V_MODEL_BOARD.md` — Auto-generated board showing phase progress
  (coverage %, requirements status, linked bugs)
- `./FUNCTIONAL_REQUIREMENTS.md` — Feature specs you maintain
- `./NONFUNCTIONAL_REQUIREMENTS.md` — Performance/reliability specs you maintain

**Workflow:**
1. Edit FUNCTIONAL/NONFUNCTIONAL_REQUIREMENTS.md
2. Tracker auto-imports every 5 minutes
3. Update status in tracker UI as you implement (Proposed → Validated)
4. View your phase progress in V_MODEL_BOARD.md
5. Link bugs to requirements when issues found

**Tracker Dashboard:** http://localhost:5173

**Auto-Sync (every 5 minutes):**
- Requirements imported from your files → Tracker DB
- V_MODEL_BOARD.md exported to your project
- Requirement status updates flow back to your board

See V_MODEL_BOARD.md in your project root for current phase progress.

---

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## SSH Setup

- **Primary key**: `~/.ssh/openhab_claude` (used for `claude` user)
- **Fallback**: Password auth available for `openhabian` user
- **Hosts**: `openhabian@192.168.3.25` or `claude@192.168.3.25`

## System Architecture

The OpenHAB 2 system is deployed remotely with the following structure:

```
/home/openhabian/homeassistant/
├── automations.yaml          # YAML-based automation rules
└── (other config files)

/etc/openhab2/
├── automation/jsr223/python/personal/
│   ├── 082_tomato_led.py     # Python automation scripts
│   └── (other Python scripts)
└── (other OpenHAB configuration)
```

**Access**: SSH key at `~/.ssh/openhab_claude` for user `claude@192.168.3.25`

## Common Commands

### Fetch Automations from Remote

```bash
# Get the current automations.yaml
scp openhabian@192.168.3.25:/home/openhabian/homeassistant/automations.yaml /tmp/automations_current.yaml

# Get a specific Python automation script
scp -i ~/.ssh/openhab_claude claude@192.168.3.25:/etc/openhab2/automation/jsr223/python/personal/082_tomato_led.py /tmp/082_tomato_led.py
```

### Deploy Automations to Remote

```bash
# Upload and replace automations.yaml
# First, edit locally, then:
cat /tmp/automations_current.yaml | ssh openhabian@192.168.3.25 "cat > /home/openhabian/homeassistant/automations.yaml"

# Upload a Python script
scp -i ~/.ssh/openhab_claude /tmp/082_tomato_led.py claude@192.168.3.25:/etc/openhab2/automation/jsr223/python/personal/082_tomato_led.py

# Transfer other files
scp -i ~/.ssh/openhab_claude /tmp/wakeomv.sh claude@192.168.3.25:/tmp/wakeomv.sh
```

### Inspect Remote System

```bash
# SSH into the system
ssh openhabian@192.168.3.25
ssh -i ~/.ssh/openhab_claude claude@192.168.3.25

# Check OpenHAB logs
ssh openhabian@192.168.3.25 "tail -f /var/log/openhab2/openhab.log"

# Verify automation files are in place
ssh -i ~/.ssh/openhab_claude claude@192.168.3.25 "ls -la /etc/openhab2/automation/jsr223/python/personal/"
```

## Workflow

1. **Fetch** current automations: `scp ... /tmp/automations_current.yaml`
2. **Edit** locally in `/tmp/` (or elsewhere)
3. **Test** by understanding the YAML/Python syntax
4. **Deploy** via `scp` or SSH piping back to the remote system
5. **Verify** with `ssh ... tail -f /var/log/openhab2/openhab.log` to check for errors

## Project Purpose

This is a working directory for managing automation rules and scripts on a remote **OpenHAB 2** home automation system running at `192.168.3.25` (user: `openhabian` and `claude`).

OpenHAB 2 is a vendor-agnostic, Java-based home automation platform. It manages:
- **Items** (logical devices/sensors)
- **Rules** (automation logic triggered by item state changes)
- **Bindings** (integrations with physical devices and services)
- **Automation scripts** (Python, JavaScript via JSR223 scripting engine)

## OpenHAB 2 Concepts

### YAML Automations
- Located in `/home/openhabian/homeassistant/automations.yaml`
- Define trigger → condition → action flows
- Triggers: item state changes, time-based, system events
- Actions: send commands to items, log messages, call scripts

### Python Automation Scripts (JSR223)
- Located in `/etc/openhab2/automation/jsr223/python/personal/`
- Run in the OpenHAB context with access to items, rules engine, logging
- Useful for complex logic, data processing, external API calls
- Scripts are auto-loaded on OpenHAB startup
