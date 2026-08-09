# Start Here: Skill #1 Parallel Deployment

## Right Now (Next 30 Minutes)

### Task 1: Start Crypto-DayTrading 24h Validation (5 min)

```bash
cd /home/vali/projects/crypto-daytrading

# Verify Skill #1 is working
curl http://localhost:8000/api/monitoring/health/websocket | jq '.status'
# Should see: "healthy"

# Start 24-hour monitoring (runs in background)
source venv/bin/activate
python3 monitor_24h.py > monitoring.log 2>&1 &

# Document baseline
echo "Baseline metrics at $(date):" >> VALIDATION_LOG.txt
echo "Circuit breaker trips: $(grep 'CIRCUIT BREAKER' logs/ 2>/dev/null | wc -l)" >> VALIDATION_LOG.txt
```

**What to expect:** Monitoring runs for 24 hours, checking health every hour.

---

### Task 2: Start Investing-Platform Phase 0 Analysis (20 min)

```bash
cd /home/vali/projects/investing-platform

# Read the adaptation plan
cat SKILL_1_ADAPTATION_PLAN.md | head -100

# Answer these 5 questions (edit ANALYSIS.md or just document):

# Q1: How is RealtimeFeed initialized?
grep -n "class RealtimeFeed" backend/infrastructure/realtime/websocket_feed.py

# Q2: How are price updates processed?
grep -n "def on_trade" backend/infrastructure/realtime/websocket_feed.py

# Q3: Is there existing health monitoring?
ls -la backend/analytics/data_health.py

# Q4: What's the circuit breaker equivalent?
grep -r "circuit\|breaker\|pause" backend/strategies/ | head -5

# Q5: What symbols are traded?
grep -r "symbols.*=" backend/strategies/*.py | grep -v "^#" | head -3
```

**What to document:**
```
Investing-Platform Architecture:
- RealtimeFeed init: [location and how it works]
- Price callback: [where to hook staleness detector]
- Health monitoring: [existing or new?]
- Candle buffer: [where is it? how to check staleness?]
- Strategy degradation: [how does strategy pause work?]
```

---

## For the Next 24 Hours

### Crypto-DayTrading (Passive)
- ✅ Monitoring runs automatically
- Every 6 hours: Quick health check
  ```bash
  curl http://localhost:8000/api/monitoring/health/websocket | jq '.details.metrics'
  ```
- Track in a spreadsheet:
  | Time | CB Trips | Reconnects | Status |
  |------|----------|-----------|--------|
  | 6h   | 0        | 0         | healthy |
  | 12h  | 0        | 1         | healthy |
  | 18h  | 0        | 2         | healthy |
  | 24h  | 0        | 3         | healthy |

### Investing-Platform (Active Development)
- **Hours 0-1:** Complete Phase 0 architecture analysis
- **Hours 1-2:** Phase 1 - Tailor thresholds
  ```python
  # From SKILL_1_ADAPTATION_PLAN.md, set:
  WARN_THRESHOLD = 3.0
  CRITICAL_THRESHOLD = 25.0  # More tolerant than crypto
  MAX_RECONNECT_ATTEMPTS = 5  # More retries
  ```
- **Hours 2-4:** Phase 2 - Design dual-feed failover
  - Sketch: Alpaca reconnect attempt 1-3
  - Sketch: Polygon fallback on attempt 4-5
- **Hours 4+:** Phase 3 - Start coding if time permits

---

## Success Metrics (Track These)

### Crypto-DayTrading (24h Test)
Goal: **REDUCE circuit breaker trips from >10/day to <1/day**

```
Every 6 hours, record:
✅ Circuit breaker trips since last check
✅ Reconnect successes logged
✅ Manual restarts needed (should be 0)
✅ Current uptime %
✅ Staleness warnings count
```

If all zeros except reconnects, you're winning! ✨

### Investing-Platform (Phase 0-3)
Goal: **Have implementation ready to deploy by day 3**

```
Every few hours:
✅ Phase 0: 5 architecture questions answered
✅ Phase 1: Thresholds documented (3 lines of code change)
✅ Phase 2: Dual-feed logic sketched (pseudocode)
✅ Phase 3: Implementation started (copy + adapt)
```

---

## Decision Points

### If Crypto Validation Shows <1 CB Trip/Day
→ **SUCCESS!** Proceed to Phase 2 (Circuit Breaker Reset)

### If Crypto Still Has >2 CB Trips/Day
→ **Tune & Retry**
```python
# Option 1: Lower CRITICAL_THRESHOLD from 15s to 10s
# Option 2: Increase MAX_RECONNECT_ATTEMPTS from 3 to 5
# Run another 24h test
```

### If Investing-Platform Analysis Shows Complex Feed Structure
→ **Ask for help** - might need custom adaptation

---

## Files to Keep Open (Bookmarks)

1. **Crypto Validation:** `/home/vali/projects/crypto-daytrading/MONITORING_PLAN_24H.md`
2. **Investing-Platform Design:** `/home/vali/projects/investing-platform/SKILL_1_ADAPTATION_PLAN.md`
3. **Parallel Plan:** `/home/vali/projects/SKILL_1_PARALLEL_DEPLOYMENT_PLAN.md`
4. **Implementation Status:** (Create a progress document)

---

## The 90-Second Version

**What's happening?**
- Crypto-DayTrading gets real-time WebSocket monitoring to prevent 3am crashes
- Same monitoring being adapted for investing-platform stocks/options
- Both run in parallel to save time

**Your job (next 24h):**
- Crypto: Just watch it work ✅ (automated)
- Investing-Platform: Design the adaptation (3-4 hours work)

**Success looks like:**
- Crypto: 0 circuit breaker trips, 0 manual restarts
- Investing-Platform: Design complete, ready to code week 2

**After 24h:** Both systems hardened, move to Phase 2 (manual recovery override)

---

## Need Help?

**Crypto debugging:** See `/home/vali/projects/crypto-daytrading/WEBSOCKET_SKILL_DEPLOYMENT.md` → "Troubleshooting"

**Investing-Platform:** See `/home/vali/projects/investing-platform/SKILL_1_ADAPTATION_PLAN.md` → "Phase 0 Questions"

**General roadmap:** See `/home/vali/projects/skill-creator/HARDENING_IMPLEMENTATION_ROADMAP.md`

---

## 🚀 Let's Go!

```bash
# Terminal 1: Crypto monitoring (leave running)
cd /home/vali/projects/crypto-daytrading
python3 monitor_24h.py

# Terminal 2: Investing-Platform analysis
cd /home/vali/projects/investing-platform
# Read SKILL_1_ADAPTATION_PLAN.md and analyze structure

# 🎉 Both working in parallel!
```

**Timeline: 24h validation + 3 days dev = Both systems hardened by end of week 1**

Good luck! 🎯
