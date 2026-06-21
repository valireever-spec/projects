# Phase A: Timer Null-Checks - Change Manifest

**Date**: 2026-06-20  
**Backup Location**: `/home/vali/projects/openhab/backups/phase_a_timer_nullchecks_20260620_230001/`  
**Scripts Modified**: 7  
**Total Timer Fixes**: 55  

---

## Overview

Adding null-checks before all `.cancel()` calls across 7 scripts to prevent AttributeError crashes when timers are None.

**Pattern Applied**:
```python
# BEFORE (crashes if timer is None):
timerName.cancel()

# AFTER (safe):
if timerName is not None:
    timerName.cancel()
```

---

## Script 1: 050_Reguli_rev20260307.py

**File Size**: 1660 lines  
**Fixes**: 26 `.cancel()` calls  
**Risk**: HIGHEST (most complex timer handling)

### Lines to Fix

| Line | Timer Name | Context |
|------|-----------|---------|
| 174 | HDtimer3 | Occupancy timer cancel |
| 230 | _occ_sufra[0] | Sufra occupancy (list) |
| 640 | occupancyTimer1 | DormC occupancy |
| 657 | occupancyTimer2 | DormP occupancy |
| 694 | occupancyTimer3 | DormC occupancy variant |
| 711 | occupancyTimer4 | DormP occupancy variant |
| 748 | occupancyTimer5 | Kitchen occupancy |
| 765 | occupancyTimer6 | Additional occupancy |
| 824 | _occ_sufra[0] | Sufra (within condition) |
| 838 | _occ_dormc[0] | DormC (within condition) |
| 852 | _occ_dormp[0] | DormP (within condition) |
| 982 | occupancyTimer7 | Extended occupancy |
| 1177 | occupancyTimer10 | Backup occupancy |
| 1182 | sourceresetTimer | Source reset timer |
| 1187 | sourceresetTimer | Source reset (retry) |
| 1201 | occupancyTimer10 | (commented - leave as is) |
| 1320 | _occ_dormp[0] | DormP (nested) |
| 1329 | _occ_dormc[0] | DormC (nested) |
| 1335 | _occ_sufra[0] | Sufra (nested) |
| 1342 | occupancyTimer7 | Timer7 (nested) |
| 1349 | _occ_dormc[0] | DormC (another) |
| 1356 | _occ_dormp[0] | DormP (another) |
| 1361 | occupancyTimer12 | Timer12 |

**Special Cases**:
- Lines 824, 838, 852: List-based timers `_occ_sufra[0]` - check list AND element
- Line 1201: Commented out - **SKIP**

### Fix Template for List-Based Timers

```python
# BEFORE:
if _occ_sufra[0].hasTerminated():
    _occ_sufra[0].cancel()

# AFTER:
if _occ_sufra[0] is not None and _occ_sufra[0].hasTerminated():
    _occ_sufra[0].cancel()
```

---

## Script 2: 017_Prize_rev20260307.py

**File Size**: 1166 lines  
**Fixes**: 11 `.cancel()` calls  
**Risk**: HIGH

### Lines to Fix

| Line | Timer Name | Context |
|------|-----------|---------|
| 231 | timerLSAdina_on | Lightstrip Adina ON |
| 236 | timerLSAdina_off | Lightstrip Adina OFF |
| 242 | timerLSAlex_on | Lightstrip Alex ON |
| 247 | timerLSAlex_off | Lightstrip Alex OFF |
| 270 | DelayTimer1 | General delay timer |
| 443 | DelayTimer2 | Priza delay timer |
| 552 | DelayTimer3 | Priza4 delay timer |
| 659 | DelayTimer4 | Priza leave delay |
| 664 | priza4LeaveDebounceTimer | Priza4 debounce |

**Commented Out (SKIP)**:
- Line 830: `#priza4Timeroff.cancel()`
- Line 853: `#priza4Timeroff.cancel()`

---

## Script 3: 016_HomePresence_rev20250307.py

**File Size**: 312 lines  
**Fixes**: 9 `.cancel()` calls  
**Risk**: MEDIUM-HIGH

### Lines to Fix

| Line | Timer Name | Context |
|------|-----------|---------|
| 54 | DelayTimer1 | Home presence delay |
| 61 | DelayTimer1_1 | Presence variant |
| 168 | DelayTimer2 | Absence detection |
| 175 | DelayTimer2_1 | Absence variant |
| 224 | DelayTimerON | Presence ON delay |
| 227 | DelayTimerGargoyleOn | Gargoyle ON |
| 230 | DelayTimerDAP0On | DAP0 ON |
| 233 | DelayTimerDAP1On | DAP1 ON |
| 236 | DelayTimerDAP2On | DAP2 ON |

---

## Script 4: 099_Switches_Logic_rev20260307.py

**File Size**: 572 lines  
**Fixes**: 9 `.cancel()` calls  
**Risk**: MEDIUM

### Lines to Fix

| Line | Timer Name | Context |
|------|-----------|---------|
| 313 | FireplaceTimerOn | Fireplace ON delay |
| 318 | FireplaceTimerOff | Fireplace OFF delay |
| 338 | Fireplace_startTimer | Fireplace start |
| 343 | Fireplace_restartTimer | Fireplace restart |
| 396 | Priza1ForceOnTimer | Priza1 force ON |
| 413 | Priza1ForceOnTimer | Priza1 force cancel |
| 454 | Priza2ForceOnTimer | Priza2 force ON |
| 471 | Priza2ForceOnTimer | Priza2 force cancel |
| 506 | Priza3ForceOnTimer | Priza3 force ON |
| 523 | Priza3ForceOnTimer | Priza3 force cancel |

---

## Script 5: 055_Cinema.py

**File Size**: 152 lines  
**Fixes**: 5 `.cancel()` calls  
**Risk**: MEDIUM

### Lines to Fix

| Line | Timer Name | Context |
|------|-----------|---------|
| 33 | occupancyTimer1 | Cinema timer 1 |
| 39 | occupancyTimer2 | Cinema timer 2 |
| 45 | occupancyTimer3 | Cinema timer 3 |
| 51 | occupancyTimer4 | Cinema timer 4 |
| 57 | occupancyTimer5 | Cinema timer 5 |

---

## Script 6: 098_fireplace_rev20260307.py

**File Size**: 151 lines  
**Fixes**: 3 `.cancel()` calls  
**Risk**: MEDIUM

### Lines to Fix

| Line | Timer Name | Context |
|------|-----------|---------|
| 100 | FireplaceTimerOn | Fireplace ON timer |
| 113 | FireplaceTimerOff | Fireplace OFF timer |
| 150 | FireplaceRestartTimer | Fireplace restart timer |

---

## Script 7: 045_Bucatarie_rev20260307.py

**File Size**: 229 lines  
**Fixes**: 3 `.cancel()` calls  
**Risk**: MEDIUM

### Lines to Fix

| Line | Timer Name | Context |
|------|-----------|---------|
| 66 | HDtimer4 | Kitchen delay timer |
| 71 | occupancyTimer13 | Kitchen occupancy |
| 119 | occupancyTimerbuca | Kitchen occupancy (Romanian) |

---

## Implementation Strategy

### Automated Fix Pattern

For each script:
1. Identify all `.cancel()` calls
2. Wrap with `if timer is not None:` guard
3. Maintain indentation
4. Preserve comments

### Special Handling

**List-Based Timers** (050_Reguli only):
```python
# _occ_sufra[0] is a list containing a timer
# Must check both list element AND timer is not None

if _occ_sufra[0] is not None:
    if _occ_sufra[0].hasTerminated():
        _occ_sufra[0].cancel()
```

**Commented-Out Lines**:
- Lines that are already commented (`#`) should be SKIPPED

---

## Regression Tests

### Per-Script Testing

**050_Reguli** (Occupancy timers):
- [ ] Room occupancy detects and timers fire
- [ ] Timers cancel properly when person leaves
- [ ] No crashes on timer expiration
- [ ] List-based timers (`_occ_sufra[0]`) work

**017_Prize** (Lightstrip + Priza timers):
- [ ] Lightstrip timers trigger
- [ ] Priza timers activate/deactivate
- [ ] No crashes on debounce timer

**016_HomePresence** (Presence detection):
- [ ] Presence/absence detection works
- [ ] Delay timers activate correctly
- [ ] DAP timers fire

**099_Switches** (Fireplace + Priza):
- [ ] Fireplace ON/OFF timers work
- [ ] Priza force ON timers work
- [ ] No AttributeError on cancel

**055_Cinema** (Cinema occupancy):
- [ ] Cinema mode occupancy timers work
- [ ] All 5 timers cancel properly

**098_fireplace** (Fireplace logic):
- [ ] Fireplace timers activate correctly
- [ ] Restart logic works

**045_Bucatarie** (Kitchen):
- [ ] Kitchen occupancy timers work
- [ ] All timers cancel properly

### Global Testing

- [ ] No new ERROR in logs
- [ ] No AttributeError related to timers
- [ ] All timers still function normally
- [ ] System stable over 24 hours

---

## Rollback Procedure

```bash
# Restore all 7 scripts
for f in /home/vali/projects/openhab/backups/phase_a_timer_nullchecks_20260620_230001/*.backup; do
  scriptname=$(basename "$f" .backup)
  scp -i ~/.ssh/openhab_claude "$f" claude@192.168.3.25:/etc/openhab2/automation/jsr223/python/personal/$scriptname
done

# Wait for reload
sleep 10

# Verify
ssh openhabian@192.168.3.25 "tail -20 /var/log/openhab2/openhab.log" | grep -i "error\|exception"
```

**Rollback Time**: < 2 minutes

---

## Summary of Changes

| Script | Fixes | Size | Effort |
|--------|-------|------|--------|
| 050_Reguli | 26 | 1660 L | 45 min |
| 017_Prize | 11 | 1166 L | 20 min |
| 016_HomePresence | 9 | 312 L | 15 min |
| 099_Switches | 9 | 572 L | 15 min |
| 055_Cinema | 5 | 152 L | 10 min |
| 098_fireplace | 3 | 151 L | 10 min |
| 045_Bucatarie | 3 | 229 L | 10 min |
| **TOTAL** | **55** | **4942 L** | **~2 hrs** |

---

**Status**: Ready for deployment with full backups and change documentation.

**Next Step**: Apply fixes and deploy to remote system.
