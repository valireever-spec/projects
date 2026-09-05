# -*- coding: utf-8 -*-
##oh_utils.py
##
## Shared constants and helper functions for all OpenHAB2 Jython rules.
## Renamed from 000_utils.py -- Jython cannot import modules whose names start
## with a digit, so 000_utils.py was never importable. This file is the
## canonical import target:
##
##   from oh_utils import ctrl_dev, safe_float, DAY, EVENING, WINTER
##
## Last updated: 2026-05-23

from org.eclipse.smarthome.core.types import UnDefType
from core.actions import LogAction, ScriptExecution
from java.math import BigDecimal, RoundingMode
from org.joda.time import DateTime
from org.eclipse.smarthome.core.library.types import OnOffType

ON  = OnOffType.ON
OFF = OnOffType.OFF

# EVENING moved DAY-side 2026-09-04: evening presence now does illum-gated auto-on
# (turn on only when dark & occupied), consistent with the Sufragerie fix. Previously
# in _TOD_NIGHT it fired unconditionally (lit the room even in natural evening light).
_TOD_DAY   = frozenset(["DAY", "AFTERNOON", "EVENING"])
_TOD_NIGHT = frozenset(["MORNING", "NIGHT", "BED"])

# Night-lamp lockout window: [22:30, per-room end). Clock_alarm overrides (wake-up light).
# Per-room end times (minutes from midnight) come from cfg; weekend mornings can run later
# (e.g. DormP 08:30, DormC 11:00). Falls back to 06:30 when a room defines no override.
_LOCK_START_MIN   = 22 * 60 + 30   # 22:30
_LOCK_END_DEFAULT = 6 * 60 + 30    # 06:30

def _room_locked(cfg, items):
    # Clock_alarm override removed 2026-09-05 (no longer used) -> lockout is absolute in-window.
    # try:
    #     if items["Clock_alarm"] == ON:
    #         return False
    # except Exception:
    #     pass
    now = DateTime.now()
    mins = now.getHourOfDay() * 60 + now.getMinuteOfHour()
    is_weekend = now.getDayOfWeek() >= 6   # Joda: MON=1 .. SAT=6, SUN=7
    if is_weekend:
        end = cfg.get("lock_end_weekend_min", cfg.get("lock_end_weekday_min", _LOCK_END_DEFAULT))
    else:
        end = cfg.get("lock_end_weekday_min", _LOCK_END_DEFAULT)
        # School-holiday sleep-in (Halstenbek Schulferien): on weekdays, if this room's
        # Schulfrei flag is ON, use the later vacation wake time (e.g. 08:30).
        sf = cfg.get("schulfrei")
        vac_end = cfg.get("lock_end_vacation_min")
        if sf is not None and vac_end is not None:
            try:
                if items[sf] == ON:
                    end = vac_end
            except Exception:
                pass
    # Window wraps past midnight: [22:30, 24:00) U [00:00, end)
    return mins >= _LOCK_START_MIN or mins < end


# Motion debounce: rooms may require N presence pulses within a rolling window before the
# lamp auto-ons, so an isolated blip (e.g. rolling over in bed) is ignored while continued
# motion (actually getting up) still triggers. State is transient (reset on reload) — fine.
_detect_hist = {}   # room name -> [epoch_ms of recent presence-ON events]

def _passes_repeat_gate(cfg):
    need = cfg.get("require_repeat_detections", 0)
    if need <= 1:
        return True
    now_ms = DateTime.now().getMillis()
    win_ms = cfg.get("repeat_window_sec", 120) * 1000
    name = cfg.get("name", "?")
    hist = [t for t in _detect_hist.get(name, []) if now_ms - t <= win_ms]
    hist.append(now_ms)
    _detect_hist[name] = hist
    return len(hist) >= need

NULL = UnDefType.NULL
UNDEF = UnDefType.UNDEF

# ---------------------------------------------------------------------------
# Time-of-day string constants
# ---------------------------------------------------------------------------

MORNING   = "MORNING"
DAY       = "DAY"
AFTERNOON = "AFTERNOON"
EVENING   = "EVENING"
NIGHT     = "NIGHT"
BED       = "BED"

# ---------------------------------------------------------------------------
# Season string constants
# ---------------------------------------------------------------------------

SPRING = "Spring"
SUMMER = "Summer"
AUTUMN = "Autumn"
WINTER = "Winter"

# ---------------------------------------------------------------------------
# Priza1 (E-bike charger) charge detection thresholds
# Centralised here so 017_Prize and 080_Power use identical values.
# ---------------------------------------------------------------------------

FULL_CURRENT         = u"0.150 A"
TAPER_START_CURRENT  = u"0.350 A"
TAPER_STABLE_SECONDS = 600

# ---------------------------------------------------------------------------
# ctrl_dev
# Send a command/update only if current state differs from desired state.
# ---------------------------------------------------------------------------

def ctrl_dev(device_name, desired_state, items, events, command_type="sendCommand"):
    current_state = items[device_name]
    if str(current_state).strip() == str(desired_state).strip():
        return
    LogAction.logInfo("ctrl_dev", "Sending " + device_name + " -> " + str(desired_state))
    if command_type == "sendCommand":
        events.sendCommand(device_name, desired_state)
    elif command_type == "postUpdate":
        events.postUpdate(device_name, desired_state)

# ---------------------------------------------------------------------------
# safe_float
# Convert any OH item state to float. Returns 0.0 on NULL/UNDEF/error.
# ---------------------------------------------------------------------------

def safe_float(val):
    if val is None or isinstance(val, UnDefType):
        return 0.0
    try:
        return float(str(val).split(" ")[0].strip())
    except Exception:
        return 0.0

# ---------------------------------------------------------------------------
# safe_to_bigdecimal
# Convert an item state to Java BigDecimal. Returns BigDecimal("0") on error.
# ---------------------------------------------------------------------------

def safe_to_bigdecimal(item_name, items, log_name="safe_to_bigdecimal"):
    val = items[item_name]
    if val in [UnDefType.UNDEF, UnDefType.NULL]:
        LogAction.logInfo(log_name, item_name + " is UNDEF or NULL - assuming 0")
        return BigDecimal("0")
    try:
        return val.toBigDecimal()
    except Exception:
        try:
            return BigDecimal(str(val).split(" ")[0].strip())
        except Exception:
            LogAction.logInfo(log_name, "Could not convert " + item_name + " value '" + str(val) + "' to BigDecimal - assuming 0")
            return BigDecimal("0")

# ---------------------------------------------------------------------------
# round_bd
# Round a BigDecimal to N decimal places (HALF_UP).
# ---------------------------------------------------------------------------

def round_bd(value, decimal_places=1):
    return value.setScale(decimal_places, RoundingMode.HALF_UP)

# ---------------------------------------------------------------------------
# is_within_time_range
# Return True if current local time is within [start_hour:start_min, end_hour:end_min].
# ---------------------------------------------------------------------------

def is_within_time_range(start_hour, start_minute, end_hour, end_minute):
    now = DateTime.now()
    now_min = now.getHourOfDay() * 60 + now.getMinuteOfHour()
    return start_hour * 60 + start_minute <= now_min <= end_hour * 60 + end_minute

# ---------------------------------------------------------------------------
# room_presence_handler
# Generic handler for 'XxxPresence changed' rules.
# Identical logic used by Sufragerie, DormP, DormC — only item names differ.
#
# cfg keys:
#   light       — item to turn on/off
#   dark        — DarkXxx item
#   perm        — PermXxx item
#   illum_sw    — Xxx_Illuminance_Switch item
#   delay_timer — DelayTimerXxx item (read live — picks up UI changes immediately)
#   dt_default  — fallback seconds if delay_timer is NULL (default 600)
#
# timer_box: list[1] of the occupancy timer, e.g. [None].
#   Use a module-level list so the mutable reference survives across calls
#   (Python 2 has no nonlocal).
#
# Improvement vs original: reads DelayTimer live so DT changes via the UI
# take effect on the next presence event rather than only after OH restart.
# ---------------------------------------------------------------------------

def room_presence_handler(cfg, event, timer_box, items, events):
    if event.itemState != ON:
        return

    light      = cfg["light"]
    dark_item  = cfg["dark"]
    perm_item  = cfg["perm"]
    illum_item = cfg["illum_sw"]
    delay_item = cfg["delay_timer"]

    # Night lamp lockout (per-room, weekend-aware — see _room_locked). Checked before
    # dark/perm so it overrides them, mirroring the Sufragerie inline rule.
    try:
        _locked = _room_locked(cfg, items)
    except Exception:
        _locked = False
    if _locked:
        events.sendCommand(light, "OFF")
        return

    try:
        on_secs = int(float(str(items[delay_item]).split(" ")[0]))
        if on_secs <= 0:
            on_secs = cfg.get("dt_default", 600)
    except Exception:
        on_secs = cfg.get("dt_default", 600)

    tod = str(items["vTimeOfDay"]).strip()

    def _timeout():
        events.sendCommand(light, "OFF")

    def _fire():
        if timer_box[0] is None or timer_box[0].hasTerminated():
            events.sendCommand(light, "ON")
            timer_box[0] = ScriptExecution.createTimer(DateTime.now().plusSeconds(on_secs), _timeout)
        else:
            timer_box[0].reschedule(DateTime.now().plusSeconds(on_secs))
            events.sendCommand(light, "ON")

    if items[dark_item] == ON:
        events.sendCommand(light, "OFF")
        return

    if items[perm_item] == ON:
        events.sendCommand(light, "ON")
        return

    # Motion debounce (opt-in per room): ignore isolated presence blips so bed-movement
    # doesn't light the room; overrides above (lockout/dark/perm) are unaffected.
    if not _passes_repeat_gate(cfg):
        return

    # Dark==OFF, Perm==OFF
    if tod in _TOD_DAY:
        if items[illum_item] == ON:
            _fire()
        else:
            # Enough natural light — set timer only, do not turn light on
            if timer_box[0] is None or timer_box[0].hasTerminated():
                timer_box[0] = ScriptExecution.createTimer(DateTime.now().plusSeconds(on_secs), _timeout)
    elif tod in _TOD_NIGHT:
        _fire()


# ---------------------------------------------------------------------------
# room_holddown_handler
# Generic handler for 'XxxPresence received command' (holddown/delay) rules.
# Used by DormP and DormC. Sufragerie is excluded (parallel Lampa circuit).
#
# cfg keys: hd_sw, hd_val, dt, dt_default, delay_timer, daytime, illum_sw, dark, perm
#
# hd_state: {"timer": None, "holddown": None, "incr": 0}
#   Module-level dict — modified in place so state persists across calls.
#
# Bug fixed vs original: timer callback assigned incr=0 as a local variable
#   (no effect). Here hd_state["incr"] = 0 correctly resets the shared counter.
# ---------------------------------------------------------------------------

def room_holddown_handler(cfg, event, hd_state, items, events):
    if event.itemCommand != ON:
        return

    hd_sw      = cfg["hd_sw"]
    hd_val     = cfg["hd_val"]
    dt_item    = cfg["dt"]
    delay_item = cfg["delay_timer"]
    daytime    = cfg["daytime"]
    illum_item = cfg["illum_sw"]
    dark_item  = cfg["dark"]
    perm_item  = cfg["perm"]
    dt_default = cfg.get("dt_default", 7)

    base_hd = (int(float(str(items[dt_item]))) * 60) / 5

    if hd_state["timer"] is None or hd_state["timer"].hasTerminated():
        hd_state["incr"]     = 0
        hd_state["holddown"] = base_hd
        events.sendCommand(hd_sw, "ON")
        def _hd_timeout():
            events.sendCommand(hd_sw, "OFF")
            hd_state["incr"] = 0
        hd_state["timer"] = ScriptExecution.createTimer(DateTime.now().plusSeconds(base_hd), _hd_timeout)
    else:
        hd_state["incr"] += 1
        time_fract = base_hd / hd_state["incr"]
        if items[daytime] == OFF:
            hd_state["holddown"] = hd_state["holddown"] + time_fract
        if items[daytime] == ON:
            hd_state["holddown"] = int(float(str(items[dt_item]))) * 60
        events.sendCommand(hd_val, str(hd_state["holddown"]))

    if int(float(str(items[dt_item]))) == 0:
        events.postUpdate(dt_item, str(dt_default))

    d_state = items[delay_item]
    if d_state == 0 or d_state == NULL:
        events.sendCommand(delay_item, str(int(float(str(items[dt_item]))) * 60 + int(float(str(items[hd_val])))))

    if (items[perm_item] == OFF or items[dark_item] == OFF) and items[illum_item] == ON:
        dt_hd = int(float(str(items[dt_item]))) * 60 + int(float(str(items[hd_val])))
        hd_state["timer"].reschedule(DateTime.now().plusSeconds(hd_state["holddown"]))
        events.sendCommand(delay_item, str(dt_hd))
        events.sendCommand(hd_sw, "ON")
