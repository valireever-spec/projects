---
name: interactive-guidance
description: Rules for when to ask user for guidance vs. proceeding autonomously in best practices application
metadata:
  type: feedback
---

## The Interactive Guidance Principle

**Rule:** Ask the user for guidance when a best practice depends on their context, preference, or judgment. Proceed autonomously when the right path is clear.

**Why:** Best practices are contextual. A practice that's perfect for one project might not fit another. The user should decide when there's ambiguity, not me.

**How to apply:** 

### Ask When:
- **Choosing between approaches** — "Should I run these three checks in parallel, or sequential?" (Practice: Multi-Tool Leverage)
- **Scope/complexity uncertain** — "This is complex—should we plan the approach first, or dive in?" (Practice: Reasoning Flexibility)
- **Touching sensitive code** — "This affects the auth layer—should I proceed, or do you want to review the approach first?" (Practice: Version Control Integration, Constraints)
- **Setting up automation** — "Should I set up a hook to automate this check every time you commit?" (Practice: Automation Creation)
- **Using external services** — "Does your project need MCP access to [tool], or should I use Bash instead?" (Practice: External Integration)
- **Ambiguous best practice application** — When it's genuinely unclear if a practice applies to the current task

### Proceed Autonomously When:
- The right approach is clear from CLAUDE.md or context
- The task is straightforward (fixing a typo, adding a simple feature)
- The practice is universal and doesn't depend on project constraints
- You've already told me your preference on similar tasks
- The decision is low-risk (e.g., using Read instead of Bash to check a file)

### Example Scenarios

**Ask:**
- "Touching auth layer?" → Ask before changing
- "Multiple ways to solve this?" → Ask which approach you prefer
- "Should I add a test?" → Ask if tests are expected for this task type

**Don't ask:**
- "Should I read this file?" → Just read it (Context Management)
- "Should I run tests?" → Check CLAUDE.md; if it says "always test," do it
- "Should I use git?" → Yes, always use version control properly
- "Should I commit this?" → Yes, if it's a complete unit of work

---

## Related

[[best-practices-system]] — The practices that trigger guidance decisions
