# Priza1_BatteryFull - Test Procedure

## Pre-Test Checklist
- [ ] Scripts deployed and loaded (check OpenHAB logs for "Loading script" messages)
- [ ] E-bike battery is NOT currently charging
- [ ] OpenHAB UI is accessible at http://localhost:8080
- [ ] SSH access available to check logs

## Test 1: Full-Charge Detection (Primary Fix)

### Objective
Verify that `Priza1_BatteryFull` is correctly activated when the battery reaches full charge.

### Steps
1. **Open logs in terminal**:
   ```bash
   ssh openhabian@192.168.3.25 "tail -f /var/log/openhab2/openhab.log" | grep -E "(E-Bike|Priza1|BatteryFull|Charging)"
   ```

2. **Start charging**:
   - In OpenHAB UI: Set `Priza1_Power_auto` = ON (or use manual override)
   - Watch logs for: `Priza1_Current` values > 0.300 A

3. **Let charging progress** (wait until battery gets close to full):
   - Current should decrease gradually over time
   - Current threshold for taper: 0.350 A
   - Current threshold for full: 0.150 A

4. **Monitor taper phase** (80% charge):
   - Watch for: `"Tapering started (current ...)"`
   - Wait ~10 minutes for stable low-current charge
   - Expect: `"Battery likely reached 80%. Stopping charge."`
   - Expect: `"Priza1_BatteryFull set ON at 80% taper"`

5. **Monitor full-charge completion** (100% charge):
   - Current will drop to ≤ 0.150 A
   - Expect: `"Charging complete (trickle current)."`
   - **CRITICAL**: Expect: `"Priza1_BatteryFull set ON — ECO sequence will skip Priza1"`

6. **Verify in OpenHAB UI**:
   - Check item `Priza1_BatteryFull` = ON
   - Check item `Priza1_Power` = OFF

### Expected Results
✓ Flag is set within 1-2 seconds of full charge detection  
✓ Log message confirms "Priza1_BatteryFull set ON"  
✓ UI shows `Priza1_BatteryFull` = ON  

### If Test Fails
❌ No "Priza1_BatteryFull set ON" log message  
→ Script may have syntax error; check: `ssh openhabian@192.168.3.25 "tail -100 /var/log/openhab2/openhab.log" | grep -i error`

❌ Current never drops to full-charge threshold  
→ May be a current sensor issue; check current reading in UI

❌ Flag shows ON but then changes to OFF unexpectedly  
→ May be cleared by 020_Scheduled or by timeout; check full logs

---

## Test 2: Manual Override Clears Flag

### Objective
Verify that manually activating `Priza1_Power_man` clears the `Priza1_BatteryFull` flag.

### Steps
1. **Prerequisite**: `Priza1_BatteryFull` should be ON from Test 1

2. **In OpenHAB UI**:
   - Set `Priza1_Power_man` = ON

3. **Check logs** for:
   ```
   [INFO ] [Priza1] Priza1_BatteryFull cleared — manual override
   ```

4. **Verify in UI**:
   - `Priza1_BatteryFull` should change to OFF
   - `Priza1_Power` should turn ON

### Expected Results
✓ Log shows "Priza1_BatteryFull cleared — manual override"  
✓ UI shows `Priza1_BatteryFull` = OFF  
✓ UI shows `Priza1_Power` = ON  

---

## Test 3: Auto ON Blocked While BatteryFull

### Objective
Verify that automatic charging (ECO sequence) is blocked while `Priza1_BatteryFull` is ON.

### Steps
1. **Prerequisite**: `Priza1_BatteryFull` = ON (from Test 1)

2. **Manually clear the flag** (to test the blocking logic):
   - In OpenHAB UI: Set `Priza1_Power_man` = OFF (to deactivate manual override)
   - Then set `Priza1_Power_auto` = OFF

3. **Set BatteryFull back to ON** (simulate full battery):
   - In OpenHAB: Manually set `Priza1_BatteryFull` = ON

4. **Try to enable auto power**:
   - Set `Priza1_Power_auto` = ON

5. **Check logs** for:
   ```
   [INFO ] [Priza1] Priza1_Power auto ON blocked — BatteryFull is ON
   ```

6. **Verify in UI**:
   - `Priza1_Power` should remain OFF
   - `Priza1_Power_auto` should revert to OFF

### Expected Results
✓ Log shows "Priza1_Power auto ON blocked — BatteryFull is ON"  
✓ Power does NOT turn ON  
✓ Auto is automatically turned OFF  

---

## Test 4: New Charge Cycle Clears Flag

### Objective
Verify that starting a new charge cycle automatically clears the `Priza1_BatteryFull` flag.

### Steps
1. **Prerequisite**: `Priza1_BatteryFull` = ON (from Test 1)

2. **Manually set Power to ON**:
   - Set `Priza1_Power_man` = ON (or use auto if not blocked)

3. **Check logs** for:
   ```
   [INFO ] [Priza1] Priza1_BatteryFull cleared — new charge cycle started
   ```

4. **Verify in UI**:
   - `Priza1_BatteryFull` should change to OFF
   - `Priza1_Power` should turn ON
   - `Priza1_Current` should increase (if charger is active)

### Expected Results
✓ Log shows "Priza1_BatteryFull cleared — new charge cycle started"  
✓ UI shows `Priza1_BatteryFull` = OFF  
✓ UI shows `Priza1_Power` = ON  

---

## Test 5: Timeout Relay Opening Does NOT Set Flag

### Objective
Verify that a timeout-based relay opening (15-minute timeout) does NOT trigger `Priza1_BatteryFull` activation.

### Steps
1. **Start charging**:
   - Set `Priza1_Power_auto` = ON
   - Current should be > 0.300 A

2. **Wait for timeout** (default 15 minutes):
   - Timeout will automatically turn off relays
   - Check logs for:
   ```
   [INFO ] [E-Bike] current=0 after timeout relay-open — BatteryFull NOT set
   ```

3. **Verify in UI**:
   - `Priza1_BatteryFull` should remain OFF (not set by timeout)

### Expected Results
✓ After timeout, current drops to 0  
✓ Log shows "current=0 after timeout relay-open — BatteryFull NOT set"  
✓ `Priza1_BatteryFull` remains OFF (not set)  

---

## Troubleshooting

### Issue: Scripts Don't Load
```bash
# Check for syntax errors
ssh openhabian@192.168.3.25 "python3 /etc/openhab2/automation/jsr223/python/personal/017_Prize_rev20260307.py"

# Check OpenHAB logs
ssh openhabian@192.168.3.25 "tail -200 /var/log/openhab2/openhab.log" | grep -E "(ERROR|Traceback|Exception)"
```

### Issue: Flag Not Activating
1. Check that `Priza1_BatteryFull` item exists:
   ```bash
   ssh openhabian@192.168.3.25 "grep 'Priza1_BatteryFull' /etc/openhab2/items/*.items"
   ```

2. Verify current sensor is working:
   ```bash
   # Check Priza1_Current in UI or:
   ssh openhabian@192.168.3.25 "grep 'Priza1_Current' /var/log/openhab2/openhab.log" | tail -5
   ```

3. Check if flag is being cleared by other rules:
   ```bash
   ssh openhabian@192.168.3.25 "grep -E 'BatteryFull.*cleared|BatteryFull.*OFF' /var/log/openhab2/openhab.log" | tail -20
   ```

### Issue: Flag Clears Unexpectedly
- Check 020_Scheduled.py for midnight/noon resets
- Verify no other scripts are setting `Priza1_BatteryFull` = OFF
- Check if manual or auto controls are interfering

---

## Sign-Off
After all tests pass, update the status below:

**Test Completion Date**: _______________  
**Tester**: _______________  
**Result**: ☐ PASS  ☐ FAIL  

**Notes**:  
_________________________________________________________________  
_________________________________________________________________  
