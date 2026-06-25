# OH 2.5.12: OnOffType / UnDefType from org.eclipse.smarthome.core.* (ESH). Normalized 2026-05-02.

from core.rules import rule
from core.triggers import when
from core.jsr223.scope import events, items
from core.actions import ScriptExecution, LogAction

from org.eclipse.smarthome.core.library.types import OnOffType
from org.eclipse.smarthome.core.types import UnDefType
from org.joda.time import DateTime

from java.math import BigDecimal, RoundingMode
from java.time import LocalTime
from java.util.concurrent.locks import ReentrantLock

# =========================================================
# LOCK
# =========================================================
lock = ReentrantLock()

# =========================================================
# SUSTAINABLE LOGGING FRAMEWORK (Added 2026-06-21)
# =========================================================
class Logger:
    """Sustainable, deduplicating logger for automation scripts."""

    def __init__(self, name):
        self.name = name
        self.last_logged = {}
        self.SPAM_THRESHOLD_SEC = 60

    def info(self, category, message, *args):
        """Log info message with deduplication."""
        try:
            msg = message.format(*args) if args else message
            key = (category, message)
            if self._should_log(key):
                LogAction.logInfo(self.name, "[{}] {}".format(category, msg))
                self.last_logged[key] = DateTime.now().getMillis()
        except Exception as e:
            LogAction.logInfo("{}_ERR".format(self.name), "Logging failed: {}".format(str(e)))

    def debug(self, category, message, *args):
        """Log debug message (only if DEBUG_VERBOSE)."""
        if DEBUG_VERBOSE:
            try:
                msg = message.format(*args) if args else message
                LogAction.logInfo("{}_DBG".format(self.name), "[{}] {}".format(category, msg))
            except:
                pass

    def error(self, category, message, *args):
        """Log error message (always logged)."""
        try:
            msg = message.format(*args) if args else message
            LogAction.logInfo("{}_ERR".format(self.name), "[{}] {}".format(category, msg))
        except Exception as e:
            LogAction.logInfo("{}_ERR".format(self.name), "Error logging failed: {}".format(str(e)))

    def _should_log(self, key):
        """Deduplicate: only log if different message or > SPAM_THRESHOLD_SEC since last."""
        if key not in self.last_logged:
            return True
        age_ms = DateTime.now().getMillis() - self.last_logged[key]
        return age_ms >= (self.SPAM_THRESHOLD_SEC * 1000)

logger = Logger("ECO")  # Sustainable logging framework

# =========================================================
# CONFIG
# =========================================================
MAX_ABS = BigDecimal("10000")
RECENT_WINDOW_MS = 7000

# Power direction thresholds (Shelly convention: + import, - export)
IMPORT_THRESHOLD = BigDecimal("50")     # positive = import
EXPORT_THRESHOLD = BigDecimal("-50")    # negative = export
DEADBAND = BigDecimal("30")
DIRECTION_HYST = BigDecimal("20")

# Filter behavior
WINDOW_SIZE = 7
ALPHA_RISE = 0.5
ALPHA_FALL = 0.6
MAX_ALPHA = 0.5
SIGN_RESET_DELTA = BigDecimal("250")
LARGE_JUMP_RESET = BigDecimal("2000")
SEQUENCE_MIN_RUNTIME = 12  # 8 seconds

# Sanity / spike handling
REL_DELTA = BigDecimal("3.0")
DISABLE_THRESHOLD = 5
INVALID_LIMIT = 8
#ABS_DELTA_CLAMP = bd(1200)  # tune: 800..2000 depending on sensor noise

# State transition timing
DEBOUNCE_SEC = 4
MIN_ON_TIME = 5
MIN_OFF_TIME = 5
INTENT_MIN_HOLD_SEC = 10
NEUTRAL_GRACE_SEC = 15

# Watchdog / scheduling
PWR_STALE_SEC = 20
FILTER_STALE_SEC = 20
SEQ_STEP_SEC = 3
SEQ_STALL_SEC = 25
SCHED_DELAY_MS = 150
RETRY_LOCK_MS = 100
BURST_GUARD_MS = 100

# ECO command gating
ECO_CMD_COOLDOWN_SEC = 20
ECO_REASSERT_SEC = 0

# String Item (define in .items) — sitemap text for which Priza the ECO sequence is stepping.
ECO_SEQUENCE_DISPLAY_ITEM = "Eco_Sequence_ActivePriza"

# =========================================================
# QUIET LOGGING PROFILE
# =========================================================
# 0 = silent, 1 = important, 2 = debug
LOG_LEVEL = 1
# periodic summaries (seconds)
LOG_SUMMARY_SEC = 15
LOG_STATE_CHANGE_ONLY = True  # suppress repeated same-state chatter
DEBUG_VERBOSE = False  # Disabled after L4 investigation (2026-06-25)

# =========================================================
# DEVICES
# =========================================================
devices_on = [
    "Priza12_Power_auto",
    "Priza7_Power",
    "Priza3_Power",
    "Priza4_Power_auto",
    "Priza9_Power",
    "Priza1_Power_auto"
]
devices_off = list(reversed(devices_on))


def eco_sequence_display(text):
    """Publish current ECO outlet step for Basic UI / sitemap Text widget."""
    try:
        events.postUpdate(ECO_SEQUENCE_DISPLAY_ITEM, str(text))
    except Exception:
        pass


# =========================================================
# STATE
# =========================================================
# Valid readings / freshness
last_valid = {"L1": None, "L2": None, "L3": None, "L4": None}
invalid_count = {"L1": 0, "L2": 0, "L3": 0}
phase_disabled = {"L1": False, "L2": False, "L3": False}
last_update = {"L1": 0, "L2": 0, "L3": 0, "L4": 0}
last_eco_cmd = None
last_eco_cmd_ts = None

# Filter / reconstruction
filtered_power = None
power_window = []
last_total = None
last_raw_power = None
last_filtered_update = None
recon_state = "INIT"

# Direction / intent
direction_state = "NEUTRAL"       # IMPORT / EXPORT / NEUTRAL
intent_state = "NEUTRAL_HOLD"     # IMPORT_MODE / EXPORT_MODE / NEUTRAL_HOLD
last_intent_change = None
neutral_since = None

# PWR command/state timing
last_state_change = None           # when PWRConsumption item actually changed
last_pwr_cmd = None                # when we last sent command to PWRConsumption
pending_state = None

# Debounce
debounce_timer = None
debounce_pending_state = None

# Sequence
sequence_mode = None               # ON / OFF / None
sequence_timer = None
sequence_index = 0
sequence_last_progress = None

# Scheduler
update_timer = None
last_exec = None

# Logs / monitor
log_counter = 0

last_summary_ts = None
last_logged = {
    "direction": None,
    "intent": None,
    "eco_cmd": None,
    "pwr_cmd": None,
    "seq_start": None
}

def _should_log(level):
    return LOG_LEVEL >= level

def log_once(key, value, msg, level=1):
    """
    Log only when value changes (if LOG_STATE_CHANGE_ONLY=True).
    """
    if LOG_STATE_CHANGE_ONLY:
        if last_logged.get(key) == value:
            return
        last_logged[key] = value

    if level == 1:
        log_important(msg)
    else:
        log_debug(msg)

def log_summary_tick():
    """
    Call from watchdog (every 5s cron). Emits one compact line every LOG_SUMMARY_SEC.
    """
    global last_summary_ts

    now_t = now()
    if last_summary_ts is not None:
        age = (now_t.getMillis() - last_summary_ts.getMillis()) / 1000.0
        if age < LOG_SUMMARY_SEC:
            return

    last_summary_ts = now_t

    pwr = items["PWRConsumption"] if items["PWRConsumption"] not in [NULL, UNDEF] else "UNDEF"
    eco = items["Eco_Power_Switch"] if items["Eco_Power_Switch"] not in [NULL, UNDEF] else "UNDEF"

    raw_s = str(last_raw_power) if last_raw_power is not None else "None"
    fil_s = str(filtered_power) if filtered_power is not None else "None"
    seq_s = "{}@{}".format(sequence_mode, sequence_index) if sequence_mode is not None else "None"

    log_important(
        "SUM raw={} filt={} dir={} intent={} pwr={} eco={} seq={}".format(
            raw_s, fil_s, direction_state, intent_state, pwr, eco, seq_s
        )
    )

# =========================================================
# HELPERS
# =========================================================
def now():
    return DateTime.now()

def bd(v):
    return BigDecimal(str(v))

def log_important(msg):
    LogAction.logInfo("ECO", msg)

def log_debug(msg):
    if DEBUG_VERBOSE:
        LogAction.logInfo("ECO_DBG", msg)

def cancel_timer(t):
    if t is not None:
        try:
            t.cancel()
        except:
            pass

def safe_bd(item_name):
    v = items[item_name]
    if v is None or isinstance(v, UnDefType):
        return bd(0)
    v_str = str(v).upper().strip()
    if v_str in ["ON", "OFF", "TRUE", "FALSE"]:  # Skip ON/OFF state values
        return bd(0)
    try:
        return v.toBigDecimal()
    except:
        log_important("WARN: {} invalid value -> {}".format(item_name, v))
        return bd(0)

def secs_since(ts):
    if ts is None:
        return None
    return (now().getMillis() - ts.getMillis()) / 1000.0

def is_priza9_allowed():
    t = LocalTime.now()
    return (LocalTime.of(8, 30) <= t <= LocalTime.of(15, 55)) or \
           (LocalTime.of(16, 30) <= t <= LocalTime.of(18, 59))

def signum(x):
    return x.signum()

def send_eco_if_needed(cmd):
    global last_eco_cmd, last_eco_cmd_ts

    cooldown_sec = ECO_CMD_COOLDOWN_SEC if 'ECO_CMD_COOLDOWN_SEC' in globals() else 12
    reassert_sec = ECO_REASSERT_SEC if 'ECO_REASSERT_SEC' in globals() else 0

    cmd = str(cmd).upper()

    # Guard for invalid commands
    if cmd not in ["ON", "OFF"]:
        log_debug("ECO_GATE skip(invalid cmd={})".format(cmd))
        return

    eco_state = str(items["Eco_Power_Switch"]).upper()
    now_t = now()
    age = None if last_eco_cmd_ts is None else (now_t.getMillis() - last_eco_cmd_ts.getMillis()) / 1000.0

    eco_is_target = (cmd == "ON" and eco_state == "ON") or (cmd == "OFF" and eco_state == "OFF")

    if eco_is_target:
        if reassert_sec > 0 and (age is None or age >= reassert_sec):
            events.sendCommand("Eco_Power_Switch", cmd)
            last_eco_cmd = cmd
            last_eco_cmd_ts = now_t
            log_debug("ECO_GATE reassert cmd={} eco={} age={}".format(cmd, eco_state, "None" if age is None else round(age, 1)))
        else:
            log_debug("ECO_GATE skip(target) cmd={} eco={} age={}".format(cmd, eco_state, "None" if age is None else round(age, 1)))
        return

    if last_eco_cmd == cmd and age is not None and age < cooldown_sec:
        log_debug("ECO_GATE skip(cooldown) cmd={} eco={} age={} < {}".format(cmd, eco_state, round(age, 1), cooldown_sec))
        return

    events.sendCommand("Eco_Power_Switch", cmd)
    last_eco_cmd = cmd
    last_eco_cmd_ts = now_t
    log_debug("ECO_GATE send cmd={} eco={} age={}".format(cmd, eco_state, "None" if age is None else round(age, 1)))

def log(msg):
    log_important(msg)
# =========================================================
# SANITIZE
# =========================================================
def sanitize(new_val, old_val, name, inv_count, disabled):
    # --- Configurable local clamp for near-zero baseline jumps ---
    ABS_DELTA_CLAMP = bd(1200)  # tune: 800..2000 depending on sensor noise
    
    if old_val is None:
        return new_val, inv_count, disabled

    # Absolute nonsense drop
    if new_val.abs().compareTo(MAX_ABS) > 0:
        log("SANITY DROP {} abs spike: {}".format(name, new_val))
        return old_val, inv_count, disabled

    delta = new_val.subtract(old_val).abs()

    # NEW: if baseline is small, protect with absolute-delta clamp
    if old_val.abs().compareTo(bd(50)) <= 0:
        if delta.compareTo(ABS_DELTA_CLAMP) > 0:
            log("SANITY DROP {} low-baseline jump: {} -> {}".format(name, old_val, new_val))
            inv_count += 1

            if inv_count >= DISABLE_THRESHOLD:
                if not disabled:
                    log("{} DISABLED temporarily".format(name))
                disabled = True

            if inv_count >= INVALID_LIMIT:
                log("RECOVERY: accepting new baseline for {}".format(name))
                return new_val, 0, False

            return old_val, inv_count, disabled

        # normal small-baseline update
        return new_val, 0, disabled

    # Relative spike check for normal baseline
    rel = delta.divide(old_val.abs(), 2, RoundingMode.HALF_UP)
    if rel.compareTo(REL_DELTA) > 0:
        log("SANITY DROP {} rel spike: {} -> {} ({}%)".format(
            name, old_val, new_val, rel.multiply(bd(100))
        ))

        inv_count += 1
        if inv_count >= DISABLE_THRESHOLD:
            if not disabled:
                log("{} DISABLED temporarily".format(name))
            disabled = True

        if inv_count >= INVALID_LIMIT:
            log("RECOVERY: accepting new baseline for {}".format(name))
            return new_val, 0, False

        return old_val, inv_count, disabled

    return new_val, 0, disabled

# =========================================================
# FILTER PIPELINE
# =========================================================
def compute_filtered_power():
    global filtered_power, power_window, last_total, last_raw_power
    global last_filtered_update, recon_state, log_counter

    now_ms = now().getMillis()

    r1 = safe_bd("Shellyem3_Leistung1")
    r2 = safe_bd("Shellyem3_Leistung2")
    r3 = safe_bd("Shellyem3_Leistung3")
    r4 = safe_bd("Priza1_Power_Cons")

    l1, invalid_count["L1"], phase_disabled["L1"] = sanitize(
        r1, last_valid["L1"], "L1", invalid_count["L1"], phase_disabled["L1"]
    )
    l2, invalid_count["L2"], phase_disabled["L2"] = sanitize(
        r2, last_valid["L2"], "L2", invalid_count["L2"], phase_disabled["L2"]
    )
    l3, invalid_count["L3"], phase_disabled["L3"] = sanitize(
        r3, last_valid["L3"], "L3", invalid_count["L3"], phase_disabled["L3"]
    )
    l4, _, _ = sanitize(r4, last_valid["L4"], "L4", 0, False)

    last_valid["L1"] = l1
    last_valid["L2"] = l2
    last_valid["L3"] = l3
    last_valid["L4"] = l4

    fresh = {}
    for p in ["L1", "L2", "L3"]:
        fresh[p] = (not phase_disabled[p] and
                    last_update[p] != 0 and
                    (now_ms - last_update[p]) <= RECENT_WINDOW_MS)

    vals = {"L1": l1, "L2": l2, "L3": l3}
    valid = [p for p in ["L1", "L2", "L3"] if fresh[p]]
    count = len(valid)

    quality = 0.3
    if count == 3:
        raw = l1.add(l2).add(l3)
        recon_state = "FULL_3PHASE"
        quality = 1.0
    elif count == 2:
        raw = bd(0)
        for p in valid:
            raw = raw.add(vals[p])
        recon_state = "DEGRADED_2PHASE"
        quality = 0.8
    elif count == 1:
        raw = vals[valid[0]].multiply(bd(3))
        recon_state = "DEGRADED_1PHASE"
        quality = 0.5
    elif last_total is not None:
        raw = last_total
        recon_state = "ESTIMATE"
        quality = 0.3
    else:
        if filtered_power is None:
            filtered_power = bd(0).setScale(1, RoundingMode.HALF_UP)
            events.postUpdate("House_Power_Consumption", "0 W")
        return filtered_power

    if last_update["L4"] != 0 and (now_ms - last_update["L4"]) <= RECENT_WINDOW_MS:
        raw = raw.add(l4)

    # Diagnostic logging: show phase freshness and L4 status
    l1_age = now_ms - last_update["L1"] if last_update["L1"] != 0 else 999999
    l2_age = now_ms - last_update["L2"] if last_update["L2"] != 0 else 999999
    l3_age = now_ms - last_update["L3"] if last_update["L3"] != 0 else 999999
    l4_age = now_ms - last_update["L4"] if last_update["L4"] != 0 else 999999

    log_debug(
        "PHASE_AGE L1={}ms L2={}ms L3={}ms L4={}ms [fresh<{}ms]".format(
            l1_age, l2_age, l3_age, l4_age, RECENT_WINDOW_MS
        )
    )

    log_debug(
        "CHECK L1={} L2={} L3={} L4={} SUM={} RAW={}".format(
            l1, l2, l3, l4,
            l1.add(l2).add(l3).add(l4),
            raw
        )
    )

    last_total = raw
    last_raw_power = raw

    # FIX 2026-06-25: L4 freshness check for consistency
    # If L4 is stale (not updated in RECENT_WINDOW_MS), exclude it from raw_total.
    # This prevents a gap between House_Real_Consumption and House_Power_Consumption
    # when L4 (E-Bike charger) loses WiFi connection.
    raw_total = l1.add(l2).add(l3)
    l4_age_ms = now_ms - last_update["L4"] if last_update["L4"] != 0 else 999999
    l4_is_fresh = last_update["L4"] != 0 and l4_age_ms <= RECENT_WINDOW_MS

    if l4_is_fresh:
        raw_total = raw_total.add(l4)
        logger.debug("L4_CHECK", "L4 fresh (age={}ms), included", l4_age_ms)
    else:
        logger.debug("L4_CHECK", "L4 stale (age={}ms), excluded", l4_age_ms)

    events.postUpdate("House_Real_Consumption", str(raw_total) + " W")

    # Sign-aware reset
    if filtered_power is not None:
        if signum(raw) != signum(filtered_power):
            if raw.subtract(filtered_power).abs().compareTo(SIGN_RESET_DELTA) > 0:
                log_important("SIGN RESET raw={} filtered={}".format(raw, filtered_power))
                filtered_power = raw
                del power_window[:]
                for _ in range(WINDOW_SIZE):
                    power_window.append(raw)

    # Large jump reset
    if filtered_power is not None:
        jump = raw.subtract(filtered_power).abs()
        if jump.compareTo(LARGE_JUMP_RESET) > 0:
            log_important("FILTER RESET raw={} filtered={}".format(raw, filtered_power))
            filtered_power = raw
            del power_window[:]
            for _ in range(WINDOW_SIZE):
                power_window.append(raw)

    power_window.append(raw)
    if len(power_window) > WINDOW_SIZE:
        power_window.pop(0)

    sorted_vals = sorted(power_window, key=lambda x: x.doubleValue())
    median = sorted_vals[len(sorted_vals) // 2]

    if filtered_power is None:
        filtered_power = median
    else:
        alpha = (ALPHA_FALL if median.compareTo(filtered_power) < 0 else ALPHA_RISE) * quality
        if alpha > MAX_ALPHA:
            alpha = MAX_ALPHA
        a = bd(alpha)
        one = bd(1)
        filtered_power = filtered_power.multiply(one.subtract(a)).add(median.multiply(a))

    filtered_power = filtered_power.setScale(1, RoundingMode.HALF_UP)
    last_filtered_update = now()

    events.postUpdate("House_Power_Consumption", str(filtered_power) + " W")
    log_counter += 1
    if log_counter % 10 == 0:
        log_important("RAW={} MEDIAN={} FILTERED={} DIR={} INTENT={}".format(raw, median, filtered_power, direction_state, intent_state))

    return filtered_power

# =========================================================
# DIRECTION + INTENT
# =========================================================
def classify_direction(p):
    # Hysteresis around last direction
    if direction_state == "IMPORT":
        if p.compareTo(IMPORT_THRESHOLD.subtract(DIRECTION_HYST)) > 0:
            return "IMPORT"

    if direction_state == "EXPORT":
        if p.compareTo(EXPORT_THRESHOLD.add(DIRECTION_HYST)) < 0:
            return "EXPORT"

    if p.abs().compareTo(DEADBAND) < 0:
        new_dir = "NEUTRAL"
    elif p.compareTo(IMPORT_THRESHOLD) > 0:
        new_dir = "IMPORT"
    elif p.compareTo(EXPORT_THRESHOLD) < 0:
        new_dir = "EXPORT"
    else:
        new_dir = "NEUTRAL"

    # Log direction changes only
    if new_dir != direction_state:
        logger.info("DIRECTION", "Power direction: {} → {} ({:.0f} W)", direction_state, new_dir, p.doubleValue())

    return new_dir

# =========================================================
# SEASONAL CHARGING (FIX 2026-06-20)
# =========================================================
def is_winter_charging_time():
    """
    Determine if current time falls in winter/shoulder scheduled charging window.
    Allows e-bike (Priza1) and laptop (Priza4) to charge even without excess solar.

    Winter (Oct–Mar): Insufficient sun → rely on grid scheduling
    - Windows: 7 AM, 2 PM, 9 PM

    Shoulder (Apr & Sept): Transitional sun → more lenient
    - Windows: 7 AM, 12 PM, 2 PM, 9 PM

    Summer (May–Aug): Abundant sun
    - Returns False → use EXPORT_MODE logic only
    """
    day_of_year = DateTime.now().getDayOfYear()
    hour = DateTime.now().getHourOfDay()

    if day_of_year >= 274 or day_of_year <= 90:
        return hour in [7, 14, 21]

    if (91 <= day_of_year <= 120) or (244 <= day_of_year <= 273):
        return hour in [7, 12, 14, 21]

    return False

def get_charging_devices_for_season():
    """
    Return device list for seasonal charging.
    All devices controlled by normal ECO logic (EXPORT/IMPORT).
    Priza1 & Priza4 additionally use winter scheduled windows.
    """
    return [
        "Priza12_Power_auto",
        "Priza7_Power",
        "Priza3_Power",
        "Priza4_Power_auto",
        "Priza9_Power",
        "Priza1_Power_auto"
    ]

def desired_intent_from_direction(dir_state):
    if dir_state == "EXPORT":
        return "EXPORT_MODE"
    if dir_state == "IMPORT":
        return "IMPORT_MODE"
    return "NEUTRAL_HOLD"

def update_intent(new_direction):
    global direction_state, intent_state, last_intent_change, neutral_since

    old_direction = direction_state
    direction_state = new_direction

    desired = desired_intent_from_direction(new_direction)
    now_t = now()

    # First initialization
    if last_intent_change is None:
        intent_state = desired
        last_intent_change = now_t
        if new_direction == "NEUTRAL":
            neutral_since = now_t
        else:
            neutral_since = None
        log_important("INIT DIR={} INTENT={}".format(direction_state, intent_state))
        return

    # Track neutral duration
    if new_direction == "NEUTRAL":
        if neutral_since is None:
            neutral_since = now_t
    else:
        neutral_since = None

    # Direction changed log
    if old_direction != new_direction:
        log_important("DIR {} -> {}".format(old_direction, new_direction))

    # Anti-oscillation hold
    held_for = secs_since(last_intent_change)
    if held_for is None:
        held_for = 9999

    # Neutral does not immediately force state changes
    if desired == "NEUTRAL_HOLD":
        if intent_state != "NEUTRAL_HOLD":
            if neutral_since is not None and secs_since(neutral_since) >= NEUTRAL_GRACE_SEC:
                intent_state = "NEUTRAL_HOLD"
                last_intent_change = now_t
                log_important("INTENT -> NEUTRAL_HOLD")
        return

    # Directional transition subject to min hold
    if intent_state != desired:
        if held_for >= INTENT_MIN_HOLD_SEC:
            intent_state = desired
            last_intent_change = now_t
            log_important("INTENT -> {}".format(intent_state))
        else:
            log_debug("INTENT HOLD active ({}s remaining)".format(round(INTENT_MIN_HOLD_SEC - held_for, 1)))

# =========================================================
# POWER STATE + DEBOUNCE
# =========================================================
def cancel_debounce():
    global debounce_timer, debounce_pending_state, pending_state
    cancel_timer(debounce_timer)
    debounce_timer = None
    debounce_pending_state = None
    pending_state = None

def set_power_state(new_state):
    global last_pwr_cmd, pending_state

    now_t = now()
    current = items["PWRConsumption"]

    if str(current) == new_state:
        pending_state = None
        return

    if last_state_change is not None:
        elapsed = secs_since(last_state_change)

        if current == OnOffType.ON and new_state == "OFF" and elapsed < MIN_ON_TIME:
            pending_state = new_state
            log_important("LOCKOUT ON->OFF ({}s left)".format(round(MIN_ON_TIME - elapsed, 1)))
            return

        if current == OnOffType.OFF and new_state == "ON" and elapsed < MIN_OFF_TIME:
            pending_state = new_state
            log_important("LOCKOUT OFF->ON ({}s left)".format(round(MIN_OFF_TIME - elapsed, 1)))
            return

    pending_state = None
    last_pwr_cmd = now_t
    log_important("CMD PWRConsumption -> {}".format(new_state))
    events.sendCommand("PWRConsumption", new_state)

def debounce_fire(expected_state):
    global debounce_timer, debounce_pending_state
    debounce_timer = None
    debounce_pending_state = None
    set_power_state(expected_state)

def schedule_state(new_state):
    global debounce_timer, debounce_pending_state

    if new_state is None:
        cancel_debounce()
        return

    if debounce_pending_state == new_state:
        return

    cancel_timer(debounce_timer)
    debounce_pending_state = new_state
    debounce_timer = ScriptExecution.createTimer(
        now().plusSeconds(DEBOUNCE_SEC),
        lambda: debounce_fire(new_state)
    )

# =========================================================
# SEQUENCE ENGINE
# =========================================================
def stop_sequence():
    global sequence_timer, sequence_mode, sequence_index, sequence_last_progress
    cancel_timer(sequence_timer)
    sequence_timer = None
    sequence_mode = None
    sequence_index = 0
    sequence_last_progress = None
    eco_sequence_display("Idle")

def is_device_allowed(dev, target):
    if dev == "Priza1_Power_auto" and target == "ON":
        if items["Priza1_BatteryFull"] == OnOffType.ON:
            log_important("Skip Priza1 (battery full)")
            return False

    if dev == "Priza4_Power_auto" and target == "ON":
        if items["Priza4_BatteryFull"] == OnOffType.ON:
            log_important("Skip Priza4 (battery full)")
            return False
    if dev == "Priza4_Power_auto" and target == "OFF":
        if items["Priza4_BatteryFull"] != OnOffType.ON:
            log_important("Skip Priza4 OFF (battery not confirmed full)")
            return False

    if dev == "Priza9_Power" and target == "ON":
        if not is_priza9_allowed():
            log_important("Skip Priza9 (time)")
            return False

    if dev == "Priza9_Power" and target == "OFF":
        if items["Priza9ForceOn"] == OnOffType.ON:
            log_important("Skip Priza9 OFF (force on)")
            return False

    return True

def next_valid_device(devs, idx, target):
    i = idx
    while i < len(devs):
        d = devs[i]
        i += 1
        if is_device_allowed(d, target):
            return d, i
    return None, i

def run_sequence():
    global sequence_timer, sequence_index, sequence_last_progress

    if sequence_mode not in ["ON", "OFF"]:
        return

    # -------------------------------------------------
    # SAFETY 1: Abort if direction contradicts sequence
    # -------------------------------------------------
    if sequence_mode == "ON" and direction_state == "IMPORT":
        log_important("SEQ ABORT: ON but now IMPORT")
        stop_sequence()
        return

    if sequence_mode == "OFF" and direction_state == "EXPORT":
        log_important("SEQ ABORT: OFF but now EXPORT")
        stop_sequence()
        return

    # -------------------------------------------------
    # SAFETY 2: Stop if objective already achieved
    # -------------------------------------------------
    if filtered_power is not None:
        # ON sequence tries to absorb surplus → stop if importing
        if sequence_mode == "ON" and filtered_power.compareTo(bd(0)) > 0:
            log_important("SEQ STOP: surplus absorbed (now IMPORT)")
            stop_sequence()
            return

        # OFF sequence tries to reduce import → stop if exporting
        if sequence_mode == "OFF" and filtered_power.compareTo(bd(20)) < 0:  # allow small import to persist before stopping, before it was bd(0)
            log_important("SEQ STOP: import resolved (now EXPORT)")
            stop_sequence()
            return

    devs = devices_on if sequence_mode == "ON" else devices_off
    target = "ON" if sequence_mode == "ON" else "OFF"

    if sequence_index >= len(devs):
        stop_sequence()
        return

    dev, sequence_index = next_valid_device(devs, sequence_index, target)
    if dev is None:
        stop_sequence()
        return

    eco_sequence_display("{} -> {} (ECO {})".format(dev, target, sequence_mode))

    if items[dev] not in [NULL, UNDEF] and str(items[dev]) != target:
        events.sendCommand(dev, target)

    sequence_last_progress = now()

    sequence_timer = ScriptExecution.createTimer(
        now().plusSeconds(SEQ_STEP_SEC),
        lambda: run_sequence()
    )

def ensure_sequence_for_intent():
    global sequence_mode, sequence_timer, sequence_index, sequence_last_progress

    desired_mode = None
    if intent_state == "EXPORT_MODE":
        desired_mode = "ON"
    elif intent_state == "IMPORT_MODE":
        desired_mode = "OFF"

    if desired_mode is None:
        stop_sequence()
        return

    # FIX 2026-06-20: Use seasonal device list (excludes Priza12 vacuum)
    seasonal_devs = get_charging_devices_for_season()
    devs = seasonal_devs if desired_mode == "ON" else list(reversed(seasonal_devs))
    target = desired_mode

    # -------------------------------------------------
    # GUARD 1: Avoid unnecessary sequence if already done
    # -------------------------------------------------
    all_done = True
    for d in devs:
        if not is_device_allowed(d, target):
            continue  # legitimately skipped — don't count as undone
        if items[d] not in [NULL, UNDEF] and str(items[d]) != target:
            all_done = False
            break

    if all_done:
        if sequence_mode is not None:
            stop_sequence()
        log_debug("SEQ_GATE all_done=True mode={}".format(desired_mode))
        return

    # -------------------------------------------------
    # GUARD 2: Prevent rapid flip (anti-oscillation)
    # -------------------------------------------------
    if sequence_mode is not None and sequence_mode != desired_mode:
        if sequence_last_progress is not None:
            elapsed = secs_since(sequence_last_progress)
            if elapsed is not None and elapsed < SEQUENCE_MIN_RUNTIME:
                log_debug("SEQ HOLD: prevent flip {} -> {} ({}s)".format(
                    sequence_mode, desired_mode, round(elapsed, 1)
                ))
                return

    # -------------------------------------------------
    # GUARD 3: Keep running current valid sequence
    # -------------------------------------------------
    if sequence_mode == desired_mode and sequence_timer is not None and not sequence_timer.hasTerminated():
        return

    # -------------------------------------------------
    # START NEW SEQUENCE
    # -------------------------------------------------
    stop_sequence()
    sequence_mode = desired_mode
    sequence_index = 0
    sequence_last_progress = now()

    log_important("Sequence START {}".format(desired_mode))
    run_sequence()

# =========================================================
# UNIFIED ARBITER (single control authority)
# =========================================================
def apply_intent():
    pwr_state = str(items["PWRConsumption"]).upper()

    if intent_state == "EXPORT_MODE":
        logger.debug("INTENT", "EXPORT_MODE: Selling power to grid")
        if pwr_state != "OFF":
            schedule_state("OFF")
        else:
            cancel_debounce()

        send_eco_if_needed("ON")
        ensure_sequence_for_intent()
        return

    if intent_state == "IMPORT_MODE":
        logger.debug("INTENT", "IMPORT_MODE: Charging/Running normally")
        if pwr_state != "ON":
            schedule_state("ON")
        else:
            cancel_debounce()

        send_eco_if_needed("OFF")
        ensure_sequence_for_intent()
        return

    # NEUTRAL_HOLD
    logger.debug("INTENT", "NEUTRAL_HOLD: Waiting for direction clarity")
    cancel_debounce()
    stop_sequence()

# =========================================================
# CONTROL TICK
# =========================================================
def control_tick():
    p = compute_filtered_power()
    if p is None:
        return

    new_direction = classify_direction(p)
    update_intent(new_direction)
    apply_intent()

def schedule_compute():
    global update_timer

    if update_timer is not None and not update_timer.hasTerminated():
        return

    def run():
        global update_timer
        update_timer = None

        if not lock.tryLock():
            ScriptExecution.createTimer(
                now().plusMillis(RETRY_LOCK_MS),
                lambda: schedule_compute()
            )
            return

        try:
            control_tick()
        finally:
            lock.unlock()

    update_timer = ScriptExecution.createTimer(
        now().plusMillis(SCHED_DELAY_MS),
        run
    )

# =========================================================
# RULES
# =========================================================
@rule("ECO CORE")
@when("Item Shellyem3_Leistung1 changed")
@when("Item Shellyem3_Leistung2 changed")
@when("Item Shellyem3_Leistung3 changed")
@when("Item Priza1_Power_Cons changed")
def eco_core(event):
    global last_exec

    t = now()
    ms = t.getMillis()

    name = event.itemName
    if name == "Shellyem3_Leistung1":
        last_update["L1"] = ms
    elif name == "Shellyem3_Leistung2":
        last_update["L2"] = ms
    elif name == "Shellyem3_Leistung3":
        last_update["L3"] = ms
    elif name == "Priza1_Power_Cons":
        last_update["L4"] = ms

    if last_exec is not None and (ms - last_exec.getMillis()) < BURST_GUARD_MS:
        return

    schedule_compute()
    last_exec = t

@rule("ECO DRIVER MONITOR")
@when("Item PWRConsumption changed")
def eco_driver_monitor(event):
    # Monitor-only: no policy commands here.
    global last_state_change
    last_state_change = now()
    log_debug("MONITOR: PWRConsumption changed -> {}".format(items["PWRConsumption"]))

@rule("ECO WATCHDOG")
@when("Time cron 0/5 * * * * ?")
def eco_watchdog(event):
    """
    Unified recovery watchdog (quiet + mismatch-only stale reassert).
    """
    # Log watchdog tick with current state summary
    power_val = safe_bd("PWRConsumption")
    logger.debug("WATCHDOG", "Tick: Power={:.0f}W Direction={} Intent={} Pwr={}",
                 power_val.doubleValue() if power_val else 0, direction_state, intent_state,
                 str(items["PWRConsumption"]).upper())

    # 1) stale filter pipeline
    if last_filtered_update is not None:
        age = secs_since(last_filtered_update)
        if age is not None and age > FILTER_STALE_SEC:
            log("WATCHDOG: filtered stale {}s -> schedule compute".format(round(age, 1)))
            schedule_compute()

    # 2) pending lockout release
    if pending_state is not None and last_state_change is not None:
        pwr_state = str(items["PWRConsumption"]).upper()
        elapsed = secs_since(last_state_change)

        if elapsed is not None:
            if pending_state == "ON" and pwr_state == "OFF" and elapsed >= MIN_OFF_TIME:
                log("WATCHDOG: release pending ON")
                schedule_state("ON")
            elif pending_state == "OFF" and pwr_state == "ON" and elapsed >= MIN_ON_TIME:
                log("WATCHDOG: release pending OFF")
                schedule_state("OFF")

    # 3) stale PWR mismatch-only reassert (no spam when already correct)
    pwr_age = secs_since(last_state_change)
    if pwr_age is not None and pwr_age >= PWR_STALE_SEC:
        pwr_state = str(items["PWRConsumption"]).upper()

        if intent_state == "IMPORT_MODE" and pwr_state != "ON":
            log("WATCHDOG: stale PWR mismatch -> reassert ON")
            schedule_state("ON")
        elif intent_state == "EXPORT_MODE" and pwr_state != "OFF":
            log("WATCHDOG: stale PWR mismatch -> reassert OFF")
            schedule_state("OFF")
        # else: intentionally no log/action

    # 4) sequence health
    if sequence_mode is not None:
        if sequence_timer is None:
            log("WATCHDOG: sequence timer missing -> recover")
            ensure_sequence_for_intent()
        elif sequence_timer.hasTerminated():
            ensure_sequence_for_intent()
        elif sequence_last_progress is not None:
            stall = secs_since(sequence_last_progress)
            if stall is not None and stall > SEQ_STALL_SEC:
                log("WATCHDOG: sequence stalled {}s -> recover".format(round(stall, 1)))
                ensure_sequence_for_intent()

    # 5) evening override
    if str(items["vTimeOfDay"]) == "EVENING":
        if str(items["Eco_Power_Switch"]).upper() != "OFF":
            events.sendCommand("Eco_Power_Switch", "OFF")
        stop_sequence()
        cancel_debounce()
        return

    # 5b) Winter scheduled charging override (FIX 2026-06-20)
    # Allow Priza1/4 to charge even in IMPORT_MODE during scheduled windows
    if is_winter_charging_time():
        priza1_full = str(items["Priza1_BatteryFull"]).strip() == "ON"
        priza1_is_off = str(items["Priza1_Power_auto"]).strip() == "OFF"
        priza4_full = str(items["Priza4_BatteryFull"]).strip() == "ON"
        priza4_is_off = str(items["Priza4_Power_auto"]).strip() == "OFF"

        activated = False

        if not priza1_full and priza1_is_off:
            events.sendCommand("Priza1_Power_auto", "ON")
            log_important("WINTER: Priza1_Power_auto ON (scheduled window)")
            activated = True

        if not priza4_full and priza4_is_off:
            events.sendCommand("Priza4_Power_auto", "ON")
            log_important("WINTER: Priza4_Power_auto ON (scheduled window)")
            activated = True

        # Skip apply_intent() to prevent ON-OFF cycling
        if activated:
            return

    # 6) enforce current intent
    apply_intent()

    # 7) optional summary tick
    log_summary_tick()