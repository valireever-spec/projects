# Priza1_BatteryFull Daily Safety Reset — Implementation

**Date:** 2026-06-24  
**Issue:** Priza1_BatteryFull stuck ON, blocking auto charging  
**Solution:** Daily auto-reset at 05:00 AM  
**Status:** ✓ DEPLOYED

---

## Problem Summary

Priza1_BatteryFull can get stuck in ON state, creating a circular dependency:

```
Priza1_BatteryFull = ON (stuck)
    ↓ BLOCKS
Auto charging (is_device_allowed returns False)
    ↓ PREVENTS
Socket turn-on (Priza1_Power stays OFF)
    ↓ PREVENTS
Flag reset (only resets when Priza1_Power turns ON in 019_Charge_curve.py)
    ↓ LOOP BACK TO STEP 1
```

**Result:** Charging never starts, flag never resets, wasted solar windows.

---

## Solution: Daily 05:00 AM Reset

Added new rule in `020_Scheduled_rev20260307.py`:

```python
@rule("Daily reset Priza1_BatteryFull", ...)
@when("Time cron 0 0 5 * * ? *")
def reset_priza1_battery_full(event):
    """Daily safety reset at 05:00 AM"""
    if items["Priza1_BatteryFull"] == "ON":
        events.sendCommand("Priza1_BatteryFull", "OFF")
```

### Why 05:00 AM?

- **Early enough:** Resets flag well before any charging windows
- **Winter:** Clears flag before first scheduled window (07:00)
- **Summer:** Clears flag before daily EXPORT periods (typically morning after sunrise ~06:00)
- **Late enough:** Gives midnight rule time to complete (midnight + 5 hours buffer)

### Timing Diagram

```
00:00 ─────→ Midnight: Stop socket, clear flag
        ↓
05:00 ─────→ Daily Reset: Safety check, ensure flag is OFF
        ↓
07:00 ─────→ Winter window (if in season): Can now trigger charging
        ↓
06:00-18:00 ─→ Summer EXPORT windows: Can now trigger charging
        ↓
12:00 ─────→ Noon: Stop socket
        ↓
21:00 ─────→ Winter window (if in season): Can trigger charging
        ↓
(next day 00:00)
```

---

## How It Breaks the Circular Dependency

**Before:**
1. Flag stuck ON
2. Auto charging blocked forever
3. Socket never turns ON
4. Flag never resets
5. Stuck forever ✗

**After:**
1. Flag stuck ON
2. Auto charging blocked
3. **05:00 AM:** Daily reset fires → flag forced OFF
4. Auto charging now possible
5. Next EXPORT/scheduled window → socket turns ON
6. Socket turn-on → flag reset happens normally
7. System recovers ✓

---

## Implementation Details

**File:** `020_Scheduled_rev20260307.py`  
**Location:** After `start_prize()` rule  
**Trigger:** Daily at 05:00 AM (`0 0 5 * * ? *` CRON)  
**Action:** Reset Priza1_BatteryFull to OFF if stuck ON  
**Logging:** Info message to track resets

### Behavior

| Condition | Action | Log |
|-----------|--------|-----|
| Flag ON at 05:00 | Reset to OFF | "Daily safety reset: Priza1_BatteryFull OFF" |
| Flag OFF at 05:00 | No change | "already OFF at 05:00 (normal)" |
| Flag UNDEF/NULL | No change | Not logged (normal state) |

---

## Deployment Log

✓ **2026-06-24 19:19:**
- Deployed `020_Scheduled_rev20260307.py` to remote
- Script loaded successfully: `Loading script 'python/personal/020_Scheduled_rev20260307.py'`
- No errors in OpenHAB logs

✓ **2026-06-24 19:20:**
- Committed to git: `bebaedfd`
- Documentation complete

---

## Testing & Monitoring

### How to Verify It Works

1. **Manual trigger test** (optional, before 05:00 AM):
   ```bash
   # Set flag to ON manually
   curl -X PUT http://localhost:8080/rest/items/Priza1_BatteryFull/state \
     -H 'Content-Type: text/plain' -d 'ON'
   
   # Wait until 05:00 (or trigger the rule directly in OH UI)
   # Check logs for reset message
   grep "Daily safety reset" /var/log/openhab2/openhab.log
   ```

2. **Monitor daily resets**:
   ```bash
   # Watch for daily reset log entries
   tail -f /var/log/openhab2/openhab.log | grep "Daily reset\|already OFF"
   ```

3. **Verify summer charging works**:
   ```bash
   # Monitor next EXPORT window (after 05:00)
   tail -f /var/log/openhab2/openhab.log | grep "EXPORT\|Priza1_Power_auto"
   ```

### Expected Logs (Daily at 05:00)

```
2026-06-25 05:00:00.XXX [INFO] [SCHEDULE] Priza1_BatteryFull daily reset at 05:00
2026-06-25 05:00:00.YYY [INFO] [Priza1] Daily safety reset: Priza1_BatteryFull OFF (05:00)
```

---

## Prevention: Why This Won't Happen Again

**Previous situation:**
- No daily reset → flag could stay stuck indefinitely
- Wasted EXPORT windows
- No visibility into problem (no logs)

**New situation:**
- Daily 05:00 reset ensures flag can't stay stuck >1 day
- Visible logging (reset attempts tracked)
- Charging can always proceed from next morning
- Complements existing midnight reset (defense in depth)

---

## Related Fixes

This daily reset works alongside earlier Priza charging fixes:

1. **Priza1ForceOn initialization (June 24):** Initializes ForceOn to OFF on startup
2. **Current detection threshold (June 24):** Changed from exact `== 0.0 A` to `<= 0.05 A`
3. **BatteryFull daily reset (June 24):** Prevents flag from staying stuck

Together, these fixes ensure robust automatic charging in all seasons.

---

## Fallback & Rollback

**If issues occur:**
- Rule is safe to disable (just stops the 05:00 reset)
- Doesn't break anything else (independent rule)
- Can be rolled back by reverting to previous `020_Scheduled_rev20260307.py`

**Command to temporarily disable** (if needed):
```bash
# Comment out the rule in 020_Scheduled_rev20260307.py
# Then reload the script via OpenHAB UI
```

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
