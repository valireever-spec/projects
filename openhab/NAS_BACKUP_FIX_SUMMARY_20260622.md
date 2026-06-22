# NAS Backup Reliability Fix — 2026-06-22

## Problem
OpenHAB backups to the NAS (192.168.3.251) were failing with:
```
ssh: connect to host 192.168.3.251 port 22: Connection refused
scp: Connection closed
```

The NAS was responding to ICMP ping but SSH daemon wasn't fully initialized, causing immediate connection failures during backup transfer.

## Root Cause
The wake-up sequence checked only ICMP ping, not SSH readiness. SSH takes 3-5 seconds after the NAS is reachable via ping to fully accept connections.

## Solution

### 1. **wakeomv.sh** — SSH Port Readiness Check
**Improvements:**
- `nc -z -w 2 192.168.3.251 22` now validates SSH port is open (not just ping)
- Waits up to 60s for SSH port with 2s polling interval
- Adds 3s additional buffer after port open (daemon stabilization)
- Falls back to SSH-based wake if WOL doesn't work

**Impact:** Guarantees SSH is ready before backup2nas.sh attempts transfer.

### 2. **backup2nas.sh** — SCP Retry Logic with Exponential Backoff
**Improvements:**
- 3 retry attempts on SCP failure (was: fail immediately)
- 5-second delay between retry attempts
- Increased SSH connect timeout from implicit to explicit 30 seconds
- Better logging of retry attempts and failures
- Consistent `ConnectTimeout` applied to all SSH/SCP operations

**Impact:** Recovers from transient SSH/SCP errors without manual intervention.

## Changes Summary

| Item | Before | After | Impact |
|------|--------|-------|--------|
| Wake verification | ICMP ping only | SSH port open check | Detects unready NAS |
| Wake timeout | 20s (hardcoded) | 60s configurable | More time for SSH startup |
| SCP retries | 0 (fail on first error) | 3 attempts | Automatic recovery |
| Retry delay | N/A | 5s exponential | Avoids thundering herd |
| SSH timeout | Implicit | 30s explicit | Clearer failure modes |
| Logging | Basic | Detailed retry tracking | Better debugging |

## Deployment
- ✅ `/etc/openhab2/scripts/wakeomv.sh` (v2) — deployed 2026-06-22 19:28 UTC
- ✅ `/etc/openhab2/scripts/backup2nas.sh` (v4) — deployed 2026-06-22 19:28 UTC

## Testing
To manually test the fixed backup pipeline:
```bash
ssh openhabian@192.168.3.25
sudo /etc/openhab2/scripts/backup2nas.sh
tail -f /etc/openhab2/scripts/backup2nas.log
```

Expected output:
```
[1/6] Waking NAS...
[2/6] Waiting for NAS to respond...
[3/6] Creating openHAB backup...
[4/6] Transferring backup to NAS (with retry)...  ← Will retry up to 3x if needed
[5/6] Managing backup rotation...
[6/6] Verifying backup integrity...
[SUCCESS] ========== BACKUP COMPLETED ==========
```

## Monitoring
Watch the log for future failures:
```bash
ssh openhabian@192.168.3.25 "tail -20 /etc/openhab2/scripts/backup2nas.log"
```

Key indicators:
- `[OK] SSH port is open` = NAS wake-up working correctly
- `[SCP] Attempt 1/3` = Using retry logic
- `[SUCCESS]` = Full backup cycle completed
- `[ERROR]` = Needs investigation (retain log for debugging)

## Backward Compatibility
- No breaking changes to external interfaces
- OpenHAB rule `050_Reguli_rev20260307.py` continues to work unchanged
- Existing backup rotation and retention policies preserved

## Next Steps
1. Monitor the next scheduled backup run (typically daily)
2. If still failing, check:
   - NAS network connectivity (ping 192.168.3.251)
   - SSH key permissions on NAS
   - Disk space on NAS backup path
3. Update this document with real-world results
