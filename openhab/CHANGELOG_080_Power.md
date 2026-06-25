# 080_Power_rev20260312.py - Change Log

## 2026-06-25 — Fix: L4 (E-Bike charger) stale data gap

### Issue
- **Symptom:** Huge gap between `House_Real_Consumption` (-147W) and `House_Power_Consumption` (-1139W)
- **Root Cause:** E-Bike charger (L4) lost WiFi connection and stopped sending updates. `House_Real_Consumption` was always including stale L4, while the filter pipeline excluded it after 7 seconds of staleness.
- **Gap Size:** ~1000W when L4 is not updating

### Changes Made

#### 1. **Fix: L4 Freshness Check** (lines 474-490)
- **Before:** `House_Real_Consumption` always included L4 (even if stale >7 seconds)
- **After:** `House_Real_Consumption` only includes L4 if fresh (<7 seconds old)
- **Benefit:** Both metrics now use consistent logic—when L4 is offline, both exclude it, eliminating the gap

#### 2. **Enhanced Diagnostics** (lines 466-477)
- Added `PHASE_AGE` debug logs showing age (in ms) of each phase measurement
- These logs show if L1, L2, L3, or L4 have stale data
- Helps diagnose WiFi connectivity issues with remote sensors

#### 3. **L4 Status Logging** (lines 483-486)
- Debug log when L4 is included or excluded based on freshness
- Shows L4 age in milliseconds
- Replaces guesswork with facts

### How to Verify the Fix
1. **Check logs:** `tail -f /var/log/openhab2/openhab.log | grep "PHASE_AGE\|L4_CHECK"`
2. **Monitor sitemap:** Open solar_power sitemap and watch "House Real Cons" and "House Total cons. PWR"
3. **Expected behavior:**
   - When L4 is online: Both should be close (within ~100W due to filter smoothing)
   - When L4 is offline: Both should show similar values (L1+L2+L3 only)

### Reverting This Change
If needed, restore the backup:
```bash
scp -i ~/.ssh/openhab_claude /path/to/080_Power_rev20260312.py.backup claude@192.168.3.25:/etc/openhab2/automation/jsr223/python/personal/080_Power_rev20260312.py
```

### Configuration
- **RECENT_WINDOW_MS:** 7000 (phases stale if not updated in 7 seconds)
- **L4 Device:** Priza1_Power_Cons (E-Bike charger power meter)

### Related Items
- `House_Real_Consumption` — Raw sum of all phases (updated in real-time)
- `House_Power_Consumption` — Filtered/smoothed sum (used for ECO control logic)
