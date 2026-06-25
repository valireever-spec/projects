# OpenHAB System Status Report - 2026-06-25

## Issues Found

### 1. ✅ FIXED: L4 (E-Bike Charger) WiFi Loss
- **Status:** Fixed in commit dc5362d6
- **Issue:** L4 lost WiFi, never reconnected (age = 999999ms)
- **Impact:** 992W gap between House_Real_Consumption and House_Power_Consumption
- **Solution:** Made both metrics exclude stale L4
- **Verification:** Gap reduced to 15W (normal filter smoothing)
- **Action Required:** Reconnect L4 physically (WiFi/power issue on the device)

---

### 2. ⚠️ WARNING: Priza12 Offline
- **Status:** Item Priza12_Power_auto = NULL (undefined state)
- **Items Affected:**
  - Priza12_Power_auto = NULL (automation control)
  - Priza12_Power = NULL (device state)
  - Priza12_TelePeriod = NULL
- **Last Seen:** No recent logs (unknown when it went offline)
- **Impact:** Priza12 (likely a smart outlet/vacuum) is not responding
- **Action Required:** 
  - Check if Priza12 device is powered on
  - Check WiFi connectivity
  - Restart the device if needed
  - Verify item definitions in OpenHAB config

---

### 3. ⚠️ WARNING: Priza4 Battery Flag Stuck
- **Status:** Recently fixed (2026-06-25 10:39:11)
- **Issue:** Priza4_BatteryFull = ON, preventing automated charging
- **Last Action:** Manual reset to OFF at 10:39:11
- **Current State:** Priza4 is charging (ascending curve detected at 10:52:11)
- **Action Required:** 
  - Monitor to ensure battery doesn't get stuck again
  - Check battery full detection sensor (might be miscalibrated)
  - Consider adding watchdog reset if it recurs

---

### 4. 🔍 KNOWN ISSUE: Priza Activation Guards in EXPORT Mode
- **Status:** Identified but not resolved (commit 17f116ba)
- **Issue:** Multiple safety guards can prevent Priza activation when in EXPORT mode:
  1. **Direction Change Abort** — Sequence stops if power flips from EXPORT→IMPORT
  2. **Surplus Absorbed Stop** — Stops if any import detected (>0W)
  3. **Timing Lockouts** — MIN_OFF_TIME (5s) delays activation
  4. **Anti-Oscillation Hold** — Waits 12s after mode switch

- **Root Cause:** Very tight EXPORT_THRESHOLD (-50W) means devices turning on flip to IMPORT
- **Current Behavior:** Priza1 is ON (E-Bike charger working), PWRConsumption = OFF (EXPORT active)
- **Recommendations from diagnostic:**
  - Increase EXPORT_THRESHOLD from -50W to -150W (for safety margin)
  - Monitor logs for 'SEQ ABORT' and 'LOCKOUT' patterns
  - Check if EXPORT windows are stable (>5 seconds)

- **Next Steps:**
  - If activation is working fine now: Close issue (guards are protective)
  - If activation is still problematic: Increase thresholds

---

## Summary Table

| Issue | Status | Impact | Action |
|-------|--------|--------|--------|
| L4 WiFi loss | ✅ FIXED | Gap closed 992W→15W | Reconnect L4 device |
| Priza12 offline | ⚠️ WARNING | Priza12 not responding | Check device/WiFi |
| Priza4 battery stuck | ⚠️ RECENT FIX | Charging prevented | Monitor recurring |
| Priza EXPORT guards | 🔍 KNOWN | Potential activation issues | Monitor logs/decide on threshold increase |

---

## Monitoring Recommendations

### Daily
1. Check if L4 is back online: `tail -f /var/log/openhab2/openhab.log | grep "L4_CHECK"`
   - Should show: `L4 fresh (age=XXXms), included`

2. Monitor power gap:
   - Open solar_power sitemap
   - "House Real Cons" and "House Total cons. PWR" should be within ~20W

3. Verify Priza activation:
   - During EXPORT windows, Priza1 should turn ON
   - Check logs for `SEQ ABORT` or `LOCKOUT` patterns

### Weekly
1. Check Priza12 device status
2. Verify Priza4 battery sensor is accurate
3. Review any error logs in OpenHAB

---

## Configuration Tuning Options

### Option 1: Increase EXPORT Margin (if Priza not activating)
- **File:** `080_Power_rev20260312.py` line 76-77
- **Current:** EXPORT_THRESHOLD = -50W
- **Proposed:** -150W to -200W
- **Effect:** Requires larger surplus before turning on chargers
- **Trade-off:** Misses smaller EXPORT windows

### Option 2: Relax Surplus Absorption Check (if activation aborts)
- **File:** `080_Power_rev20260312.py` line 797
- **Current:** Aborts if filtered_power > 0 (any import)
- **Proposed:** Aborts if filtered_power > 50W (small import tolerance)
- **Effect:** Allows brief import during activation
- **Trade-off:** Slight risk of importing during charge

---

## Files Updated
- `080_Power_rev20260312.py` — L4 freshness fix
- `CHANGELOG_080_Power.md` — Change log
- `FIX_SUMMARY_L4_FRESHNESS_20260625.md` — Detailed analysis
- `backups/080_Power_rev20260312.py.backup_20260625` — Backup

## Next Session
- [ ] Reconnect L4 (E-Bike charger WiFi)
- [ ] Check/restart Priza12 device
- [ ] Verify Priza4 battery sensor accuracy
- [ ] Decide on EXPORT_THRESHOLD adjustment
