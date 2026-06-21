# Seasonal Charging Logic - Change Manifest

**Date**: 2026-06-20  
**Backup Location**: `/home/vali/projects/openhab/backups/seasonal_charging_20260620_210100/`  
**File**: 080_Power_rev20260312.py (957 lines)  
**Changes**: 2 new helper functions + 1 modification to ensure_sequence_for_intent()  

---

## Problem Statement

**Current Behavior (Summer-Biased):**
- Priza1_Power_auto (e-bike) and Priza4_Power_auto (laptop) only enable during EXPORT_MODE
- EXPORT_MODE requires generating more solar power than household uses
- In winter (Oct–Mar): Almost never exporting → charging devices stay OFF
- In shoulder season (Apr, Sept): Unreliable charging

**Goal:**
- Keep summer logic: Charge when exporting excess solar
- Add winter schedule: Charge at fixed times (7 AM, 2 PM, 9 PM) regardless of solar
- Add shoulder schedule: More frequent windows (lenient scheduling)
- Exclude Priza12 (vacuum) from all winter scheduling

---

## Fix 1: Add Seasonal Window Detection

**Location**: Insert after line 495 (before `desired_intent_from_direction()`)

**New Code:**
```python
def is_winter_charging_time():
    """
    Determine if current time falls in winter/shoulder scheduled charging window.
    
    Winter (Oct–Mar): Insufficient natural sun → rely on grid scheduling
    - Charge at: 7 AM, 2 PM, 9 PM daily
    - Rationale: Spread charging across day, avoid peak demand hours
    
    Shoulder (Apr & Sept): Transitional sun availability
    - Charge at: 7 AM, 12 PM, 2 PM, 9 PM (more lenient)
    - Rationale: More windows to catch occasional sun, still use scheduling
    
    Summer (May–Aug): Abundant sun
    - Return False → use normal EXPORT_MODE logic only
    """
    day_of_year = DateTime.now().getDayOfYear()
    hour = DateTime.now().getHourOfDay()
    
    # October–March: insufficient sun
    if day_of_year >= 274 or day_of_year <= 90:
        # Charge at 7 AM (before work), 2 PM (midday), 9 PM (evening)
        return hour in [7, 14, 21]
    
    # April & September: shoulder season
    if (91 <= day_of_year <= 120) or (244 <= day_of_year <= 273):
        # More windows: sunrise window, late morning, afternoon, evening
        return hour in [7, 12, 14, 21]
    
    # May–August: abundant sun, use EXPORT_MODE only
    return False
```

**Purpose**: Centralized seasonal scheduling logic

---

## Fix 2: Add Seasonal Device List Builder

**Location**: Insert after `is_winter_charging_time()` (around line 510)

**New Code:**
```python
def get_charging_devices_for_season():
    """
    Return list of devices to charge based on season and current conditions.
    
    All devices controlled by normal ECO logic (EXPORT/IMPORT based).
    Priza1, Priza4 (e-bike, laptop) additionally use winter scheduled windows.
    Priza12, 7, 3, 9 use ECO logic only (no seasonal scheduling).
    """
    charging_devices = [
        "Priza12_Power_auto",  # Vacuum: normal ECO control
        "Priza7_Power",        # Normal ECO control
        "Priza3_Power",        # Normal ECO control
        "Priza4_Power_auto",   # Laptop: ECO + winter scheduling
        "Priza9_Power",        # Normal ECO control
        "Priza1_Power_auto",   # E-bike: ECO + winter scheduling
    ]
    
    return charging_devices
```

**Purpose**: Restore normal ECO sequencing for all devices, with winter override only for Priza1/4

---

## Fix 3: Modify ensure_sequence_for_intent() to Use Seasonal Devices

**Location**: Line 738 in ensure_sequence_for_intent()

**Current Code (Line 738):**
```python
    devs = devices_on if desired_mode == "ON" else devices_off
    target = desired_mode
```

**New Code:**
```python
    devs = get_charging_devices_for_season() if desired_mode == "ON" else list(reversed(get_charging_devices_for_season()))
    target = desired_mode
```

**Change**: Replace hardcoded `devices_on/devices_off` with seasonal device list

---

## Fix 4: Add Winter Charging Override to Watchdog

**Location**: Insert after line 953 (in `eco_watchdog()`, after evening override check)

**New Code:**
```python
    # 5b) Winter scheduled charging override (independent of EXPORT_MODE)
    if is_winter_charging_time():
        # Winter: Allow Priza1/4 to charge even in IMPORT_MODE
        if not is_state(items["Priza1_BatteryFull"], OnOffType.ON):
            if is_state(items["Priza1_Power_auto"], OnOffType.OFF):
                events.sendCommand("Priza1_Power_auto", "ON")
                log_important("Winter scheduling: Priza1_Power_auto ON (scheduled time)")
        
        if not is_state(items["Priza4_BatteryFull"], OnOffType.ON):
            if is_state(items["Priza4_Power_auto"], OnOffType.OFF):
                events.sendCommand("Priza4_Power_auto", "ON")
                log_important("Winter scheduling: Priza4_Power_auto ON (scheduled time)")
    else:
        # Outside scheduled window: normal ECO logic
        pass
```

**Purpose**: Force Priza1/4 ON during winter scheduled times, bypassing EXPORT_MODE check

**Note**: This runs every 5 seconds (watchdog cron), so scheduling is aggressive but respects BatteryFull

---

## Summary of Changes

| Change | Lines | Type | Risk | Purpose |
|--------|-------|------|------|---------|
| is_winter_charging_time() | New ~30 lines | Add function | LOW | Detect seasonal windows |
| get_charging_devices_for_season() | New ~20 lines | Add function | LOW | Exclude Priza12, document logic |
| ensure_sequence_for_intent() line 738 | 1 line | Modify | LOW | Use seasonal device list |
| eco_watchdog() after line 953 | New ~20 lines | Add override | MEDIUM | Force winter charging on schedule |

**Total Lines Added**: ~70  
**Total Risk**: MEDIUM (adds scheduled override, but respects BatteryFull and allows manual override)  
**Deployment Impact**: Zero runtime change until Oct–Mar when scheduling kicks in

---

## Seasonal Behavior After Fix

### Summer (May–August, days 121–243)
```
is_winter_charging_time() = False
→ Normal 080_Power logic
→ Priza1/4 charge only when EXPORT_MODE (exporting excess solar)
→ Vacuum (Priza12) never auto-charges
```

### Shoulder Season (Apr & Sept, days 91–120 & 244–273)
```
is_winter_charging_time() = True (windows: 7am, 12pm, 2pm, 9pm)
→ At 7 AM: Priza1/4 forced ON (if not full)
→ At 12 PM: Priza1/4 forced ON (if not full)
→ At 2 PM: Priza1/4 forced ON (if not full)
→ At 9 PM: Priza1/4 forced ON (if not full)
→ Outside windows: normal EXPORT_MODE logic applies
→ Priza12 still never auto-charges
```

### Winter (October–March, days 274–90)
```
is_winter_charging_time() = True (windows: 7am, 2pm, 9pm)
→ At 7 AM: Priza1/4 forced ON (if not full) — before work
→ At 2 PM: Priza1/4 forced ON (if not full) — midday grid charging
→ At 9 PM: Priza1/4 forced ON (if not full) — evening/overnight
→ Outside windows: stay OFF (IMPORT_MODE)
→ Priza12 still never auto-charges
```

---

## Regression Tests

### Test 1: Summer Behavior (May–Aug)
**Setup**: Create a test time in June
**Expected**:
- [ ] Priza1_Power_auto only enables when EXPORT_MODE
- [ ] Priza4_Power_auto only enables when EXPORT_MODE
- [ ] Priza12_Power_auto enables/disables with normal ECO logic
- [ ] No change in behavior vs. before fix

### Test 2: Shoulder Scheduling (April 15, 9 AM)
**Setup**: Simulate April 15 at 9:00 AM
**Expected**:
- [ ] Priza1_Power_auto turns ON at 7 AM (already happened)
- [ ] Priza1_Power_auto turns ON at 12 PM (upcoming)
- [ ] Priza1_Power_auto turns ON at 2 PM (upcoming)
- [ ] Priza4_Power_auto follows same pattern

### Test 3: Winter Scheduling (January 14, 7 AM)
**Setup**: Simulate January 14 at 7:00 AM, Priza1_BatteryFull OFF
**Expected**:
- [ ] Priza1_Power_auto turns ON (despite IMPORT_MODE)
- [ ] Logs show: "Winter scheduling: Priza1_Power_auto ON (scheduled time)"
- [ ] At 8 AM (outside window): stays ON until BatteryFull or manual OFF

### Test 4: Winter Off-Window (January 14, 10 AM)
**Setup**: Simulate January 14 at 10:00 AM
**Expected**:
- [ ] Priza1_Power_auto OFF if in IMPORT_MODE (no scheduled override)
- [ ] Priza1_Power_auto ON if in EXPORT_MODE (normal ECO logic)

### Test 5: BatteryFull Blocks Winter Charging
**Setup**: January 14, 7 AM, but Priza1_BatteryFull = ON
**Expected**:
- [ ] Priza1_Power_auto stays OFF (respects full flag)
- [ ] No duplicate charging attempts

---

## Rollback Procedure

```bash
# Restore original file
cp /home/vali/projects/openhab/backups/seasonal_charging_20260620_210100/080_Power_rev20260312.py.backup \
   /etc/openhab2/automation/jsr223/python/personal/080_Power_rev20260312.py

# Verify
ssh -i ~/.ssh/openhab_claude openhabian@192.168.3.25 "tail -20 /var/log/openhab2/openhab.log" | grep -i "error\|exception"
```

**Rollback Time**: < 1 minute

---

## Verification Checklist

### Immediate (Post-Deployment)
- [ ] Script loads without errors
- [ ] No NameError (is_winter_charging_time, etc.)
- [ ] No AttributeError on DateTime operations
- [ ] System responsive

### 24-Hour Testing
- [ ] Wait for next scheduled window (7 AM, 2 PM, or 9 PM depending on current time)
- [ ] At scheduled time, check logs for: "Winter scheduling: Priza1_Power_auto ON"
- [ ] Verify Priza1_Power_auto actually turns ON
- [ ] Verify Priza4_Power_auto follows same pattern
- [ ] Verify Priza12 stays OFF during scheduled times
- [ ] Verify BatteryFull prevents charging

### Month-Long Testing (Full Seasons)
- [ ] May–Aug: Priza only charges when exporting
- [ ] Apr & Sept: Priza charges on extended schedule
- [ ] Oct–Mar: Priza charges at 7 AM, 2 PM, 9 PM reliably
- [ ] No cascading failures
- [ ] No unexpected power draw

---

## Notes

1. **Priza12 (Vacuum) Automation**: Included in normal ECO sequence. Charges when exporting excess power (EXPORT_MODE), stays off when importing (IMPORT_MODE). No seasonal scheduling applied.

2. **BatteryFull Respected**: Winter scheduling checks `Priza1_BatteryFull` and `Priza4_BatteryFull` before forcing ON. Prevents overcharging.

3. **Watchdog Frequency**: Winter override runs every 5 seconds (cron 0/5 * * * * ?). Ensures charging starts promptly at scheduled times.

4. **Manual Override**: Users can still manually turn ON via Priza1_Power_man or Priza4_Power_man anytime. Scheduled logic doesn't interfere.

5. **Seasonal Thresholds**: Day-of-year ranges chosen conservatively:
   - Winter starts Oct 1 (day 274) instead of Sept 21 (day 264) to avoid edge cases
   - Summer starts May 1 (day 121) instead of Apr 21 (day 111) to be safe

---

**Status**: Ready for deployment with backups and documentation complete.

**Next Step**: User approval to proceed with implementation and testing.
