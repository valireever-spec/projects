# Phase 1 Monitoring Checklist
**Date**: 2026-06-21  
**Script**: 080_Power_rev20260312.py  
**Status**: Deployed & Monitoring  
**Duration**: 24 hours (or until direction changes observed)

---

## What to Monitor

### 1. Logger Framework Works
- [ ] Script loads without errors
- [ ] Existing logs still appear (SUM, RAW, MEDIAN, FILTERED)
- [ ] No performance degradation
- [ ] No exceptions in logs

### 2. Direction Changes Logged
**When it happens**: Power crosses ±50W thresholds
- [ ] See `[DIRECTION]` log with old/new state
- [ ] Format: `Power direction: X → Y (power W)`
- [ ] Only logged once when crossing threshold (not repeatedly)

### 3. Intent Mode Changes Logged
**When it happens**: Mode transitions between IMPORT/EXPORT/NEUTRAL
- [ ] See `[INTENT]` log explaining the mode
- [ ] One of:
  - `IMPORT_MODE: Charging/Running normally`
  - `EXPORT_MODE: Selling power to grid`
  - `NEUTRAL_HOLD: Waiting for direction clarity`

### 4. Deduplication Works
**Spam Prevention**: Same message max once per 60 seconds
- [ ] Don't see identical `[DIRECTION]` repeated more than once/minute
- [ ] Don't see identical `[INTENT]` repeated more than once/minute
- [ ] If direction stays same for 5 min, log still appears every 60s (not zero)

### 5. No Unexpected Errors
- [ ] No AttributeError
- [ ] No KeyError from Logger
- [ ] No DateTime issues
- [ ] No state comparison failures

---

## Log Viewing Commands

### Real-Time Monitoring (Recommended)
```bash
ssh openhabian@192.168.3.25 "tail -f /var/log/openhab2/openhab.log" | grep -E "\[DIRECTION\]|\[INTENT\]|\[WATCHDOG\]|ERROR"
```

**What to expect**: 
- New `[DIRECTION]` logs when power swings
- New `[INTENT]` logs when mode transitions
- Existing SUM/RAW/MEDIAN/FILTERED logs continue

---

### Historical View (If Real-Time Not Available)
```bash
ssh openhabian@192.168.3.25 "grep -E '\[DIRECTION\]|\[INTENT\]|\[WATCHDOG\]' /var/log/openhab2/openhab.log | tail -50"
```

**Shows**: Last 50 direction/intent logs

---

### Check for Errors
```bash
ssh openhabian@192.168.3.25 "grep -i 'error\|exception\|traceback' /var/log/openhab2/openhab.log | tail -20"
```

**Verify**: No new errors since deployment

---

### Count New Log Categories
```bash
ssh openhabian@192.168.3.25 "grep -c '\[DIRECTION\]' /var/log/openhab2/openhab.log"
ssh openhabian@192.168.3.25 "grep -c '\[INTENT\]' /var/log/openhab2/openhab.log"
ssh openhabian@192.168.3.25 "grep -c '\[WATCHDOG\]' /var/log/openhab2/openhab.log"
```

**Expected**:
- `[DIRECTION]`: 1-5 logs (depends on power swings)
- `[INTENT]`: 0-3 logs (depends on mode changes)
- `[WATCHDOG]`: 0 logs (unless DEBUG_VERBOSE=true)

---

## Events to Watch For

### ✅ Good: Direction Change Expected
**When**: 
- Morning: Sun rises, export mode → import mode  
- Midday: High cloud cover, import → export  
- Evening: Sun sets, import → neutral  
- Seasonal shifts: Summer→shoulder, shoulder→winter

**Expected Log**:
```
[ECO] [DIRECTION] Power direction: NEUTRAL → IMPORT (285.0 W)
[ECO] [DIRECTION] Power direction: IMPORT → EXPORT (-75.0 W)
```

### ✅ Good: Intent Mode Change Expected
**When**:
- Power starts importing (50W+ sustained)
- Power starts exporting (-50W+ sustained)
- Power becomes ambiguous (±50W)

**Expected Log**:
```
[ECO] [INTENT] IMPORT_MODE: Charging/Running normally
[ECO] [INTENT] EXPORT_MODE: Selling power to grid
[ECO] [INTENT] NEUTRAL_HOLD: Waiting for direction clarity
```

### ❌ Bad: No Logs After 6 Hours
**Indicates**:
- Power never moves (stuck at same state)
- Logger not being called
- Script crashed silently
- Threshold tuning needed (50W might be too high)

**Action**: Check logs for errors, verify script loaded

---

## Monitoring Checklist

### Hour 0-1 (Immediate)
- [ ] Script deployed without errors
- [ ] Existing logs (SUM, RAW, FILTERED) still appearing
- [ ] No new errors in error log
- [ ] System responsive

### Hour 1-6 (First Half-Day)
- [ ] At least 1 `[DIRECTION]` log appears (if power changes)
- [ ] At least 1 `[INTENT]` log appears (if mode changes)
- [ ] No log spam (< 5 identical messages per minute)
- [ ] Performance normal

### Hour 6-24 (Second Half-Day)
- [ ] At least 3 `[DIRECTION]` logs total (morning/noon/evening)
- [ ] At least 2 `[INTENT]` logs total
- [ ] Deduplication confirmed (same message max once/min)
- [ ] No system slowdown

### After 24 Hours
- [ ] [ ] Summarize findings
- [ ] [ ] Check SPAM_THRESHOLD_SEC needs adjustment?
- [ ] [ ] Ready to proceed to Phase 2?

---

## Troubleshooting Guide

### Issue: No `[DIRECTION]` logs after 12 hours
**Cause**: Power not crossing ±50W thresholds  
**Check**:
```bash
ssh openhabian@192.168.3.25 "grep 'FILTERED' /var/log/openhab2/openhab.log | tail -5"
```
**Look for**: Power value and current direction  
**Action**: 
- If power stable (same direction): Normal, wait for weather change
- If power swings but no log: Debug threshold logic
- If direction keeps flipping: Deglitch might help

---

### Issue: Too Many Logs (Spam)
**Symptom**: Same message logged 100+ times in 10 minutes  
**Cause**: SPAM_THRESHOLD_SEC too low (60s might be too frequent)  
**Action**: Increase to 300s (5 minutes) if needed
```python
# In 080_Power line 27:
self.SPAM_THRESHOLD_SEC = 300  # Changed from 60
```

---

### Issue: No Logs at All for New Categories
**Symptom**: No `[DIRECTION]` or `[INTENT]` logs appear  
**Cause**: 
1. Script not reloaded
2. Logger class not instantiated
3. State comparison failing silently
4. DEBUG_VERBOSE blocking debug logs

**Check**:
```bash
# Verify script loaded
ssh openhabian@192.168.3.25 "grep 'Script loaded' /var/log/openhab2/openhab.log | grep 080_Power"

# Check for Python errors
ssh openhabian@192.168.3.25 "grep -E 'Traceback|Error in script' /var/log/openhab2/openhab.log"
```

---

### Issue: Logger Errors (AttributeError, KeyError)
**Symptom**: Logs show `AttributeError` or `KeyError` in Logger class  
**Cause**: DateTime import missing or wrong object type  
**Action**: Verify DateTime imported at top of file
```python
from org.joda.time import DateTime
```

---

## Real-Time Monitoring Command (Recommended)

Run this in a terminal to see new logs as they appear:

```bash
ssh openhabian@192.168.3.25 "tail -f /var/log/openhab2/openhab.log" | grep -E "\[ECO\].*\[(DIRECTION|INTENT|WATCHDOG)\]|ERROR|EXCEPTION"
```

**Output will show**:
```
2026-06-21 14:15:23.456 [INFO ] [ECO] [DIRECTION] Power direction: NEUTRAL → IMPORT (285.0 W)
2026-06-21 14:15:24.123 [INFO ] [ECO] [INTENT] IMPORT_MODE: Charging/Running normally
2026-06-21 14:15:25.789 [INFO ] [ECO] SUM raw=285.2 filt=285.0 dir=IMPORT intent=IMPORT_MODE pwr=ON eco=OFF
```

---

## Metrics to Track

| Metric | Baseline | Target | Success |
|--------|----------|--------|---------|
| New log count (24h) | 0 | 5-10 | ✅ if 3+ |
| Log spam rate | 0 | <1x/min | ✅ if dedup works |
| Performance (ms) | <10 | <10 | ✅ if unchanged |
| Errors | 0 | 0 | ✅ if 0 |
| System responsiveness | Good | Good | ✅ if unchanged |

---

## When to Report Findings

### Report Immediately (If Bad)
- Script crashes on load
- Logger causes AttributeError/KeyError
- Logs spam at 100+/min
- System becomes unresponsive

### Report After 1 Hour (Expected)
- Script loaded, existing logs working
- No new errors
- System stable

### Report After 6 Hours (Key Events)
- First direction/intent changes observed
- Deduplication confirmed working
- No unexpected behavior

### Report After 24 Hours (Final)
- Summary of all direction/intent changes
- Any spam issues observed
- Recommendation for Phase 2

---

## Next Steps After Monitoring

### If Successful ✅
- All metrics green
- Direction/intent logs appearing on schedule
- No spam
- **→ Proceed to Phase 2**

### If Issues Found 🔧
- Adjust SPAM_THRESHOLD_SEC if needed
- Fix any errors found
- Re-deploy and re-monitor
- **→ Fix issues, then Phase 2**

### If Unexpected Behavior 🤔
- Check if script reloaded properly
- Verify Logger class instantiated
- Check for state comparison issues
- **→ Debug before proceeding**

---

## Timeline

```
2026-06-21 10:20 ← Deployment complete (now)
2026-06-21 10:25   Hour 0 checkpoint
2026-06-21 15:20   Hour 5 checkpoint
2026-06-21 22:20   Hour 12 checkpoint  ← Key event window (day/night)
2026-06-22 10:20   Hour 24 checkpoint  ← Ready for Phase 2?
```

---

## Documentation

- ✅ Deployment summary: `PHASE1_DEPLOYMENT_COMPLETE_20260621.md`
- ✅ Implementation details: `LOGGING_PHASE1_IMPLEMENTATION_20260621.md`
- ✅ Framework guide: `LOGGING_FRAMEWORK_SUSTAINABLE_20260621.md`
- ✅ Monitoring plan: This file

---

## Quick Reference

**Start Monitoring**:
```bash
ssh openhabian@192.168.3.25 "tail -f /var/log/openhab2/openhab.log" | grep -E "DIRECTION|INTENT|WATCHDOG"
```

**Check Status**:
```bash
ssh openhabian@192.168.3.25 "grep -E '\[DIRECTION\]|\[INTENT\]' /var/log/openhab2/openhab.log | wc -l"
```

**Look for Errors**:
```bash
ssh openhabian@192.168.3.25 "grep -i error /var/log/openhab2/openhab.log | tail -10"
```

---

**Status**: 🟡 MONITORING  
**Next Update**: When direction/intent changes observed or after 24 hours  
**Action**: Monitor and report findings

