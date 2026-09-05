# 023_SchoolHolidaySync_rev20260905.py
# Daily auto-sync of Schulfrei_Alex / Schulfrei_Adina from the Schleswig-Holstein
# (Halstenbek) school-holiday calendar. When today is a SH Schulferien day the flags
# go ON, so the kids' bedroom lockout uses the vacation wake time (08:30 on weekdays)
# -- see oh_utils._room_locked / 050_Reguli _DORMP/_DORMC cfg.
#
# Data: openholidaysapi.org (subdivision DE-SH). Fetch is done by a shell wrapper
# (/etc/openhab2/scripts/fetch_sh_holidays.sh) which caches the last good result and
# falls back to it on API failure, so an outage cannot break the wake logic.
# NOTE: cron and System-started are SEPARATE rules on purpose (mixing "System started"
# with other triggers on one JSR223 rule can load it uninitialized -- see openhab notes).

from core.rules import rule
from core.triggers import when
from core.actions import LogAction
from org.eclipse.smarthome.model.script.actions.Exec import executeCommandLine
from org.joda.time import DateTime
from core.jsr223.scope import events, items
import json

FLAGS = ["Schulfrei_Alex", "Schulfrei_Adina"]
SCRIPT = "/etc/openhab2/scripts/fetch_sh_holidays.sh"


def _sync(reason):
    now = DateTime.now()
    frm = now.minusDays(31).toString("yyyy-MM-dd")
    to = now.plusDays(62).toString("yyyy-MM-dd")
    raw = executeCommandLine(SCRIPT + " " + frm + " " + to, 30000)
    if not raw or not raw.strip().startswith("["):
        LogAction.logWarn("SchoolHolidays", "sync (%s): no data (API+cache failed) -> flags unchanged" % reason)
        return
    try:
        holidays = json.loads(raw)
    except Exception as e:
        LogAction.logWarn("SchoolHolidays", "sync (%s): parse error (%s) -> flags unchanged" % (reason, e))
        return
    today = now.toString("yyyy-MM-dd")
    active = None
    for h in holidays:
        s = str(h.get("startDate", ""))[:10]
        e = str(h.get("endDate", ""))[:10]
        if s and e and s <= today <= e:
            active = h
            break
    want = "ON" if active else "OFF"
    name = ""
    if active:
        try:
            name = str(active.get("name", [{}])[0].get("text", ""))
        except Exception:
            name = ""
    for it in FLAGS:
        try:
            if str(items[it]) != want:
                events.sendCommand(it, want)
        except Exception:
            pass
    LogAction.logInfo("SchoolHolidays",
                      "sync (%s): today=%s holiday=%s%s -> %s"
                      % (reason, today, bool(active), (" (" + name + ")" if name else ""), want))


@rule("School holiday sync SH (cron)", description="Daily SH Schulferien -> Schulfrei flags", tags=["cron", "SchoolHolidays"])
@when("Time cron 0 0 4 * * ? *")
def school_holiday_sync_cron(event):
    _sync("cron 04:00")


@rule("School holiday sync SH (startup)", description="Set Schulfrei flags on startup", tags=["SchoolHolidays"])
@when("System started")
def school_holiday_sync_startup(event):
    _sync("startup")
