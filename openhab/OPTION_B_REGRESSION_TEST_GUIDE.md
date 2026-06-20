# Option B: Regression Test Guide

**Date**: 2026-06-20  
**Testing Duration**: 24-48 hours post-deployment  
**Scope**: All 10 modified scripts + system integration  

---

## Why Regression Testing is Critical

The `is_state()` pattern is proven (deployed 3x today in 017, 019, 020), but:
- These 10 scripts are larger and more complex
- Interconnections between scripts are more numerous  
- State comparisons are deeply embedded in logic chains
- Any failure will cascade to dependent rules

**Regression testing catches issues that logs might miss.**

---

## Testing Phases

### Phase 1: Immediate (First 5 Minutes Post-Deployment)

**Automated Checks**:
```bash
# Watch logs for import errors
tail -f /var/log/openhab2/openhab.log | grep -iE "NameError|AttributeError|ImportError|StringType|OnOffType"

# Look for script loading messages
tail -f /var/log/openhab2/openhab.log | grep "Loading script.*011_Illumination\|016_HomePresence\|050_Reguli"
```

**Success Criteria**:
- [ ] All 10 scripts show "Loading script" with no errors
- [ ] No NameError or AttributeError in logs
- [ ] No "is_state" not defined errors
- [ ] System responsive

**If any error**: Immediately execute rollback (see Rollback Procedure section)

---

### Phase 2: Functional Tests (First Hour)

#### Test 1: 011_Illumination_rev20260307.py
**Trigger**: Illuminance sensor reading changes or time-of-day changes

**What to Check**:
1. Manually change Illuminance_Switch or DarkXxx items
2. Observe room lights respond
3. Check logs for:
   ```
   ✓ Illumination rule fired
   ✗ ERROR in logs
   ✗ State comparison failure
   ```

**Test Commands**:
```bash
# Change an item to trigger the rule
ssh openhabian@192.168.3.25 "echo 'sendCommand Sufragerie1_Daytime ON' | nc localhost 5005"

# Check logs
ssh openhabian@192.168.3.25 "tail -20 /var/log/openhab2/openhab.log | grep -i sufra"
```

**Success**: Lights respond to state changes without errors

---

#### Test 2: 016_HomePresence_rev20250307.py
**Trigger**: HomePresence status changes

**What to Check**:
1. Change HomePresence item
2. Verify presence-dependent rules execute
3. Check for errors in logs

**Success Criteria**:
- [ ] Rules trigger when HomePresence changes
- [ ] Automation sequences work
- [ ] No state comparison errors

---

#### Test 3: 050_Reguli_rev20260307.py (Largest Script)
**Trigger**: Multiple rules should fire

**What to Check**:
1. Monitor logs for rule execution
2. Verify Logging item works
3. Verify Sonoffmini state detection
4. Check for rule interactions

**Critical**: This is the largest script (1653 lines), most likely to reveal cascade failures

**Watch For**:
- Rules executing in expected order
- No deadlocks or infinite loops
- No unexpected state changes
- Rule completion times normal

---

#### Test 4: 099_Switches_Logic_rev20260307.py
**Trigger**: Sonoffmini state changes, Priza state changes

**What to Check**:
1. Toggle Sonoffmini devices
2. Verify Priza states update correctly
3. Check for state inconsistencies

**Critical**: Many dependencies on state comparisons

---

#### Test 5: 045_Bucatarie_rev20260307.py
**Trigger**: Kitchen item changes

**What to Check**:
1. Toggle kitchen controls
2. Verify response
3. Monitor logs

---

#### Test 6-10: Remaining Scripts
**Light Testing**:
- [ ] 082_tomato_led.py - Toggle tomato LED
- [ ] 055_Cinema.py - Activate/deactivate cinema mode
- [ ] 018_Delay_rev20260307.py - Test delay functionality
- [ ] 030_priza2_runtime_rev20260307.py - Monitor runtime
- [ ] 083_Priza9_ForceOn.py - Test Priza9 control

---

### Phase 3: Integration Testing (1-4 Hours)

**Test Scenario 1: Complex State Transitions**
```bash
# Rapid state changes to test concurrent execution
# Open multiple terminals:
Terminal 1: for i in {1..5}; do ssh ... "sendCommand Item1 ON"; sleep 2; done
Terminal 2: for i in {1..5}; do ssh ... "sendCommand Item2 OFF"; sleep 2; done
Terminal 3: tail -f /var/log/openhab2/openhab.log

# Watch for:
# - Rules executing in correct order
# - No missed events
# - No state corruption
```

**Test Scenario 2: Rule Chain Execution**
```bash
# Trigger a rule that depends on multiple state comparisons
# Monitor the entire chain:
# - Item A changes → Rule1 fires → Item B changes → Rule2 fires → Item C changes → Rule3 fires

# Verify:
[ ] All rules in chain execute
[ ] Order is correct
[ ] No rules are skipped
[ ] Final state is correct
```

**Test Scenario 3: Concurrent Rule Execution**
```bash
# Multiple rules firing simultaneously
# Monitor for:
[ ] No race conditions
[ ] No deadlocks
[ ] No state inconsistencies
[ ] All rules complete successfully
```

---

### Phase 4: Scheduled Events Testing (4-24 Hours)

**Cron-Triggered Rules**:
- [ ] Midnight rules execute (20_Scheduled)
- [ ] Noon rules execute (20_Scheduled)
- [ ] Hourly rules if any
- [ ] 10-minute intervals (Sonoffmini watchdog)

**Monitor During Scheduled Times**:
```bash
# Continuously watch for the scheduled time
watch -n 5 "tail -20 /var/log/openhab2/openhab.log"

# Specific triggers to watch:
# - 00:00 (midnight): Check BatteryFull reset
# - 12:00 (noon): Check scheduled tasks
# - Every 10 min: Check Sonoffmini watchdog
```

---

### Phase 5: 24-Hour Stability Testing

**Metrics to Track**:
| Metric | Baseline | After Fix | Status |
|--------|----------|-----------|--------|
| ERROR count in logs | <10 | <10 | ✓ |
| NameError count | 0 | 0 | ✓ |
| Rule execution time | Normal | Normal | ✓ |
| Rule miss count | ~0 | ~0 | ✓ |
| System responsiveness | Good | Good | ✓ |
| Cascading failures | None | None | ✓ |

**Automated Check**:
```bash
# Run every hour
ssh openhabian@192.168.3.25 "grep -c ERROR /var/log/openhab2/openhab.log"
ssh openhabian@192.168.3.25 "grep -c NameError /var/log/openhab2/openhab.log"
ssh openhabian@192.168.3.25 "grep -c AttributeError /var/log/openhab2/openhab.log"
```

---

## Rollback Procedure

**IMMEDIATE ROLLBACK TRIGGERS**:
1. Any NameError in logs
2. Any AttributeError in logs
3. Any "is_state not defined" error
4. Rule fails to execute when expected
5. More than 3 ERROR messages in 5 minutes
6. System becomes unresponsive

**Rollback Steps**:

```bash
#!/bin/bash
echo "=== EXECUTING ROLLBACK ==="
echo "Time: $(date)"

# Stop OpenHAB (optional, depends on situation)
# ssh openhabian@192.168.3.25 "sudo systemctl stop openhab2"

# Restore all backups
echo "Restoring backups..."
for f in /home/vali/projects/openhab/backups/option_b_comprehensive_fix_20260620_192008/*.backup; do
  scriptname=$(basename "$f" .backup)
  echo "Restoring $scriptname..."
  scp -i ~/.ssh/openhab_claude "$f" claude@192.168.3.25:/etc/openhab2/automation/jsr223/python/personal/$scriptname
done

# Wait for reload
echo "Waiting for OpenHAB to reload scripts (10 seconds)..."
sleep 10

# Verify
echo "Verifying rollback..."
ssh openhabian@192.168.3.25 "tail -20 /var/log/openhab2/openhab.log | grep -iE 'Loading.*011_Illumination|Loading.*016_HomePresence|ERROR'"

echo "Rollback complete. Check logs above for any errors."
```

**Save this script as `/home/vali/projects/openhab/rollback_option_b.sh`**

---

## Log Monitoring Commands

### Real-Time Monitoring (During Testing)
```bash
# Watch all errors
ssh openhabian@192.168.3.25 "tail -f /var/log/openhab2/openhab.log" | grep -iE "ERROR|Exception|NameError|is_state"

# Watch specific scripts
ssh openhabian@192.168.3.25 "tail -f /var/log/openhab2/openhab.log" | grep -E "011_Illumination|016_HomePresence|050_Reguli|099_Switches"
```

### Post-Test Analysis
```bash
# Count errors by type
ssh openhabian@192.168.3.25 "grep -i NameError /var/log/openhab2/openhab.log | wc -l"
ssh openhabian@192.168.3.25 "grep -i AttributeError /var/log/openhab2/openhab.log | wc -l"
ssh openhabian@192.168.3.25 "grep -i ERROR /var/log/openhab2/openhab.log | wc -l"

# Show all errors with timestamps
ssh openhabian@192.168.3.25 "grep 'ERROR\|NameError' /var/log/openhab2/openhab.log"
```

---

## Test Result Documentation

**Document Your Findings**:

```markdown
# Option B Testing Results - 2026-06-20

## Phase 1: Immediate Testing (5 min)
- [x] Scripts loaded without errors
- [x] No NameError or AttributeError
- [ ] (Any issues found)

## Phase 2: Functional Testing (1 hour)
### 011_Illumination
- [x] Lights respond to illuminance changes
- [x] No errors in logs
- [ ] (Any issues)

### 016_HomePresence
- [x] Presence rules execute
- [ ] (Any issues)

(Continue for each script...)

## Phase 3: Integration Testing
- [x] Concurrent rules execute without issues
- [x] No race conditions detected
- [ ] (Any issues)

## Phase 4: Scheduled Events
- [x] Midnight rules executed at 00:00
- [x] Noon rules executed at 12:00
- [ ] (Any issues)

## Phase 5: 24-Hour Stability
- ERROR count: 3 (acceptable baseline)
- NameError count: 0 (target met)
- System responsive: Yes
- Overall: PASSED

## Conclusion
Testing successful. No regressions detected.
```

---

## Success Criteria

### All Tests Must Pass:
- ✅ No NameError or AttributeError in logs
- ✅ All scheduled rules execute on time
- ✅ All triggered rules execute on event
- ✅ System responsive and stable
- ✅ No cascading failures
- ✅ No new ERROR messages
- ✅ State transitions work correctly
- ✅ Rules execute in expected order

### If Any Test Fails:
→ Document findings → Rollback immediately → Investigate root cause

---

## Timeline

| Phase | Duration | When |
|-------|----------|------|
| Phase 1 (Immediate) | 5 min | Immediately after deployment |
| Phase 2 (Functional) | 1 hour | First hour |
| Phase 3 (Integration) | 3 hours | Hours 1-4 |
| Phase 4 (Scheduled) | Variable | Next scheduled times |
| Phase 5 (Stability) | 24 hours | Full 24-hour cycle |

**Total Testing Time**: 24-48 hours recommended before marking complete

---

*Regression testing is not optional—it's essential for a 10-script change.*  
*These tests protect your production system.*
