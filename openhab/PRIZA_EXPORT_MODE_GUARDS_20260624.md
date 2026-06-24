# Potential Guards Preventing Priza Activation in EXPORT Mode

**Date:** 2026-06-24  
**Question:** Is there something else preventing Prizas from starting when EXPORT mode is on?  
**Answer:** YES — Multiple safety guards could abort the sequence

---

## Guard 1: Direction Change Abort (CRITICAL)

**Location:** `run_sequence()` line 776-778 in 080_Power.py

```python
if sequence_mode == "ON" and direction_state == "IMPORT":
    log_important("SEQ ABORT: ON but now IMPORT")
    stop_sequence()
    return
```

**Issue:** If power direction changes from EXPORT → IMPORT while activating Priza, sequence aborts immediately

**When this happens:**
1. System detects EXPORT (-50W threshold)
2. Starts sequence: "Turn ON Priza1_Power_auto"
3. But turning ON a device increases local consumption
4. Power flow flips from -50W (export) → +20W (import)
5. **Sequence aborts before Priza fully activates**

**Result:** Priza never turns ON, but logs show "EXPORT detected"

---

## Guard 2: Surplus Absorbed Stop (ALSO BLOCKS)

**Location:** `run_sequence()` line 791 in 080_Power.py

```python
if sequence_mode == "ON" and filtered_power.compareTo(bd(0)) > 0:
    log_important("SEQ STOP: surplus absorbed (now IMPORT)")
    stop_sequence()
    return
```

**Issue:** Aborts ON sequence if any amount of power is being imported (> 0W)

**Asymmetric logic:**
- ON sequence (charging): Aborts if import > 0W
- OFF sequence (stopping): Allows import < 20W

**Example scenario:**
- EXPORT: -60W
- Priza turns ON: Consumption rises to 1000W
- Net power: -60W + 1000W = +940W (now importing)
- **Sequence aborts, Priza doesn't stay ON**

---

## Guard 3: Timing Lockouts

**Location:** `set_power_state()` line 681-688 in 080_Power.py

```python
if elapsed < MIN_ON_TIME:    # 5 seconds
    # Can't turn OFF yet
if elapsed < MIN_OFF_TIME:   # 5 seconds  
    # Can't turn ON yet
```

**Issue:** MIN_OFF_TIME lockout may prevent Priza from turning ON if PWRConsumption recently turned OFF

**Timing chain:**
1. EXPORT detected
2. apply_intent() calls `schedule_state("OFF")` for PWRConsumption
3. Debounce waits 4 seconds, then sends OFF command
4. MIN_OFF_TIME requires 5 seconds before next ON command
5. **Sequence tries to activate but gets locked out**

---

## Guard 4: Anti-Oscillation Hold

**Location:** `ensure_sequence_for_intent()` line 862-871 in 080_Power.py

```python
if sequence_mode is not None and sequence_mode != desired_mode:
    if elapsed < SEQUENCE_MIN_RUNTIME:  # 12 seconds
        log_important("SEQ HOLD: prevent flip")
        return
```

**Issue:** If sequence just finished an OFF operation, must wait 12 seconds before starting ON

**Example:**
- 14:27: Power flips IMPORT, sequence turns Priza OFF
- 14:29: Power flips back to EXPORT
- Sequence tries to turn ON but only 2 seconds have passed
- **Waits 10 more seconds to prevent oscillation**
- Meanwhile, EXPORT window passes

---

## EXPORT Threshold

**Value:** EXPORT_THRESHOLD = -50W (negative = selling to grid)

**Problem:** Very small EXPORT margin
- Typical Priza consumption: 500-1000W
- To maintain EXPORT, generation must exceed consumption by >550W
- If generation is only 500W total, activating Priza flips to IMPORT immediately

**Example:**
- PV generation: 500W
- Household consumption: 450W
- Net EXPORT: 50W (barely triggers charging)
- Turn on Priza1: +800W needed
- New net: -250W (IMPORT) 
- **Sequence aborts**

---

## Test: Is Power Oscillating?

To diagnose if this is the issue, check logs for:

```bash
# Pattern 1: Power oscillating around EXPORT threshold
grep "DIR=EXPORT\|DIR=IMPORT" /var/log/openhab2/openhab.log | tail -50

# Pattern 2: Sequence aborting due to direction change
grep "SEQ ABORT.*IMPORT" /var/log/openhab2/openhab.log

# Pattern 3: Surplus already absorbed
grep "SEQ STOP.*absorbed" /var/log/openhab2/openhab.log

# Pattern 4: Timing lockout
grep "LOCKOUT" /var/log/openhab2/openhab.log
```

---

## Recommendations

1. **Increase EXPORT_THRESHOLD** (from -50W to -150W or -200W)
   - Only trigger charging when there's solid margin
   - Prevents immediate flip back to IMPORT
   - Trade-off: Misses marginal EXPORT windows

2. **Increase SEQUENCE_MIN_RUNTIME** (from 12s to 20s)
   - Allows more time for sequence to complete
   - Reduces oscillation risk

3. **Adjust anti-oscillation hold** 
   - Add grace period for power to stabilize after direction change
   - Currently aborts immediately on direction flip

4. **Monitor power stability**
   - Check if EXPORT window is stable (sustains >5 seconds)
   - Or if it's fleeting (<2 seconds)

---

## Historical Context

The sequence abort logic was added as a safety feature to prevent:
- Charging when actually importing (wasting money)
- Continuous ON-OFF cycling (damaging equipment)
- Load oscillation loops

But this safety may be **too aggressive** for edge cases where EXPORT margin is small.

---

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
