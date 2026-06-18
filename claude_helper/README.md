# Claude Code Best Practices Helper

A system for applying Anthropic's Claude Code best practices across all your projects consistently.

## What's Here

1. **BEST_PRACTICES.md** — The 9 core practices from the Anthropic course, with explanations and when to apply each
2. **CLAUDE_TEMPLATE.md** — A reusable template for creating `CLAUDE.md` files in your projects
3. **Memory system** — Practices stored so Claude applies them automatically in every session

## Quick Start

### For Each of Your Projects

1. Copy `CLAUDE_TEMPLATE.md` to your project as `CLAUDE.md`
2. Fill it out with:
   - Which of the 9 practices apply
   - Critical files and architecture
   - Constraints and how to run the project
   - Any project-specific preferences
3. At the start of a Claude session, I'll read it and apply the practices

### How It Works

- **I apply practices by default** — All 9 practices unless your CLAUDE.md says otherwise
- **I ask for guidance when unclear** — "Should I proceed with this change, or does it need review first?"
- **You stay in control** — Each CLAUDE.md is project-specific; you decide what applies

## The 9 Practices (Quick Reference)

| # | Practice | Always? | Key Idea |
|---|----------|---------|----------|
| 1 | Architecture Understanding | ✓ | Know the codebase structure first |
| 2 | Multi-Tool Leverage | ✓ | Use the right tool for each task, parallelize when possible |
| 3 | Context Management | ✓ | Keep context focused; reference specific files |
| 4 | Visual Communication | ~ | Use screenshots for UI work |
| 5 | Automation Creation | ~ | Create hooks for repetitive workflows |
| 6 | External Integration | ~ | Use MCP servers for external services |
| 7 | Version Control | ✓ | Follow git discipline and commit conventions |
| 8 | Reasoning Flexibility | ✓ | Match approach to task complexity |
| 9 | Prerequisites & Environment | ✓ | Ensure proper setup |

**✓** = applies to every project  
**~** = applies when conditions exist

## Example: Setting Up a New Project

```bash
# In your new project directory:
cp ../claude_helper/CLAUDE_TEMPLATE.md ./CLAUDE.md

# Edit CLAUDE.md to fill in:
# - Project name/type
# - Critical files
# - Constraints
# - How to run/test
# - Which practices apply
```

Then, at the start of your Claude session in that project:

```
I'll read CLAUDE.md, understand your setup, and apply the best practices automatically.
```

## When I Ask You Questions

I'll ask when:
- **Uncertain about approach** — "Should I plan this first, or dive in?"
- **Touching sensitive code** — "This affects X—should I proceed?"
- **Multiple valid paths** — "Should I run these in parallel or sequential?"
- **Automation setup** — "Should I create a hook for this?"

Answer concisely—your feedback shapes how I proceed.

## Files & Structure

```
/claude_helper
  BEST_PRACTICES.md      — Full guide (read this first)
  CLAUDE_TEMPLATE.md     — Template for your projects
  README.md              — This file
  /memory
    MEMORY.md            — Index of practices in memory
    best-practices-system.md
    interactive-guidance.md
```

## What Each Practice Does

### 1. Architecture Understanding
Read CLAUDE.md first. Understand the structure before diving in.

### 2. Multi-Tool Leverage
Use Read for exploration, Edit for changes, Bash for git/scripts, Agent for complex tasks. Parallelize independent operations.

### 3. Context Management
Reference specific files and line numbers. Don't dump entire codebases. Use screenshots for UI work.

### 4. Visual Communication
Show me screenshots of your app. Share before/after comparisons.

### 5. Automation Creation
If you repeat something >2x, we can automate it via hooks in settings.json.

### 6. External Integration
Need to talk to an API, database, or service? Set up MCP servers.

### 7. Version Control Integration
Clean commits, meaningful messages, follow project conventions.

### 8. Reasoning Flexibility
Simple tasks get direct execution. Complex architecture decisions get a planning phase first.

### 9. Prerequisites & Environment
Ensure you have bash/git fundamentals and project-specific tools installed.

## Next Steps

1. Read **BEST_PRACTICES.md** (10 min read) to understand the full system
2. Copy **CLAUDE_TEMPLATE.md** to your first project and customize it
3. Start a Claude session in that project—I'll read CLAUDE.md and apply practices
4. As I work, I'll ask you for guidance when it's needed

---

**Questions?** Each practice has a "When Claude asks you" section in BEST_PRACTICES.md that shows what guidance you might give.
