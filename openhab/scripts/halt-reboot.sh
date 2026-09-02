#!/bin/bash

# halt-reboot.sh - Safely shutdown openHAB and reboot the system

LOG_FILE="/var/log/openhab2/halt-reboot.log"

log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

log_msg "[START] Shutdown sequence initiated"

# Step 1: Backup RRD4J database (while openHAB is still up)
log_msg "[1/3] Backing up RRD4J database..."
if /etc/openhab2/scripts/backup_rrd4j.sh create >> "$LOG_FILE" 2>&1; then
    log_msg "[OK] RRD4J backup completed"
else
    log_msg "[WARN] RRD4J backup failed (continuing with shutdown)"
fi

# Step 2: Schedule the reboot FIRST, so it is owned by systemd and survives
# openHAB being stopped in step 3.
#
# WHY: this script is normally spawned by the openHAB process (executeCommandLine).
# If we stopped openHAB *before* triggering the reboot, systemd's cgroup teardown
# for openhab2.service would kill this script mid-run (this happened 2026-09-01:
# openHAB stopped but the reboot never fired, leaving the box up with openHAB down).
# Scheduling the reboot first hands it to systemd/logind, which is independent of
# openHAB's process tree.
log_msg "[2/3] Scheduling reboot (+1 min, owned by systemd)..."
if sudo /sbin/shutdown -r +1 "openHAB maintenance reboot"; then
    log_msg "[OK] Reboot scheduled"
else
    log_msg "[WARN] Failed to schedule reboot"
fi

# Step 3: Stop OpenHAB gracefully now; the pending reboot remains scheduled
# even if this script is killed when openHAB stops.
log_msg "[3/3] Stopping OpenHAB gracefully..."
if sudo systemctl stop openhab2; then
    log_msg "[OK] OpenHAB stopped; reboot pending"
else
    log_msg "[WARN] OpenHAB stop command failed (reboot still pending)"
fi
