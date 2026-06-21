# Comprehensive Logging Improvements - Master Changelog
**Date**: 2026-06-21  
**Scope**: Add logging to 5 critical automation scripts  
**Backup**: `/home/vali/projects/openhab/backups/comprehensive_logging_20260621/`  
**Status**: ✅ BACKUP COMPLETE - Ready for implementation

---

## Overview

Adding structured logging to 5 critical scripts that currently have zero or minimal logging visibility. These scripts control:
- ECO power management
- Battery charging
- Charging curves
- Scheduled device control  
- Switch logic coordination

---

## Script 1: 080_Power_rev20260312.py (1026 lines)

**Current Logging**: 0 entries  
**Priority**: 🔴 CRITICAL  
**Impact**: Most critical automation - ECO mode, power thresholds

### Logging Additions (12 locations):

| Line | Location | What to Log | Type |
|------|----------|------------|------|
| 941 | `eco_watchdog()` entry | "ECO watchdog tick: power={} W, direction={}" | INFO |
| 478 | `classify_direction()` | "Power direction classified: IMPORT/EXPORT/NEUTRAL" | DEBUG |
| 546 | `update_intent()` | "Intent change: {} → {}" | INFO |
| 539 | `desired_intent_from_direction()` | "Desired intent from {}: {}" | DEBUG |
| 709 | `run_sequence()` start | "Sequence START: target={}, devices=[...]" | INFO |
| 664 | `stop_sequence()` | "Sequence STOP (reason)" | INFO |
| 499 | `is_winter_charging_time()` | "Winter charging window active: [start]-[end]" | INFO |
| 524 | `get_charging_devices_for_season()` | "Seasonal devices: [list]" | DEBUG |
| 835 | `apply_intent()` EXPORT | "EXPORT_MODE: disabling non-critical devices" | INFO |
| 835 | `apply_intent()` IMPORT | "IMPORT_MODE: normal charging allowed" | INFO |
| 249 | `send_eco_if_needed()` | "ECO command sent: {}" | DEBUG |
| 625 | Power threshold | "Power threshold breach: {} W > {} W" | INFO |

### Implementation Strategy:
- Use existing `log_important()` and `log_debug()` functions
- Add 12 strategic log points
- Estimated changes: 12 lines of code
- Estimated effort: 1.5 hours

---

## Script 2: 017_Prize_rev20260307.py (1206 lines)

**Current Logging**: 0 entries  
**Priority**: 🔴 CRITICAL  
**Impact**: Priza battery charging, BatteryFull flags

### Logging Additions (10 locations):

| Line | Location | What to Log | Type |
|------|----------|------------|------|
| ~340 | Taper detection | "Priza{} taper detected: {} A → {} A" | INFO |
| ~366 | Battery full | "Priza{} battery FULL detected" | INFO |
| ~384 | BatteryFull flag | "Priza{}_BatteryFull set to {}" | DEBUG |
| ~420 | Power cycling | "Priza{} power cycling for charge" | DEBUG |
| ~550 | Debounce trigger | "Debounce: {} checks before action" | DEBUG |
| ~650 | State change | "Priza{} state: {} → {}" | INFO |
| ~750 | Charging start | "Priza{} charging STARTED" | INFO |
| ~800 | Charging stop | "Priza{} charging STOPPED" | INFO |
| ~900 | Force on/off | "Priza{} force command: {}" | DEBUG |
| ~1000 | Daily reset | "Priza status reset for new day" | INFO |

### Implementation Strategy:
- Add module-level logger: `log = logging.getLogger("priza")`
- Add 10 strategic log points
- Estimated changes: 12 lines of code + logger setup
- Estimated effort: 1.5 hours

---

## Script 3: 019_Charge_curve_rev20260307.py (277 lines)

**Current Logging**: 0 entries  
**Priority**: 🔴 CRITICAL  
**Impact**: Charging algorithm decisions

### Logging Additions (8 locations):

| Line | Location | What to Log | Type |
|------|----------|------------|------|
| ~50 | Curve calculation | "Charging curve updated: slope={}, intercept={}" | DEBUG |
| ~80 | Current/voltage read | "Priza{}: I={} A, V={} V" | DEBUG |
| ~120 | Taper detection | "Taper curve reached: {} A threshold" | INFO |
| ~150 | Algorithm decision | "Charge action: {}" | DEBUG |
| ~180 | State transition | "Charge state: {} → {}" | INFO |
| ~200 | Error condition | "Charging error: {}" | ERROR |
| ~220 | Curve reset | "Curve reset for new charge cycle" | INFO |
| ~250 | Summary | "Charge summary: {} cycles, avg current={} A" | INFO |

### Implementation Strategy:
- Add module-level logger
- Add 8 logging points at algorithm boundaries
- Estimated changes: 10 lines of code
- Estimated effort: 1 hour

---

## Script 4: 020_Scheduled_rev20260307.py (503 lines)

**Current Logging**: 0 entries  
**Priority**: 🟠 HIGH  
**Impact**: Scheduled device control, audit trail

### Logging Additions (8 locations):

| Line | Location | What to Log | Type |
|------|----------|------------|------|
| ~80 | Schedule check | "Schedule evaluation: condition={}" | DEBUG |
| ~120 | Action execute | "Executing scheduled action: device={}, target={}" | INFO |
| ~150 | Timer start | "Timer started: {} seconds" | DEBUG |
| ~180 | Timer cancel | "Timer cancelled" | DEBUG |
| ~220 | Condition met | "Condition met: restart allowed" | INFO |
| ~280 | Device restart | "Device {} restart initiated" | INFO |
| ~320 | Schedule complete | "Schedule complete: {}" | INFO |
| ~400 | Error occurred | "Scheduled task error: {}" | ERROR |

### Implementation Strategy:
- Add module-level logger
- Add 8 logging points
- Estimated changes: 10 lines of code
- Estimated effort: 1 hour

---

## Script 5: 099_Switches_Logic_rev20260307.py (583 lines)

**Current Logging**: 2 entries (0.34%)  
**Priority**: 🟠 HIGH  
**Impact**: Switch coordination, decision points

### Logging Additions (10 locations):

| Line | Location | What to Log | Type |
|------|----------|------------|------|
| ~100 | Logic branch | "Switch logic branch: {}" | DEBUG |
| ~150 | State check | "State verification: {} = {}" | DEBUG |
| ~200 | Dependency check | "Dependency check: {} requires {}" | DEBUG |
| ~250 | Conflict resolution | "Conflict: {} vs {}. Resolution: {}" | INFO |
| ~300 | Switch command | "Sending switch command: {} → {}" | INFO |
| ~350 | Coordination event | "Device coordination: {} activated {}" | INFO |
| ~400 | Lock acquired | "Lock acquired for switch group: {}" | DEBUG |
| ~450 | Lock released | "Lock released" | DEBUG |
| ~500 | Error condition | "Switch error: {}" | ERROR |
| ~550 | Summary | "Switch operation complete: status={}" | INFO |

### Implementation Strategy:
- Enhance existing minimal logging
- Add 10 new logging points
- Estimated changes: 12 lines of code
- Estimated effort: 1.5 hours

---

## Implementation Plan

### Phase 1: Immediate (Today)
1. ✅ Backup all scripts
2. ⏳ Add logging to 080_Power (most critical)
3. ⏳ Add logging to 017_Prize
4. ⏳ Add logging to 019_Charge_curve
5. Deploy & verify Phase 1

### Phase 2: Follow-up
6. Add logging to 020_Scheduled
7. Add logging to 099_Switches
8. Deploy & verify Phase 2

### Estimated Total Effort: 6-7 hours

---

## Verification Plan

### For Each Script After Deployment:
1. **Syntax Check**: Script loads without errors
2. **Log Output**: Logs appear at expected intervals
3. **Log Content**: Logs contain expected values
4. **No Spam**: Logs don't repeat unnecessarily
5. **Error Handling**: Error conditions are logged

### Test Scenarios:

#### 080_Power:
- [ ] Log shows power direction changes (IMPORT→EXPORT)
- [ ] Log shows intent changes
- [ ] Log shows sequence start/stop
- [ ] Winter charging override logged

#### 017_Prize:
- [ ] Log shows battery detection
- [ ] Log shows BatteryFull flag changes
- [ ] Log shows taper detection

#### 019_Charge_curve:
- [ ] Log shows curve calculations
- [ ] Log shows state transitions
- [ ] Log shows taper events

#### 020_Scheduled:
- [ ] Log shows schedule checks
- [ ] Log shows action execution
- [ ] Log shows timer events

#### 099_Switches:
- [ ] Log shows logic branches
- [ ] Log shows switch commands
- [ ] Log shows conflicts/resolution

---

## Rollback Plan

If issues arise after deployment:

```bash
# Restore from backup
for script in 080_Power_rev20260312.py 017_Prize_rev20260307.py 019_Charge_curve_rev20260307.py 020_Scheduled_rev20260307.py 099_Switches_Logic_rev20260307.py; do
  cp /home/vali/projects/openhab/backups/comprehensive_logging_20260621/$script.backup \
     /etc/openhab2/automation/jsr223/python/personal/$script
done
```

Rollback time: < 2 minutes

---

## Expected Impact After Implementation

| Metric | Before | After |
|--------|--------|-------|
| Logging coverage | 18% (2/11 scripts) | 90%+ (10/11 scripts) |
| Critical system visibility | 0% | 100% |
| Debugging time | Hours | 10-15 minutes |
| Audit trail | None | Complete |
| Issue diagnosis | Blind guessing | Root cause identifiable |

---

## Success Criteria

✅ All 5 scripts deploy without errors  
✅ Logs appear in /var/log/openhab2/openhab.log  
✅ Key state changes are logged  
✅ No excessive log spam (one entry per state change)  
✅ System performance unaffected  
✅ All existing functionality preserved  

---

**Status**: Ready for implementation  
**Backup Date**: 2026-06-21 09:50 UTC  
**Next Step**: Begin Phase 1 logging additions

