# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This projects directory contains a portfolio of software systems that you analyze and validate using a systematic **8-pillar architecture validation framework**. The goal is to:

- Identify architecture gaps, scalability risks, and modernization opportunities across projects
- Apply engineering standards from NASA, Tesla, Apple, and Toyota
- Recommend prioritized improvements backed by structured analysis

## The Architecture Validation Framework

**Location**: `/home/vali/projects/project-designer/`

The framework assesses software architecture against 8 foundational pillars, grounded in world-class engineering standards:

1. **Architecture Discipline & Traceability** — Documented design, ADRs, explicit boundaries, no circular deps
2. **Build Quality In / Error-Proofing** — Type-checking, linting, schema validation, pinned dependencies, no secrets
3. **Verification & Validation** — Test gates, coverage on critical paths, integration/chaos tests, bounded complexity
4. **Continuous Integration & Safe Delivery** — Automated gates before prod, reversible migrations, rollback paths
5. **Root-Cause Driven Improvement** — Post-mortems, refactor recurring patterns, tech-debt cadence
6. **Security & Privacy by Design** — Least-privilege defaults, secrets management, input validation, CVE scanning
7. **Observability & Telemetry** — Structured logging, SLO-driven alerts, tested runbooks
8. **Maintainability & Sustainable Pace** — Domain-meaningful naming, bounded file size, justified dependencies

## Key Framework Files

### Analyze a New Project (Start Here)
- **`FRAMEWORK.md`** — 48 detailed rules (6 per pillar) with principles, verification methods, test scenarios, acceptable equivalents
- **`CHECKLIST.md`** — Scoreable rubric to apply to any project (mark ✅ Met / ⚠️ Partial / ❌ Gap / N/A)
- **`RULES_SUMMARY.md`** — One-page quick reference for fast scanning all rules

### Understand Maturity Levels & Improvements
- **`MATURITY_ROADMAP.md`** — How to progress from prototype (40%) → viable (60%) → production (80%) → mature (95%)
- **`PLAYBOOKS.md`** — 8 step-by-step guides for fixing common gaps (FastAPI + Python focused, copy-paste ready)
- **`scripts/auto_check.py`** — Automated checker for 13 mechanical rules; generates quick feedback

### Real-World Examples
- **`PORTFOLIO_SUMMARY.md`** — Cross-portfolio analysis of all projects with patterns and priority order
- **`reviews/`** — Detailed dated analysis of individual projects following the structure: Snapshot → Strengths → Gaps (ranked) → Recommendations

## How to Analyze a Project

### Quick Audit (15–30 minutes)
1. Read the target project's `README.md` and architecture docs
2. Scan `project-designer/RULES_SUMMARY.md` to familiarize yourself with the 48 rules
3. Run `python project-designer/scripts/auto_check.py /path/to/project` for mechanical findings
4. Apply a subset of `CHECKLIST.md` focused on high-risk areas (Security, CI/CD, testing)

### Full Analysis (1–3 hours)
1. Read `project-designer/FRAMEWORK.md` pillars 1 and 2 (Architecture Discipline, Build Quality In)
2. Use `project-designer/CHECKLIST.md` as a scoring sheet: walk through each rule, mark status, gather evidence
3. Create a dated review in `project-designer/reviews/YYYY-MM-DD-<project-name>.md` with:
   - **Snapshot** — Tech stack, team size, deployment pattern
   - **Score** — % Met (✅), % Partial (⚠️), % Gap (❌)
   - **Strengths** — What's working well (2–4 items)
   - **Top Gaps** — Ranked by impact × effort; reference playbooks where available
   - **Recommendations** — Prioritized actions with effort estimates
4. If needed, reference `project-designer/PLAYBOOKS.md` for implementation guides

## Common Commands

```bash
# Run automated checker on a project (13 mechanical rules)
python project-designer/scripts/auto_check.py /path/to/project

# View the checklist for manual scoring
less project-designer/CHECKLIST.md

# Check recent reviews
ls -lt project-designer/reviews/

# See portfolio summary (cross-project patterns)
less project-designer/PORTFOLIO_SUMMARY.md
```

## Architecture Review Workflow

1. **Receive request** → Which project? What's the goal (quick assessment vs. detailed review)?
2. **Gather evidence** → Read code, tests, CI config, docs; run auto-check.py if applicable
3. **Score against framework** → Use CHECKLIST.md or RULES_SUMMARY.md to identify gaps
4. **Rank by impact** — Pair risk (if unaddressed) with effort (to fix); prioritize high-impact, low-effort wins
5. **Write dated review** → Follow structure in `reviews/` examples; link to PLAYBOOKS.md for fixes
6. **Suggest next steps** — Use MATURITY_ROADMAP.md to frame progress trajectory

## Key Principles

- **Systems thinking**: Assess whole architecture, not just one layer or component
- **Standards-grounded**: Every pillar and rule traces to NASA, Tesla, Apple, or Toyota practices
- **Evidence-based**: Mark findings with proof (code location, test results, docs)
- **Actionable**: Rank recommendations by impact and effort; link to playbooks for implementation
- **Iterative**: Reviews inform tech-debt backlog; revisit quarterly to track progress

## Related Projects

- **`investing-platform/`** — First detailed review (40% score initially); extensive playbook references and quick wins
- **Other projects** — See `PORTFOLIO_SUMMARY.md` for quick assessment of all 10 projects
