# Claude Configuration - [PROJECT_NAME]

This file configures how Claude Code works with this project. Copy this template to your project as `CLAUDE.md` and customize it.

---

## Project Overview

**Name:** [Project name]  
**Type:** [CLI / Web / API / Library / Monorepo / Other]  
**Primary Language:** [Go / Python / TypeScript / Rust / etc.]  
**Purpose:** [What does this project do? 1-2 sentences]

---

## Best Practices Applied

Which of the 9 core practices apply here? (See BEST_PRACTICES.md for details)

- [ ] 1. Architecture Understanding — Document key files/patterns below
- [ ] 2. Multi-Tool Leverage — Project uses complex workflows
- [ ] 3. Context Management — High file count, careful with context
- [ ] 4. Visual Communication — UI/UX work included
- [ ] 5. Automation Creation — Has hooks/custom workflows
- [ ] 6. External Integration — Uses MCP servers or APIs
- [ ] 7. Version Control Integration — Strict git/PR workflow
- [ ] 8. Reasoning Flexibility — Complex architecture decisions
- [ ] 9. Prerequisites & Environment — Special setup needed

---

## Critical Files & Architecture

List the core modules/files Claude should know about:

```
/src
  /core          - Core functionality
  /handlers      - Request handlers / APIs
  /utils         - Shared utilities
/tests           - Test suite
```

**Key patterns:**
- [Pattern 1: e.g., "All handlers follow middleware → validation → action → response"]
- [Pattern 2: e.g., "Database models in /models, migrations in /migrations"]

---

## Constraints & Decisions

What should Claude know before touching this code?

- **No changes to:** [e.g., "authentication layer without review"]
- **Always test:** [e.g., "database migrations against staging first"]
- **Performance-critical:** [e.g., "request loop is under SLA, profile before optimizing"]
- **Compliance/Legal:** [e.g., "payment handling must pass PCI audit"]

---

## How to Run & Test

```bash
# Development
[how to start the dev server / run the CLI]

# Tests
[how to run tests]

# Build
[how to build for production]
```

---

## External Services & Tools

Does this project need MCP access?

- [ ] Database (which service?)
- [ ] API calls (which endpoints?)
- [ ] Browser automation
- [ ] File storage
- [ ] Other: [specify]

---

## Commit & PR Style

**Commit message format:**
```
[type]: Brief description (50 chars max)

Longer explanation if needed (72 char line wrap).
```

**Types:** `fix:`, `feat:`, `refactor:`, `test:`, `docs:`, `chore:`

**PR expectations:**
- [ ] Tests included
- [ ] No breaking changes without discussion
- [ ] Code reviewed before merge
- [ ] Changelog updated

---

## Common Workflows

### Adding a Feature
1. Create a branch: `git checkout -b feat/[name]`
2. [Any special setup?]
3. Add tests first (TDD) or after?
4. Commit and open PR

### Fixing a Bug
1. Create a branch: `git checkout -b fix/[issue]`
2. Add a failing test first
3. Fix the bug
4. Verify test passes

### Running Tests
```bash
[command]
```

---

## What Claude Should Ask You

I'll ask for guidance when:
- A practice might not apply to this task
- You have a choice between two approaches
- A change could break something important
- I'm uncertain about project scope

**Example:** "This touches the auth layer—should I proceed, or do you want to review the approach first?"

---

## Contact / Notes

- **Owner:** [Your name]
- **Slack/Chat:** [Where to reach you if needed]
- **Related projects:** [Any dependencies or related codebases]
- **Known issues:** [Anything Claude should avoid]

---

## Last Updated
[Date] — Update this when you change CLAUDE.md
