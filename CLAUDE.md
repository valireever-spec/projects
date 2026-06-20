# CLAUDE.md

This projects directory validates software architecture across a portfolio using an **8-pillar framework** grounded in NASA, Tesla, Apple, and Toyota standards.

## Quick Start: Review a Project

```bash
cd project-designer
bash scripts/prepare-review.sh /path/to/project ProjectName
```

This auto-generates a review template + mechanical findings. See [REVIEW_QUICK_START.md](project-designer/REVIEW_QUICK_START.md) for details.

## The 8 Pillars

1. **Architecture Discipline & Traceability** — Documented design, ADRs, explicit boundaries
2. **Build Quality In / Error-Proofing** — Type hints, linting, pinned dependencies, no secrets
3. **Verification & Validation** — Test gates, coverage, chaos tests, bounded complexity
4. **Continuous Integration & Safe Delivery** — Automated gates, reversible migrations, rollback
5. **Root-Cause Driven Improvement** — Post-mortems, refactor patterns, tech-debt cadence
6. **Security & Privacy by Design** — Least-privilege, secrets, input validation, CVE scanning
7. **Observability & Telemetry** — Structured logging, SLOs, dashboards, runbooks
8. **Maintainability & Sustainable Pace** — Domain naming, bounded file size, justified deps

## Framework Resources

- **[FRAMEWORK.md](project-designer/FRAMEWORK.md)** — 48 rules (6 per pillar)
- **[CHECKLIST.md](project-designer/CHECKLIST.md)** — Scoreable rubric
- **[PLAYBOOKS.md](project-designer/PLAYBOOKS.md)** — Step-by-step fixes
- **[RULES_SUMMARY.md](project-designer/RULES_SUMMARY.md)** — One-page reference
- **[reviews/](project-designer/reviews/)** — Dated project analyses

## Token-Saving Setup

See [SETUP_FOR_REVIEWS.md](project-designer/SETUP_FOR_REVIEWS.md) for presets that avoid re-reading framework docs. Memory files cache reusable knowledge:
- `~/.claude/projects/-home-vali-projects/memory/framework_pillar_reference.md`
- `~/.claude/projects/-home-vali-projects/memory/common_review_patterns.md`
- `~/.claude/projects/-home-vali-projects/memory/playbook_index.md`

## Architecture Review Workflow

1. Run prep script → auto-generates template + auto_check.py findings
2. Fill Snapshot, Strengths, Gaps sections (reference past reviews)
3. Score using [CHECKLIST.md](project-designer/CHECKLIST.md)
4. Link gaps to [PLAYBOOKS.md](project-designer/PLAYBOOKS.md) (don't re-derive)
5. Recommend next steps using [MATURITY_ROADMAP.md](project-designer/MATURITY_ROADMAP.md)
