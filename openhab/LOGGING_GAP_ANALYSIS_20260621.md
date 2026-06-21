# Logging Gap Analysis - Complete System Audit
**Date**: 2026-06-21 11:15 UTC  
**Status**: Partial Coverage (3 of 6 critical scripts enhanced)

---

## Coverage Summary

| Script | Lines | Logs | Coverage | Status | Priority |
|--------|-------|------|----------|--------|----------|
| **080_Power_rev20260312** | 1026 | 15+ | 1.5% | ✅ Phase 1 | CRITICAL |
| **017_Prize_rev20260307** | 1206 | 5 | 0.4% | ✅ Phase 2a | CRITICAL |
| **019_Charge_curve_rev20260307** | 324 | 10+ | 3.1% | ✅ Phase 2b | CRITICAL |
| **020_Scheduled_rev20260307** | 503 | 9 | 1.8% | 🟡 No Logger | HIGH |
| **011_Illumination_rev20260307** | 653 | 6 | 0.9% | 🟡 No Logger | HIGH |
| **082_tomato_led** | 159 | 0 | 0% | ❌ None | MEDIUM |
| **084_metno_direct_fetch** | 61 | 0 | 0% | ❌ None | MEDIUM |
| **018_Delay_rev20260307** | 78 | 0 | 0% | ❌ None | LOW |
| **030_priza2_runtime_rev20260307** | 143 | 0 | 0% | ❌ None | LOW |

---

## Critical Gaps (HIGH Priority)

### 1. 020_Scheduled_rev20260307 (503 lines, 9 existing logs)
**Purpose**: Scheduled charging windows for e-bike/laptop/devices  
**Current**: Basic LogAction.logInfo() calls (no deduplication)  
**Gap**: No Logger framework, missing strategic decision points

**Key Functions Without Logging**:
- Midnight reset logic
- Scheduled window transitions
- Device on/off sequences
- Winter/shoulder charging decisions

**Recommendation**: Apply Logger framework (HIGH priority - affects charging schedule)

---

### 2. 011_Illumination_rev20260307 (653 lines, 6 existing logs)
**Purpose**: Lightstrip control (Adina, Alex, Sufragerie, Dormitor)  
**Current**: Minimal logging (0.9% coverage)  
**Gap**: No visibility into lightstrip trigger logic

**Key Functions Without Logging**:
- Presence detection transitions
- Time-based lightstrip rules
- Cinema mode activation
- Brightness/color calculations

**Recommendation**: Apply Logger framework (HIGH priority - complex automation)

---

## Medium Priority Gaps

### 3. 082_tomato_led.py (159 lines, 0 logs)
**Purpose**: Daily LED control for tomato growing (cloud %, LED duration)  
**Current**: No logging at all  
**Gap**: Can't debug LED timing issues, can't track forecast decisions

**Key Functions Without Logging**:
- Cloud coverage calculation
- LED duration determination (0-120 min)
- Daily forecast parsing
- Tomato status checks (on balcony?)

**Recommendation**: Add Logger framework (MEDIUM - diagnostics only, not critical)

---

### 4. 084_metno_direct_fetch.py (61 lines, 0 logs)
**Purpose**: Weather API calls (met.no) for cloud coverage + temperature  
**Current**: No logging (though it logs errors to stdout)  
**Gap**: Can't track API success/failure, can't see data flow

**Key Functions Without Logging**:
- API call attempts/failures
- Cloud coverage updates
- Temperature readings
- Data parsing

**Recommendation**: Add Logger framework (MEDIUM - data source validation)

---

## Low Priority Gaps

### 5. 018_Delay_rev20260307 (78 lines, 0 logs)
**Purpose**: Relay delay timing (fire relay timing control?)  
**Current**: No logging  
**Gap**: Unknown - need to inspect

---

### 6. 030_priza2_runtime_rev20260307 (143 lines, 0 logs)
**Purpose**: Device runtime tracking  
**Current**: No logging  
**Gap**: Unknown - need to inspect

---

## Logging Framework Coverage

### ✅ Deployed (Logger Class + Categories)
1. **080_Power** - Categories: DIRECTION, INTENT, WATCHDOG
2. **017_Prize** - Categories: TAPER, BATTERY, TIMEOUT  
3. **019_Charge_curve** - Categories: BATTERY, CURVE

### 🟡 Existing Logs (No Framework)
4. **020_Scheduled** - 9 LogAction.logInfo() calls (needs refactoring)
5. **011_Illumination** - 6 LogAction.logInfo() calls (needs refactoring)

### ❌ No Logging
6. **082_tomato_led** - 0 logs (needs Logger framework)
7. **084_metno_direct_fetch** - 0 logs (needs Logger framework)
8. **018_Delay** - 0 logs
9. **030_priza2_runtime** - 0 logs

---

## Critical Decision Points Missing Logging

### Power & Charging System
- ✅ 080_Power: Direction changes logged
- ✅ 017_Prize: Battery taper/full logged
- ✅ 019_Charge_curve: Curve transitions logged
- 🟡 020_Scheduled: Schedule window transitions (OLD format)

### Control System
- 🟡 011_Illumination: Lightstrip triggers (minimal)
- ❌ 082_tomato_led: LED duration decisions (NONE)
- ❌ 084_metno_direct_fetch: Weather data source (NONE)

### Device Management
- ❌ 018_Delay: Relay timing (NONE)
- ❌ 030_priza2: Device runtime (NONE)

---

## Recommended Action Plan

### Phase 3: Apply Logger Framework (High Priority)

**Option A: Complete Coverage (3-4 hours)**
1. 020_Scheduled - Add Logger + logging at decision points
2. 011_Illumination - Add Logger + logging at trigger points
3. 082_tomato_led - Add Logger + logging for LED calculations
4. 084_metno_direct_fetch - Add Logger + logging for API/weather

**Option B: Critical Only (1-2 hours)**
1. 020_Scheduled - Add Logger (scheduling is critical)
2. 011_Illumination - Add Logger (complex automation)
3. Skip 082_tomato_led and 084_metno for now

**Option C: Monitoring Priority (30 min)**
1. Focus on 020_Scheduled only (most critical)

---

## What Each Script Would Gain

### 020_Scheduled
```
[SCHEDULE] Entering 7AM charging window
[DEVICE] Priza1 scheduled ON at 07:00
[WINDOW] Shoulder season: 100W threshold active
[TIMEOUT] Charging timeout in 60 minutes
[COMPLETE] Charging window completed successfully
```

### 011_Illumination
```
[TRIGGER] Presence detected: Cinema mode
[BRIGHTNESS] Cinema: 10% brightness
[TIMER] Timeout set for 30 minutes
[STATE] Lightstrip: OFF (no motion detected)
[SCHEDULE] Night mode: All strips OFF
```

### 082_tomato_led
```
[FORECAST] Today cloud cover: 37%
[CALCULATION] LED duration: 57 minutes
[STATUS] Tomatoes: On balcony
[LED] Turning ON: 57 min (cloud=37%)
[CYCLE] LED cycle complete
```

### 084_metno_direct_fetch
```
[API] Fetching from met.no...
[SUCCESS] Cloud: 37%, Temp: 22°C
[PARSE] Daily average: 37% (14 daylight hours)
[MQTT] Published to stat/weather_home/cloud
[ERROR] API timeout (retrying)
```

---

## Questions for Prioritization

**Which is most important to monitor?**
1. **Charging schedule** (20_Scheduled) - affects e-bike/laptop battery
2. **Lightstrip control** (011_Illumination) - affects environment/comfort
3. **Tomato LED** (082_tomato_led) - affects plant growth
4. **Weather data** (084_metno_direct_fetch) - affects all solar logic

**Current Issues?**
- Are there problems with 020_Scheduled timing?
- Are lightstrips behaving unexpectedly?
- Is LED timing for tomatoes correct?
- Are weather readings reliable?

---

## Estimated Implementation Time

| Script | Effort | Time | Risk |
|--------|--------|------|------|
| 020_Scheduled | Medium | 45 min | Low |
| 011_Illumination | Medium | 60 min | Low |
| 082_tomato_led | Low | 30 min | Low |
| 084_metno_direct_fetch | Low | 30 min | Low |

**Total for all 4**: ~2.5 hours  
**Total for top 2**: ~1.75 hours  
**Total for top 1**: ~45 min

---

## Current System Status

**Well-Instrumented** ✅
- Power flow: Real-time direction/intent logging
- Battery charging: Taper/full detection logging
- Charging curves: Device-by-device curve tracking

**Partially Instrumented** 🟡
- Scheduled charging: Basic logs, needs framework
- Lightstrip control: Minimal logs, needs expansion

**Not Instrumented** ❌
- Tomato LED: No logs (medium priority)
- Weather data: No logs (medium priority)
- Other devices: No logs (low priority)

---

## Recommendation

**For complete visibility across automation system**: Enhance Phase 3 with at least **020_Scheduled** and **011_Illumination** (HIGH priority).

**For focused critical path**: Enhance only **020_Scheduled** (CRITICAL - affects charging reliability).

**Proceed with:**
1. 020_Scheduled (CRITICAL - 45 min)
2. 011_Illumination (HIGH - 60 min)  
3. 082_tomato_led (MEDIUM - 30 min, optional)
4. 084_metno_direct_fetch (MEDIUM - 30 min, optional)

---

**Total Enhanced Scripts After Phase 3**: 7 of 9 (78% coverage)  
**Critical Scripts**: 5 of 5 (100% coverage)

