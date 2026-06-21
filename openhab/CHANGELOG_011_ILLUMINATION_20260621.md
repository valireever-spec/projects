# Changelog: 011_Illumination Logger Framework
**Date**: 2026-06-21 12:30 UTC  
**Script**: 011_Illumination_rev20260307.py  
**Changes**: Added Logger framework, fixed malformed logging

---

## What Changed

### 1. Logger Framework Added (Lines 32-57)
- Added `Logger` class with deduplication (60-second threshold)
- Prevents log spam from event-driven triggers
- Instance: `logger = Logger("ILLUM")`

### 2. Fixed Malformed Logging
**Before** (Broken - won't execute):
```python
sufra1_daytime_switch.log.info("Daytime received command ON")
bucatarie2_illum.log.info("Philips sensor measured enough light")
```

**After** (Fixed - works):
```python
logger.info("DAYTIME", "Sufragerie1: Daytime ON")
logger.info("SENSOR", "Bucatarie2: Enough light detected")
```

### 3. Logging Categories Added

| Category | Purpose | When |
|----------|---------|------|
| **DAYTIME** | Daytime switch ON/OFF | On state change |
| **SENSOR** | Illuminance/light level changes | On measurement change |
| **DAYLIGHT** | Natural light conditions | Global daylight status |

### 4. Strategic Logging Points (13 total)

**DAYTIME logs** (10 logs):
- Sufragerie1 ON/OFF
- Sufragerie2 ON/OFF
- Bucatarie1 ON/OFF
- Bucatarie2 ON/OFF
- DormitorP1 ON/OFF
- DormitorP2 ON/OFF
- DormitorC1 ON/OFF
- DormitorC2 ON/OFF

**SENSOR logs** (2 logs):
- Bucatarie2 illuminance status
- Sufra light level changes

**DAYLIGHT logs** (3 logs):
- DormitorC insufficient light
- Bucatarie insufficient light
- Global insufficient light

---

## Deduplication Behavior

**Max 1 log per category per 60 seconds**

Example:
- T=0:00: "Sufragerie1: Daytime ON" → **LOGGED**
- T=0:30: "Sufragerie1: Daytime ON" → **SKIPPED** (same, <60s)
- T=1:00: "Sufragerie1: Daytime ON" → **LOGGED** (60s passed)
- T=1:05: "Sufragerie1: Daytime OFF" → **LOGGED** (different message)

**Result**: No spam, only real state changes visible

---

## Risks Mitigated

✅ **Sensor Churn**: Event-driven triggers won't flood (60s dedup)  
✅ **Broken Patterns**: All malformed `.log.info()` replaced with `logger.info()`  
✅ **Consistency**: Now uses same framework as Phase 1-4  
✅ **Sustainability**: Reusable Logger class prevents future regressions

---

## Files Modified

- 011_Illumination_rev20260307.py: +30 lines (Logger class), ~15 logging replacements
- Before: 653 lines
- After: ~683 lines

---

## Monitoring Points

**Expected logs after deployment**:
```
[ILLUM] [DAYTIME] Sufragerie1: Daytime ON
[ILLUM] [DAYTIME] Sufragerie2: Daytime OFF
[ILLUM] [DAYLIGHT] System: Insufficient natural light globally
[ILLUM] [SENSOR] Sufra illuminance changed to 42 lx
```

**Frequency**: Only on actual state changes (event-driven)  
**Volume**: Low (event-triggered, 60s deduplication)  
**Pattern**: Should see logs whenever motion/light sensors trigger illumination logic

---

## Rollback

```bash
cp /home/vali/projects/openhab/backups/phase2_logging_20260621/011_Illumination_rev20260307.py.backup \
   /etc/openhab2/automation/jsr223/python/personal/011_Illumination_rev20260307.py
```

---

**Status**: Ready for deployment & monitoring  
**Risk Level**: LOW (only logging changes, no logic changes)  
**Expected Impact**: Visibility into illumination decisions without spam

