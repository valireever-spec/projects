#!/bin/bash

# halt-reboot.sh - Safely shutdown openHAB and system

LOG_FILE="/var/log/openhab2/halt-reboot.log"

log_msg() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

log_msg "[START] Shutdown sequence initiated"

# Step 1: Backup RRD4J database
log_msg "[1/3] Backing up RRD4J database..."
if /etc/openhab2/scripts/backup_rrd4j.sh create >> "$LOG_FILE" 2>&1; then
    log_msg "[OK] RRD4J backup completed"
else
    log_msg "[WARN] RRD4J backup failed (continuing with shutdown)"
fi

# Step 2: Stop OpenHAB gracefully before reboot
log_msg "[2/3] Stopping OpenHAB gracefully..."
if sudo systemctl stop openhab2; then
    log_msg "[OK] OpenHAB stopped"
else
    log_msg "[WARN] OpenHAB stop command failed (continuing with shutdown)"
fi

# Step 3: Reboot system
log_msg "[3/3] Rebooting system..."
sudo /sbin/shutdown -r now
