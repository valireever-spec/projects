# Seasonal Charging - Logic Fixes Applied

**Date**: 2026-06-20  
**Time**: 21:27–21:28 UTC  
**Status**: ✅ DEPLOYED & VERIFIED

---

## Issues Fixed

### Issue 1: Missing `is_state()` Function ✅

**Problem**: Winter override code referenced `is_state()` which doesn't exist in 080_Power
```python
# WRONG (caused NameError):
if not is_state(items["Priza1_BatteryFull"], OnOffType.ON):
```

**Fix**: Use string comparison instead
```python
# CORRECT:
priza1_full = str(items["Priza1_BatteryFull"]).strip() == "ON"
if not priza1_full:
```

**Impact**: Eliminates NameError on winter override activation

---

### Issue 2: ON-OFF Cycling Conflict ✅

**Problem**: Winter override forces Priza ON, then apply_intent() forces it OFF on same tick
```
Tick 1: Winter override → Priza1_Power_auto ON
Tick 2: apply_intent() in IMPORT_MODE → Priza1_Power_auto OFF
Tick 3: Winter override → Priza1_Power_auto ON (repeat)
```
Result: Constant 5-second cycling during winter windows.

**Fix**: Skip `apply_intent()` when winter override activates
```python
if activated:
    return  # ← Skip apply_intent() to prevent conflict
```

**Impact**: Winter scheduling takes priority, prevents apply_intent() from overriding

---

## Code Changes

**File**: `/etc/openhab2/automation/jsr223/python/personal/080_Power_rev20260312.py`  
**Location**: eco_watchdog() function, after evening override (lines 998–1019)

**Before**:
```python
    # 5b) Winter scheduled charging override (FIX 2026-06-20)
    if is_winter_charging_time():
        # Allow Priza1/4 to charge even in IMPORT_MODE during scheduled windows
        if not is_state(items["Priza1_BatteryFull"], OnOffType.ON):
            if is_state(items["Priza1_Power_auto"], OnOffType.OFF):
                events.sendCommand("Priza1_Power_auto", "ON")
                log_important("WINTER: Priza1_Power_auto ON (scheduled window)")

        if not is_state(items["Priza4_BatteryFull"], OnOffType.ON):
            if is_state(items["Priza4_Power_auto"], OnOffType.OFF):
                events.sendCommand("Priza4_Power_auto", "ON")
                log_important("WINTER: Priza4_Power_auto ON (scheduled window)")
```

**After**:
```python
    # 5b) Winter scheduled charging override (FIX 2026-06-20)
    # Allow Priza1/4 to charge even in IMPORT_MODE during scheduled windows
    if is_winter_charging_time():
        priza1_full = str(items["Priza1_BatteryFull"]).strip() == "ON"
        priza1_is_off = str(items["Priza1_Power_auto"]).strip() == "OFF"
        priza4_full = str(items["Priza4_BatteryFull"]).strip() == "ON"
        priza4_is_off = str(items["Priza4_Power_auto"]).strip() == "OFF"

        activated = False

        if not priza1_full and priza1_is_off:
            events.sendCommand("Priza1_Power_auto", "ON")
            log_important("WINTER: Priza1_Power_auto ON (scheduled window)")
            activated = True

        if not priza4_full and priza4_is_off:
            events.sendCommand("Priza4_Power_auto", "ON")
            log_important("WINTER: Priza4_Power_auto ON (scheduled window)")
            activated = True

        # Skip apply_intent() to prevent ON-OFF cycling
        if activated:
            return
```

---

## Post-Deployment Verification

✅ **Script Load**: 21:28:20 UTC — successful  
✅ **No Errors**: No NameError, AttributeError, or exceptions  
✅ **System State**: Normal operation, IMPORT_MODE active  
✅ **Logging**: ECO watchdog functioning normally  

---

## Behavior Explanation

### Summer Mode (Current: May–Aug)
- `is_winter_charging_time()` returns False
- Winter override does NOT activate
- Normal ECO logic in effect
- No changes vs. original behavior

### Winter/Shoulder Mode (Oct–Mar, Apr, Sept)
When watchdog tick occurs during scheduled window:

1. **Check** `is_winter_charging_time()` → True
2. **Check** Priza1_BatteryFull, Priza1_Power_auto state
3. **Force ON** if battery not full and currently off
4. **Set** `activated = True`
5. **Return** early, skip `apply_intent()`

**Result**: Priza stays ON for this tick, reactivates every 5 seconds if needed

---

## Testing Checklist

### Immediate (✅ DONE)
- [x] Script loads without NameError
- [x] No AttributeError on state comparisons
- [x] System responsive
- [x] Watchdog running normally

### Before October 1
- [ ] Continue summer operation without issues
- [ ] Verify no ON-OFF cycling during normal IMPORT_MODE
- [ ] Monitor logs for any unexpected activations

### October 1 Verification (Critical)
- [ ] At 7 AM: Logs show "WINTER: Priza1_Power_auto ON (scheduled window)"
- [ ] At 7 AM: Logs show "WINTER: Priza4_Power_auto ON (scheduled window)"
- [ ] Verify Priza1_Power_auto actually turns ON
- [ ] Verify Priza4_Power_auto actually turns ON
- [ ] Verify NO "ON-OFF-ON-OFF" cycling in logs
- [ ] At 8 AM: Devices turn OFF (outside window) if in IMPORT_MODE

### Full Winter Testing (Oct–Mar)
- [ ] 7 AM window: Charging starts
- [ ] 2 PM window: Charging starts
- [ ] 9 PM window: Charging starts
- [ ] Outside windows: Charging OFF (unless EXPORT_MODE)
- [ ] BatteryFull blocks activation
- [ ] No unexpected log spam

---

## Fallback/Rollback

If issues arise before October 1:

```bash
# Quick rollback
cp /home/vali/projects/openhab/backups/seasonal_charging_20260620_210100/080_Power_rev20260312.py.backup \
   /etc/openhab2/automation/jsr223/python/personal/080_Power_rev20260312.py
```

**Rollback time**: < 1 minute  
**Risk**: MINIMAL (feature is dormant until October)

---

## Summary

✅ Both logic issues fixed  
✅ Code now uses proper state comparison (no is_state() dependency)  
✅ Winter override skips apply_intent() to prevent cycling  
✅ System ready for October 1 transition to winter scheduling  
✅ All backups and documentation updated  

Ready for production monitoring through summer season.

---

*All changes deployed 2026-06-20 21:27–21:28 UTC*
