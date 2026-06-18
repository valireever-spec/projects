# Claude Code Best Practices System

A comprehensive guide for applying Claude effectively across all projects. Not all practices apply to every project—this system helps identify which ones are relevant.

---

## 1. Architecture Understanding
**What it means:** Grasp how AI assistants interact with codebases through tool integration and code analysis mechanics.

**When to apply:** Every project
- Understand the codebase structure before asking for help
- Brief Claude on critical dependencies and patterns
- Identify which tools (Read, Edit, Bash, etc.) are most relevant to the task

**How to apply:**
- [ ] Document key architectural patterns in CLAUDE.md
- [ ] Identify critical files or modules upfront
- [ ] Clarify dependencies and constraints

**When Claude asks you:** "Should I proceed with reading these files, or should I focus on a specific area first?"

---

## 2. Multi-Tool Leverage
**What it means:** Combine multiple tools (Read, Edit, Bash, Agent) to handle complex, multi-step tasks.

**When to apply:** Projects with >3 file edits, build/test workflows, or codebase exploration
- Use specialized tools (Bash for git, Read for exploration, Edit for changes)
- Chain tools efficiently (avoid redundant reads)
- Parallelize independent operations

**How to apply:**
- [ ] Identify which tools solve which parts of your task
- [ ] Run independent operations in parallel
- [ ] Avoid switching between tools unnecessarily

**When Claude asks you:** "Should I run these three checks in parallel, or do you want them sequential?"

---

## 3. Context Management Strategy
**What it means:** Maintain focused conversations by referencing only relevant project resources.

**When to apply:** Every project
- Don't dump entire codebases into context
- Reference specific files, line numbers, or patterns
- Use visual inputs (screenshots) for UI/UX clarification

**How to apply:**
- [ ] Provide file paths and line numbers, not full code dumps
- [ ] Use screenshots for UI changes
- [ ] Summarize rather than paste large outputs
- [ ] Clear context when pivoting to a new task

**When Claude asks you:** "I see multiple approaches—should I focus on X or Y?"

---

## 4. Visual Communication
**What it means:** Use screenshots and diagrams to convey changes clearly, reducing ambiguity.

**When to apply:** UI/UX work, design reviews, visual debugging
- Share screenshots before/after changes
- Use mockups for new interfaces
- Annotate diagrams for complex flows

**How to apply:**
- [ ] Screenshot the app running with your changes
- [ ] Show before/after comparisons
- [ ] Use mockups or diagrams for architecture discussions

**When Claude asks you:** "Can you share a screenshot so I can see the current state?"

---

## 5. Automation Creation
**What it means:** Build reusable custom commands and hooks to eliminate repetitive work.

**When to apply:** Workflows you repeat >2x, pre-commit checks, automated testing
- Hook into Claude's settings.json for automated behaviors
- Create CLI shortcuts for common tasks
- Set up MCP servers for specialized workflows

**How to apply:**
- [ ] Identify repetitive patterns in your workflow
- [ ] Create hooks in settings.json (e.g., "before committing, run tests")
- [ ] Build custom commands if needed (skills, agents)

**When Claude asks you:** "Should I set up a hook to automate this check every time you commit?"

---

## 6. External Integration
**What it means:** Extend capabilities through MCP servers for specialized workflows.

**When to apply:** Browser automation, API testing, specialized tools
- Use MCP servers for common integrations (databases, APIs, browsers)
- Document which external services your project needs
- Set up authentication and credentials securely

**How to apply:**
- [ ] Identify which external tools your project needs
- [ ] Configure relevant MCP servers
- [ ] Test integrations early

**When Claude asks you:** "Does your project need MCP access to [tool], or should I use Bash instead?"

---

## 7. Version Control Integration
**What it means:** Set up automated code review and integrate AI assistance into GitHub workflows.

**When to apply:** Every project with git
- Use GitHub integration for PR reviews
- Automate checks before push
- Maintain clean commit history

**How to apply:**
- [ ] Set up pre-commit hooks if relevant
- [ ] Use code review before pushing
- [ ] Follow commit message conventions (linked in CLAUDE.md)
- [ ] Leverage git history to understand decisions

**When Claude asks you:** "Should I create a new commit or amend the previous one?"

---

## 8. Reasoning Flexibility
**What it means:** Apply different thinking modes based on task complexity.

**When to apply:** All tasks
- Simple tasks: Direct execution
- Complex refactors/architecture: Planning mode, code review
- Debugging: Exploratory, hypothesis-driven approach

**How to apply:**
- [ ] Let Claude suggest planning for complex tasks
- [ ] Use code review for high-stakes changes
- [ ] Use exploratory mode for debugging
- [ ] Match the approach to the task complexity

**When Claude asks you:** "This is complex—should we plan the approach first, or dive in?"

---

## 9. Prerequisites & Environment
**What it means:** Ensure foundational skills and environment setup.

**When to apply:** Before starting any project
- [ ] Command-line proficiency (bash basics)
- [ ] Git version control fundamentals
- [ ] Project-specific tools installed and configured
- [ ] CI/CD pipeline understanding (if relevant)

---

## Using This System

### For Every New Project
1. Create a `CLAUDE.md` in the project (use the template in this repo)
2. Document which practices apply to this project
3. Note any project-specific constraints or patterns
4. Share this with Claude at the start of each session

### For Claude
- Apply all 9 practices by default
- **Ask you** when a practice might not apply, or when you need to choose between approaches
- Defer to project-specific guidance in CLAUDE.md

### When Claude Asks
Pay attention when Claude asks a question—it means the practice depends on your context or preference. Answer concisely so we stay aligned.

---

## Quick Reference

| Practice | Every Project? | Key Signal |
|----------|---|---|
| Architecture Understanding | Yes | Read CLAUDE.md first |
| Multi-Tool Leverage | Yes | Chain tools efficiently |
| Context Management | Yes | Keep context focused |
| Visual Communication | No* | When working on UI |
| Automation Creation | No* | When pattern repeats |
| External Integration | No* | When using external services |
| Version Control | Yes | Use git mindfully |
| Reasoning Flexibility | Yes | Match approach to complexity |
| Prerequisites | Yes | Set up environment |

*Applies when conditions are met
