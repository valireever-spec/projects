# OpenHAB Automation System - Additional Bugs & Gaps Analysis

**Date**: 2026-06-20  
**Scope**: Full automation suite (017_Prize, 019_Charge_curve, 020_Scheduled, 080_Power, etc.)

---

## Critical Issues

### 1. **State Comparison Bug Propagates to 080_Power (CRITICAL)**
**File**: 080_Power_rev20260312.py  
**Lines**: 632, 637, 641  
**Issue**: Same unreliable state comparison pattern found in 017/019, now in power management

```python
# PROBLEMATIC (lines 632-641)
if dev == "Priza1_Power_auto" and target == "ON":
    if items["Priza1_BatteryFull"] == OnOffType.ON:  # ← Direct comparison (unreliable)
        log("BatteryFull is ON, skipping Priza1")
        return
...
if items["Priza4_BatteryFull"] != OnOffType.ON:  # ← Using != instead of ==OFF
```

**Impact**: ECO sequence may fail to skip Priza1 when battery is full, causing unwanted power cycles

**Fix Required**: Apply same `is_state()` helper pattern to 080_Power

---

### 2. **Missing StringType Import (BLOCKING)**
**File**: 020_Scheduled_rev20260307.py  
**Lines**: 301, 305, 309, 328, 343, 346, 349  
**Issue**: Script uses `StringType()` without importing it

```python
# Line 301:
if event.itemState == StringType(evening):  # ← StringType not imported
    if items["HomePresence"] == ON:
```

**Impact**: Script will fail at runtime with `NameError: name 'StringType' is not defined`

**Fix Required**:
```python
from org.eclipse.smarthome.core.library.types import StringType, OnOffType
```

---

### 3. **Duplicate Function Definition (SILENT FAILURE)**
**File**: 020_Scheduled_rev20260307.py  
**Lines**: 210 and 231  
**Issue**: Function `permsufra_forced_switch_state` defined twice; second overwrites first

```python
# Line 210 (OVERWRITTEN)
def permsufra_forced_switch_state(event):
    if items["Sonoffmini3_Alive"] == OFF:
        if items["PermSufra_Forced"] == ON:
            events.sendCommand("PermSufra_Forced", "OFF")

# Line 231 (OVERWRITES LINE 210)
def permsufra_forced_switch_state(event):
    events.sendCommand("Restart_Openhab", "ON")
```

**Impact**: The OpenHAB restart rule silently overwrites the PermSufra watchdog logic

**Fix Required**: Rename line 231 function to match the rule name or purpose (e.g., `restart_openhab_monthly`)

---

### 4. **State Comparison Issues Throughout 020_Scheduled (PERVASIVE)**
**File**: 020_Scheduled_rev20260307.py  
**Lines**: 56, 70, 141-142, 179, 186, 188, 204, 220, 237, 243, 249, 255, 261, 267, 273, 278, 302, 329, 343, 344, 346, 349, 457  
**Issue**: All use direct `==`, `!=` comparison with ON/OFF/UNDEF instead of safe string comparison

```python
# Examples:
Line 56:   if items["Vacanta"] != ON:
Line 70:   if items["Sufragerie_Daytime"] == OFF or items["Sufragerie_Illuminance_Switch"] == ON:
Line 141:  if items["Kodi_restart"] == OFF:
Line 186:  if items["Sonoff1_Latency"] == UNDEF:
Line 237:  if items["Sonoff1_Latency"] == UNDEF or items["Sonoff1_Latency"] == NULL:
Line 457:  if items["Priza1_BatteryFull"] != OFF:  # ← Same issue we just fixed!
```

**Impact**: Rules may fail silently or behave unpredictably depending on state type

**Fix Required**: Add `is_state()` helper and apply throughout file

---

### 5. **ON/OFF Import Missing in 020_Scheduled (SECONDARY)**
**File**: 020_Scheduled_rev20260307.py  
**Issue**: Script uses ON and OFF constants but only imports UnDefType

```python
# Line 19 imports:
from org.eclipse.smarthome.core.types import UnDefType

# But lines 56-461 use ON/OFF without importing them
if items["Vacanta"] != ON:
```

**Impact**: Script will fail with `NameError: name 'ON' is not defined` at runtime

**Fix Required**:
```python
from org.eclipse.smarthome.core.library.types import OnOffType
ON = OnOffType.ON
OFF = OnOffType.OFF
```

---

## High Priority Issues

### 6. **Race Condition in Sonoffmini Watchdog (ACKNOWLEDGED BUT UNRESOLVED)**
**File**: 020_Scheduled_rev20260307.py  
**Lines**: 179, 195, 211  
**Issue**: Code has explicit race condition comments but no mitigation

```python
# Line 179:
if items["Sonoffmini1_Alive"] == OFF:   ###Posibil Race condition daca Alive nu se activeaza la timp
    if items["PermDormC_Forced"] == ON:
        events.sendCommand("PermDormC_Forced", "OFF")
```

**Scenario**: 
1. Sonoff device goes offline
2. Watchdog reads `Sonoffmini1_Alive` == OFF
3. But between check and action, device comes back online
4. Action still executes, causing false positives

**Fix Required**: Add timestamp-based debouncing (hold state for N consecutive checks before acting)

---

### 7. **No Priza1_BatteryFull Reset on Midnight Bug**
**File**: 020_Scheduled_rev20260307.py  
**Lines**: 456-459  
**Issue**: Logic appears correct but will fail due to state comparison bug (#4)

```python
if DateTime.now().getHourOfDay() == 0:
    if items["Priza1_BatteryFull"] != OFF:  # ← This comparison is unreliable!
        events.sendCommand("Priza1_BatteryFull", "OFF")
```

**Impact**: Midnight reset of BatteryFull flag may not work correctly, causing e-bike to stay in full-battery state

**Fix Required**: Fix state comparison issue (covered in #4)

---

### 8. **Unsafe Timer Cancellation**
**File**: 020_Scheduled_rev20260307.py  
**Lines**: 287, 319  
**Issue**: Calls `.cancel()` on potentially None timers

```python
# Line 287:
def timer_priza8():
    events.sendCommand("Priza8_Power", "OFF")
    events.sendCommand("Priza11_Power", "OFF")
    priza8TimerOff.cancel()  # ← What if priza8TimerOff is still None?

# Line 319:
def timer_fireplace():
    events.sendCommand("Fireplace", "OFF")
    LogAction.logInfo("fireplace_cinema", "Fireplace is off due to Cinema off")
    Fireplacetimer.cancel()  # ← Same issue
```

**Impact**: If timer callback is called abnormally, `.cancel()` on None will raise AttributeError

**Fix Required**: 
```python
def timer_priza8():
    events.sendCommand("Priza8_Power", "OFF")
    events.sendCommand("Priza11_Power", "OFF")
    if priza8TimerOff is not None:
        priza8TimerOff.cancel()
```

---

## Medium Priority Issues

### 9. **Excessive Direct Item State Comparisons in 080_Power (PATTERN ISSUE)**
**File**: 080_Power_rev20260312.py  
**Issue**: Large script uses direct `==` and `!=` with state objects throughout (50+ instances likely)

**Example from earlier grep**:
```python
if items["PWRConsumption"] == ...
if str(items["Eco_Power_Switch"]).upper() == "ON"  # ← This one does string conversion!
```

**Impact**: Inconsistent behavior; some comparisons work, others fail randomly

**Fix Required**: Standardize all state comparisons; add `is_state()` helper to 080_Power

---

### 10. **Incomplete Priza1_Power State Reset Logic**
**File**: 020_Scheduled_rev20260307.py  
**Lines**: 456-460  
**Issue**: Function name `stop_prize` but only affects Priza1_Power and BatteryFull

```python
def stop_prize(event):
    if DateTime.now().getHourOfDay() == 0:
        if items["Priza1_BatteryFull"] != OFF:
            events.sendCommand("Priza1_BatteryFull", "OFF")
    events.sendCommand("Priza1_Power", "OFF")  # ← Turns off for both midnight AND noon
```

**Comment says**: Priza1_BatteryFull reset "only at midnight before Priza1_Power OFF"  
**But code does**: Resets BatteryFull at midnight, then turns OFF power at both midnight and noon

**Fix Status**: Logic is correct but confusing (noon power-off might be intentional)

---

### 11. **Missing Priza4_BatteryFull Reset at Midnight**
**File**: 020_Scheduled_rev20260307.py  
**Lines**: 456-460  
**Issue**: Only Priza1_BatteryFull is reset at midnight; Priza4_BatteryFull is not reset

**Comment in 017_Prize** says:
```python
# - Priza4_BatteryFull: same pattern — reset when Priza4_Power turns ON
```

**Gap**: No scheduled reset at midnight like Priza1. If laptop battery shows full but device is unplugged, flag never clears.

**Fix Required**: Add Priza4_BatteryFull midnight reset:
```python
if DateTime.now().getHourOfDay() == 0:
    if items["Priza1_BatteryFull"] != OFF:
        events.sendCommand("Priza1_BatteryFull", "OFF")
    if items["Priza4_BatteryFull"] != OFF:
        events.sendCommand("Priza4_BatteryFull", "OFF")
```

---

## Low Priority Issues

### 12. **Commented-out Priza1 Control Logic**
**File**: 020_Scheduled_rev20260307.py  
**Lines**: 67, 94, 470  
**Issue**: Multiple lines comment out Priza1_Power commands with note "A fost transformata Priza1 pentru E-Bike"

```python
#events.sendCommand("Priza1_Power", "ON") ###18.10.2025### A fost transformata Priza1 pentru E-Bike
```

**Impact**: Low - this appears intentional (Priza1 is now e-bike charger, not controlled by these schedules)

**Recommendation**: Clean up comments or document the change

---

### 13. **Kodi2 Switch State Duplicate**
**File**: 020_Scheduled_rev20260307.py  
**Lines**: 138-148  
**Issue**: Two nearly identical rules for Kodi and Kodi2 (copy-paste)

```python
# Line 138-142
def kodi_switch_state(event):
    if items["Kodi_restart"] == OFF:
        events.sendCommand("Kodi_restart", "ON")

# Line 144-148
def kodi2_switch_state(event):
    if items["Kodi2_restart"] == OFF:
        events.sendCommand("Kodi2_restart", "ON")
```

**Impact**: Low - functional but suggests code duplication that could be refactored

---

## Summary of Fixes Needed

| Priority | Issue | File | Type |
|----------|-------|------|------|
| CRITICAL | State comparison bug in 080_Power | 080_Power_rev20260312.py | Implement fix |
| BLOCKING | Missing StringType import | 020_Scheduled_rev20260307.py | Add import |
| BLOCKING | Missing ON/OFF import | 020_Scheduled_rev20260307.py | Add import |
| CRITICAL | Duplicate function definition | 020_Scheduled_rev20260307.py | Rename function |
| CRITICAL | State comparison issues (22+ lines) | 020_Scheduled_rev20260307.py | Apply is_state() |
| HIGH | Race condition in Sonoffmini | 020_Scheduled_rev20260307.py | Add debouncing |
| HIGH | Priza4_BatteryFull missing midnight reset | 020_Scheduled_rev20260307.py | Add reset |
| MEDIUM | Timer null-check missing | 020_Scheduled_rev20260307.py | Add guard |
| MEDIUM | State comparison pattern (50+) | 080_Power_rev20260312.py | Apply fix |

---

## Testing Recommendations

After fixes are applied:

1. **020_Scheduled startup**: Verify no `NameError` exceptions in logs
2. **Midnight/Noon cycles**: Verify Priza1_BatteryFull and Priza4_BatteryFull reset correctly
3. **Sonoffmini watchdog**: Simulate device offline/online transitions; verify no false positives
4. **ECO sequence**: Verify Priza1 is skipped when `Priza1_BatteryFull` = ON
5. **Kodi automation**: Verify both Kodi and Kodi2 switch states are maintained

---

## Recommended Implementation Order

1. **Today**: Fix blocking import errors in 020_Scheduled
2. **Today**: Fix duplicate function definition
3. **Today**: Add state comparison fixes to 020_Scheduled and 080_Power
4. **Next cycle**: Add Priza4_BatteryFull midnight reset
5. **Next cycle**: Implement Sonoffmini debouncing
6. **Nice-to-have**: Refactor Kodi duplicate rules
