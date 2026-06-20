# OpenHAB Bugs - Quick Reference

## 🔴 BLOCKING ISSUES (Will cause immediate failures)

### 1. Missing Imports in 020_Scheduled
**File**: `020_Scheduled_rev20260307.py`  
**Fix**: Add line 20 (after existing imports):
```python
from org.eclipse.smarthome.core.library.types import StringType, OnOffType
ON = OnOffType.ON
OFF = OnOffType.OFF
```
**Why**: Script uses `StringType()`, `ON`, `OFF` but doesn't import them

---

### 2. Duplicate Function Definition
**File**: `020_Scheduled_rev20260307.py`  
**Problem**: Line 231 defines `permsufra_forced_switch_state()` but it already exists at line 210  
**Result**: The restart function overwrites the Sonoffmini3 watchdog

**Fix**: Rename line 231 function from:
```python
def permsufra_forced_switch_state(event):  # ← WRONG
    events.sendCommand("Restart_Openhab", "ON")
```
To:
```python
def restart_openhab_monthly(event):  # ← CORRECT
    events.sendCommand("Restart_Openhab", "ON")
```

---

## 🟠 CRITICAL ISSUES (Unreliable behavior)

### 3. State Comparison Bug Everywhere
**Files**: 
- `020_Scheduled_rev20260307.py` (22+ lines)
- `080_Power_rev20260312.py` (50+ lines, discovered)
- `017_Prize_rev20260307.py` (ALREADY FIXED)
- `019_Charge_curve_rev20260307.py` (ALREADY FIXED)

**Problem**: Direct comparison with ON/OFF/UNDEF (Java objects) is unreliable

**Already Fixed In**: 017_Prize & 019_Charge_curve (deployed 2026-06-20)

**Still Broken In**: 020_Scheduled & 080_Power

**Impact**: Rules fail randomly; ECO sequence won't skip Priza1 when full

---

### 4. ECO Sequence Respects BatteryFull but Using Buggy Comparison
**File**: `080_Power_rev20260312.py` lines 632-641  
**Current Code**:
```python
if items["Priza1_BatteryFull"] == OnOffType.ON:  # ← Unreliable!
    log("BatteryFull is ON, skipping Priza1")
    return
```

**Impact**: May not skip Priza1 when battery is full

---

## 🟡 HIGH PRIORITY ISSUES (Design gaps)

### 5. Missing Priza4_BatteryFull Midnight Reset
**File**: `020_Scheduled_rev20260307.py` line 456  
**Current**: Only resets Priza1_BatteryFull at midnight  
**Missing**: Priza4_BatteryFull reset (laptop charger)

**Gap**: If laptop charger shows full battery but device is unplugged, flag never clears

---

### 6. Sonoffmini Race Condition (Acknowledged but Unresolved)
**File**: `020_Scheduled_rev20260307.py` lines 179, 195, 211  
**Issue**: Code explicitly comments "Posibil Race condition"  
**Problem**: Watches Sonoffmini alive state but no debouncing

---

## 📊 Issues by Severity

| Count | Severity | Category |
|-------|----------|----------|
| 2 | 🔴 BLOCKING | Missing imports & duplicate function |
| 4 | 🟠 CRITICAL | State comparison bugs (3 files) |
| 2 | 🟡 HIGH | Missing reset & race condition |
| 2 | 🔵 MEDIUM | Timer safety & pattern issues |
| 4 | ⚪ LOW | Code cleanup / documentation |

---

## Action Items

### Today
- [ ] Add missing imports to 020_Scheduled
- [ ] Rename duplicate function in 020_Scheduled
- [ ] Fix state comparisons in 020_Scheduled (apply same `is_state()` pattern as 017/019)
- [ ] Fix state comparisons in 080_Power (apply same `is_state()` pattern)

### This Week
- [ ] Add Priza4_BatteryFull midnight reset
- [ ] Add timer null-checks to 020_Scheduled

### Next Sprint
- [ ] Implement Sonoffmini debouncing
- [ ] Refactor duplicate Kodi rules
