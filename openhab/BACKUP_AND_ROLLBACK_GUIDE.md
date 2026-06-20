# Backup & Rollback Guide

**Backup Date**: 2026-06-20 18:03  
**Backup Location**: `/home/vali/projects/openhab/backups/20260620_180321/`

---

## Backup Contents

### Files Backed Up
```
✓ 020_Scheduled_rev20260307.py.backup (24 KB)
✓ 080_Power_rev20260312.py.backup (31 KB)
```

### Verify Backups
```bash
# Check backup files exist
ls -lh /home/vali/projects/openhab/backups/20260620_180321/

# Check file sizes match originals
# 020_Scheduled: ~24 KB ✓
# 080_Power: ~31 KB ✓

# Verify checksums (for integrity)
md5sum /home/vali/projects/openhab/backups/20260620_180321/*
```

---

## What Will Be Changed

### 020_Scheduled_rev20260307.py
- **Lines added**: 4 (imports) + 3 (helper function) = 7 new lines
- **Lines changed**: 26 state comparisons
- **Lines renamed**: 1 function definition
- **Total**: 34 lines modified/added out of 479 lines (7%)

### 080_Power_rev20260312.py
- **Lines added**: 3 (helper function) new lines
- **Lines changed**: 3 state comparisons
- **Total**: 6 lines modified/added out of ~900 lines (<1%)

---

## Quick Rollback (If Needed)

### Option 1: Automated Rollback
```bash
#!/bin/bash
# Restore both files
scp -i ~/.ssh/openhab_claude /home/vali/projects/openhab/backups/20260620_180321/020_Scheduled_rev20260307.py.backup \
    claude@192.168.3.25:/etc/openhab2/automation/jsr223/python/personal/020_Scheduled_rev20260307.py

scp -i ~/.ssh/openhab_claude /home/vali/projects/openhab/backups/20260620_180321/080_Power_rev20260312.py.backup \
    claude@192.168.3.25:/etc/openhab2/automation/jsr223/python/personal/080_Power_rev20260312.py

# Verify in logs (wait 10 seconds)
ssh openhabian@192.168.3.25 "tail -20 /var/log/openhab2/openhab.log | grep -E 'Loading|ERROR'"
```

### Option 2: Manual Rollback
1. SSH to OpenHAB: `ssh -i ~/.ssh/openhab_claude claude@192.168.3.25`
2. Restore files:
   ```bash
   cp /tmp/020_Scheduled_rev20260307.py.backup /etc/openhab2/automation/jsr223/python/personal/020_Scheduled_rev20260307.py
   cp /tmp/080_Power_rev20260312.py.backup /etc/openhab2/automation/jsr223/python/personal/080_Power_rev20260312.py
   ```
3. Wait for OpenHAB to reload (watch logs)

---

## Timeline of Changes

| Date/Time | Event | Status |
|-----------|-------|--------|
| 2026-06-20 17:47 | 017_Prize & 019_Charge_curve deployed | ✓ COMPLETE |
| 2026-06-20 18:03 | Backups created | ✓ COMPLETE |
| 2026-06-20 18:05 | Change manifest documented | ✓ COMPLETE |
| **PENDING** | **User approval** | ⏳ AWAITING |
| **PENDING** | **Deploy changes** | ⏳ AWAITING |
| **PENDING** | **Verify in logs** | ⏳ AWAITING |
| **PENDING** | **Functional testing** | ⏳ AWAITING |

---

## Risk Assessment

### Low Risk Changes (Safe to deploy)
- Adding `is_state()` helper function (new code, no impact if unused)
- Adding imports (required, will fail WITHOUT them)

### Medium Risk Changes (Standard refactoring)
- Replacing state comparisons (same logic, just more reliable)
- 26 comparison replacements in 020_Scheduled

### Minimal Risk Changes (One rename)
- Rename duplicate function (fixes silent bug, improves clarity)

### Tested Changes (Already validated)
- Same `is_state()` pattern already deployed in 017_Prize & 019_Charge_curve on 2026-06-20 17:47
- Pattern works correctly (confirmed by OpenHAB logs)

---

## Validation After Deployment

### Immediate (First 1 minute)
```bash
# Watch OpenHAB reload the scripts
tail -f /var/log/openhab2/openhab.log | grep -E '020_Scheduled|080_Power|ERROR|Exception'

# Expected output:
# [INFO] Loading script 'python/personal/020_Scheduled_rev20260307.py'
# [INFO] Loading script 'python/personal/080_Power_rev20260312.py'
# (no ERROR messages)
```

### Short-term (Next few hours)
- **Evening (18:00-22:00)**: Priza8 and Priza9 rules fire (use StringType) → verify no NameErrors
- **Anytime**: Monitor for ECO sequence running (check Priza1/Priza4 skipping)
- **Midnight (00:00)**: Priza1_BatteryFull midnight reset fires → verify correct

### Functional Testing
See: `PRIZA1_BATTFULL_TEST_PROCEDURE.md` for comprehensive test checklist

---

## Before You Approve

**Please verify**:
1. ✓ Backup files exist at `/home/vali/projects/openhab/backups/20260620_180321/`
2. ✓ Change manifest at `/home/vali/projects/openhab/CHANGE_MANIFEST_20260620.md` is clear
3. ✓ You understand each change being made
4. ✓ Rollback procedure is clear if needed

**Then reply**: "Approved - proceed with changes" or ask for clarification on any change

---

## Archive for Audit Trail

This backup and manifest are kept for:
- Audit trail (what changed and when)
- Quick rollback if issues arise
- Reference for similar changes in the future
- Incident post-mortem if anything breaks

Backups are automatically retained for 30 days.
