# 080_Power Oven/Water Heater Fix - 2026-06-25

## Issue
Power readings broken when oven and water heater turn on simultaneously.

**Symptoms:**
- SANITY DROP messages: L1 and L3 spiking 2000-2100W
- Power gap: Expected -243W, showing -1303W (1034W gap)
- Root cause misidentified as "corruption" initially

## Root Cause
**NOT a malfunction** — legitimate high-power appliances

When oven + water heater both on:
- Oven draws: ~2000W on L1, L3
- Water heater draws: ~2000W on L1, L3
- Combined: ~4000W on two phases

Sanitization threshold too strict:
- ABS_DELTA_CLAMP = 1200W
- Oven jump (2000W) > threshold (1200W)
- Sanitization rejects as "spike"
- Falls back to stale cached values
- Creates 1034W gap

## Solution
**Increase ABS_DELTA_CLAMP** to allow legitimate household loads

```python
# Before (line 345):
ABS_DELTA_CLAMP = bd(1200)  # tune: 800..2000

# After:
ABS_DELTA_CLAMP = bd(3000)  # tune: 800..5000
# Oven ~2000W, AC ~2500W, water heater ~3000W
```

## Balancing Act
**Challenge:** High threshold protects large appliances but may miss small consumer issues

**Mitigations:**
1. **REL_DELTA check** (line 378): Still catches >300% relative jumps (protects small baseline)
   - If small device at 100W jumps to 400W: 300% jump → rejected
   - Only absolute jumps >3000W bypass this

2. **Phase disabled logic** (line 362-366): After 5+ invalid readings, phase gets disabled
   - Protects against persistent small sensor issues
   
3. **LARGE_JUMP_RESET** (line 490): Resets filter if jump >2000W detected
   - Catches large sudden changes even after acceptance

**Result:** 3000W threshold allows oven/heater but still protects small device monitoring

## Rationale
- Household ovens: 2000-3000W
- Electric water heaters: 2000-3000W  
- AC/Heat systems: 2000-3000W
- Old threshold (1200W) excluded normal appliances
- New threshold (3000W) allows typical loads
- Still protects against actual corruption (>3000W)

## Testing
Deployed 2026-06-25 11:40 UTC

Expected outcome:
- When oven/water heater on: No SANITY DROP messages
- Power readings normalize to correct values (~-300 to -400W)
- Filter recovers to proper state

## Files Changed
- 080_Power_rev20260312.py (line 345)
- Backup: 080_Power_rev20260312.py.backup_20260625_oven_fix

## Lessons Learned
1. Don't assume spikes = corruption without context
2. Know your system's max appliance draws
3. Sanitization thresholds must match real-world loads
4. Large gaps in power metrics warrant investigation, not assumptions

## Related Issues
- L4 WiFi loss: Actual connectivity problem ✅ Fixed
- Priza12 offline: Actual device issue ✅ Responding
- Shellyem3 spikes: Legitimate oven/heater loads ✅ Fix applied
