# OpenHAB Rules Audit - 2026-06-25

## Overview
Checked DSL Rules files (`.rules`) in `/etc/openhab2/rules/`

---

## Rules Files Found

| File | Size | Status | Last Modified |
|------|------|--------|----------------|
| startup.rules | 1.6K | ✅ OK | 2025-05-24 |
| TOD.rules | 2.9K | ✅ OK | 2024-12-01 |
| rhasspy.rules | 1.1K | ⚠️ BUG | 2021-11-04 |
| rhasspy.rules.nok | (backup) | ⚠️ BUG | 2021-11-04 |
| Scheduled.rule | 1.6K | ❓ OLD | 2021-02-23 |
| Seasons.rule | 639B | ❓ OLD | 2022-01-11 |
| Switches.rule | 77B | ❓ EMPTY | 2025-05-23 |
| TOD.rules1 | 2.8K | ❓ BACKUP | 2021-10-23 |
| TOD.rules3 | 3.0K | ❓ BACKUP | 2025-02-19 |

---

## Detailed Findings

### ✅ GOOD: startup.rules
- **Purpose:** Reset devices to safe state on OpenHAB startup
- **Syntax:** Valid DSL Rules
- **Status:** Working correctly
- **Lines:** 61
- **Devices controlled:** 20+ items (PIR sensors, presence, lights, media players, outlets)

### ✅ GOOD: TOD.rules
- **Purpose:** Calculate time of day (Morning, Day, Afternoon, Evening, Night, Bed)
- **Triggers:** Sunrise/sunset changes, cron jobs, system start
- **Syntax:** Valid DSL Rules with Joda DateTime
- **Status:** Working correctly
- **Features:** Dual time-of-day calculation (primary + kids schedule)

### ⚠️ BUG: rhasspy.rules
- **Purpose:** Handle Rhasspy voice intent commands
- **Issue:** Line 24 has a critical bug

**Problematic code:**
```
var String rhasspyIntent = transform("JSONPATH", "$..intentName", json)
...
rhasspyIntent.sendCommand(rhasspySlot1Value)  // ← LINE 24: BUG!
```

**Problem:** 
- `rhasspyIntent` is a String variable (not an Item)
- Calling `.sendCommand()` on a String is invalid
- This will cause a runtime error when rule executes

**Impact:**
- Rule will fail silently if rhasspy_intent_lights ever changes
- No voice commands from Rhasspy will work
- No errors logged (unless loglevel changed)

**Fix:** 
Need to send command to an actual Item, not a String variable:
```
// WRONG (current):
rhasspyIntent.sendCommand(rhasspySlot1Value)

// CORRECT (one option):
var Item targetItem = ir.getItem(rhasspySlot1Value)
targetItem.sendCommand("ON")  // or appropriate state

// OR: Use Home Assistant bridge + MQTT instead
```

### ⚠️ BUG: rhasspy.rules.nok
- Backup version with same bug as above
- File extension `.nok` suggests it's known broken
- Should be deleted or fixed

### ❓ OLD/UNUSED: Scheduled.rule, Seasons.rule
- Syntax appears valid but haven't been updated since 2021-2022
- Likely superseded by Python automation scripts
- Low risk (if not triggered, they won't cause problems)

### ❓ BACKUP: TOD.rules1, TOD.rules3
- Multiple versions suggest evolution of the rule
- TOD.rules3 is newest (2025-02-19)
- Could be cleaned up (keep only active version)

### ❓ EMPTY: Switches.rule
- Only 77 bytes (likely empty or minimal)
- Should be reviewed or removed

---

## Logs Check

**No recent errors found in OpenHAB logs:**
- No `rhasspy` rule execution errors
- No `sendCommand` failures
- No Rules parsing errors

**Possible reasons:**
1. Rhasspy is not actively used (rhasspy_intent_lights never receives updates)
2. Errors are silently swallowed
3. Rules file is disabled or not loaded

---

## Recommendations

### Priority 1: Fix or Disable rhasspy.rules
**Option A: Delete (if Rhasspy not used)**
```bash
rm /etc/openhab2/rules/rhasspy.rules
rm /etc/openhab2/rules/rhasspy.rules.nok
```

**Option B: Fix (if Rhasspy is needed)**
```
# Get item name from JSON, use HomeAssistant bridge, or refactor
# Current DSL Rules don't support dynamic Item references well
# Consider using Python script instead (like other automations)
```

### Priority 2: Clean Up Backup Files
```bash
rm /etc/openhab2/rules/TOD.rules1    # Keep only TOD.rules (active)
rm /etc/openhab2/rules/TOD.rules3    # If TOD.rules3 is newer, rename to TOD.rules
rm /etc/openhab2/rules/Switches.rule # Empty file, no purpose
```

### Priority 3: Review Old Rules
```bash
# Check if these are still needed or superseded by Python scripts:
ls -la /etc/openhab2/rules/Scheduled.rule /etc/openhab2/rules/Seasons.rule
# Decide: keep, fix, or delete
```

### Priority 4: Consolidate to Python
The system is already heavily using Python automation scripts. Consider:
- Moving DSL Rules logic to Python (more flexible, easier to debug)
- Retiring old DSL Rules that are no longer maintained
- This would centralize automation logic in one place

---

## Files Status Summary

```
✅ 2 Good   — startup.rules, TOD.rules
⚠️  2 Buggy  — rhasspy.rules, rhasspy.rules.nok
❓ 4 Old    — Scheduled.rule, Seasons.rule, TOD.rules1, TOD.rules3, Switches.rule
```

**Overall:** Most Rules are working fine. Single bug in rhasspy (low risk if unused).

---

## Next Steps

1. **Determine if Rhasspy is used** — Check if anyone uses voice commands
2. **Choose action:** Delete or fix rhasspy.rules
3. **Clean up backups** — Remove TOD.rules1/3 redundancy
4. **Review old rules** — Scheduled.rule, Seasons.rule still needed?

Let me know if you'd like me to:
- Fix the rhasspy.rules bug
- Delete unused Rules files
- Port any rules to Python
