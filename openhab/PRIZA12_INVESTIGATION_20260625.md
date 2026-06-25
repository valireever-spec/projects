# Priza12 Investigation Report - 2026-06-25

## Summary
**Priza12 is referenced in automation but NOT configured as a device.**

---

## Finding 1: Device Not Configured
Priza12 does NOT exist as an MQTT Thing in OpenHAB.

**Configured Priza devices:**
```
✅ Priza1 (ONLINE)
✅ Priza2 (ONLINE)
✅ Priza3 (ONLINE)
✅ Priza4 (ONLINE)
✅ Priza5 (ONLINE)
✅ Priza6 (ONLINE)
✅ Priza7 (ONLINE)
✅ Priza8 (ONLINE)
✅ Priza9 (ONLINE)
❌ Priza12 (NOT CONFIGURED)
```

**Verification:**
```bash
curl -s 'http://localhost:8080/rest/things' | jq '.[] | select(.label | startswith("Priza"))'
# Returns Priza1-9, but NOT Priza12
```

---

## Finding 2: Items Exist But Have No Data
Items for Priza12 exist in OpenHAB but are all NULL (never updated):

| Item | Type | State | LastUpdate |
|------|------|-------|-----------|
| Priza12_Power_auto | Switch | NULL | null |
| Priza12_Power | Switch | NULL | null |
| Priza12_TelePeriod | Number | NULL | null |

**These items were never initialized because there's no device feeding data to them.**

---

## Finding 3: Referenced in Automation
Priza12_Power_auto IS referenced in the ECO automation logic:

**File:** `080_Power_rev20260312.py`
- **Line 133:** Listed in `devices_on` array (charging sequence)
- **Line 615:** Listed in `get_charging_devices_for_season()` (charging device list)
- **Comment:** "vacuum" (suggests it's a vacuum cleaner or similar)

**Problem:** The automation tries to control a device that doesn't exist.

---

## Root Causes

### Option A: Priza12 Was Never Added
- Device was referenced in automation but never configured
- Someone wrote the automation expecting a Priza12 device that was never set up
- Likely a vacuum cleaner or smart outlet that was planned but not implemented

### Option B: Priza12 Was Decommissioned
- Device existed previously but was removed/decommissioned
- Automation script was not updated to remove the reference
- Items are orphaned (no Thing to feed them data)

### Option C: Priza12 Hardware Died
- Device was configured but hardware failed
- Device does not reconnect to WiFi
- Items show NULL state (not receiving updates)
- **But:** No corresponding Thing would exist in API (contradicts this)

---

## Impact Analysis

### Current Behavior
1. **Automation tries to control Priza12:**
   - Line 816 in 080_Power: `events.sendCommand("Priza12_Power_auto", "ON")`
   - Gets NULL state, command likely silently ignored

2. **Error Handling:**
   - Line 816-817 checks: `if items[dev] not in [NULL, UNDEF]`
   - Since Priza12_Power_auto = NULL, condition is False
   - Device is skipped (no command sent, no error logged)

3. **Safety Impact:**
   - ✅ No harm done (invalid commands are ignored)
   - ⚠️ Charging sequence spends time checking a non-existent device
   - ⚠️ Priza12 never activates (obviously, since it doesn't exist)

### Consequences
- **Charging delays:** ECO sequence spends ~3 seconds per device step (line 822)
- **Missing capacity:** If Priza12 is supposed to absorb surplus, it doesn't
- **Confusion:** Logs might show Priza12 skipped ("Skip Priza12 (no device)")

---

## Solution Options

### Option 1: Add Priza12 Device (Recommended if needed)
If Priza12 is supposed to exist:

1. **Identify the hardware:**
   - What device is supposed to be Priza12? (vacuum, outlet, etc.)
   - What's its IP/MAC address?
   - Is it powered on?

2. **Configure in OpenHAB:**
   - Add MQTT Thing to home.things or via UI
   - Create items for Priza12_Power_auto, Priza12_Power, Priza12_TelePeriod
   - Verify MQTT connection (check Home Assistant or MQTT broker)

3. **Verify:**
   - Device should appear in REST API as ONLINE
   - Items should have non-NULL states

### Option 2: Remove from Automation (Recommended if not needed)
If Priza12 is no longer used:

1. **Remove from 080_Power_rev20260312.py:**
   - Line 133: Remove "Priza12_Power_auto" from `devices_on`
   - Line 615: Remove from `get_charging_devices_for_season()`

2. **Benefit:**
   - Faster charging sequences (3 seconds saved per activation)
   - Cleaner automation logs
   - No confusion about missing devices

3. **Change:**
   ```python
   # Before
   devices_on = [
       "Priza12_Power_auto",  # ← Remove this line
       "Priza7_Power",
       ...
   ]
   
   # After
   devices_on = [
       "Priza7_Power",
       ...
   ]
   ```

### Option 3: Mark as Disabled (If Temporarily Offline)
If Priza12 hardware is temporarily unavailable:

1. **Keep in config but add guard:**
   ```python
   def is_device_allowed(dev, target):
       if dev == "Priza12_Power_auto":
           return False  # Disabled until reconnected
       ...
   ```

2. **Benefit:**
   - Easy to re-enable later
   - Clear intent in code

---

## Recommendation

**Choose based on your setup:**

1. **You still have the Priza12 device hardware:**
   → Use **Option 1** (Add/configure it)

2. **You don't need/have Priza12:**
   → Use **Option 2** (Remove from automation)

3. **Priza12 is temporarily offline:**
   → Use **Option 3** (Add disabled guard)

---

## Next Steps
1. Identify what Priza12 was supposed to be (check commit history, old configs, or memory)
2. Choose an option above
3. Implement and test

Let me know what you'd like to do!
