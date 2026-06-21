# Phase 4 Technical Debt Fixes - Change Manifest

**Date**: 2026-06-20  
**Backup Location**: `/home/vali/projects/openhab/backups/phase_4_technical_debt_20260620_202326/`  
**File**: 020_Scheduled_rev20260307.py (479 lines)  
**Changes**: 3 fixes  

---

## Fix 1: Add Priza4_BatteryFull Midnight Reset

**Priority**: HIGH  
**Risk**: LOW  
**Lines to Change**: Around line 456-460 (stop_prize function)  

### Issue
Only `Priza1_BatteryFull` is reset at midnight. `Priza4_BatteryFull` (laptop charger) is never reset, causing the laptop charger to stay locked in "full" state indefinitely.

### Current Code
```python
@rule("Stop Prize", description="Stop prize", tags=["cron", "Prize"])
@when("Time cron 0 0 0 * * ? *")
@when("Time cron 0 0 12 * * ? *")
def stop_prize(event):
    if DateTime.now().getHourOfDay() == 0:
        if items["Priza1_BatteryFull"] != OFF:
            events.sendCommand("Priza1_BatteryFull", "OFF")
            LogAction.logInfo("Priza1", "Priza1_BatteryFull OFF — end of day (midnight)")
    events.sendCommand("Priza1_Power", "OFF")
```

### Fix
Add Priza4_BatteryFull reset at midnight (same logic as Priza1):

```python
@rule("Stop Prize", description="Stop prize", tags=["cron", "Prize"])
@when("Time cron 0 0 0 * * ? *")
@when("Time cron 0 0 12 * * ? *")
def stop_prize(event):
    if DateTime.now().getHourOfDay() == 0:
        if items["Priza1_BatteryFull"] != OFF:
            events.sendCommand("Priza1_BatteryFull", "OFF")
            LogAction.logInfo("Priza1", "Priza1_BatteryFull OFF — end of day (midnight)")
        if items["Priza4_BatteryFull"] != OFF:
            events.sendCommand("Priza4_BatteryFull", "OFF")
            LogAction.logInfo("Priza4", "Priza4_BatteryFull OFF — end of day (midnight)")
    events.sendCommand("Priza1_Power", "OFF")
```

### Regression Tests
- [ ] Verify Priza1_BatteryFull resets at midnight (00:00)
- [ ] Verify Priza4_BatteryFull resets at midnight (00:00)
- [ ] Verify no errors in logs
- [ ] Verify Priza1_Power still turns OFF at both midnight and noon

---

## Fix 2: Add Sonoffmini Debouncing (Race Condition)

**Priority**: HIGH  
**Risk**: MEDIUM (adds timing logic)  
**Lines to Change**: Lines 176-190 (permsufra_forced_switch_state) and similar functions  

### Issue
Sonoffmini watchdog checks state without debouncing. Can trigger on transient glitches where device momentarily appears offline then comes back online within a few seconds.

### Current Code (Lines 208-222 - permsufra_forced_switch_state)
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

### Fix Strategy
Add a persistent counter that requires the state to be OFF for 2+ consecutive checks (20+ seconds at 10-minute cron):

```python
# NEW module-level state tracking
sonoffmini_offline_count = {"sonoff1": 0, "sonoff2": 0, "sonoff3": 0}
SONOFFMINI_DEBOUNCE_CHECKS = 2  # Require 2+ consecutive OFF readings before acting

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
        sonoffmini_offline_count["sonoff3"] = 0  # Reset counter when device is online
```

### Affected Functions (3 total - same pattern)
- Line 176-190: `permdormc_forced_switch_state` (Sonoffmini1)
- Line 192-206: `permdormp_forced_switch_state` (Sonoffmini2)
- Line 208-222: `permsufra_forced_switch_state` (Sonoffmini3)

### Regression Tests
- [ ] Test Sonoffmini offline detection (still works after 2+ checks)
- [ ] Test transient glitch handling (device goes offline then online quickly)
- [ ] Verify PermSufra/PermDormC/PermDormP don't toggle on transients
- [ ] Verify no errors in logs

---

## Fix 3: Add Timer Null-Checks

**Priority**: HIGH  
**Risk**: LOW  
**Lines to Change**: Lines 284-287 (timer_priza8) and lines 316-319 (timer_fireplace)  

### Issue
Functions call `.cancel()` on timers that might still be None, causing AttributeError if callback fires in unusual state.

### Current Code - Line 284-287
```python
def timer_priza8():
    events.sendCommand("Priza8_Power", "OFF")
    events.sendCommand("Priza11_Power", "OFF")
    priza8TimerOff.cancel()  # ← Crashes if priza8TimerOff is None
```

### Fix
Add null-check before canceling:

```python
def timer_priza8():
    events.sendCommand("Priza8_Power", "OFF")
    events.sendCommand("Priza11_Power", "OFF")
    if priza8TimerOff is not None:
        priza8TimerOff.cancel()
```

### Current Code - Line 316-319
```python
def timer_fireplace():
    events.sendCommand("Fireplace", "OFF")
    LogAction.logInfo("fireplace_cinema", "Fireplace is off due to Cinema off")
    Fireplacetimer.cancel()  # ← Crashes if Fireplacetimer is None
```

### Fix
Add null-check before canceling:

```python
def timer_fireplace():
    events.sendCommand("Fireplace", "OFF")
    LogAction.logInfo("fireplace_cinema", "Fireplace is off due to Cinema off")
    if Fireplacetimer is not None:
        Fireplacetimer.cancel()
```

### Affected Locations
- Line 287: `priza8TimerOff.cancel()`
- Line 319: `Fireplacetimer.cancel()`

### Regression Tests
- [ ] Test Priza8 timer functionality
- [ ] Test Fireplace timer functionality
- [ ] Verify no AttributeError in logs
- [ ] Verify timers still cancel properly

---

## Summary of Changes

| Fix | Lines | Type | Risk | Effort |
|-----|-------|------|------|--------|
| Priza4 midnight reset | 456-460 | Add 4 lines | LOW | 5 min |
| Sonoffmini debouncing | 176-222 | Modify 3 functions | MEDIUM | 30 min |
| Timer null-checks | 287, 319 | Add 2 guards | LOW | 5 min |

**Total Changes**: ~10 lines added/modified  
**Total Effort**: ~40 minutes  
**Total Risk**: MEDIUM (debouncing adds state, but simple logic)

---

## Rollback Procedure

```bash
# Restore original file
cp /home/vali/projects/openhab/backups/phase_4_technical_debt_20260620_202326/020_Scheduled_rev20260307.py.backup \
   /etc/openhab2/automation/jsr223/python/personal/020_Scheduled_rev20260307.py

# Verify
ssh openhabian@192.168.3.25 "tail -20 /var/log/openhab2/openhab.log" | grep -i "Loading script.*020_Scheduled\|ERROR"
```

---

## Verification Checklist

### Post-Deployment (Immediate)
- [ ] Script loads without errors
- [ ] No NameError or AttributeError in logs
- [ ] System responsive
- [ ] All existing automations still working

### Functional Testing (Next 1-4 hours)
- [ ] Priza4_BatteryFull resets at midnight
- [ ] Sonoffmini debounce prevents transient toggles
- [ ] Timer callbacks still work
- [ ] No unexpected errors

### 24-Hour Stability
- [ ] Midnight reset executes correctly
- [ ] No new ERROR messages
- [ ] System stable

---

**Status**: Ready for deployment with backups and documentation complete.

**Next Step**: User approval to proceed with fixes.
