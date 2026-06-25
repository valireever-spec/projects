# Fix Summary: L4 Freshness & House Power Gap (2026-06-25)

## Problem Diagnosed
**Huge gap between House power metrics:**
- House_Real_Consumption: -147.1 W
- House_Power_Consumption: -1139.0 W
- **Gap: ~992W** ❌

**Root Cause:** E-Bike charger (L4/Priza1_Power_Cons) lost WiFi connection and never reconnected.
- L4 age: 999999ms (never updated since script initialization)
- House_Real_Consumption was including stale L4 (always)
- House_Power_Consumption excluded stale L4 (after 7 seconds)
- Result: Large gap between the two metrics

---

## Solution Applied

### Change: L4 Freshness Check
**File:** `080_Power_rev20260312.py` (lines 474-490)

**Before:**
```python
raw_total = l1.add(l2).add(l3).add(l4)  # Always included L4
events.postUpdate("House_Real_Consumption", str(raw_total) + " W")
```

**After:**
```python
raw_total = l1.add(l2).add(l3)
if l4_is_fresh:  # Only include if <7 seconds old
    raw_total = raw_total.add(l4)
events.postUpdate("House_Real_Consumption", str(raw_total) + " W")
```

### Added Diagnostics
1. **PHASE_AGE** logs — shows age (in ms) of each phase:
   ```
   PHASE_AGE L1=4297ms L2=150ms L3=1203ms L4=999999ms [fresh<7000ms]
   ```

2. **L4_CHECK** logs — shows if L4 is included or excluded:
   ```
   [L4_CHECK] L4 stale (age=999999ms), excluded
   ```

These help diagnose WiFi connectivity issues with remote sensors.

---

## Results After Fix

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| House_Real_Consumption | -147.1 W | -387.5 W | ✓ Updated |
| House_Power_Consumption | -1139.0 W | -372.0 W | ✓ Stable |
| **Gap** | **~992W** | **~15.5W** | ✓ **Fixed** |

**Remaining 15W gap:** Normal filter smoothing (median + exponential moving average), not a bug.

---

## How to Monitor

### Check L4 Status
```bash
tail -f /var/log/openhab2/openhab.log | grep "L4_CHECK"
```

**Expected output:**
- **When L4 is online:** `L4 fresh (age=XXXms), included`
- **When L4 is offline:** `L4 stale (age=999999ms), excluded`

### Watch the Metrics
Open **solar_power sitemap** → "Power Gen & Cons" frame:
- "House Total cons. PWR" (House_Power_Consumption)
- "House Real Cons" (House_Real_Consumption)

**Expected:** Both should be within ~20W of each other (filter smoothing tolerance).

---

## Reversing This Fix

If needed, restore the backup:
```bash
scp -i ~/.ssh/openhab_claude /home/vali/projects/openhab/backups/080_Power_rev20260312.py.backup_20260625 \
    claude@192.168.3.25:/etc/openhab2/automation/jsr223/python/personal/080_Power_rev20260312.py
```

---

## Next Steps (Optional)

1. **Reconnect L4 (E-Bike charger):**
   - Check WiFi credentials
   - Verify sensor power supply
   - Restart sensor if needed
   - Once reconnected, L4_CHECK logs should show `L4 fresh`

2. **Increase Freshness Window (if L4 updates slowly):**
   - Current: 7000ms (7 seconds)
   - Config: Line 73 `RECENT_WINDOW_MS = 7000`
   - Change if L4 updates less frequently

3. **Optional: Enable Verbose Logging for Troubleshooting:**
   - Line 127: `DEBUG_VERBOSE = False` → change to `True`
   - Shows all phase ages and calculations (log spam warning)
   - Disable after troubleshooting

---

## Files Changed
- **Script:** `/etc/openhab2/automation/jsr223/python/personal/080_Power_rev20260312.py`
- **Backup:** `/home/vali/projects/openhab/backups/080_Power_rev20260312.py.backup_20260625`
- **Changelog:** `/home/vali/projects/openhab/CHANGELOG_080_Power.md`

---

## Safety Assessment

✓ **Safe improvement** because:
1. Consistent logic across both metrics (no more special-casing)
2. Matches the design intent of the filter pipeline
3. Prevents misleading power readings when L4 is offline
4. Fully reversible with backup
5. Added diagnostics for future troubleshooting
