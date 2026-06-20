# Priza1_BatteryFull Activation Fix - Implementation Summary

## Date Deployed
2026-06-20 17:47 UTC

## Issues Fixed

### 1. **Unreliable State Comparison (CRITICAL)**
**Files**: 017_Prize_rev20260307.py, 019_Charge_curve_rev20260307.py

**Root Cause**: Direct Java State object comparison using `!=` and `==` operators is unreliable in Jython. OpenHAB State objects (OnOffType) may not compare correctly with object identity matching.

**Solution**: Added `is_state()` helper function that uses string conversion for reliable comparison:
```python
def is_state(item_state, target_state):
    """Safe state comparison using string conversion. Handles Java State objects reliably."""
    return str(item_state).strip() == str(target_state).strip()
```

**Changed Locations**:
- 017_Prize.py: Lines 57-58, 357-358, 385-386, 403-409, 412-421
- 019_Charge_curve.py: Lines 49-60, 76-82

### 2. **Race Condition on Power-Off (CRITICAL)**
**File**: 017_Prize_rev20260307.py  
**Location**: Lines 371-389 (full-charge detection block)

**Root Cause**: The function returned early if `Priza1_Power` was already OFF, preventing `Priza1_BatteryFull` from being set. Race condition scenario:
1. Battery reaches full charge (current ≤ 0.150 A)
2. `priza1_Current` event fires
3. Check `if items["Priza1_Power"] == OFF:` → returns early
4. `Priza1_BatteryFull` never gets set to ON

**Solution**: Restructured logic to:
1. Always set `Priza1_BatteryFull` when full charge is detected
2. Only skip if it's a timeout relay-opening (checked via `_p1_timer_relay_open` flag)
3. Only turn off Power if it's currently ON

**Changed Code**:
```python
# OLD (BUGGY):
if current <= QuantityType(FULL_CURRENT):
    if items["Priza1_Power"] == OFF:
        return  # ← EARLY RETURN - misses BatteryFull activation!
    # ... set BatteryFull ...
    ctrl_dev("Priza1_Power", "OFF", items, events)

# NEW (FIXED):
if current <= QuantityType(FULL_CURRENT):
    # Guard only for timeout relay-opens
    if _p1_timer_relay_open:
        _p1_timer_relay_open = False
        return
    # Always set BatteryFull when full charge detected
    # Set flag even if Power is already OFF
    if not is_state(items["Priza1_BatteryFull"], OnOffType.ON):
        events.sendCommand("Priza1_BatteryFull", "ON")
    # Only turn off Power if it's currently ON
    if is_state(items["Priza1_Power"], OnOffType.ON):
        ctrl_dev("Priza1_Power", "OFF", items, events)
```

## Testing Recommendations

### 1. **Monitor the Charge Cycle**
When charging the e-bike, watch the OpenHAB logs for:
```
[INFO ] [E-Bike] Tapering started (current ...)
[INFO ] [E-Bike] Battery likely reached 80%. Stopping charge.
[INFO ] [E-Bike] Priza1_BatteryFull set ON at 80% taper
```

Or for full-charge detection:
```
[INFO ] [E-Bike] Charging complete (trickle current).
[INFO ] [E-Bike] Priza1_BatteryFull set ON — ECO sequence will skip Priza1
```

### 2. **Verify State Transitions**
1. **Full Charge State**: After full charge detected, verify:
   - `Priza1_BatteryFull` = ON (item state in OpenHAB UI)
   - `Priza1_Power` = OFF
   - Current reading = 0 A or very low

2. **New Charge Cycle**: When restarting charge, verify:
   - Manual control: `Priza1_Power_man` → ON → clears `Priza1_BatteryFull`
   - Auto control: `Priza1_Power_auto` → ON → clears `Priza1_BatteryFull`

3. **ECO Sequence**: Verify that `080_Power` script respects the flag:
   - When `Priza1_BatteryFull` = ON, Priza1 should NOT be included in ECO ON-sequence
   - When `Priza1_BatteryFull` = OFF, Priza1 should be included in ECO ON-sequence

### 3. **Edge Cases to Test**
1. **Rapid Power Cycles**: Toggle power ON/OFF multiple times during charge
   - Verify `Priza1_BatteryFull` is set when charge completes, regardless of toggle history
   
2. **Timeout Relay Opening**: Let charge timeout (15 minutes default)
   - Verify `Priza1_BatteryFull` is NOT set (timeout flag prevents it)
   - Verify log shows "current=0 after timeout relay-open — BatteryFull NOT set"

3. **Manual Override**: Press manual ON while battery is fully charged
   - Verify `Priza1_BatteryFull` is cleared to OFF
   - Verify log shows "Priza1_BatteryFull cleared — manual override"

4. **Auto Blocking**: Test that `Priza1_Power_auto` is blocked when battery is full
   - Set `Priza1_Power_auto` = ON while `Priza1_BatteryFull` = ON
   - Verify power does NOT turn ON
   - Verify log shows "Priza1_Power auto ON blocked — BatteryFull is ON"

## Related Files Unchanged
- `080_Power.py` — Respects the `Priza1_BatteryFull` flag to skip Priza1 in ECO sequence
- `020_Scheduled.py` — Resets `Priza1_BatteryFull` at midnight/noon if needed
- Item definitions in `.items` file — Must have `Priza1_BatteryFull` initialized with default OFF

## Rollback Plan
If issues occur:
1. Revert to backup versions (if available)
2. Or disable these scripts and run `020_Scheduled` manually to reset `Priza1_BatteryFull`

## Additional Notes
- The `is_state()` function follows the pattern used in `oh_utils.py:ctrl_dev()` for safety
- All comparisons now use OnOffType constants imported from `org.eclipse.smarthome.core.library.types`
- Changes are backward-compatible (same external behavior, more reliable internals)
- No changes to YAML automations or configuration needed
