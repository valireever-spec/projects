# Quick Start Guide

Get your project set up with Claude best practices in 5 minutes.

## Step 1: Copy the Template (2 min)

```bash
cp /home/vali/projects/claude_helper/CLAUDE_TEMPLATE.md ./CLAUDE.md
```

## Step 2: Fill Out CLAUDE.md (3 min)

Edit `CLAUDE.md` in your project:

```markdown
# Claude Configuration - [YOUR_PROJECT]

## Project Overview
Name: [your project name]
Type: [Web / CLI / API / Library / etc.]
Primary Language: [Python / TypeScript / Go / etc.]
Purpose: [What does it do? 1-2 sentences]

## Critical Files
- /src → Core code
- /tests → Tests
- /config → Configuration

## Key Patterns
- [Describe 1-2 architectural patterns]

## Constraints
- [What should I avoid? What's sensitive?]

## How to Run
[Your build/run commands]

## Practices Applied
- [x] Architecture Understanding
- [x] Multi-Tool Leverage
- [x] Context Management
- [ ] Visual Communication (not UI work)
- [ ] Automation Creation (no repetitive workflows yet)
[etc.]
```

## Step 3: Start a Claude Session

When you open Claude in your project, I will:
1. Read `CLAUDE.md`
2. Apply the 9 best practices
3. Ask for guidance when unclear

That's it!

---

## What Happens Next

### I Will:
✓ Read CLAUDE.md automatically  
✓ Understand your project structure  
✓ Apply best practices from day one  
✓ Ask questions when I need your input  

### You Do:
→ Answer concisely when I ask  
→ Update CLAUDE.md if things change  
→ Trust the practices (they come from Anthropic's course)  

---

## Common Questions

**Q: Do I have to fill out CLAUDE.md perfectly?**  
A: No. Fill in what you know; we can refine it as we work.

**Q: Will Claude ask me about everything?**  
A: No—only when there's a real choice or uncertainty. Most work happens without questions.

**Q: Can I disable a practice for my project?**  
A: Yes. In CLAUDE.md, note which practices don't apply. I'll respect that.

**Q: What if I have multiple projects?**  
A: Each project gets its own CLAUDE.md. They can be different.

---

## Example: Minimal CLAUDE.md

Don't overthink it. Here's a minimal version:

```markdown
# Claude Configuration - MyProject

## Project
- Name: MyProject
- Type: Python CLI
- Purpose: Data processing tool

## Key Files
- /src/main.py → entry point
- /src/processor.py → core logic
- /tests → test suite

## How to Run
python -m src.main [args]

## Practices
All 9 apply as-is.
```

That's enough to get started!

---

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| BEST_PRACTICES.md | /claude_helper/ | Full reference |
| CLAUDE_TEMPLATE.md | /claude_helper/ | Copy to your projects |
| QUICK_START.md | /claude_helper/ | This file |
| CLAUDE.md | Each project | Project-specific config |

---

## Next: Read the Full Guide

Once your CLAUDE.md is created, read **BEST_PRACTICES.md** to understand the 9 practices in detail. (Optional but recommended—it's only 10 min.)

Ready to go! 🚀
