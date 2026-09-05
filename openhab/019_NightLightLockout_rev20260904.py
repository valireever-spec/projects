# 019_NightLightLockout — 2026-09-04
# Enforces a hard "no lamp auto-on" window between 22:30 and 06:30.
# Approach B (dedicated lockout switch) chosen over retiming TOD boundaries so that
# fireplace / Priza8 / night charging-bands (which key off vTimeOfDay==NIGHT) are untouched.
#
# NightLightLockout == ON  ==> lamp turn-on paths in 011/017/050 are blocked
#   (they check: NightLightLockout==ON and Clock_alarm!=ON).
# Clock_alarm == ON is the single override (wake-up light exception), matching the
# pre-existing BED/MORNING Clock_alarm behaviour.
#
# This script owns ONLY the switch state (crons + startup) and a force-off sweep when
# the window opens. It does not turn anything ON.

from core.rules import rule
from core.triggers import when
from core.actions import ScriptExecution, LogAction
from org.joda.time import DateTime
from core.jsr223.scope import events, items

# Lamps that must go dark for the night. Kids' RGB night-lights (Led_Contr_Alex/Adina)
# are intentionally NOT included — they are deliberate sleep night-lights.
_LOCKOUT_LAMPS = [
    "gBec_LampaSufra",
    "Priza5_Power",
    "Striplight_Alex",
    "Striplight_Adina",
]

LOCK_START_H = 22
LOCK_START_M = 30
LOCK_END_H = 6
LOCK_END_M = 30
LOCK_END_WEEKEND_H = 8      # weekend sleep-in: window ends 08:30 (Sufragerie + DormP)
LOCK_END_WEEKEND_M = 30     # (DormC extends further to 11:00 via its own _room_locked in oh_utils)


def _in_lockout_window():
    now = DateTime.now()
    mins = now.getHourOfDay() * 60 + now.getMinuteOfHour()
    start = LOCK_START_H * 60 + LOCK_START_M   # 1350 (22:30)
    if now.getDayOfWeek() >= 6:               # Joda: SAT=6, SUN=7
        end = LOCK_END_WEEKEND_H * 60 + LOCK_END_WEEKEND_M   # 510 (08:30)
    else:
        end = LOCK_END_H * 60 + LOCK_END_M                   # 390 (06:30)
    # Window wraps past midnight: [22:30, 24:00) U [00:00, end)
    return mins >= start or mins < end


def _apply_state(reason):
    want = "ON" if _in_lockout_window() else "OFF"
    cur = str(items["NightLightLockout"])
    if cur != want:
        events.sendCommand("NightLightLockout", want)
        LogAction.logInfo("NightLightLockout", "%s -> %s (%s)" % (cur, want, reason))


@rule("NightLightLockout start", description="Open the no-light window at 22:30", tags=["cron", "NightLightLockout"])
@when("Time cron 0 30 22 * * ? *")
def nll_start(event):
    _apply_state("cron 22:30")


@rule("NightLightLockout end", description="Close the no-light window at 06:30 (weekday)", tags=["cron", "NightLightLockout"])
@when("Time cron 0 30 6 * * ? *")
def nll_end(event):
    _apply_state("cron 06:30")


@rule("NightLightLockout end weekend", description="Close the no-light window at 08:30 (weekend)", tags=["cron", "NightLightLockout"])
@when("Time cron 0 30 8 * * ? *")
def nll_end_weekend(event):
    _apply_state("cron 08:30")


@rule("NightLightLockout init", description="Set lockout state on startup / hourly safety re-check", tags=["NightLightLockout"])
@when("System started")
@when("Time cron 0 0 * * * ? *")
def nll_init(event):
    _apply_state("init/hourly")


@rule("NightLightLockout force off", description="Sweep lamps off when the window opens", tags=["NightLightLockout"])
@when("Item NightLightLockout changed to ON")
def nll_force_off(event):
    # Clear the 'permanent/forced ON' latches so no room lamp can stay/come on overnight.
    for sw in ("PermSufra", "PermSufra_Forced",
               "PermDormP", "PermDormP_Forced",
               "PermDormC", "PermDormC_Forced"):
        try:
            if str(items[sw]) != "OFF":
                events.sendCommand(sw, "OFF")
        except:
            pass
    # Clock_alarm override removed 2026-09-05 (no longer used) -> always force lamps off.
    # if items["Clock_alarm"] == ON:
    #     LogAction.logInfo("NightLightLockout", "window opened but Clock_alarm ON -> not forcing lamps off")
    #     return
    for it in _LOCKOUT_LAMPS:
        try:
            events.sendCommand(it, "OFF")
        except:
            pass
    try:
        events.postUpdate("Bec_TechPro8_Dimmer", "0")
        events.postUpdate("Bec_TechPro9_Dimmer", "0")
        events.sendCommand("OffFlagLamp", "ON")
    except:
        pass
    LogAction.logInfo("NightLightLockout", "window opened -> forced lamps OFF")
