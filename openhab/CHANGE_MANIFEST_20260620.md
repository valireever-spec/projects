# Change Manifest - OpenHAB Automation Bug Fixes
**Date**: 2026-06-20  
**Backup Location**: `/home/vali/projects/openhab/backups/20260620_180321/`

---

## Summary of Changes

This document describes **exactly** which lines will change in which files, with before/after code comparison.

### Files to be Modified
1. **020_Scheduled_rev20260307.py** - 4 changes (blocking imports, duplicate function, state comparisons)
2. **080_Power_rev20260312.py** - 3 changes (state comparisons)

**Files NOT being modified yet**:
- 017_Prize_rev20260307.py (ALREADY FIXED on 2026-06-20 17:47)
- 019_Charge_curve_rev20260307.py (ALREADY FIXED on 2026-06-20 17:47)

---

## File 1: 020_Scheduled_rev20260307.py

### Change 1: Add Missing Imports (BLOCKING)
**Priority**: BLOCKING - Script will crash if StringType rules fire  
**Location**: After line 27 (after existing imports)  
**Type**: INSERT new code

**BEFORE**:
```python
from core.log import logging
from core.jsr223 import scope

NULL = UnDefType.NULL
```

**AFTER**:
```python
from core.log import logging
from core.jsr223 import scope
from org.eclipse.smarthome.core.library.types import StringType, OnOffType

NULL = UnDefType.NULL
UNDEF = UnDefType.UNDEF
ON = OnOffType.ON
OFF = OnOffType.OFF
```

**Reason**: Script uses `StringType()`, `ON`, `OFF` constants but doesn't import them. Will cause `NameError` when rules fire.

---

### Change 2: Add Safe State Comparison Helper (QUALITY)
**Priority**: HIGH - Prevents random rule failures  
**Location**: After imports, before first rule definition (around line 50)  
**Type**: INSERT new code

**AFTER imports, INSERT**:
```python
def is_state(item_state, target_state):
    """Safe state comparison using string conversion. Handles Java State objects reliably."""
    return str(item_state).strip() == str(target_state).strip()
```

**Reason**: Replaces unreliable direct `==` and `!=` comparisons with Java State objects.

---

### Change 3: Fix Duplicate Function Definition (CRITICAL)
**Priority**: CRITICAL - Silently overwrites Sonoffmini watchdog  
**Location**: Line 231  
**Type**: RENAME function

**BEFORE** (line 231):
```python
@rule("Restart Openhab cronjob", description="Restart Openhab cronjob", tags=["cron", "openHAB"])
@when("Time cron 0 30 11 1 * ?")
def permsufra_forced_switch_state(event):
    events.sendCommand("Restart_Openhab", "ON")
```

**AFTER** (line 231):
```python
@rule("Restart Openhab monthly", description="Restart Openhab on 1st of month at 11:30", tags=["cron", "openHAB"])
@when("Time cron 0 30 11 1 * ?")
def restart_openhab_monthly(event):
    events.sendCommand("Restart_Openhab", "ON")
```

**Changes**:
- Rename function from `permsufra_forced_switch_state` to `restart_openhab_monthly`
- Update rule description to be more specific
- Update tag for clarity

**Reason**: Function with same name as line 210 silently overwrites it in the rule registry, losing Sonoffmini3 watchdog logic.

---

### Change 4: Fix State Comparisons (Replace == with is_state)
**Priority**: HIGH - Prevents silent rule failures  
**Location**: Multiple lines  
**Type**: REPLACE direct comparisons with `is_state()` calls

**Lines to change**:

#### 4a. Line 56 (Vacanta check)
```python
# BEFORE:
if items["Vacanta"] != ON:

# AFTER:
if not is_state(items["Vacanta"], ON):
```

#### 4b. Line 70 (Sufragerie checks)
```python
# BEFORE:
if items["Sufragerie_Daytime"] == OFF or items["Sufragerie_Illuminance_Switch"] == ON:

# AFTER:
if is_state(items["Sufragerie_Daytime"], OFF) or is_state(items["Sufragerie_Illuminance_Switch"], ON):
```

#### 4c. Line 141 (Kodi check)
```python
# BEFORE:
if items["Kodi_restart"] == OFF:

# AFTER:
if is_state(items["Kodi_restart"], OFF):
```

#### 4d. Line 147 (Kodi2 check)
```python
# BEFORE:
if items["Kodi2_restart"] == OFF:

# AFTER:
if is_state(items["Kodi2_restart"], OFF):
```

#### 4e. Line 179 (Sonoffmini1)
```python
# BEFORE:
if items["Sonoffmini1_Alive"] == OFF:

# AFTER:
if is_state(items["Sonoffmini1_Alive"], OFF):
```

#### 4f. Line 180 (PermDormC)
```python
# BEFORE:
if items["PermDormC_Forced"] == ON:

# AFTER:
if is_state(items["PermDormC_Forced"], ON):
```

#### 4g. Line 186 (Sonoff1 UNDEF check)
```python
# BEFORE:
if items["Sonoff1_Latency"] == UNDEF:

# AFTER:
if is_state(items["Sonoff1_Latency"], UNDEF):
```

#### 4h. Line 188 (Sonoffmini1_Alive)
```python
# BEFORE:
if items["Sonoffmini1_Alive"] != OFF:

# AFTER:
if not is_state(items["Sonoffmini1_Alive"], OFF):
```

#### 4i. Line 195 (Sonoffmini2)
```python
# BEFORE:
if items["Sonoffmini2_Alive"] == OFF:

# AFTER:
if is_state(items["Sonoffmini2_Alive"], OFF):
```

#### 4j. Line 196 (PermDormP)
```python
# BEFORE:
if items["PermDormP_Forced"] == ON:

# AFTER:
if is_state(items["PermDormP_Forced"], ON):
```

#### 4k. Line 202 (Sonoff2 UNDEF)
```python
# BEFORE:
if items["Sonoff2_Latency"] == UNDEF:

# AFTER:
if is_state(items["Sonoff2_Latency"], UNDEF):
```

#### 4l. Line 204 (Sonoffmini2)
```python
# BEFORE:
if items["Sonoffmini2_Alive"] != OFF:

# AFTER:
if not is_state(items["Sonoffmini2_Alive"], OFF):
```

#### 4m. Line 211 (Sonoffmini3)
```python
# BEFORE:
if items["Sonoffmini3_Alive"] == OFF:

# AFTER:
if is_state(items["Sonoffmini3_Alive"], OFF):
```

#### 4n. Line 212 (PermSufra)
```python
# BEFORE:
if items["PermSufra_Forced"] == ON:

# AFTER:
if is_state(items["PermSufra_Forced"], ON):
```

#### 4o. Line 217 (Sonoff3 UNDEF)
```python
# BEFORE:
if items["Sonoff3_Latency"] == UNDEF:

# AFTER:
if is_state(items["Sonoff3_Latency"], UNDEF):
```

#### 4p. Line 220 (Sonoffmini3)
```python
# BEFORE:
if items["Sonoffmini3_Alive"] != OFF:

# AFTER:
if not is_state(items["Sonoffmini3_Alive"], OFF):
```

#### 4q. Line 237 (Sonoff1 double check)
```python
# BEFORE:
if items["Sonoff1_Latency"] == UNDEF or items["Sonoff1_Latency"] == NULL:

# AFTER:
if is_state(items["Sonoff1_Latency"], UNDEF) or is_state(items["Sonoff1_Latency"], NULL):
```

#### 4r. Line 243 (Sonoff2 double check)
```python
# BEFORE:
if items["Sonoff2_Latency"] == UNDEF or items["Sonoff2_Latency"] == NULL:

# AFTER:
if is_state(items["Sonoff2_Latency"], UNDEF) or is_state(items["Sonoff2_Latency"], NULL):
```

#### 4s. Line 249 (Sonoff3 double check)
```python
# BEFORE:
if items["Sonoff3_Latency"] == UNDEF or items["Sonoff3_Latency"] == NULL:

# AFTER:
if is_state(items["Sonoff3_Latency"], UNDEF) or is_state(items["Sonoff3_Latency"], NULL):
```

#### 4t. Line 255, 261, 267 (ScriptParrot checks)
```python
# BEFORE (line 255):
if items["ScriptParrot_Sonoff1_up"] == OFF:

# AFTER:
if is_state(items["ScriptParrot_Sonoff1_up"], OFF):

# BEFORE (line 261):
if items["ScriptParrot_Sonoff2_up"] == OFF:

# AFTER:
if is_state(items["ScriptParrot_Sonoff2_up"], OFF):

# BEFORE (line 267):
if items["ScriptParrot_Sonoff3_up"] == OFF:

# AFTER:
if is_state(items["ScriptParrot_Sonoff3_up"], OFF):
```

#### 4u. Line 273, 278 (Tube_Lamp)
```python
# BEFORE (line 273):
if event.itemState == OFF:

# AFTER:
if is_state(event.itemState, OFF):

# BEFORE (line 278):
if event.itemState == ON:

# AFTER:
if is_state(event.itemState, ON):
```

#### 4v. Line 302, 305, 309 (priza8_tod_state)
```python
# BEFORE (line 302):
if event.itemState == StringType(evening):

# AFTER:
if is_state(event.itemState, StringType(evening)):

# BEFORE (line 305):
elif event.itemState == StringType(night):

# AFTER:
elif is_state(event.itemState, StringType(night)):

# BEFORE (line 309):
elif event.itemState == StringType(bed):

# AFTER:
elif is_state(event.itemState, StringType(bed)):
```

#### 4w. Line 328, 329 (fireplace_cinema)
```python
# BEFORE (line 328):
if items["vTimeOfDay"] == StringType(evening):

# AFTER:
if is_state(items["vTimeOfDay"], StringType(evening)):

# BEFORE (line 329):
if event.itemState == OFF:

# AFTER:
if is_state(event.itemState, OFF):
```

#### 4x. Line 332 (fireplace ON)
```python
# BEFORE:
elif event.itemState == ON:

# AFTER:
elif is_state(event.itemState, ON):
```

#### 4y. Line 343, 344, 346, 349 (priza9_tod_hp_state)
```python
# BEFORE (line 343):
if items["vTimeOfDay"] == StringType(day) or items["vTimeOfDay"] == StringType(afternoon):

# AFTER:
if is_state(items["vTimeOfDay"], StringType(day)) or is_state(items["vTimeOfDay"], StringType(afternoon)):

# BEFORE (line 344):
if items["Eco_Power_Switch"] == ON:

# AFTER:
if is_state(items["Eco_Power_Switch"], ON):

# BEFORE (line 346):
elif items["vTimeOfDay"] == StringType(evening):

# AFTER:
elif is_state(items["vTimeOfDay"], StringType(evening)):

# BEFORE (line 349):
if items["vTimeOfDay"] == StringType(evening):

# AFTER:
if is_state(items["vTimeOfDay"], StringType(evening)):
```

#### 4z. Line 457 (Priza1_BatteryFull midnight reset - CRITICAL)
```python
# BEFORE:
if items["Priza1_BatteryFull"] != OFF:

# AFTER:
if not is_state(items["Priza1_BatteryFull"], OFF):
```

**Reason**: All these direct comparisons are unreliable with Java State objects. Using `is_state()` ensures safe string-based comparison.

---

## File 2: 080_Power_rev20260312.py

### Change 1: Add Safe State Comparison Helper
**Priority**: HIGH  
**Location**: After imports, before first rule definition (around line 50)  
**Type**: INSERT new code

**AFTER imports, INSERT**:
```python
def is_state(item_state, target_state):
    """Safe state comparison using string conversion. Handles Java State objects reliably."""
    return str(item_state).strip() == str(target_state).strip()
```

---

### Change 2: Fix Priza1_BatteryFull Check in ECO Sequence
**Priority**: CRITICAL - Prevents Priza1 skipping when battery full  
**Location**: Line 632  
**Type**: REPLACE

**BEFORE**:
```python
if items["Priza1_BatteryFull"] == OnOffType.ON:
```

**AFTER**:
```python
if is_state(items["Priza1_BatteryFull"], OnOffType.ON):
```

---

### Change 3: Fix Priza4_BatteryFull Check in ECO Sequence
**Priority**: HIGH  
**Location**: Line 637, 641  
**Type**: REPLACE

**BEFORE** (line 637):
```python
if items["Priza4_BatteryFull"] == OnOffType.ON:
```

**AFTER**:
```python
if is_state(items["Priza4_BatteryFull"], OnOffType.ON):
```

**BEFORE** (line 641):
```python
if items["Priza4_BatteryFull"] != OnOffType.ON:
```

**AFTER**:
```python
if not is_state(items["Priza4_BatteryFull"], OnOffType.ON):
```

---

## Summary Table

| File | Changes | Lines | Type | Priority |
|------|---------|-------|------|----------|
| 020_Scheduled | Add imports | +4 | INSERT | BLOCKING |
| 020_Scheduled | Add helper function | +3 | INSERT | HIGH |
| 020_Scheduled | Rename function | 231 | RENAME | CRITICAL |
| 020_Scheduled | Fix comparisons | 26 lines | REPLACE | HIGH |
| 080_Power | Add helper function | +3 | INSERT | HIGH |
| 080_Power | Fix BatteryFull checks | 3 lines | REPLACE | CRITICAL |

**Total Changes**: 39 lines modified/added across 2 files

---

## Rollback Procedure

If issues occur after deployment, rollback is simple:

```bash
# Restore from backup
cp /home/vali/projects/openhab/backups/20260620_180321/020_Scheduled_rev20260307.py.backup \
   /etc/openhab2/automation/jsr223/python/personal/020_Scheduled_rev20260307.py

cp /home/vali/projects/openhab/backups/20260620_180321/080_Power_rev20260312.py.backup \
   /etc/openhab2/automation/jsr223/python/personal/080_Power_rev20260312.py

# Wait for OpenHAB to reload scripts (check logs)
```

---

## Deployment Checklist

- [ ] User approves this change manifest
- [ ] Changes applied to local files
- [ ] Files syntax-checked (Python compile test)
- [ ] Files deployed to remote system
- [ ] OpenHAB logs checked for load confirmation
- [ ] Functional testing performed (see test procedures in PRIZA1_BATTFULL_TEST_PROCEDURE.md)

---

## Monitoring After Deployment

**Watch for**:
1. ✓ "Loading script" messages in logs (confirm no errors)
2. ✓ Evening time: StringType rules should fire without NameError
3. ✓ Priza1_BatteryFull checks in ECO sequence
4. ✓ No new exceptions in logs

**Expected behavior**:
- All rules continue to work as before
- State comparisons are now more reliable
- No runtime errors introduced
