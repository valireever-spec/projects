# Multi-Project Token Optimization Guide

**Overview:** Analysis and recommendations for 5 major projects. Prioritized by token impact.

---

## 🚨 CRITICAL: business-dev-platform

**Status:** 10,814 venv files committed to git (100+ MB)  
**Impact:** ~50K tokens wasted per session  
**Priority:** URGENT — Fix immediately

### What's Wrong
- `venv/` directory (10,814 files) is in git — should never be committed
- `dist/` and `build/` directories also in git
- This bloats the repo and wastes ~50K tokens when Claude loads it

### Fix (Step-by-step)

```bash
cd business-dev-platform

# 1. Remove venv from git history (one-time)
git filter-branch --tree-filter 'rm -rf venv dist build' -- --all

# 2. Force push to replace history
git push origin master --force-with-lease

# 3. Add to .gitignore
echo "venv/" >> .gitignore
echo "dist/" >> .gitignore
echo "build/" >> .gitignore
echo ".pytest_cache/" >> .gitignore
echo ".mypy_cache/" >> .gitignore
git add .gitignore
git commit -m "Add venv, dist, build to .gitignore"
git push origin master
```

### Why It Matters
- Venv is machine-specific; should not be in version control
- 100+ MB of binary files slows down clone/pull for all team members
- Claude Code scans these files, wasting 50K+ tokens per session

### Verification
```bash
git ls-files | grep "^venv/" # Should return nothing
git ls-files | grep "^dist/" # Should return nothing
```

---

## ⚠️ MEDIUM: testing-validation-platform

**Status:** 2 old phase/assessment files  
**Impact:** ~100 tokens/session  
**Priority:** Medium

### What's Here
- `ARCHITECTURE_ANALYSIS_20260620.md` (29 KB)
- `PHASE1_COMPLETION_REPORT.md` (11 KB)

These are assessment snapshots from June 20. Probably not actively used.

### Fix
```bash
mkdir -p .archive/assessments
mv ARCHITECTURE_ANALYSIS_20260620.md PHASE1_COMPLETION_REPORT.md .archive/assessments/
git add .archive/assessments/
git commit -m "Archive old phase and assessment reports"
git push origin master
```

### Optional
Check if these are referenced in tests or docs:
```bash
grep -r "ARCHITECTURE_ANALYSIS\|PHASE1_COMPLETION" . --include="*.py" --include="*.md"
```

If not referenced, they can be deleted entirely.

---

## 📋 LOW: car-platform

**Status:** Large ARCHITECTURE_STANDARDS.md (38 KB)  
**Impact:** ~200 tokens/session  
**Priority:** Low

### What's Here
- `ARCHITECTURE_STANDARDS.md` — comprehensive standards doc
- Useful if actively maintained; redundant if not

### Recommendation
**Keep it** unless:
1. It's duplicated in another doc
2. It's not referenced in code or tests
3. It's outdated

### Action
Check if it's actively used:
```bash
grep -r "ARCHITECTURE_STANDARDS" . --include="*.py" --include="*.md"
```

If used, keep it. If not, archive to `.archive/`.

---

## ✅ LOW: network-automation

**Status:** Clean  
**Files:** 4 small .md files (well-organized)  
**Impact:** None  
**Action:** None needed

---

## ✅ LOW: claude_course

**Status:** Clean  
**Files:** 4 small .md files (tracker integration docs)  
**Impact:** None  
**Action:** None needed

---

## Summary Table

| Project | Priority | Issue | Fix | Savings |
|---------|----------|-------|-----|---------|
| business-dev-platform | 🚨 CRITICAL | 10K venv files in git | Remove from history | 50K tokens |
| testing-validation-platform | ⚠️ MEDIUM | 2 old reports | Archive | 100 tokens |
| car-platform | 📋 LOW | Large ARCH_STANDARDS.md | Review usage | 200 tokens |
| network-automation | ✅ CLEAN | — | — | — |
| claude_course | ✅ CLEAN | — | — | — |
| **TOTAL** | — | — | — | **~50.3K tokens** |

---

## Implementation Checklist

### Week 1 (CRITICAL)
- [ ] Fix business-dev-platform venv issue (filter-branch + force-push)
- [ ] Verify venv files removed from git
- [ ] Update team: "Don't commit venv/ anymore"

### Week 2 (MEDIUM)
- [ ] Archive testing-validation-platform old reports
- [ ] Verify archives are gitignored
- [ ] Check car-platform ARCHITECTURE_STANDARDS usage

### Week 3+ (NICE-TO-HAVE)
- [ ] Review ARCHITECTURE_STANDARDS.md across all projects
- [ ] Consolidate duplicate documentation standards if present
- [ ] Add `venv/`, `dist/`, `build/` to root `.gitignore` template for future projects

---

## Questions for the Team

1. **business-dev-platform**: Why was venv/ committed? (Usually added by mistake)
2. **testing-validation-platform**: Are those old reports still referenced?
3. **car-platform**: Is ARCHITECTURE_STANDARDS.md actively maintained?

---

## References

- **Invested-platform cleanup:** See `TECH_DEBT_TOKEN_OPTIMIZATION.md` (similar approach)
- **Archive manifest:** See `ARCHIVE_MANIFEST.md` (inventory of archived files)

---

**Created:** June 20, 2026  
**Assigned to:** Tech Team  
**Review date:** [TBD]
