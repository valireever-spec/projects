# Shellyem3 Sensor Malfunction - 2026-06-25

## Critical Issue: Power Sensor Spikes

**Device:** Shellyem3 (three-phase energy meter)
**Time:** 2026-06-25 11:30:27 onwards
**Impact:** Power calculations completely broken (1034W gap)

---

## Evidence

### Spike Pattern
```
11:30:27 SANITY DROP L1 low-baseline jump: 2.0 -> 2086.5 W     ← +2084.5W spike!
11:30:27 SANITY DROP L3 low-baseline jump: 14.1 -> 2123.0 W    ← +2108.9W spike!
11:30:28 SANITY DROP L1 low-baseline jump: 2.0 -> 1916.5 W     ← Still spiking
11:30:28 SANITY DROP L3 low-baseline jump: 14.1 -> 1959.7 W    ← Still spiking
11:30:30 SANITY DROP L1 low-baseline jump: 2.0 -> 2088.6 W     ← Continues
11:30:30 SANITY DROP L3 low-baseline jump: 14.1 -> 2124.7 W    ← Continues
(repeats continuously)
```

### Current Readings
```
Expected (from phases):
  L1 = 2.0 W
  L2 = -421.8 W
  L3 = 12.7 W
  L4 = 164.0 W
  SUM = -243.1 W

Actual readings show:
  RAW = -1277.4 W  ← 1034W difference!
  House_Real_Consumption = -411.1 W  ← Wrong
  House_Power_Consumption = -1303.2 W  ← Way off
```

---

## Root Cause

**Shellyem3 device is sending corrupted power measurements** — likely due to:
1. **WiFi connectivity loss** (same as L4 issue earlier)
2. Intermittent connection causes measurement glitches
3. Sensor overflows or firmware bug
4. Loose connection / power supply issue

---

## How Sanitization is Responding

✅ **Good news:** Sanitization is correctly rejecting the spikes:
```python
SANITY DROP L1 low-baseline jump: 2.0 -> 2086.5
# Rejected because: |2086.5 - 2.0| = 2084.5 > ABS_DELTA_CLAMP (1200)
```

❌ **Bad news:** Cached old values are being used:
```python
# When sanitization rejects L1 spike, it returns last_valid["L1"]
# This is probably an old value from before the spike started
# So raw_total calculation uses stale L1, creating the gap
```

---

## Impact

| Component | Status | Problem |
|-----------|--------|---------|
| Sanitation | ✅ Working | Correctly rejects spikes |
| Filter | ❌ Broken | Using stale cached L1/L3 values |
| Power readings | ❌ Broken | 1034W gap between expected and actual |
| ECO automation | ⚠️ Degraded | Working but with wrong power values |

---

## Immediate Symptoms

1. **Power metrics completely wrong:**
   - Should show ~-243W (solar export)
   - Shows -1303W (fake massive export)

2. **House_Real_Consumption at -411W** instead of expected -243W
   - Indicates L1/L3 are stuck at cached old values

3. **Continuous SANITY DROP logs** (11:30:27 onwards)
   - Indicates problem is **ongoing**, not a one-time spike

---

## Solution Options

### Option A: Restart Shellyem3 Device (Recommended)
1. Power cycle the Shellyem3 meter:
   ```bash
   # Physical power off for 10 seconds, power back on
   ```
2. Wait 1-2 minutes for sensor to reconnect
3. Check if spikes stop and power readings normalize

**Time to fix:** 5 minutes

### Option B: Check Shellyem3 WiFi Connection
1. Access Shellyem3 web interface (check its IP)
2. Verify WiFi signal strength (RSSI)
3. Check if device is connected to MQTT broker
4. Restart WiFi connection if weak

### Option C: Increase Spike Tolerance (Temporary)
Modify `ABS_DELTA_CLAMP` in 080_Power to allow larger spikes:
```python
ABS_DELTA_CLAMP = bd(3000)  # Was 1200, now 3000
```
⚠️ **Not recommended** — defeats spike protection

### Option D: Disable Shellyem3 Readings (Last Resort)
If device is permanently broken:
1. Comment out L1, L2, L3 readings in power calculation
2. Fall back to Priza1 (L4) only
3. But this removes grid import/export monitoring

---

## Why This Matters

**Shellyem3 is critical:**
- Measures **grid import/export** (L1, L2, L3)
- Without it, can't determine if system is:
  - Selling power to grid (EXPORT)
  - Buying from grid (IMPORT)
  - Balanced (NEUTRAL)

**Impact on automation:**
- Priza charging decisions based on power direction
- Battery charging timing
- Load shedding (if implemented)
- All depend on accurate Shellyem3 readings

---

## Parallels to Earlier Issues

| Issue | Symptom | Cause | Solution |
|-------|---------|-------|----------|
| L4 | NULL state | WiFi lost | Re-trigger/reconnect |
| Priza12 | NULL state | Not publishing | Manual trigger |
| Shellyem3 | Massive spikes | WiFi/corruption | Power cycle |

**Pattern:** All remote sensors losing connectivity or sending corrupt data.

---

## Recommended Action

1. **Immediately:** Power cycle Shellyem3 and monitor logs
   ```bash
   # Watch for SANITY DROP messages to stop
   ssh openhabian@192.168.3.25 "tail -f /var/log/openhab2/openhab.log | grep SANITY"
   ```

2. **If not fixed:** Check Shellyem3 web interface for WiFi issues

3. **If still broken:** Consider replacing device (may be hardware failure)

---

## Monitoring

To track when this is fixed:
```bash
# Current state (broken):
curl -s 'http://localhost:8080/rest/items/House_Power_Consumption' | jq '.state'
# Returns: "-1303.2 W" (wrong)

# After fix:
# Should return: "-250W to -300W" (correct - around phase sum)
```

---

## Next Steps

Recommend: **Restart Shellyem3 now and check if logs show spikes continuing.**

Would you like me to:
- Create a monitoring script to detect when spikes stop?
- Document the Shellyem3 device configuration?
- Set up alerts for future spike detection?
