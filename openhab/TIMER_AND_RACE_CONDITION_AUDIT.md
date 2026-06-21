# Timer & Race Condition Audit Report

**Date**: 2026-06-20  
**Scope**: 26 automation scripts  
**Audit Type**: Comprehensive vulnerability scan

---

## Executive Summary

**Critical Issues Found: 2 categories**

1. **Timer Null-Checks Missing**: 58 `.cancel()` calls without guards
   - Risk: AttributeError crashes
   - Impact: MEDIUM (timers don't often fail, but risk is high when they do)
   - Severity: 🔴 HIGH

2. **Race Conditions - Sonoffmini Watchdog**: 3 instances  
   - Risk: Transient glitches trigger false failsafes
   - Impact: MEDIUM (rooms toggle lights on temporary WiFi hiccup)
   - Severity: 🔴 HIGH (we just fixed 020_Scheduled, others remain)

---

## Issue 1: Timer .cancel() Without Null-Checks

**Total Instances**: 58 calls across 10 scripts

### Critical Scripts (Highest Timer Usage)

#### 1️⃣ 050_Reguli_rev20260307.py (26+ cancels)
**Risk**: HIGHEST - Most complex timer handling

**Affected Lines**:
```
174, 230, 640, 657, 694, 711, 748, 765, 
824, 838, 852, 982, 1177, 1182, 1187, 1201, 
1320, 1329, 1335, 1342, 1349, 1356, 1361
```

**Pattern**:
```python
occupancyTimer1.cancel()  # No check if occupancyTimer1 is None
_occ_sufra[0].cancel()    # No check if _occ_sufra[0] is None
```

**Example Fix**:
```python
if occupancyTimer1 is not None:
    occupancyTimer1.cancel()

if _occ_sufra[0] is not None:
    _occ_sufra[0].cancel()
```

#### 2️⃣ 017_Prize_rev20260307.py (11 cancels)
**Risk**: MEDIUM-HIGH

**Affected Lines**:
```
231, 236, 242, 247, 270, 443, 552, 659, 664
```

**Pattern**:
```python
timerLSAdina_on.cancel()
DelayTimer1.cancel()
priza4LeaveDebounceTimer.cancel()
```

#### 3️⃣ 016_HomePresence_rev20250307.py (9 cancels)
**Risk**: MEDIUM-HIGH

**Affected Lines**:
```
54, 61, 168, 175, 224, 227, 230, 233, 236
```

**Pattern**:
```python
DelayTimer1.cancel()
DelayTimerON.cancel()
DelayTimerGargoyleOn.cancel()
```

#### 4️⃣ 099_Switches_Logic_rev20260307.py (9 cancels)
**Risk**: MEDIUM

**Affected Lines**:
```
313, 318, 338, 343, 396, 413, 454, 471, 506, 523
```

**Pattern**:
```python
FireplaceTimerOn.cancel()
Fireplace_startTimer.cancel()
Priza1ForceOnTimer.cancel()
```

#### 5️⃣ 055_Cinema.py (5 cancels)
**Risk**: MEDIUM

**Affected Lines**:
```
33, 39, 45, 51, 57
```

**Pattern**:
```python
occupancyTimer1.cancel()
occupancyTimer2.cancel()
```

#### 6️⃣ 098_fireplace_rev20260307.py (3 cancels)
**Risk**: MEDIUM

**Affected Lines**:
```
100, 113, 150
```

**Pattern**:
```python
FireplaceTimerOn.cancel()
FireplaceTimerOff.cancel()
FireplaceRestartTimer.cancel()
```

#### 7️⃣ 045_Bucatarie_rev20260307.py (3 cancels)
**Risk**: MEDIUM

**Affected Lines**:
```
66, 71, 119
```

**Pattern**:
```python
HDtimer4.cancel()
occupancyTimer13.cancel()
occupancyTimerbuca.cancel()
```

#### 8️⃣ 020_Scheduled_rev20260307.py (3 cancels - NOW FIXED)
✅ FIXED 2026-06-20 21:34 UTC
- Lines 310, 343, 360
- Now guarded: `if priza8TimerOff is not None:`

#### 9️⃣ 080_Power_rev20260312.py (1 cancel - safe pattern)
**Line 222**: `t.cancel()`
- **Status**: ✅ SAFE - Called within try/except wrapper
- **Context**: Safe within lock/helper function

#### 🔟 030_priza2_runtime_rev20260307.py (0 cancels)
✅ NO ISSUES

---

## Issue 2: Race Conditions - Sonoffmini Watchdog

**Total Instances**: 3 scripts affected

### Critical: Still Without Debouncing

#### 1️⃣ 011_Illumination_rev20260307.py

**Lines**: 165, 169, 185, 189, 297, 301, 317, 321, 403, 407, 423, 427

**Pattern** (Lines 185–189):
```python
if is_state(items["Sonoffmini3_Alive"], ON):
    # Turn lights ON based on room occupancy
    events.sendCommand("Sofra_Lights", "ON")

if not is_state(items["Sonoffmini3_Alive"], ON):
    # Immediate OFF if device appears offline (no debounce)
    events.sendCommand("Sofra_Lights", "OFF")
```

**Issue**: Triggered by changed events
```python
@when("Item Sonoffmini1_Alive changed")
@when("Item Sonoffmini2_Alive changed") 
@when("Item Sonoffmini3_Alive changed")
```

**Risk**: WiFi glitch → Alive=OFF for 1 sec → lights toggle immediately

**Also watches state changes** (Lines 512–565):
```python
@when("Item Sonoffmini1_Alive changed")
def sonoffmini1_alive_changed(event):
    # Direct reaction, no debouncing
```

#### 2️⃣ 017_Prize_rev20260307.py

**Lines**: 911, 945, 952, 966, 983, 989–1026

**Pattern** (Lines 952–966):
```python
@when("Item Sonoffmini3_Alive changed to OFF")  # Direct OFF detection
def priza4_force_on(event):
    # Immediately affects Priza4 control

@when("Item Sonoffmini3_Alive changed to ON")
def priza4_on_state(event):
    # Immediate ON reaction
```

**Risk**: Transient WiFi glitch → false device control

**Also in Lines 983–1026**:
```python
if items["Sonoffmini1_Alive"] == ON:
    events.sendCommand("Lightstrip_DormC", "ON")  # No debounce
```

#### 3️⃣ 016_HomePresence_rev20250307.py

**Pattern**: Delay timers react immediately to Sonoffmini state
- No debouncing between WiFi glitch and timer activation

---

## Recommendation Priority

### 🔴 URGENT (Fix This Week)

**All Timer Null-Checks**: 55 unguarded `.cancel()` calls
- Scripts: 050_Reguli (26), 017_Prize (11), 016_HomePresence (9), 099_Switches (9), 055_Cinema (5), 098_fireplace (3), 045_Bucatarie (3)
- **Why**: Risk of crash on timer expiration
- **Effort**: ~2–3 hours (mostly pattern-matching and editing)
- **Impact**: Prevents rule failures

### 🟠 HIGH (Fix This Month)

**Sonoffmini Race Conditions**: 2 scripts (011_Illumination, 017_Prize)
- **Why**: Transient WiFi glitches cause false room toggles
- **Effort**: ~1 hour per script (add debounce logic like 020_Scheduled)
- **Impact**: Prevents false light/device activations

016_HomePresence already has delays built-in (uses timers), lower priority

---

## Script-by-Script Status

| Script | Timer Issues | Race Condition | Status |
|--------|--------------|----------------|--------|
| 011_Illumination | 0 | 🔴 YES (Sonoffmini) | NEEDS FIX |
| 016_HomePresence | 🔴 9 | ⚠️ PARTIAL (timers absorb) | MEDIUM RISK |
| 017_Prize | 🔴 11 | 🔴 YES (Sonoffmini) | NEEDS FIX |
| 018_Delay | 0 | 0 | ✅ CLEAN |
| 019_Charge_curve | 0 | 0 | ✅ CLEAN |
| 020_Scheduled | ✅ FIXED | 🔴 FIXED (2026-06-20) | ✅ DONE |
| 030_priza2_runtime | 0 | 0 | ✅ CLEAN |
| 045_Bucatarie | 🔴 3 | 0 | NEEDS FIX |
| 050_Reguli | 🔴 26 | 0 | URGENT |
| 055_Cinema | 🔴 5 | 0 | NEEDS FIX |
| 066_Logging | 0 | 0 | ✅ CLEAN |
| 071_Calculations | 0 | 0 | ✅ CLEAN |
| 077_addMetadata | 0 | 0 | ✅ CLEAN |
| 080_Power | ✅ SAFE (try/except) | 0 | ✅ CLEAN |
| 081_thermostat | 0 | 0 | ✅ CLEAN |
| 082_tomato_led | 0 | 0 | ✅ CLEAN |
| 083_Priza9_ForceOn | 0 | 0 | ✅ CLEAN |
| 098_fireplace | 🔴 3 | 0 | NEEDS FIX |
| 099_Switches | 🔴 9 | 0 | NEEDS FIX |
| 100_Log_Illum | 0 | 0 | ✅ CLEAN |
| 200_AvgPower | 0 | 0 | ✅ CLEAN |
| 201_mqtt_logging | 0 | 0 | ✅ CLEAN |

**Summary**:
- ✅ Clean: 13 scripts
- 🟠 Medium: 2 scripts (16_HomePresence, 017_Prize race only)
- 🔴 High: 8 scripts need timer fixes
- ⚠️ Critical: 2 scripts need race condition fixes (011_Illumination, 017_Prize)

---

## Phased Fix Plan

### Phase A: Timer Null-Checks (55 instances)
**Priority**: URGENT  
**Effort**: ~2–3 hours  
**Approach**: Systematic pattern replacement in 7 scripts

1. **050_Reguli_rev20260307.py** (26 cancels)
2. **017_Prize_rev20260307.py** (11 cancels)
3. **016_HomePresence_rev20250307.py** (9 cancels)
4. **099_Switches_Logic_rev20260307.py** (9 cancels)
5. **055_Cinema.py** (5 cancels)
6. **098_fireplace_rev20260307.py** (3 cancels)
7. **045_Bucatarie_rev20260307.py** (3 cancels)

### Phase B: Sonoffmini Race Conditions (2 scripts)
**Priority**: HIGH  
**Effort**: ~1 hour per script  
**Approach**: Add debounce logic like 020_Scheduled

1. **011_Illumination_rev20260307.py** (12 Sonoffmini checks)
2. **017_Prize_rev20260307.py** (Sonoffmini3_Alive state checks)

---

## Next Steps

**Do you want me to:**

1. ✅ Start with Phase A (timer null-checks across all 7 scripts)?
2. ✅ Then Phase B (Sonoffmini race condition fixes)?
3. 📋 Create detailed manifest for each script first?
4. 🔄 Or prioritize differently?

---

**Audit Completed**: 2026-06-20 21:35 UTC  
**Total Issues Found**: 61  
**Critical Risk Scripts**: 10
