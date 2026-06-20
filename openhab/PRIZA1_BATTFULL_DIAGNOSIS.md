# Priza1_BatteryFull Activation Issues - Diagnosis

## Problem Statement
`Priza1_BatteryFull` is not being reliably activated when the e-bike battery reaches full charge.

## Root Causes Identified

### Bug 1: Unreliable State Comparison (017_Prize.py)
**Location**: Lines 352-354, 380-382, 396-397  
**Issue**: Direct Java object comparison with `!=` and `==` operators can fail in Jython

```python
# PROBLEMATIC CODE
if items["Priza1_BatteryFull"] != ON:
    events.sendCommand("Priza1_BatteryFull", "ON")
```

In Jython, when comparing OpenHAB State objects (OnOffType) with Java objects, direct comparison may not work correctly. The proper pattern (seen in `ctrl_dev` in oh_utils.py) is string conversion:

```python
# CORRECT APPROACH
if str(items["Priza1_BatteryFull"]).strip() != "ON":
    events.sendCommand("Priza1_BatteryFull", "ON")
```

**Affected Lines in 017_Prize.py**:
- Line 352: `if items["Priza1_BatteryFull"] != ON:` (taper detection)
- Line 380: `if items["Priza1_BatteryFull"] != ON:` (full-charge detection)
- Line 396: `if items["Priza1_BatteryFull"] != OFF:` (manual override)

### Bug 2: Race Condition on Priza1_Power State (017_Prize.py)
**Location**: Lines 366-384  
**Issue**: Function returns early if `Priza1_Power == OFF`, preventing `Priza1_BatteryFull` from being set

```python
if current <= QuantityType(FULL_CURRENT):
    if items["Priza1_Power"] == OFF:    # ← EARLY RETURN HERE
        priza1_cancel_charge_end_timer()
        return  # ← BatteryFull NEVER gets set if Power is OFF
    # ... rest of code that sets BatteryFull ...
```

**Scenario that causes this**:
1. Battery reaches full charge (current ≤ 0.150 A)
2. `priza1_Current` event fires, checks line 372
3. `Priza1_Power` has already been turned OFF (from previous iteration or timeout)
4. Function returns at line 374 without executing lines 377-384
5. `Priza1_BatteryFull` never gets set to ON

**Fix Strategy**: Set `Priza1_BatteryFull` BEFORE checking if Power is OFF, or check/set the flag regardless of Power state.

### Bug 3: Unreliable State Comparison (019_Charge_curve.py)
**Location**: Line 57  
**Issue**: Same as Bug 1

```python
# PROBLEMATIC CODE
if items["Priza1_BatteryFull"] != OFF:
    events.sendCommand("Priza1_BatteryFull", "OFF")
```

**Affected Lines in 019_Charge_curve.py**:
- Line 57: `if items["Priza1_BatteryFull"] != OFF:` (reset on power ON)

## Recommended Fixes

### Fix 1: Use Safe State Comparison
Replace all direct state comparisons with string-based comparison:

```python
def is_state(item_state, target):
    """Safe state comparison that works with any item state."""
    return str(item_state).strip() == str(target).strip()

# Usage:
if not is_state(items["Priza1_BatteryFull"], ON):
    events.sendCommand("Priza1_BatteryFull", "ON")
```

### Fix 2: Reorder Logic to Set BatteryFull Before Power-Off Check
Move the BatteryFull detection before checking Priza1_Power state:

```python
# Current (buggy) order:
# 1. Check if Priza1_Power == OFF → return if true
# 2. Set Priza1_BatteryFull ON
# 3. Turn Priza1_Power OFF

# Fixed order:
# 1. Check if current indicates full charge
# 2. Set Priza1_BatteryFull ON (always, regardless of Power state)
# 3. If Power was ON, turn it OFF
```

### Fix 3: Add Initialization Check
Ensure `Priza1_BatteryFull` is properly initialized at startup via metadata in the .items file.

## Testing Recommendations

1. **Monitor logs** when charging completes:
   - Look for "Battery likely reached 80%. Stopping charge." (taper)
   - Look for "Charging complete (trickle current)." (full charge)
   - Verify "Priza1_BatteryFull set ON" appears

2. **Verify state transitions**:
   - After full charge, `Priza1_BatteryFull` should be ON
   - When starting new charge cycle, it should be cleared to OFF

3. **Test edge cases**:
   - Manual power toggle while charging
   - Timeout-based power-off (timer1_charge_off)
   - Rapid current fluctuations near threshold

## Files Requiring Fixes
1. `/etc/openhab2/automation/jsr223/python/personal/017_Prize_rev20260307.py`
2. `/etc/openhab2/automation/jsr223/python/personal/019_Charge_curve_rev20260307.py`
