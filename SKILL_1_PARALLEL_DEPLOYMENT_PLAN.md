# Skill #1 Parallel Deployment: Crypto + Investing-Platform

## Overview

**Objective:** Harden both crypto-daytrading and investing-platform with WebSocket Staleness Detection (Skill #1) in parallel.

**Timeline:** 7-10 days total
- **Days 1-1 (Today):** Deploy Skill #1 to crypto-daytrading + start investing-platform prep
- **Days 1-2 (24h passive):** Validate crypto-daytrading Skill #1 in production
- **Days 2-3:** Implement investing-platform Skill #1 (while crypto validates)
- **Days 3-4 (24h passive):** Validate investing-platform Skill #1
- **Days 4+:** Move to Phase 2 (Circuit Breaker Reset) for both platforms

---

## Current Status

### ✅ Crypto-DayTrading: Skill #1 Complete

| Item | Status | Notes |
|------|--------|-------|
| Code | ✅ Written | websocket_staleness_monitor.py |
| Tests | ✅ Passed | Scenario 1 (network blip) validated |
| Integration | ✅ Done | Lifecycle, health endpoint, websocket manager |
| Deployment | ✅ Ready | Can start 24h validation anytime |
| Monitoring Plan | ✅ Written | See MONITORING_PLAN_24H.md |

### 🟡 Investing-Platform: Skill #1 In Prep

| Item | Status | Notes |
|------|--------|-------|
| Architecture | 🔵 Pending | Need to analyze dual-feed setup |
| Design | 🔵 Pending | Thresholds + failover logic |
| Implementation | 🔵 Ready to Start | See SKILL_1_ADAPTATION_PLAN.md |
| Testing | 🔵 Pending | Will do after implementation |
| Deployment | 🔵 Ready (2-3h away) | Can start right after crypto deploys |

---

## Week 1 Action Plan

### Day 1 (Today): Deploy + Start Prep

**Crypto-DayTrading (1 hour):**
```bash
# 1. Verify Skill #1 is running
curl http://localhost:8000/api/monitoring/health/websocket | jq

# 2. Start 24-hour validation
cd /home/vali/projects/crypto-daytrading
python3 monitor_24h.py &

# 3. Set baseline metrics
# - Document current state: CB trips/day, restarts/week
# - Start watching logs for "Reconnect successful" messages
```

**Investing-Platform (2 hours):**
```bash
# 1. Run Phase 0: Architecture Analysis (1 hour)
cd /home/vali/projects/investing-platform
# Answer 5 questions in SKILL_1_ADAPTATION_PLAN.md:
#   - How is RealtimeFeed initialized?
#   - How are price updates processed?
#   - What's the candle buffer structure?
#   - Is there existing health monitoring?
#   - What's the circuit breaker equivalent?

# 2. Document findings
# - Create README: "Skill #1 Architecture Analysis - [Date]"
# - Note differences from crypto-daytrading

# 3. Start Phase 1: Tailor Thresholds (1 hour)
# - Review crypto's thresholds
# - Adjust for stock trading (see SKILL_1_ADAPTATION_PLAN.md)
# - Document rationale
```

---

### Days 2-3 (Parallel Work)

**Crypto-DayTrading (Passive):**
- ✅ Monitoring runs automatically (monitor_24h.py)
- Check every 6 hours:
  ```bash
  curl http://localhost:8000/api/monitoring/health/websocket | jq '.details.metrics'
  grep "Reconnect successful" logs/ | wc -l
  ```
- Track: Circuit breaker trips, reconnect events, uptime

**Investing-Platform (Active Development):**
- Phase 2: Design dual-feed failover (1 hour)
  - How does Alpaca feed expose reconnect()?
  - How does Polygon feed expose reconnect()?
  - Design: Try Alpaca 3x, then switch to Polygon

- Phase 3: Start implementation (2-3 hours)
  - Copy websocket_staleness_monitor.py from crypto-daytrading
  - Adapt thresholds (Phase 1 work)
  - Add dual-feed logic (Phase 2 work)
  - Integrate into lifecycle.py
  - Add health endpoint
  - Create tests

---

### Day 4 (After Crypto Validation)

**Crypto-DayTrading:**
- Review 24h results
- Create SKILL_1_VALIDATION_RESULTS.md
- Decision tree:
  - ✅ **If passed:** Proceed to Phase 2 (Circuit Breaker Reset)
  - ❌ **If failed:** Tune thresholds, run another 24h test

**Investing-Platform:**
- Finish implementation (if not done)
- Run unit/integration tests
- Deploy to dev/staging
- Start 24h validation

---

## Key Files to Monitor

### Crypto-DayTrading

**Deployment Docs:**
- ✅ `SKILL_1_QUICK_START.md` — 5-min startup guide
- ✅ `WEBSOCKET_SKILL_DEPLOYMENT.md` — Full guide + testing
- 🆕 `MONITORING_PLAN_24H.md` — Validation plan (24 hours)
- 🔵 `SKILL_1_VALIDATION_RESULTS.md` — Results (after 24h)

**Implementation:**
- ✅ `backend/exchange/websocket_staleness_monitor.py` — Core skill
- ✅ `backend/exchange/websocket_manager.py` — Reconnect method
- ✅ `backend/api/lifecycle.py` — Initialization
- ✅ `backend/api/routers/monitoring.py` — Health endpoint

**Monitoring:**
- `logs/` or `/tmp/crypto_daytrading.log` — Event stream
- `http://localhost:8000/api/monitoring/health/websocket` — Real-time metrics

### Investing-Platform

**Deployment Docs:**
- 🆕 `SKILL_1_ADAPTATION_PLAN.md` — Design + implementation guide
- 🔵 `SKILL_1_VALIDATION_RESULTS.md` — Results (after 24h)

**Implementation (To Create):**
- `backend/infrastructure/realtime/websocket_staleness_monitor.py`
- `backend/api/lifecycle.py` (modify)
- `backend/api/routers/monitoring.py` (modify)
- `tests/test_websocket_staleness.py`

---

## Success Criteria

### After Day 2 (24h Crypto Validation)

✅ **Must Have:**
- [ ] Circuit breaker trips: 0-1 (was >10/day)
- [ ] Reconnect successes: 1+ (skill actively recovering)
- [ ] Manual restarts: 0 (was 1-2/week)
- [ ] No cascading failures observed
- [ ] Logs show clear recovery events

✅ **Should Have:**
- [ ] Uptime >99%
- [ ] Staleness detection within 15s
- [ ] <100 staleness warnings/day

### After Day 4 (Investing-Platform Ready)

✅ **Implementation Complete:**
- [ ] Dual-feed failover designed
- [ ] Unit tests passing
- [ ] Health endpoint working
- [ ] Ready to deploy

---

## Commands Quick Reference

### Start 24h Validation (Crypto)
```bash
cd /home/vali/projects/crypto-daytrading
python3 monitor_24h.py
```

### Check Health (Crypto)
```bash
curl http://localhost:8000/api/monitoring/health/websocket | jq
```

### Check Reconnects (Crypto)
```bash
grep "Reconnect" /path/to/logs/ | tail -20
```

### Analyze Investing-Platform (Start Phase 0)
```bash
cd /home/vali/projects/investing-platform
# Edit SKILL_1_ADAPTATION_PLAN.md and answer the 5 questions
```

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Crypto validation shows CB still trips | Medium | Tune thresholds, extend validation |
| Investing-platform has custom feed structure | Medium | Phase 0 analysis catches this early |
| Dual-feed failover logic is complex | Low | Copy pattern from circuit breaker logic |
| 24h validation takes longer than expected | Low | Run both in parallel anyway; crypto doesn't block investing-platform |

---

## Phase 2 Roadmap (After This Week)

Once both systems pass 24h validation, proceed to:

### Phase 2: Circuit Breaker State Reset (Both platforms, ~3h each)
- Add `/admin/reset-breaker` endpoint
- Persist CB state to Redis
- Allow manual recovery without full restart

### Phase 3: HA Failover (Crypto-DayTrading only, ~5h)
- Detect PRIMARY/BACKUP communication loss
- Force failover without hung PRIMARY blocking it
- Auto-promotion logic

### Phase 4: API Stuck-State Recovery (Crypto-DayTrading only, ~4h)
- Detect hung processes (socket limits, lock timeouts)
- Graceful restart + state recovery
- Systemd watchdog integration

---

## Success Looks Like

**After Week 1:**
- ✅ Crypto-DayTrading: 24h validation complete, <1 CB trip, 0 manual restarts
- ✅ Investing-Platform: Ready to deploy (code complete, tests passing)
- ✅ Both: Clear logs showing auto-recovery events
- ✅ Team: Confidence that WebSocket failures don't cascade

**After Week 2:**
- ✅ Investing-Platform: 24h validation complete, similar metrics
- ✅ Both: Phase 2 (Circuit Breaker Reset) in development
- ✅ Operational: Runbooks updated with new monitoring procedures

---

## Questions?

**For crypto-daytrading Skill #1:**
- See: `WEBSOCKET_SKILL_DEPLOYMENT.md` (full deployment guide)
- See: `MONITORING_PLAN_24H.md` (24h validation plan)

**For investing-platform Skill #1:**
- See: `SKILL_1_ADAPTATION_PLAN.md` (design + implementation plan)

**General hardening roadmap:**
- See: `/home/vali/projects/skill-creator/HARDENING_IMPLEMENTATION_ROADMAP.md`

---

## Start Now! 🚀

```bash
# Step 1: Crypto (should already be running)
cd /home/vali/projects/crypto-daytrading
python3 monitor_24h.py &

# Step 2: Investing-Platform (start Phase 0)
cd /home/vali/projects/investing-platform
# Read SKILL_1_ADAPTATION_PLAN.md Phase 0 section
# Answer the 5 architecture questions

# You're now running both systems in parallel!
```

**Estimated completion: Week 1 end = 2 fully hardened systems + Phase 2 ready to go.**

Good luck! 🎉
