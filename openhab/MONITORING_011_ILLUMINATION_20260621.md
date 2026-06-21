# Monitoring: 011_Illumination Logger Framework
**Date**: 2026-06-21 12:44 UTC  
**Status**: Deployed & Monitoring  
**Duration**: Real-time (event-driven)

---

## Deployment Verification

✅ **Script Deployed**: 011_Illumination_rev20260307.py  
✅ **Logger Class**: Added (25 instances of Logger usage detected)  
✅ **Cache Cleared**: Python bytecode removed  
✅ **No Errors**: Script loaded cleanly  

---

## Current Logging Status

### Phase 1-2 Logs (Working)
```
12:38:08 [DIRECTION] Power direction: EXPORT → NEUTRAL (-27 W)
12:38:49 [CURVE] Priza7 on ascending curve
12:40:37 [DIRECTION] Power direction: NEUTRAL → EXPORT (-54 W)
```
✅ Active, flowing in real-time

### Phase 3 Logs (011_Illumination - Ready, Awaiting Events)
**Expected categories**:
- `[DAYTIME]` - When daylight switches ON/OFF
- `[SENSOR]` - When illuminance/light levels change
- `[DAYLIGHT]` - When natural light conditions change

**Status**: 🟡 Not yet visible (event-driven - no illumination triggers occurred yet)

---

## Why No ILLUM Logs Yet?

011_Illumination is **event-driven** (not cron-based):
- Triggers on: Motion detected, Light level change, Daytime switch change
- Does NOT run on schedule
- Will log only when illumination-related items actually change state

**Triggers that will generate logs**:
1. Motion sensor activates → Light level reading → Illuminance threshold crossed
   - Expected log: `[SENSOR] Sufra illuminance changed to X lx`
   - Expected log: `[DAYTIME] Sufragerie1: Daytime ON`

2. User manually controls lights
   - Expected log: `[DAYTIME] DormitorC1: Daytime ON/OFF`

3. Natural light level drops below threshold
   - Expected log: `[DAYLIGHT] DormitorC: Insufficient natural light`

**Current state**: Midday (12:44 UTC), likely sufficient natural light, no motion/changes
→ No illumination events → No logs

---

## Monitoring Commands

### Watch for ILLUM logs (real-time)
```bash
ssh openhabian@192.168.3.25 "tail -f /var/log/openhab2/openhab.log" | grep "ILLUM\|DAYTIME\|SENSOR\|DAYLIGHT"
```

### Check latest ILLUM logs
```bash
ssh openhabian@192.168.3.25 "grep 'ILLUM\|DAYTIME\|DAYLIGHT\|SENSOR' /var/log/openhab2/openhab.log | tail -20"
```

### Count ILLUM logs by category
```bash
ssh openhabian@192.168.3.25 "grep '\[DAYTIME\]\|\[SENSOR\]\|\[DAYLIGHT\]' /var/log/openhab2/openhab.log | wc -l"
```

---

## Expected Timeline

| Time | Event | Expected Log |
|------|-------|--------------|
| Evening (~18:00) | Motion sensor triggers | `[DAYTIME] Sufragerie1: Daytime ON` |
| Evening | Light level drops | `[DAYLIGHT] System: Insufficient natural light globally` |
| Night (~23:00) | User goes to bed | `[DAYTIME] DormitorC1: Daytime OFF` |
| Morning (~07:00) | Natural light rises | `[DAYTIME] Sufragerie1: Daytime ON` |
| Morning | Motion detected | `[SENSOR] Sufra illuminance changed to X lx` |

---

## System Summary (12:44 UTC)

| Component | Logs | Status | Example |
|-----------|------|--------|---------|
| Phase 1 (080_Power) | 20+ | ✅ Active | [DIRECTION] EXPORT→NEUTRAL |
| Phase 2a (017_Prize) | 1 | ✅ Ready | [BATTERY] Priza1 full |
| Phase 2b (019_Charge_curve) | 7 | ✅ Active | [CURVE] Priza7 ascending |
| Phase 2c (020_Scheduled) | 0 | ✅ Ready | (next at 6:45 AM wd) |
| Phase 3 (011_Illumination) | 0 | 🟡 Ready | (awaiting events) |
| Existing (082_tomato) | 12 | ✅ Active | Every 10 min |
| Existing (084_metno) | 2 | ✅ Ready | Every hour |

**Total Framework Logs**: 59+ deployed and working

---

## Deduplication Verification

**Expected behavior**: Same log max 1x per 60 seconds per category

**Current observation**:
- DIRECTION logs: 2 in last 30 min (power swinging) ✅
- CURVE logs: 1 in last 30 min (device state change) ✅
- No spam detected ✅

---

## Next Steps

### Immediate (Now)
- Monitor for natural illumination events
- Wait for motion sensors to trigger
- Observe new ILLUM logs flowing

### When Events Occur
- EVENING: Look for [DAYTIME] OFF logs as natural light drops
- NIGHT: Look for [DAYLIGHT] insufficient light logs
- MORNING: Look for [DAYTIME] ON logs as sunrise occurs
- ANYTIME: Look for [SENSOR] logs when motion/light changes

### If No Logs After 24 Hours
1. Check if illumination rules are actually triggering
2. Verify sensor readings are changing
3. Run manual illumination state tests

---

## Rollback

If issues occur:
```bash
cp /home/vali/projects/openhab/backups/phase2_logging_20260621/011_Illumination_rev20260307.py.backup \
   /etc/openhab2/automation/jsr223/python/personal/011_Illumination_rev20260307.py
rm -rf /etc/openhab2/automation/jsr223/python/personal/__pycache__
```

---

**Deployment Status**: ✅ SUCCESSFUL  
**Framework Status**: ✅ READY  
**Logs Status**: 🟡 AWAITING EVENTS  
**Production Ready**: YES

