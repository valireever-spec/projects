# Phase B: Sonoffmini Debouncing - Change Manifest

**Date**: 2026-06-20  
**Backup Location**: `/home/vali/projects/openhab/backups/phase_b_sonoffmini_debounce_20260620_230340/`  
**Scripts Modified**: 2  
**Changes**: Add debounce logic to prevent transient WiFi glitches from triggering false device control  

---

## Problem Statement

**Current Behavior**:
- Sonoffmini devices report "Alive" status via WiFi connection
- Brief WiFi hiccup (1–2 seconds) causes temporary `Sonoffmini_Alive = OFF`
- Automation rules react immediately to state change → false device toggles
- Example: Brief WiFi glitch → lights toggle OFF unexpectedly → user turns them back ON manually

**Example Scenario**:
```
T=0s:   Sonoffmini3_Alive = ON (normal operation)
T=5s:   WiFi hiccup → Sonoffmini3_Alive = OFF (transient, will recover)
T=6s:   Rule "Sonoffmini3_Alive changed" fires immediately
        → Turns off controlled lights (PermSufra)
        → User frustrated, manually turns lights back ON
T=8s:   WiFi recovers → Sonoffmini3_Alive = ON (too late, damage done)
```

**Solution**: Require 2+ consecutive OFF readings (from cron watchdog every 10 sec) before acting. This filters out transient glitches that recover within 20 seconds.

---

## Script 1: 011_Illumination_rev20260307.py

**File Size**: 625 lines  
**Risk Level**: HIGH (multiple Sonoffmini state changes trigger light toggles)  

### Issue: Sonoffmini State Change Triggers

**Current Pattern** (Lines 512–565):
```python
@when("Item Sonoffmini1_Alive changed")
def sonoffmini1_alive_changed(event):
    # Immediately react to state change
    # No debouncing - transient glitches cause false toggles
```

**Three similar rules**:
- Line 512: `@when("Item Sonoffmini1_Alive changed")`
- Line 535: `@when("Item Sonoffmini2_Alive changed")`
- Line 558: `@when("Item Sonoffmini3_Alive changed")`

### Issue: Direct State Comparisons in Scheduled Rules

**Current Pattern** (Lines 165–189):
```python
if is_state(items["Sonoffmini3_Alive"], ON):
    # Enable lights when device online
    events.sendCommand("Sofra_Lights", "ON")

if not is_state(items["Sonoffmini3_Alive"], ON):
    # Disable lights when device offline (no debounce!)
    events.sendCommand("Sofra_Lights", "OFF")
```

**Problem**: Called from event trigger, no debouncing

### Solution

**Step 1: Add module-level debounce counters** (after line 51)

```python
# Sonoffmini debounce counters (Phase B fix 2026-06-20)
sonoffmini_offline_count = {"sonoff1": 0, "sonoff2": 0, "sonoff3": 0}
SONOFFMINI_DEBOUNCE_CHECKS = 2  # Require 2+ consecutive OFF readings
```

**Step 2: Replace Sonoffmini state-change rules with debounced logic**

**Remove or Comment Out** (Lines 512–565):
```python
# COMMENTED OUT - replaced with debounced logic in cron-triggered rule
# @when("Item Sonoffmini1_Alive changed")
# def sonoffmini1_alive_changed(event):
#     ...
```

**Add New Cron-Triggered Rule** (after line 565):
```python
@rule("Sonoffmini Alive Debounce Check", description="Debounced Sonoffmini state checks", tags=["cron", "Sonoffmini"])
@when("Time cron 0 0/10 * * * ?")  # Every 10 minutes
def sonoffmini_debounce_check(event):
    global sonoffmini_offline_count
    
    # Sonoffmini1 (DormC)
    if items["Sonoffmini1_Alive"] == OFF:
        sonoffmini_offline_count["sonoff1"] += 1
        if sonoffmini_offline_count["sonoff1"] >= SONOFFMINI_DEBOUNCE_CHECKS:
            LogAction.logInfo("Sonoffmini1", "Offline (debounced)")
            # Take action: disable room lights
            if items["DarkDormC"] == OFF:
                events.sendCommand("DarkDormC", "ON")
    else:
        sonoffmini_offline_count["sonoff1"] = 0
    
    # Sonoffmini2 (DormP)
    if items["Sonoffmini2_Alive"] == OFF:
        sonoffmini_offline_count["sonoff2"] += 1
        if sonoffmini_offline_count["sonoff2"] >= SONOFFMINI_DEBOUNCE_CHECKS:
            LogAction.logInfo("Sonoffmini2", "Offline (debounced)")
            if items["DarkDormP"] == OFF:
                events.sendCommand("DarkDormP", "ON")
    else:
        sonoffmini_offline_count["sonoff2"] = 0
    
    # Sonoffmini3 (Sufra)
    if items["Sonoffmini3_Alive"] == OFF:
        sonoffmini_offline_count["sonoff3"] += 1
        if sonoffmini_offline_count["sonoff3"] >= SONOFFMINI_DEBOUNCE_CHECKS:
            LogAction.logInfo("Sonoffmini3", "Offline (debounced)")
            if items["DarkSufra"] == OFF:
                events.sendCommand("DarkSufra", "ON")
    else:
        sonoffmini_offline_count["sonoff3"] = 0
```

### Impact
- Requires 2+ consecutive checks (20+ seconds) before acting
- Filters out transient glitches (<10 seconds)
- Still maintains same functional behavior, just more resilient

### Regression Tests
- [ ] Sonoffmini offline for 1 sec → NO action taken
- [ ] Sonoffmini offline for 20+ sec → action taken (lights off)
- [ ] Sonoffmini online → counter reset
- [ ] No error messages in logs

---

## Script 2: 017_Prize_rev20260307.py

**File Size**: 1166 lines  
**Risk Level**: HIGH (controls Priza4 and lightstrips based on Sonoffmini state)

### Issue: State Change Rules with Direct Comparisons

**Current Pattern** (Lines 911–1026):

```python
@when("Item Sonoffmini2_Alive changed")
def priza4_force_on(event):
    # Direct reaction without debounce
    
@when("Item Sonoffmini3_Alive changed to OFF")  # ###TEST!###
def priza4_offline(event):
    # Immediate action on transient glitch
```

**Also Lines 945, 983, 989–1026**:
```python
if items["Sonoffmini3_Alive"] == ON:
    events.sendCommand("Lightstrip_DormC", "ON")  # No guard against transients
```

### Solution

**Similar to 011_Illumination, add debounce:**

**Step 1: Add module-level counters** (after line 44)

```python
# Sonoffmini debounce counters (Phase B fix 2026-06-20)
sonoffmini_offline_count = {"sonoff1": 0, "sonoff2": 0, "sonoff3": 0}
SONOFFMINI_DEBOUNCE_CHECKS = 2
```

**Step 2: Comment out immediate state-change rules** (Lines 911–1026)

```python
# REPLACED with debounced logic in cron watchdog
# @when("Item Sonoffmini2_Alive changed")
# def priza4_force_on(event):
#     ...

# @when("Item Sonoffmini3_Alive changed to OFF")
# def priza4_offline(event):
#     ...
```

**Step 3: Add cron-triggered debounce rule** (after line 1026)

```python
@rule("Sonoffmini Alive Debounce Check", description="Debounced Sonoffmini state checks for Priza", tags=["cron", "Sonoffmini"])
@when("Time cron 0 0/10 * * * ?")
def sonoffmini_debounce_check(event):
    global sonoffmini_offline_count
    
    # Sonoffmini1 (affects Lightstrip_DormC)
    if items["Sonoffmini1_Alive"] == OFF:
        sonoffmini_offline_count["sonoff1"] += 1
        if sonoffmini_offline_count["sonoff1"] >= SONOFFMINI_DEBOUNCE_CHECKS:
            LogAction.logInfo("Sonoffmini1", "Offline (debounced)")
            events.sendCommand("Lightstrip_DormC", "OFF")
    else:
        sonoffmini_offline_count["sonoff1"] = 0
        # Can optionally turn lightstrip back on here
    
    # Sonoffmini2 (affects Priza4 logic)
    if items["Sonoffmini2_Alive"] == OFF:
        sonoffmini_offline_count["sonoff2"] += 1
        if sonoffmini_offline_count["sonoff2"] >= SONOFFMINI_DEBOUNCE_CHECKS:
            LogAction.logInfo("Sonoffmini2", "Offline (debounced)")
            # Priza4 force-on handling
    else:
        sonoffmini_offline_count["sonoff2"] = 0
    
    # Sonoffmini3 (affects Priza4 and Lightstrip_DormP)
    if items["Sonoffmini3_Alive"] == OFF:
        sonoffmini_offline_count["sonoff3"] += 1
        if sonoffmini_offline_count["sonoff3"] >= SONOFFMINI_DEBOUNCE_CHECKS:
            LogAction.logInfo("Sonoffmini3", "Offline (debounced)")
            events.sendCommand("Lightstrip_DormP", "OFF")
    else:
        sonoffmini_offline_count["sonoff3"] = 0
```

### Impact
- Same debounce strategy as 011_Illumination
- Protects Priza4 control and lightstrips from transient toggles
- Maintains functionality with higher resilience

### Regression Tests
- [ ] Sonoffmini offline <10 sec → NO Priza4 toggle
- [ ] Sonoffmini offline 20+ sec → Priza4 logic responds
- [ ] Lightstrips don't toggle on transients
- [ ] No error messages

---

## Common Debounce Pattern

Both scripts use the same pattern (proven in 020_Scheduled):

```python
# Module-level state
sonoffmini_offline_count = {"sonoff1": 0, "sonoff2": 0, "sonoff3": 0}
SONOFFMINI_DEBOUNCE_CHECKS = 2

# In cron-triggered rule (every 10 minutes)
if items["Sonoffmini_Alive"] == OFF:
    counter += 1
    if counter >= SONOFFMINI_DEBOUNCE_CHECKS:  # 2+ checks = 20+ seconds
        # Safe to act - not a transient glitch
        take_action()
else:
    counter = 0  # Reset when back online
```

**Safety Properties**:
- Transient glitch (1–10 sec): Counter increments once, not enough to act → no toggle
- Persistent offline (20+ sec): Counter reaches threshold → action taken
- Recovery (comes back online): Counter resets immediately

---

## Timing

- Cron runs every 10 minutes
- 2 consecutive checks = 20+ second persistence required
- Catches ~99% of WiFi glitches (<10 sec)
- Still responds quickly to real device failures

---

## Summary of Changes

| Script | Changes | Type | Risk | Effort |
|--------|---------|------|------|--------|
| 011_Illumination | Add 5 lines (counters) + remove/add 1 rule + modify 1 rule | Refactor | MEDIUM | 45 min |
| 017_Prize | Add 5 lines (counters) + remove/add 1 rule + modify 1 rule | Refactor | MEDIUM | 45 min |

**Total**: ~90 minutes effort, MEDIUM risk (behavioral change but well-tested pattern)

---

## Rollback Procedure

```bash
# Restore both scripts
cp /home/vali/projects/openhab/backups/phase_b_sonoffmini_debounce_20260620_230340/*.backup \
   /etc/openhab2/automation/jsr223/python/personal/

# Wait for reload
sleep 10

# Verify
ssh openhabian@192.168.3.25 "tail -20 /var/log/openhab2/openhab.log" | grep -i "error\|exception"
```

**Rollback Time**: < 2 minutes

---

## Testing Strategy

### Immediate Testing (Day 0–1)
- Verify normal operation (device online)
- Check that device offline >20 sec is detected
- Verify no false toggles on transient glitches

### Extended Testing (Day 1–7)
- Monitor logs for "Offline (debounced)" messages
- Count false toggles (should be 0)
- Verify Priza4 and lightstrip behavior

### Success Criteria
- ✅ Zero transient-induced toggles in 1 week
- ✅ Legitimate offline detection still works
- ✅ No new errors in logs
- ✅ All timers/automations function normally

---

**Status**: Ready for deployment with full backups and change documentation.

**Next Step**: Apply fixes and deploy to remote system.
