# Remaining Bugs and Gaps - Comprehensive Audit

**Date**: 2026-06-20  
**Scope**: All 25 automation scripts  
**Status**: Post-deployment analysis

---

## Executive Summary

After deploying fixes to 017_Prize, 019_Charge_curve, and 020_Scheduled, a broader scan reveals **systemic state comparison issues across 13 additional scripts**.

| Category | Count | Priority |
|----------|-------|----------|
| Scripts with state comparison issues | 13 | CRITICAL |
| Scripts missing OnOffType import | 5 | BLOCKING |
| Potential failures if rules fire | 7 | HIGH |
| Already fixed today | 3 | ✅ |

---

## Critical: Scripts Missing OnOffType Import

These scripts use ON/OFF comparisons but **don't import OnOffType**, causing **NameError at runtime when rules fire**:

### 1. **011_Illumination_rev20260307.py** (618 lines)
- **Issue**: 162 state comparisons, NO OnOffType import
- **Risk**: BLOCKING - Will crash when any lighting rule fires
- **Examples**:
  ```python
  if items["Sufra1_Light_Illuminance"] >= QuantityType(u"18.0 lx") and items["Sufragerie1_Daytime"] != ON:
  if items["Sufra2_Light_Illuminance"] < QuantityType(u"18.0 lx") and items["Sufragerie2_Daytime"] != OFF:
  ```
- **Impact**: Entire illumination system could fail

### 2. **016_HomePresence_rev20250307.py** (306 lines)
- **Issue**: 45 state comparisons, NO OnOffType import
- **Risk**: BLOCKING - Will crash when presence detection fires
- **Examples**:
  ```python
  if TelOnline.state != ON and items["HomePresence"] != OFF:
  if items["HomePresence"] != ON:
  if event.itemState == OFF:
  ```
- **Impact**: Home presence detection could fail

### 3. **030_priza2_runtime_rev20260307.py** (136 lines)
- **Issue**: 2 state comparisons, NO OnOffType import
- **Risk**: MEDIUM - Only 2 occurrences, might not fire
- **Examples**:
  ```python
  if new_minutes >= LIMIT_MINUTES and items[SWITCH_ITEM_NAME] != ON:
  if event.itemState == ON:
  ```
- **Impact**: Priza2 runtime monitoring could fail

### 4. **055_Cinema.py** (145 lines)
- **Issue**: 23 state comparisons, NO OnOffType import
- **Risk**: MEDIUM - Uses ON/OFF for logic
- **Examples**:
  ```python
  if event.itemState == ON:
  ```
- **Impact**: Cinema automation could fail

### 5. **083_Priza9_ForceOn.py** (19 lines)
- **Issue**: 1 state comparison, NO OnOffType import
- **Risk**: LOW - Only 1 occurrence, small script
- **Examples**:
  ```python
  if items["Priza9_Power"] != ON:
  ```
- **Impact**: Priza9 force-on could fail occasionally

---

## High Priority: Unreliable Comparisons (Have OnOffType, But Using != Instead of ==)

These scripts have OnOffType imported but use unreliable patterns:

### 6. **050_Reguli_rev20260307.py** (1653 lines - LARGEST SCRIPT)
- **Issue**: 217 state comparisons using direct == and !=
- **Risk**: HIGH - Largest and most complex script
- **Impact**: Could affect multiple rule chains
- **Note**: Has OnOffType, so might work, but unreliable

### 7. **099_Switches_Logic_rev20260307.py** (567 lines)
- **Issue**: 83 state comparisons, uses unreliable patterns
- **Risk**: HIGH - Complex switching logic
- **Examples**:
  ```python
  if items["Sonoffmini1_Alive"] == OFF:
  if items["Priza1_BatteryFull"] == ON:
  ```
- **Impact**: Sonoffmini and Priza logic could fail

### 8. **011_Illumination_rev20260307.py** (618 lines)
- **Issue**: 162 direct comparisons
- **Risk**: CRITICAL - Largest number of comparisons
- **Impact**: Lighting system unreliable

### 9. **016_HomePresence_rev20250307.py** (306 lines)
- **Issue**: 45 direct comparisons
- **Risk**: HIGH - Presence detection core logic
- **Impact**: Home automation triggers unreliable

### 10. **045_Bucatarie_rev20260307.py** (222 lines)
- **Issue**: 36 direct comparisons, uses both == and !=
- **Risk**: MEDIUM-HIGH
- **Impact**: Kitchen automation could be unreliable

---

## Medium Priority: Minimal Issues

### 11. **018_Delay_rev20260307.py** (72 lines)
- **Issue**: 5 direct comparisons
- **Risk**: LOW - Small script, has OnOffType
- **Status**: Low impact

### 12. **082_tomato_led.py** (428 lines)
- **Issue**: 3 direct comparisons
- **Risk**: LOW - Minimal impact, has OnOffType
- **Status**: Low impact

### 13. **017_Prize_rev20260307.py** (1166 lines)
- **Status**: ✅ ALREADY FIXED (deployed 2026-06-20 17:47)

### 14. **019_Charge_curve_rev20260307.py** (273 lines)
- **Status**: ✅ ALREADY FIXED (deployed 2026-06-20 17:47)

### 15. **020_Scheduled_rev20260307.py** (479 lines)
- **Status**: ✅ ALREADY FIXED (deployed 2026-06-20 19:12)

---

## Systemic Issues Summary

### By Script Size (Risk Correlation)
| Size | Script | Comparisons | Status |
|------|--------|------------|--------|
| 1653 | 050_Reguli | 217 | ⚠️ Unfixed |
| 1166 | 017_Prize | 162+ | ✅ Fixed |
| 618 | 011_Illumination | 162 | 🔴 Unfixed, BLOCKING |
| 567 | 099_Switches_Logic | 83 | ⚠️ Unfixed |
| 479 | 020_Scheduled | 26 | ✅ Fixed |
| 428 | 082_tomato_led | 3 | ⚠️ Unfixed, Low-risk |
| 306 | 016_HomePresence | 45 | 🔴 Unfixed, BLOCKING |
| 273 | 019_Charge_curve | 26+ | ✅ Fixed |
| 222 | 045_Bucatarie | 36 | ⚠️ Unfixed |
| 145 | 055_Cinema | 23 | 🔴 Unfixed, BLOCKING |
| 136 | 030_priza2_runtime | 2 | 🟡 Unfixed |
| 72 | 018_Delay | 5 | ⚠️ Unfixed, Low-risk |
| 19 | 083_Priza9_ForceOn | 1 | 🟡 Unfixed, Low-risk |

---

## Other Identified Gaps

### 16. Missing Priza4_BatteryFull Midnight Reset
**File**: 020_Scheduled_rev20260307.py  
**Status**: IDENTIFIED (not yet fixed)  
**Issue**: Only Priza1_BatteryFull resets at midnight; Priza4 never resets if not charged  
**Recommendation**: Add reset for Priza4_BatteryFull at midnight

### 17. Sonoffmini Race Condition
**File**: 020_Scheduled_rev20260307.py  
**Status**: IDENTIFIED (not yet fixed)  
**Issue**: Watchdog checks state without debouncing; can trigger on transient glitches  
**Lines**: 179, 195, 211  
**Recommendation**: Add minimum hold time (debouncing) before acting

### 18. Unsafe Timer Cancellation
**File**: 020_Scheduled_rev20260307.py  
**Status**: IDENTIFIED (not yet fixed)  
**Issue**: Calls `.cancel()` on potentially None timers  
**Lines**: 287, 319  
**Recommendation**: Add null-check before cancel

---

## Recommended Fix Priority

### Phase 1 (CRITICAL - Fix Immediately)
Priority order by impact:

1. **011_Illumination_rev20260307.py** (162 comparisons, BLOCKING import missing)
2. **016_HomePresence_rev20250307.py** (45 comparisons, BLOCKING import missing)
3. **050_Reguli_rev20260307.py** (217 comparisons, largest script)

**Estimated effort**: ~1 hour for all three

### Phase 2 (HIGH - Fix This Week)
4. **099_Switches_Logic_rev20260307.py** (83 comparisons)
5. **045_Bucatarie_rev20260307.py** (36 comparisons)
6. **055_Cinema.py** (23 comparisons, missing import)
7. **030_priza2_runtime_rev20260307.py** (2 comparisons, missing import)

**Estimated effort**: ~1-2 hours

### Phase 3 (MEDIUM - Fix Next Sprint)
8. **082_tomato_led.py** (3 comparisons, has import)
9. **018_Delay_rev20260307.py** (5 comparisons, has import)
10. **083_Priza9_ForceOn.py** (1 comparison, missing import)

**Estimated effort**: ~30 minutes

### Phase 4 (LOW - Technical Debt)
- Add Priza4_BatteryFull midnight reset
- Implement Sonoffmini debouncing
- Add timer null-checks
- Code deduplication (Kodi rules, etc.)

---

## Evidence from Current Logs

Currently, the system is operating despite these issues because:
1. **Most rules aren't firing right now** (early evening)
2. **Some comparisons work by accident** if object type matches
3. **Errors would only appear when the rule fires**

**When will issues manifest?**
- **055_Cinema.py**: Evening when Cinema mode activates
- **011_Illumination.py**: When any room illumination rules trigger
- **016_HomePresence.py**: Next presence detection event
- **Others**: At various times depending on triggers

---

## Recommended Immediate Action

### Option A: Minimal (Blocking Issues Only)
Fix only scripts with missing OnOffType imports:
- 011_Illumination (BLOCKING)
- 016_HomePresence (BLOCKING)
- 055_Cinema (BLOCKING)
- 030_priza2_runtime (Low-risk)
- 083_Priza9_ForceOn (Low-risk)

**Time**: ~30 minutes  
**Risk**: Low (same fix pattern already validated)  

### Option B: Comprehensive (All State Comparison Issues)
Apply the `is_state()` helper to all 13 scripts:
- All from Option A plus:
- 050_Reguli (217 comparisons)
- 099_Switches_Logic (83 comparisons)
- 045_Bucatarie (36 comparisons)
- 082_tomato_led (3 comparisons)
- 018_Delay (5 comparisons)

**Time**: ~2-3 hours  
**Risk**: Low (same pattern, but larger scope)  
**Benefit**: Eliminates systemic reliability issue

### Option C: Defensive (Monitor & Defer)
- Keep current backups
- Monitor logs for errors when rules fire
- Fix issues as they occur

**Time**: Immediate, ~0 minutes  
**Risk**: High (will see real failures)  
**Benefit**: Lowest effort

---

## My Recommendation

**Implement Option A immediately**, then schedule Option B for this week:

1. **Today**: Add missing OnOffType imports to 5 scripts (30 min)
2. **This week**: Apply `is_state()` helper to 8 more scripts (2-3 hours)
3. **Keep deployed**: Current backups & rollback procedures

This eliminates **blocking errors** immediately and fixes **systemic reliability issues** within a week.

---

## Questions for You

1. Should I proceed with Option A (blocking imports only) today?
2. Or would you prefer Option B (all state comparison fixes)?
3. Or Option C (monitor and defer)?

The pattern is proven (we just fixed it 3 times today), so the risk is very low for either A or B.

---

*Analysis completed 2026-06-20 at 19:15 UTC*  
*Based on scan of all 25 automation scripts*  
*Evidence: Log analysis + code review*
