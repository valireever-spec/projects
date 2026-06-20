# Runbooks: Troubleshooting & Escalation

**Version:** 1.0 | **Last Updated:** June 20, 2026

This document provides step-by-step runbooks for common operational issues with the investing-platform V-Model tracker.

---

## Table of Contents

1. [Tracker API Connection Issues](#tracker-api-connection-issues)
2. [Sync Failures](#sync-failures)
3. [High Latency](#high-latency)
4. [Data Inconsistencies](#data-inconsistencies)
5. [Escalation Procedures](#escalation-procedures)

---

## Tracker API Connection Issues

**Symptoms:** "Cannot reach tracker" errors, gap reporting disabled, failed sync operations

### Root Cause Analysis

1. **Check tracker service status:**
   ```bash
   curl -s http://127.0.0.1:8001/health | jq .
   # Expected: {"status": "healthy"}
   ```

2. **Check network connectivity:**
   ```bash
   ping 127.0.0.1  # or tracker host if remote
   telnet 127.0.0.1 8001
   ```

3. **Check logs for specific errors:**
   ```bash
   grep "ConnectionError\|Network error" logs/*.log
   ```

### Recovery Steps

**Level 1: Automatic Recovery (built-in)**
- System will retry with exponential backoff (3 attempts, 2-4 second delays)
- Gap reporting is non-blocking (system continues even if tracker unavailable)
- Check logs to see retry attempts: `grep "retry" logs/*.log`

**Level 2: Manual Restart**
1. Verify tracker service is running: `systemctl status tracker-service`
2. If stopped, start it: `systemctl start tracker-service`
3. Wait 10 seconds for service to stabilize
4. Check health endpoint again

**Level 3: Network Troubleshooting**
1. Check firewall rules: `sudo iptables -L | grep 8001`
2. Verify DNS resolution: `nslookup tracker-host`
3. Check if port 8001 is listening: `sudo netstat -tlnp | grep 8001`

### Escalation

- **If problem persists >2 minutes:** Contact DevOps team
- **SLA:** Connection restored within 5 minutes
- **Escalation email:** devops@team.com

---

## Sync Failures

**Symptoms:** Sync loop stops, requirements not updating, gaps not imported

### Root Cause Analysis

1. **Check sync logs:**
   ```bash
   tail -100 logs/vmodel_sync.log | grep -E "error|failed"
   ```

2. **Verify markdown files exist:**
   ```bash
   ls -la FUNCTIONAL_REQUIREMENTS.md NONFUNCTIONAL_REQUIREMENTS.md V_MODEL_BOARD.md
   ```

3. **Check markdown format:**
   ```bash
   grep -E "^- \*\*[A-Z]+-\d+\*\*" FUNCTIONAL_REQUIREMENTS.md | head -5
   # Expected output: - **FR-001** — Description (Status)
   ```

4. **Verify tracker project exists:**
   ```bash
   curl -s http://127.0.0.1:8001/api/projects | jq '.[] | select(.name=="investing-platform")'
   ```

### Recovery Steps

**Level 1: Verify Markdown Format**
1. Check for valid requirement IDs: `grep -c "^- \*\*[A-Z]+-\d+\*\*" FUNCTIONAL_REQUIREMENTS.md`
2. Ensure status in parentheses: `grep -E "\(Proposed\|\(Implemented\)" FUNCTIONAL_REQUIREMENTS.md`
3. Re-run sync: `python -m backend.core.vmodel_sync`

**Level 2: Reset Sync State**
1. Clear sync cache: `rm -f .sync_state.json`
2. Verify tracker project: `curl http://127.0.0.1:8001/api/projects/1`
3. Re-run sync with debug: `python -m backend.core.vmodel_sync --debug`

**Level 3: Rebuild from Scratch**
1. Backup current state: `git stash`
2. Export requirements from tracker: `curl http://127.0.0.1:8001/api/projects/1/requirements > requirements_backup.json`
3. Recreate markdown files from backup
4. Re-sync: `python -m backend.core.vmodel_sync`

### Escalation

- **If problem persists >5 minutes:** Check tracker database integrity
- **SLA:** Sync restored within 10 minutes
- **Escalation email:** platform-team@company.com

---

## High Latency

**Symptoms:** API calls taking >1 second, timeouts on tracker requests

### Metrics to Check

1. **Check recent latency (p95):**
   ```bash
   # In logs, look for p95_latency_ms
   grep "p95_latency" logs/metrics.log | tail -5
   ```

2. **Check error rate:**
   ```bash
   grep "error_rate_percent" logs/metrics.log | tail -5
   ```

3. **Check tracker health:**
   ```bash
   curl -s http://127.0.0.1:8001/health | jq .
   ```

### Root Cause Analysis

1. **Network latency:** `ping 127.0.0.1` (should be <1ms local)
2. **Tracker load:** Check tracker logs for slow queries
3. **Connection pool exhaustion:** Check active connections via `netstat`
4. **Large payload:** Check recent requests in logs

### Recovery Steps

**Level 1: Check Tracker Metrics**
1. Query tracker SLOs: `curl http://127.0.0.1:8001/metrics`
2. Look for operations with p95 > 500ms
3. If tracker itself is slow, scale up resources

**Level 2: Connection Pool Reset**
1. Restart the application: `systemctl restart vmodel-tracker`
2. Monitor latency: `tail -f logs/*.log | grep duration`

**Level 3: Timeout Adjustment**
1. Increase timeout in config: `API_TIMEOUT=60` (in seconds)
2. Restart: `systemctl restart vmodel-tracker`
3. Monitor if issue resolves

### Escalation

- **If p95 latency > 5 seconds:** Page on-call engineer
- **SLA:** Latency <500ms p95
- **Escalation:** #incidents Slack channel

---

## Data Inconsistencies

**Symptoms:** Requirement counts don't match, gaps appear/disappear, data drifts from source

### Root Cause Analysis

1. **Count discrepancies:**
   ```bash
   LOCAL_COUNT=$(grep -c "^- \*\*FR-\d+\*\*" FUNCTIONAL_REQUIREMENTS.md)
   TRACKER_COUNT=$(curl -s http://127.0.0.1:8001/api/projects/1/requirements | jq 'length')
   echo "Local: $LOCAL_COUNT, Tracker: $TRACKER_COUNT"
   ```

2. **Check sync history:**
   ```bash
   git log --grep="sync" --oneline | head -10
   ```

3. **Verify markdown vs tracker:**
   ```bash
   # Export tracker requirements
   curl -s http://127.0.0.1:8001/api/projects/1/requirements > tracker_export.json
   # Compare with markdown
   grep "^- \*\*" FUNCTIONAL_REQUIREMENTS.md | wc -l
   ```

### Recovery Steps

**Level 1: Detect Drift**
1. Export current state from tracker
2. Parse markdown files
3. Compare requirement IDs

**Level 2: Rebuild from Source of Truth**
1. Identify source of truth (markdown files are primary)
2. Clear tracker requirements: `DELETE FROM requirements WHERE project_id=1`
3. Re-sync from markdown: `python -m backend.core.vmodel_sync --force`

**Level 3: Manual Reconciliation**
1. Create reconciliation report: `python scripts/audit_requirements.py`
2. Review discrepancies
3. Manually fix via tracker UI or API
4. Document changes in git

### Escalation

- **If data loss occurred:** Restore from backup
- **SLA:** Data consistency verified within 15 minutes
- **Escalation:** Data integrity team

---

## Escalation Procedures

### On-Call Escalation Path

```
Level 1: Application Team (15 min response)
├─ Check logs, restart services
├─ Verify configuration
└─ Contact DevOps if network/infrastructure issue

Level 2: Platform/DevOps Team (30 min response)
├─ Check infrastructure metrics
├─ Verify external service health
├─ Scale resources if needed
└─ Contact Site Reliability Engineer if critical

Level 3: Site Reliability Engineer (on-call rotation)
├─ Deep infrastructure investigation
├─ Database integrity checks
├─ Coordination with external dependencies
└─ Post-incident review
```

### Escalation Contacts

| Role | Slack | Email | Response Time |
|------|-------|-------|----------------|
| Application Lead | @app-lead | lead@company.com | 15 min |
| DevOps Engineer | @devops-oncall | devops@company.com | 30 min |
| SRE | @sre-oncall | sre@company.com | 5 min (critical) |

### Critical Alert Thresholds

- **Error rate > 10%:** Page application team
- **Latency p95 > 5s:** Page DevOps
- **Tracker unavailable > 2min:** Page SRE
- **Data loss detected:** Page SRE + Security

---

## Health Check Endpoints

### Self-Check Commands

```bash
# Check application health
curl http://127.0.0.1:8004/health

# Check tracker connectivity
curl http://127.0.0.1:8001/health

# Check metrics/SLOs
curl http://127.0.0.1:8004/metrics

# Verify requirements sync
curl http://127.0.0.1:8001/api/projects/1/requirements | jq 'length'

# Check recent errors
tail -100 logs/*.log | grep -i error
```

---

## Prevention & Best Practices

1. **Monitor metrics continuously:**
   - Set up dashboards for latency, error rate, availability
   - Alert on SLO violations

2. **Regular backups:**
   - Daily export of tracker data
   - Git commits of all requirement changes

3. **Gradual deployments:**
   - Test changes in staging environment first
   - Use canary deployments for production changes

4. **Documentation:**
   - Keep runbooks current
   - Document all manual interventions
   - Regular drills (monthly)

---

## Questions?

Refer to:
- **Architecture:** See `project-designer/FRAMEWORK.md`
- **Configuration:** See `.env.example`
- **Testing:** See `pytest.ini` and `tests/`
- **Logs:** See `logs/` directory (JSON formatted)

Last updated: June 20, 2026
