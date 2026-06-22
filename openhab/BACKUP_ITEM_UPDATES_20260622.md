# Backup Items Sitemap Updates — 2026-06-22

## Problem
Backup items (`Backup_Openhab2`, `Backup_rrd4j`) existed in OpenHAB but had **no status feedback on sitemaps**:
- ❌ Clicking the switch triggered the rule but showed no "In Progress" indicator
- ❌ No confirmation when backup completed
- ❌ No timestamp of last successful backup
- ❌ No visibility into NAS backup status

## Solution

### 1. New Status Items Added
**File:** `/etc/openhab2/items/backup.items`

```
// Status items to display in sitemap
String Backup_Openhab2_Status "OpenHAB Backup Status" <backup>
DateTime Backup_Openhab2_LastRun "OpenHAB Backup Last Run" <time>
String Backup_rrd4j_Status "RRD4J Backup Status" <database>
DateTime Backup_rrd4j_LastRun "RRD4J Backup Last Run" <time>

// NAS-related status items
String NAS_Status "NAS Status" <network>
DateTime NAS_LastBackup "NAS Last Backup" <time>
Number NAS_Backup_Size "NAS Backup Size" <database> [%.0f MB]
```

### 2. Automation Rule Updated
**File:** `/etc/openhab2/automation/jsr223/python/personal/021_Backup_Handler_rev20260621.py`

Now updates status items:
- **On start:** `Backup_Openhab2_Status = "In Progress"`
- **On success:** 
  - `Backup_Openhab2_Status = "Success"`
  - `Backup_Openhab2_LastRun = <current timestamp>`
- **On failure:** `Backup_Openhab2_Status = "Failed"`

Same logic applies to RRD4J backup.

### 3. Sitemap Integration
Add to your sitemap (`/etc/openhab2/sitemaps/home.sitemap`):

```
Frame label="Backups" {
    // Backup triggers
    Switch item=Backup_Openhab2 label="Backup OpenHAB Now"
    Text item=Backup_Openhab2_Status label="Status: [%s]"
    Text item=Backup_Openhab2_LastRun label="Last Run: [%1$tY-%1$tm-%1$td %1$tH:%1$tM]"

    Switch item=Backup_rrd4j label="Backup RRD4J Now"
    Text item=Backup_rrd4j_Status label="Status: [%s]"
    Text item=Backup_rrd4j_LastRun label="Last Run: [%1$tY-%1$tm-%1$td %1$tH:%1$tM]"

    // NAS status
    Text item=NAS_Status label="NAS: [%s]"
    Text item=NAS_LastBackup label="NAS Backup: [%1$tY-%1$tm-%1$td %1$tH:%1$tM]"
    Text item=NAS_Backup_Size label="Backup Size: [%,.0f MB]"
}
```

## Deployment Status
- ✅ `/etc/openhab2/items/backup.items` — deployed 2026-06-22
- ✅ `/etc/openhab2/automation/jsr223/python/personal/021_Backup_Handler_rev20260621.py` — deployed 2026-06-22

## What You'll See on Sitemaps Now
**Before backup:**
```
Backup OpenHAB Now     [OFF]
Status: [    ]  (empty/unknown)
Last Run: [    ]
```

**During backup:**
```
Backup OpenHAB Now     [ON]
Status: [In Progress]
Last Run: [2026-06-22 19:30]  (previous run)
```

**After success:**
```
Backup OpenHAB Now     [OFF]
Status: [Success]
Last Run: [2026-06-22 19:35]  (new timestamp)
```

**On failure:**
```
Backup OpenHAB Now     [OFF]
Status: [Failed]
Last Run: [2026-06-22 19:30]  (unchanged)
```

## OpenHAB Reload Required
After deploying the updated items and rules:
1. **Reload items:** Go to OpenHAB UI → Settings → Developer Tools → Items → RELOAD
2. **Reload rules:** Go to OpenHAB UI → Settings → Developer Tools → Rules → RELOAD
   - Or restart OpenHAB: `sudo systemctl restart openhab2`

## Future Enhancements
- **NAS backup status:** Update `NAS_Status`, `NAS_LastBackup`, `NAS_Backup_Size` from `backup2nas.sh` script
- **Backup size tracking:** Log backup file sizes to OpenHAB items
- **Failed backup alerts:** Send MQTT notification or log alert when backup fails
- **Scheduled backups:** Trigger `Backup_Openhab2` on a timer (050_Reguli or dedicated rule)

## Troubleshooting
If status items aren't updating:
1. **Check items exist:** `grep Backup_Openhab2_Status /etc/openhab2/items/backup.items`
2. **Check rule loaded:** OpenHAB UI → Settings → Developer Tools → Rules → look for "Backup OpenHAB 2 Configuration"
3. **Check logs:** `tail -50 /var/log/openhab2/openhab.log | grep BACKUP`
4. **Reload OpenHAB:** `sudo systemctl restart openhab2`

## Git Commit
This change should be committed with the NAS backup fixes as a single feature: "Add backup status tracking to sitemaps"
