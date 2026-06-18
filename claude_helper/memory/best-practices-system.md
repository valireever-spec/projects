---
name: best-practices-system
description: 9 core practices from Anthropic Claude Code course for applying Claude across all projects, with guidance on when each applies
metadata:
  type: project
---

## The 9 Core Practices

**Always apply:** Architecture Understanding, Multi-Tool Leverage, Context Management, Version Control Integration, Reasoning Flexibility, Prerequisites

**Apply when relevant:** Visual Communication (UI work), Automation Creation (repeated workflows), External Integration (APIs/MCP servers)

### 1. Architecture Understanding
- Grasp codebase structure before requesting help
- Brief on critical dependencies and patterns
- Identify relevant tools (Read, Edit, Bash, Agent)

**How to apply:** Document key architectural patterns in CLAUDE.md; identify critical files upfront; clarify dependencies

### 2. Multi-Tool Leverage
- Use specialized tools to handle complex multi-step tasks
- Chain tools efficiently; parallelize independent operations
- Avoid redundant reads or unnecessary tool-switching

**How to apply:** Identify which tools solve which parts; run independent operations in parallel; use appropriate tools for each task type

### 3. Context Management Strategy
- Maintain focused conversations by referencing only relevant resources
- Don't dump entire codebases; use file paths and line numbers
- Use visual inputs (screenshots) for UI/UX clarity

**How to apply:** Provide specific file paths/line numbers; use screenshots for UI changes; summarize rather than paste large outputs

### 4. Visual Communication
- Use screenshots/diagrams to convey changes clearly, reduce ambiguity
- Share before/after comparisons; use mockups for new interfaces

**How to apply:** Screenshot the app; show before/after; use diagrams for complex flows

### 5. Automation Creation
- Build reusable custom commands/hooks to eliminate repetitive work
- Hook into settings.json; create CLI shortcuts; set up MCP servers

**How to apply:** Identify repetitive patterns; create hooks in settings.json; build custom commands if needed

### 6. External Integration
- Extend capabilities through MCP servers for specialized workflows
- Document required external services; set up auth/credentials securely

**How to apply:** Identify external tools needed; configure relevant MCP servers; test integrations early

### 7. Version Control Integration
- Set up automated code review; integrate AI assistance into GitHub workflows
- Maintain clean commit history; follow conventions

**How to apply:** Use pre-commit hooks if relevant; code review before pushing; follow commit message conventions

### 8. Reasoning Flexibility
- Apply different thinking modes based on task complexity
- Simple tasks: direct execution; complex: planning mode, code review; debugging: exploratory approach

**How to apply:** Let Claude suggest planning for complex tasks; use code review for high-stakes changes; match approach to complexity

### 9. Prerequisites & Environment
- Ensure foundational skills and environment setup (CLI proficiency, Git fundamentals)
- Document project-specific tool requirements

**How to apply:** Have bash basics, Git fundamentals; document special setup needs in CLAUDE.md

---

## How I Apply These

**In every project/session:**
1. Read CLAUDE.md first (if it exists) to understand which practices apply
2. Apply all 9 practices by default UNLESS the project says otherwise
3. Use the appropriate tools and approach for the task type
4. Ask you when uncertain or when a practice might not apply

**Key principle:** These are guidelines, not rules. If a project's CLAUDE.md disables a practice, I respect that. Otherwise, I apply them proactively.
