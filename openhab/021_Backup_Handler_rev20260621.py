# Backup Handler for OpenHAB 2
# Triggered when Backup_Openhab2 or Backup_rrd4j items receive ON command
# Add this to a new Python script file or to an existing automation script

from core.rules import rule
from core.triggers import when
from core.actions import Exec
from core.jsr223.scope import events
from core.actions import LogAction
from org.eclipse.smarthome.model.script.actions.Exec import executeCommandLine
from org.joda.time import DateTime

@rule("Backup OpenHAB 2 Configuration", description="Execute full OpenHAB backup", tags=["Backup"])
@when("Item Backup_Openhab2 received command ON")
def backup_openhab2(event):
    """Execute full OpenHAB 2 configuration backup"""
    LogAction.logInfo("BACKUP", "Starting OpenHAB 2 full backup")

    # Set status to "In Progress" for sitemap visibility
    events.postUpdate("Backup_Openhab2_Status", "In Progress")

    try:
        # Execute backup script
        result = executeCommandLine("/etc/openhab2/scripts/backup_openhab.sh", 300000)  # 5 min timeout
        LogAction.logInfo("BACKUP", "OpenHAB backup completed: {}".format(result))

        # Update status and timestamp on success
        events.postUpdate("Backup_Openhab2_Status", "Success")
        events.postUpdate("Backup_Openhab2_LastRun", DateTime.now().toString("yyyy-MM-dd'T'HH:mm:ss"))

        # Set item back to OFF after backup completes
        events.sendCommand("Backup_Openhab2", "OFF")
    except Exception as e:
        LogAction.logError("BACKUP_ERROR", "Backup failed: {}".format(str(e)))
        events.postUpdate("Backup_Openhab2_Status", "Failed")
        events.sendCommand("Backup_Openhab2", "OFF")


@rule("Backup RRD4J Database", description="RRD4J database backup handler", tags=["Backup"])
@when("Item Backup_rrd4j received command ON")
def backup_rrd4j(event):
    """Backup RRD4J database files"""
    LogAction.logInfo("BACKUP", "RRD4J backup activated")

    # Set status to "In Progress" for sitemap visibility
    events.postUpdate("Backup_rrd4j_Status", "In Progress")

    try:
        # Copy RRD4J files to timestamped backup
        import os

        timestamp = DateTime.now().toString("yyyyMMdd_HHmmss")
        rrd_src = "/var/lib/openhab2/rrd4j"
        rrd_backup = "/var/backups/openhab2/rrd4j_backup_{}".format(timestamp)

        # Create backup directory (Jython 2.7: no exist_ok kwarg)
        if not os.path.exists("/var/backups/openhab2"):
            os.makedirs("/var/backups/openhab2")

        # Use tar to backup RRD4J
        cmd = "tar -czf {}.tar.gz -C /var/lib/openhab2 rrd4j".format(rrd_backup)
        result = executeCommandLine(cmd, 60000)

        LogAction.logInfo("BACKUP", "RRD4J backup completed: {}.tar.gz".format(rrd_backup))

        # Update status and timestamp on success
        events.postUpdate("Backup_rrd4j_Status", "Success")
        events.postUpdate("Backup_rrd4j_LastRun", DateTime.now().toString("yyyy-MM-dd'T'HH:mm:ss"))
        events.sendCommand("Backup_rrd4j", "OFF")
    except Exception as e:
        LogAction.logError("BACKUP_ERROR", "RRD4J backup failed: {}".format(str(e)))
        events.postUpdate("Backup_rrd4j_Status", "Failed")
        events.sendCommand("Backup_rrd4j", "OFF")
