# Phase 4 Partial Fixes - Change Manifest

**Date**: 2026-06-20  
**Backup Location**: `/home/vali/projects/openhab/backups/phase_4_partial_20260620_213233/`  
**File**: 020_Scheduled_rev20260307.py (479 lines)  
**Changes**: 2 fixes (Sonoffmini debouncing + timer null-checks)  
**Skipped**: Priza4 midnight reset  

---

## Fix 1: Add Sonoffmini Debouncing (Race Condition)

**Priority**: HIGH  
**Risk**: MEDIUM (adds state tracking)  
**Lines to Change**: Lines 176–190, 192–206, 208–222 (three watchdog functions)  
**Effort**: ~30 minutes

### Issue
Sonoffmini watchdog checks state without debouncing. Can trigger on transient glitches where device momentarily appears offline then comes back online within seconds.

**Example**: WiFi hiccup causes Sonoffmini3_Alive = OFF for 1 second → forces PermSufra_Forced OFF → room lights turn off unexpectedly → 5 seconds later device comes back online (Alive = ON) but room stays dark

### Current Code (Lines 208–222)
```python
@rule("Restore PermSufra_Forced switch state cronjob", description="Restore PermSufra_Forced switch state", tags=["cron", "PermSufra_Forced"])
@when("Time cron 0 0/10 * * * ?")
def permsufra_forced_switch_state(event):
    if items["Sonoffmini3_Alive"] == OFF:   ###Posibil Race condition daca Alive nu se activeaza la timp
        if items["PermSufra_Forced"] == ON:
            events.sendCommand("PermSufra_Forced", "OFF")
            events.sendCommand("PermSufra", "OFF")
    # ... rest of function
```

### Solution
Add module-level counters that require 2+ consecutive OFF readings before acting:

**Add at module level (after line 46)**:
```python
# Sonoffmini debounce counters (Phase 4 fix 2026-06-20)
sonoffmini_offline_count = {"sonoff1": 0, "sonoff2": 0, "sonoff3": 0}
SONOFFMINI_DEBOUNCE_CHECKS = 2
```

**Modify permdormc_forced_switch_state** (lines 176–190):
```python
@rule("Restore PermDormC_Forced switch state cronjob", description="Restore PermDormC_Forced switch state", tags=["cron", "PermDormC_Forced"])
@when("Time cron 0 0/10 * * * ?")
def permdormc_forced_switch_state(event):
    global sonoffmini_offline_count
    
    if items["Sonoffmini1_Alive"] == OFF:
        sonoffmini_offline_count["sonoff1"] += 1
        if sonoffmini_offline_count["sonoff1"] >= SONOFFMINI_DEBOUNCE_CHECKS:
            if items["PermDormC_Forced"] == ON:
                events.sendCommand("PermDormC_Forced", "OFF")
                events.sendCommand("PermDormC", "OFF")
    else:
        sonoffmini_offline_count["sonoff1"] = 0
```

**Modify permdormp_forced_switch_state** (lines 192–206):
```python
@rule("Restore PermDormP_Forced switch state cronjob", description="Restore PermDormP_Forced switch state", tags=["cron", "PermDormP_Forced"])
@when("Time cron 0 0/10 * * * ?")
def permdormp_forced_switch_state(event):
    global sonoffmini_offline_count
    
    if items["Sonoffmini2_Alive"] == OFF:
        sonoffmini_offline_count["sonoff2"] += 1
        if sonoffmini_offline_count["sonoff2"] >= SONOFFMINI_DEBOUNCE_CHECKS:
            if items["PermDormP_Forced"] == ON:
                events.sendCommand("PermDormP_Forced", "OFF")
                events.sendCommand("PermDormP", "OFF")
    else:
        sonoffmini_offline_count["sonoff2"] = 0
```

**Modify permsufra_forced_switch_state** (lines 208–222):
```python
@rule("Restore PermSufra_Forced switch state cronjob", description="Restore PermSufra_Forced switch state", tags=["cron", "PermSufra_Forced"])
@when("Time cron 0 0/10 * * * ?")
def permsufra_forced_switch_state(event):
    global sonoffmini_offline_count
    
    if items["Sonoffmini3_Alive"] == OFF:
        sonoffmini_offline_count["sonoff3"] += 1
        if sonoffmini_offline_count["sonoff3"] >= SONOFFMINI_DEBOUNCE_CHECKS:
            if items["PermSufra_Forced"] == ON:
                events.sendCommand("PermSufra_Forced", "OFF")
                events.sendCommand("PermSufra", "OFF")
    else:
        sonoffmini_offline_count["sonoff3"] = 0
```

### Regression Tests
- [ ] Test Sonoffmini offline detection (still works after 2+ checks)
- [ ] Test transient glitch handling (device goes offline then online quickly)
  * Manually disconnect WiFi from Sonoffmini for 1 second → should NOT trigger failsafe
  * Disconnect for 20+ seconds → should trigger failsafe
- [ ] Verify PermSufra/PermDormC/PermDormP don't toggle on transients
- [ ] Verify no errors in logs

---

## Fix 2: Add Timer Null-Checks

**Priority**: HIGH  
**Risk**: LOW  
**Lines to Change**: Lines 287 and 319 (timer callback functions)  
**Effort**: ~5 minutes

### Issue
Functions call `.cancel()` on timers that might be None, causing AttributeError if callback fires in unusual state.

**Scenario**: If timer is created, then cancelled externally, but callback still fires somehow → tries to call `.cancel()` on None → crash

### Current Code - Line 284–287
```python
def timer_priza8():
    events.sendCommand("Priza8_Power", "OFF")
    events.sendCommand("Priza11_Power", "OFF")
    priza8TimerOff.cancel()  # ← Crashes if priza8TimerOff is None
```

### Fix
```python
def timer_priza8():
    events.sendCommand("Priza8_Power", "OFF")
    events.sendCommand("Priza11_Power", "OFF")
    if priza8TimerOff is not None:
        priza8TimerOff.cancel()
```

### Current Code - Line 316–319
```python
def timer_fireplace():
    events.sendCommand("Fireplace", "OFF")
    LogAction.logInfo("fireplace_cinema", "Fireplace is off due to Cinema off")
    Fireplacetimer.cancel()  # ← Crashes if Fireplacetimer is None
```

### Fix
```python
def timer_fireplace():
    events.sendCommand("Fireplace", "OFF")
    LogAction.logInfo("fireplace_cinema", "Fireplace is off due to Cinema off")
    if Fireplacetimer is not None:
        Fireplacetimer.cancel()
```

### Regression Tests
- [ ] Test Priza8 timer functionality (set, wait, cancel)
- [ ] Test Fireplace timer functionality (set, wait, cancel)
- [ ] Verify no AttributeError in logs
- [ ] Verify timers still cancel properly when not None
- [ ] Verify devices turn OFF when timers expire

---

## Summary of Changes

| Fix | Lines | Type | Risk | Effort |
|-----|-------|------|------|--------|
| Sonoffmini debouncing | 46, 176–222 | Add module var + modify 3 functions | MEDIUM | 30 min |
| Timer null-checks | 287, 319 | Add 2 guards | LOW | 5 min |

**Total Changes**: ~50 lines added/modified  
**Total Effort**: ~35 minutes  
**Total Risk**: MEDIUM (debouncing adds state, but simple logic)

---

## Rollback Procedure

```bash
# Restore original file
cp /home/vali/projects/openhab/backups/phase_4_partial_20260620_213233/020_Scheduled_rev20260307.py.backup \
   /etc/openhab2/automation/jsr223/python/personal/020_Scheduled_rev20260307.py

# Verify
ssh openhabian@192.168.3.25 "tail -20 /var/log/openhab2/openhab.log" | grep -i "error\|exception"
```

**Rollback Time**: < 1 minute

---

## Verification Checklist

### Post-Deployment (Immediate)
- [ ] Script loads without errors
- [ ] No NameError (sonoffmini_offline_count, etc.)
- [ ] No AttributeError on timer operations
- [ ] System responsive
- [ ] All existing automations still working

### Functional Testing (Next 1-4 hours)
- [ ] Sonoffmini debounce prevents transient toggles
- [ ] Timer callbacks still work
- [ ] No unexpected errors

### 24-Hour Stability
- [ ] No new ERROR messages
- [ ] System stable
- [ ] Watchdog timers execute normally

---

**Status**: Ready for deployment with backups and documentation complete.

**Next Step**: User approval to proceed with implementation.
