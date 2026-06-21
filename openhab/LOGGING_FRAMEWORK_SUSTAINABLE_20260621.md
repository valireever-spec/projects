# Sustainable Logging Framework
**Date**: 2026-06-21  
**Goal**: Create reusable, maintainable logging pattern for all automation scripts

---

## Problem with Current Logging

```python
# Current: Hard to parse, inconsistent format
LogAction.logInfo("ECO", "SUM raw=292.2 filt=290.5 dir=IMPORT intent=IMPORT_MODE pwr=ON eco=OFF seq=None")
LogAction.logInfo("ECO", "Skip Priza4 OFF (battery not confirmed full)")
```

**Issues**:
- ❌ Inconsistent formatting
- ❌ Hard to parse machine-readable logs
- ❌ No log levels (debug vs error)
- ❌ Difficult to search/filter
- ❌ No timestamp context (uses system time only)
- ❌ Hard to add new logs without knowing pattern

---

## Sustainable Logging Framework

### 1. Logging Utility Class (Add to each script)

```python
class Logger:
    """Sustainable logging framework for OpenHAB automation scripts."""
    
    def __init__(self, name):
        self.name = name
        self.last_logged = {}  # Deduplicate spam
        self.SPAM_THRESHOLD_SEC = 60  # Don't log same message more than once per minute
    
    def info(self, category, message, *args):
        """Log info-level message with automatic deduplication."""
        msg = message.format(*args) if args else message
        key = (category, message)  # Use template as key, not formatted message
        
        # Deduplicate: only log if different message or > 60 sec since last
        if self._should_log(key):
            LogAction.logInfo(self.name, "[{}] {}".format(category, msg))
            self.last_logged[key] = secs_since(DateTime.now())
    
    def debug(self, category, message, *args):
        """Log debug-level message (only if DEBUG enabled)."""
        if DEBUG_VERBOSE:
            msg = message.format(*args) if args else message
            LogAction.logInfo("{}_DBG".format(self.name), "[{}] {}".format(category, msg))
    
    def error(self, category, message, *args):
        """Log error-level message (always logged)."""
        msg = message.format(*args) if args else message
        LogAction.logInfo("{}_ERR".format(self.name), "[{}] {}".format(category, msg))
    
    def _should_log(self, key):
        """Check if message should be logged (deduplicate spam)."""
        if key not in self.last_logged:
            return True
        age = secs_since(self.last_logged[key]) if isinstance(self.last_logged[key], (int, float)) else 0
        return age is None or age > self.SPAM_THRESHOLD_SEC

# Initialize at module level
log = Logger("ECO")  # For 080_Power
log = Logger("PRIZA")  # For 017_Prize
log = Logger("CHARGE")  # For 019_Charge_curve
```

### 2. Logging Categories (Consistent Naming)

Use categories to organize logs by system area:

```python
# 080_Power categories
"POWER"     # Power measurements and filtering
"DIRECTION" # Import/Export classification
"INTENT"    # Mode changes (IMPORT/EXPORT/NEUTRAL)
"DEVICE"    # Device control commands
"SEQUENCE"  # Sequence start/stop
"WINTER"    # Winter charging logic
"ERROR"     # Error conditions

# 017_Prize categories
"BATTERY"   # Battery state
"CHARGE"    # Charging logic
"TAPER"     # Taper detection
"DEBOUNCE"  # Debounce events
"STATE"     # Device state changes

# 019_Charge_curve categories
"CURVE"     # Curve calculations
"ALGORITHM" # Algorithm decisions
"STATE"     # State transitions
"ERROR"     # Error conditions
```

### 3. Log Message Format (Structured, Parseable)

```python
# BAD (hard to parse):
"SUM raw=292.2 filt=290.5 dir=IMPORT intent=IMPORT_MODE pwr=ON eco=OFF seq=None"

# GOOD (structured, clear):
log.info("POWER", "Raw={:.1f} Filtered={:.1f} → Direction={} Intent={} Pwr={} Eco={}", 
         raw_power, filtered_power, direction, intent, pwr_state, eco_mode)

# Output:
# [POWER] Raw=292.2 Filtered=290.5 → Direction=IMPORT Intent=IMPORT_MODE Pwr=ON Eco=OFF
```

### 4. Log Entry Checklist

For each log statement, ask:

- ✅ **Clear**: Is the message understandable without reading code?
- ✅ **Actionable**: Would this log help debug an issue?
- ✅ **Categorized**: Does it have a category that groups similar logs?
- ✅ **Deduplicatable**: Will it spam if run repeatedly?
- ✅ **Contextual**: Does it explain WHY, not just WHAT?

**Good Examples**:
```python
log.info("DIRECTION", "Power direction: {} ({:.0f} W)", direction, power)
log.info("INTENT", "Intent change: {} → {}", old_intent, new_intent)
log.error("DEVICE", "Priza{} control failed: {}", device_id, error_msg)
```

**Bad Examples**:
```python
log.info("DEBUG", "OK")  # Not actionable
log.info("DATA", str(raw_dict))  # Unparseable
log.info("STATE", "Changed")  # Missing context
```

---

## Implementation Strategy

### Step 1: Add Logger Class to Each Script
```python
# Add at module level (after imports, before functions)
class Logger:
    # ... (code above)

log = Logger("SCRIPTNAME")
```

### Step 2: Replace Existing log() with New Framework
```python
# OLD:
log("WATCHDOG: filtered stale {}s -> schedule compute".format(age))

# NEW:
log.info("POWER", "Filtered data stale ({:.1f}s) - triggering recompute", age)
```

### Step 3: Add New Logs at Decision Points
```python
# At direction changes:
if direction != old_direction:
    log.info("DIRECTION", "Classification: {} ({:.0f} W)", direction, power)

# At intent changes:
if new_intent != current_intent:
    log.info("INTENT", "Mode change: {} → {}", current_intent, new_intent)

# At device control:
log.debug("DEVICE", "Command sent: {} = {}", device_name, target_state)

# At errors:
log.error("ERROR", "Failed to control {}: {}", device_name, error)
```

### Step 4: Monitor & Adjust
- Run for 1 hour
- Check for spam (same message repeated 100+ times)
- Adjust SPAM_THRESHOLD_SEC if needed
- Verify all critical decisions are logged

---

## Benefits of This Framework

| Benefit | How |
|---------|-----|
| **Deduplication** | Logger class tracks last_logged, prevents spam |
| **Consistency** | All logs follow same format: [CATEGORY] Message |
| **Parseability** | Structured format, easy to grep/filter |
| **Debuggability** | Context explains why decision was made |
| **Maintainability** | New developers know where to add logs |
| **Sustainability** | Can be reused across all scripts |
| **Auditability** | Full trail of state changes |

---

## Log Output Examples

### Current (Hard to Use)
```
[ECO] SUM raw=292.2 filt=290.5 dir=IMPORT intent=IMPORT_MODE pwr=ON eco=OFF seq=None
[ECO] Skip Priza4 OFF (battery not confirmed full)
[ECO] RAW=278.5 MEDIAN=292.2 FILTERED=292.0 DIR=IMPORT INTENT=IMPORT_MODE
```

### Sustainable (Easy to Use)
```
[POWER] Raw=292.2 Filtered=290.5 → Direction=IMPORT Intent=IMPORT_MODE Pwr=ON Eco=OFF
[BATTERY] Priza4: Battery not full, action skipped (Batt=67%, Full=95%)
[POWER] New power sample: Raw=278.5 Median=292.2 Filtered=292.0 Direction=IMPORT
[INTENT] Mode transition: IMPORT_MODE (power > 50W import threshold)
[DEVICE] Priza1 control: Command=OFF Reason=EXPORT_mode
[ERROR] Priza4 communication failed: timeout after 5s
```

---

## Rollout Plan

### Phase 1: Framework (1 hour)
- Add Logger class to 080_Power
- Test deduplication works
- Verify log format

### Phase 2: Critical Script (2 hours)
- 080_Power: Add 15 logs at decision points
- Deploy and monitor for spam
- Adjust threshold if needed

### Phase 3: Remaining Scripts (2 hours)
- 017_Prize: Add 10 logs
- 019_Charge_curve: Enhance existing logs
- Deploy

### Phase 4: Maintenance (Ongoing)
- Review logs weekly for spam
- Add new logs as new issues discovered
- Adjust thresholds based on real usage

---

## Sustainability Checklist

- ✅ Logging framework is reusable (copy to other scripts)
- ✅ Deduplication prevents spam
- ✅ Consistent format easy to search
- ✅ Log levels (info/debug/error) for filtering
- ✅ Categories organize related logs
- ✅ Documentation makes it maintainable
- ✅ Easy to add new logs without disruption

---

**Next Step**: Implement Logger class in 080_Power, deploy Phase 1

