##020_Scheduled_rev20260307.py

#2021.07.18 Adaugare regula "Change extension name for inactive files"
#2022.04.30 Adaugare ScriptParrot_Sonoff1_up, ScriptParrot_Sonoff2_up, ScriptParrot_Sonoff3_up
#2026.03.07 Removed eco_timer_on/off block and eco_power_switch_state rule — sequencing
#           now handled entirely by 080_Power. Eco_Power_Switch remains a manual override
#           watched by 080_Power directly.
#           Priza1_BatteryFull: cleared at midnight before Priza1_Power OFF (stop_prize),
#           and when Priza1_Power turns ON in 019_Charge_curve (new charge cycle).
# 2026-05-02: UnDefType from org.eclipse.smarthome.core.types (ESH; OH 2.5.12 convention).
# 2026-05-23 FIX-A: stop_prize trigger detection replaced. getattr(event, "trigger", None)
#            always returns None for cron events in OH 2.5 JSR223, so the midnight
#            BatteryFull reset never fired. Now uses DateTime.now().getHourOfDay() == 0
#            to distinguish midnight from noon — reliable regardless of event metadata.
###
from core.rules import rule
from core.triggers import when
from core.actions import Exec
from org.eclipse.smarthome.core.types import UnDefType
from org.eclipse.smarthome.core.library.types import OnOffType
from org.joda.time import DateTime
from org.eclipse.smarthome.model.script.actions.Exec import executeCommandLine
from core.actions import ScriptExecution
from core.jsr223.scope import events, items
#from core.utils import sendCommandCheckFirst, postUpdateCheckFirst
from core.actions import LogAction
from core.log import logging
from core.jsr223 import scope

NULL = UnDefType.NULL
UNDEF = UnDefType.UNDEF
ON = OnOffType.ON
OFF = OnOffType.OFF

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

    def _should_log(self, key):
        """Deduplicate: only log if different message or > SPAM_THRESHOLD_SEC since last."""
        if key not in self.last_logged:
            return True
        age_ms = DateTime.now().getMillis() - self.last_logged[key]
        return age_ms >= (self.SPAM_THRESHOLD_SEC * 1000)

logger = Logger("SCHEDULE")  # Sustainable logging framework

priza8TimerOff = None
FireplaceTimerOff = None
Fireplacetimer = None
day = "DAY"
afternoon = "AFTERNOON"
night = "NIGHT"
bed = "BED"
evening = "EVENING"
winter = "Winter"

createTimer = ScriptExecution.createTimer

TubeLamp_irraw = 0,9325,4520,595,555,595,555,595,555,595,555,590,555,595,555,590,560,595,555,595,1665,590,1670,595,1670,590,1670,595,555,590,1670,590,1670,570,1690,590,1670,590,1670,590,555,590,555,590,560,590,555,570,580,570,580,590,555,595,555,590,1670,590,1670,595,1670,595,1670,590,1670,590,1670,595,41130,9270,2250,590

# Sonoffmini debounce counters (Phase 4 fix 2026-06-20)
sonoffmini_offline_count = {"sonoff1": 0, "sonoff2": 0, "sonoff3": 0}
SONOFFMINI_DEBOUNCE_CHECKS = 2

# Initialize other rules
#@rule("Change extension name for inactive files", description="Startup extension change", tags=["Startup", "Extension"])
#@when("System started")
#def system_start(event):
#	change_extension = Exec.executeCommandLine("/etc/openhab2/scripts/change_ext_py.sh", 5000)

@rule("Scheduled tasks cronjob vacation conditioned", description="Sensors reset and other functions using cron", tags=["cron", "Schedule"])
@when("Time cron 0 45 6 ? * MON,TUE,WED,THU,FRI *")
@when("Time cron 0 30 8 ? * SAT,SUN *")
def scheduled_tasks(event):
	logger.info("SCHEDULE", "Morning schedule: Resetting devices")
	if items["Vacanta"] != ON:
		events.sendCommand("Cinema", "OFF")
		events.sendCommand("DarkSufra", "OFF")
		events.sendCommand("PermSufra", "OFF")
		events.sendCommand("DarkDormC", "OFF")
		events.sendCommand("PermDormC", "OFF")
		events.sendCommand("DarkDormP", "OFF")
		events.sendCommand("PermDormP", "OFF")
		events.sendCommand("DarkBucatarie", "OFF")
		events.sendCommand("PermBucatarie", "OFF")
		events.sendCommand("Backup_Openhab2", "OFF")
		#events.sendCommand("Priza1_Power", "ON") ###18.10.2025### A fost transformata Priza1 pentru E-Bike
		events.sendCommand("Priza2_Power", "ON")
		# Guard: Don't turn ON Priza3 if ECO is managing power
		if items["PWRConsumption"] != OnOffType.ON:
			events.sendCommand("Priza3_Power", "ON")
		if items["Sufragerie_Daytime"] == OFF or items["Sufragerie_Illuminance_Switch"] == ON:  # update 06.06.2022 #este intuneric in camera
			events.sendCommand("Priza5_Power", "ON")

	if items["Schulfrei_Adina"] != ON:
		if items["DormC_Daytime"] == OFF or items["DormitorC_Illuminance_Switch"] == ON: # update 06.06.2022 #este intuneric in camera
			events.sendCommand("Led_Contr_Adina_Color", "120,2,5")
			events.sendCommand("Scene_Led_Adina", "ON")
			events.sendCommand("Led_Contr_Adina_Power", "ON")


@rule("Scheduled tasks cronjob", description="Sensors reset using cron at 9AM", tags=["cron", "Schedule"])
@when("Time cron 0 0 9 * * ? *")
def scheduled_tasks2(event):
	logger.info("SCHEDULE", "9 AM schedule: Resetting devices")
	if items["Vacanta"] == ON:
		events.sendCommand("Cinema", "OFF")
		events.sendCommand("DarkSufra", "OFF")
		events.sendCommand("PermSufra", "OFF")
		events.sendCommand("DarkDormC", "OFF")
		events.sendCommand("PermDormC", "OFF")
		events.sendCommand("DarkDormP", "OFF")
		events.sendCommand("PermDormP", "OFF")
		events.sendCommand("DarkBucatarie", "OFF")
		events.sendCommand("PermBucatarie", "OFF")
		events.sendCommand("Backup_Openhab2", "OFF")
		#events.sendCommand("Priza1_Power", "ON") ###18.10.2025### A fost transformata Priza1 pentru E-Bike
		events.sendCommand("Priza2_Power", "ON")
		# Guard: Don't turn ON Priza3/4 if ECO is managing power
		if items["PWRConsumption"] != OnOffType.ON:
			events.sendCommand("Priza3_Power", "ON")
			events.sendCommand("Priza4_Power", "ON") ###08.05.2022### A fost transformata Priza4 pentru laptop
		else:
			if items["Priza4_Power"] != OnOffType.ON:
				events.sendCommand("Priza4_Power", "ON")
		#events.sendCommand("Priza5_Power", "ON")
		#events.sendCommand("Priza6_Power", "ON")

@rule("Scheduled tasks cronjob vacation conditioned Alex", description="Sensors reset and other functions using cron", tags=["cron", "Schedule"])
@when("Time cron 0 0 7 ? * MON,TUE,WED,THU,FRI *")
@when("Time cron 0 30 8 ? * SAT,SUN *")
def scheduled_tasks3(event):
	if items["Schulfrei_Alex"] != ON:
		if items["DormP_Daytime"] == OFF or items["DormitorP_Illuminance_Switch"] == ON: # update 02.03.2025
			events.sendCommand("Led_Contr_Alex_Color", "120,2,5")
			events.sendCommand("Scene_Led_Alex", "ON")
			events.sendCommand("Led_Contr_Alex_Power", "ON")

@rule("Scheduled tasks cronjob 22:30 Led_Contr_Alex_Power", description="Led_Contr_Alex_Power using cron", tags=["cron", "Schedule"])
@when("Time cron 0 0 22 * * ? *")
def scheduled_tasks4(event):
	events.sendCommand("Led_Contr_Alex_Power", "OFF")

@rule("Kodi restart cronjob", description="Restart Kodi periodically", tags=["cron", "Kodi"])
@when("Time cron 0 15 5 * * ? *")
def kodi_restart(event):
	events.sendCommand("Kodi_restart", "ON")   # ON este starea inactiva

@rule("Kodi reset to OFF state cronjob", description="Kodi reset to OFF state cronjob", tags=["cron", "Kodi"])
@when("Time cron 0 0 5 * * ? *")
def kodi_reset_state(event):
	events.postUpdate("Kodi_restart", "OFF")   # OFF este starea activa

@rule("PermDormC activate", description="Activate PermDormC", tags=["cron", "PermDormC"])
@when("Time cron 0 0 20 * * ? *")
def perm_dormc_on(event):
	events.sendCommand("PermDormC", "ON")
	events.sendCommand("Dorm2_Presence", "ON")

@rule("PermDormC deactivate", description="Deactivate PermDormC", tags=["cron", "PermDormC"])
@when("Time cron 0 0 23 * * ? *")
def perm_dormc_off(event):
	events.sendCommand("PermDormC", "OFF")
	events.sendCommand("Dorm2_Presence", "OFF")

@rule("Restore Kodi switch state cronjob", description="Restore Kodi switch state", tags=["cron", "Kodi_switch_state"])
@when("Time cron 0 0/30 * * * ?")
def kodi_switch_state(event):
	if items["Kodi_restart"] == OFF:
		events.sendCommand("Kodi_restart", "ON")

@rule("Restore Kodi2 switch state cronjob", description="Restore Kodi2 switch state", tags=["cron", "Kodi2_switch_state"])
@when("Time cron 0 0/30 * * * ?")
def kodi2_switch_state(event):
	if items["Kodi2_restart"] == OFF:
		events.sendCommand("Kodi2_restart", "ON")

@rule("Switch off NAS during night cronjob", description="Switch off NAS during night", tags=["cron", "NAS"])
@when("Time cron 0 15 23 ? * SUN,MON,TUE,WED,THU *")
@when("Time cron 0 30 0 ? * FRI,SAT *")
def nas_off(event):
	events.sendCommand("NAS", "OFF")

@rule("Update_VPN_List cronjob", description="Update_VPN_List pfsense", tags=["cron", "Update_VPN_List"])
@when("Time cron 0 0 5 * * ? *")
def vpn_list_cronjob(event):
	events.sendCommand("Update_VPN_List", "ON")

@rule("Backup Openhab2 to NAS cronjob", description="Backup Openhab2 to NAS once a week", tags=["cron", "Backup"])
@when("Time cron 0 30 6 ? * MON *")
def backup_openhab2_nas(event):
	events.sendCommand("Backup_Openhab2", "ON")

#@rule("RTR_OH2 restart cronjob", description="Restart RTR_OH2 Router periodically", tags=["cron", "RTR_OH2"])
#@when("Time cron 0 30 12 ? * * *")
#def rtr_oh2_restart(event):
#	events.sendCommand("RTR_OH2_restart", "OFF")   # OFF este starea activa

#@rule("RTR_OH2 reset to inactive state cronjob", description="RTR_OH2 reset to inactive state cronjob", tags=["cron", "RTR_OH2"])
#@when("Time cron 0 31 12 ? * * *")
#def rtr_oh2_reset_state(event):
#	events.postUpdate("RTR_OH2_restart", "ON")   # ON este starea inactiva

@rule("Restore PermDormC_Forced switch state cronjob", description="Restore PermDormC_Forced switch state", tags=["cron", "PermDormC_Forced"])
@when("Time cron 0 0/10 * * * ?")
def permdormc_forced_switch_state(event):
	global sonoffmini_offline_count
	# FIX 2026-06-20: Debounce Sonoffmini1_Alive (require 2+ checks before acting)
	if items["Sonoffmini1_Alive"] == OFF:
		sonoffmini_offline_count["sonoff1"] += 1
		if sonoffmini_offline_count["sonoff1"] >= SONOFFMINI_DEBOUNCE_CHECKS:
			if items["PermDormC_Forced"] == ON:
				events.sendCommand("PermDormC_Forced", "OFF")
				#events.sendCommand("PermDormC", "OFF")
	else:
		sonoffmini_offline_count["sonoff1"] = 0
#	if ir.getItem("Sonoffmini1_Alive").state == NULL:   ###Nou 03.04.2022
#		events.sendCommand("Sonoffmini1_Alive", "OFF")
#	if isinstance(items["Sonoff1_Latency"], UnDefType):   ###Nou 03.04.2022
	if items["Sonoff1_Latency"] == UNDEF:   ###Nou 03.04.2022
		#LogAction.logInfo("Sonoff1_Latency", "Sonoffmini1 este inactiv")
		if items["Sonoffmini1_Alive"] != OFF:
			events.sendCommand("Sonoffmini1_Alive", "OFF")
			LogAction.logInfo("Sonoff1_Latency", "Sonoff1_Latency a dezactivat Sonoffmini1_Alive")

@rule("Restore PermDormP_Forced switch state cronjob", description="Restore PermDormP_Forced switch state", tags=["cron", "PermDormP_Forced"])
@when("Time cron 0 0/10 * * * ?")
def permdormp_forced_switch_state(event):
	global sonoffmini_offline_count
	# FIX 2026-06-20: Debounce Sonoffmini2_Alive (require 2+ checks before acting)
	if items["Sonoffmini2_Alive"] == OFF:
		sonoffmini_offline_count["sonoff2"] += 1
		if sonoffmini_offline_count["sonoff2"] >= SONOFFMINI_DEBOUNCE_CHECKS:
			if items["PermDormP_Forced"] == ON:
				events.sendCommand("PermDormP_Forced", "OFF")
				events.sendCommand("PermDormP", "OFF")
	else:
		sonoffmini_offline_count["sonoff2"] = 0
#	if ir.getItem("Sonoffmini2_Alive").state == NULL:  ###Nou 03.04.2022
#		events.sendCommand("Sonoffmini2_Alive", "OFF")
#	if isinstance(items["Sonoff2_Latency"], UnDefType):   ###Nou 03.04.2022
	if items["Sonoff2_Latency"] == UNDEF:   ###Nou 03.04.2022
		#LogAction.logInfo("Sonoff2_Latency", "Sonoffmini2 este inactiv")
		if items["Sonoffmini2_Alive"] != OFF:
			events.sendCommand("Sonoffmini2_Alive", "OFF")
			LogAction.logInfo("Sonoff2_Latency", "Sonoff2_Latency a dezactivat Sonoffmini2_Alive")

@rule("Restore PermSufra_Forced switch state cronjob", description="Restore PermSufra_Forced switch state", tags=["cron", "PermSufra_Forced"])
@when("Time cron 0 0/10 * * * ?")
def permsufra_forced_switch_state(event):
	global sonoffmini_offline_count
	# FIX 2026-06-20: Debounce Sonoffmini3_Alive (require 2+ checks before acting)
	if items["Sonoffmini3_Alive"] == OFF:
		sonoffmini_offline_count["sonoff3"] += 1
		if sonoffmini_offline_count["sonoff3"] >= SONOFFMINI_DEBOUNCE_CHECKS:
			if items["PermSufra_Forced"] == ON:
				events.sendCommand("PermSufra_Forced", "OFF")
				events.sendCommand("PermSufra", "OFF")
	else:
		sonoffmini_offline_count["sonoff3"] = 0
#	if ir.getItem("Sonoffmini3_Alive").state == NULL:   ###Nou 03.04.2022
#		events.sendCommand("Sonoffmini3_Alive", "OFF")
	if items["Sonoff3_Latency"] == UNDEF:   ###Nou 03.04.2022
#	if isinstance(items["Sonoff3_Latency"], UnDefType):   ###Nou 03.04.2022
		#LogAction.logInfo("Sonoff3_Latency", "Sonoffmini3 este inactiv")
		if items["Sonoffmini3_Alive"] != OFF:
			events.sendCommand("Sonoffmini3_Alive", "OFF")
			LogAction.logInfo("Sonoff3_Latency", "Sonoff3_Latency a dezactivat Sonoffmini3_Alive")

#@rule("Restart Openhab cronjob", description="Restart Openhab cronjob", tags=["cron", "openHAB"])
#@when("Time cron 0 30 11 ? * MON,THU,SUN *")
#def permsufra_forced_switch_state(event):
#	events.sendCommand("Restart_Openhab", "ON")  ###Restartul se face cu comanda "ON"

@rule("Restart Openhab cronjob", description="Restart Openhab cronjob", tags=["cron", "openHAB"])
@when("Time cron 0 30 11 1 * ?")   ###27.11.2022 Restart periodic in fiecare data de 1 a fiecarei luni, la ora 11:30 AM #https://www.freeformatter.com/cron-expression-generator-quartz.html
def permsufra_forced_switch_state(event):
	events.sendCommand("Restart_Openhab", "ON")  ###Restartul se face cu comanda "ON"

@rule("Sonoff1 reachable state cronjob", description="Sonoff1 reachable state", tags=["cron", "Sonoff1_Latency"])
@when("Time cron 0 0/10 * * * ?")
def sonoff1_latency_state(event):
	if items["Sonoff1_Latency"] == UNDEF or items["Sonoff1_Latency"] == NULL:
		events.sendCommand("Sonoffmini1_Alive", "OFF")

@rule("Sonoff2 reachable state cronjob", description="Sonoff2 reachable state", tags=["cron", "Sonoff2_Latency"])
@when("Time cron 0 0/10 * * * ?")
def sonoff2_latency_state(event):
	if items["Sonoff2_Latency"] == UNDEF or items["Sonoff2_Latency"] == NULL:
		events.sendCommand("Sonoffmini2_Alive", "OFF")

@rule("Sonoff3 reachable state cronjob", description="Sonoff3 reachable state", tags=["cron", "Sonoff3_Latency"])
@when("Time cron 0 0/10 * * * ?")
def sonoff3_latency_state(event):
	if items["Sonoff3_Latency"] == UNDEF or items["Sonoff3_Latency"] == NULL:
		events.sendCommand("Sonoffmini3_Alive", "OFF")

@rule("ScriptParrot_Sonoff1_up state cronjob", description="ScriptParrot_Sonoff1_up state", tags=["cron", "ScriptParrot_Sonoff1_up"])
@when("Time cron 0 0/5 * * * ?")
def scriptparrot_sonoff1_up_state(event):
	if items["ScriptParrot_Sonoff1_up"] == OFF:
		events.sendCommand("Sonoffmini1_Alive", "OFF")

@rule("ScriptParrot_Sonoff2_up state cronjob", description="ScriptParrot_Sonoff2_up state", tags=["cron", "ScriptParrot_Sonoff2_up"])
@when("Time cron 0 0/5 * * * ?")
def scriptparrot_sonoff2_up_state(event):
	if items["ScriptParrot_Sonoff2_up"] == OFF:
		events.sendCommand("Sonoffmini2_Alive", "OFF")

@rule("ScriptParrot_Sonoff3_up state cronjob", description="ScriptParrot_Sonoff3_up state", tags=["cron", "ScriptParrot_Sonoff3_up"])
@when("Time cron 0 0/5 * * * ?")
def scriptparrot_sonoff3_up_state(event):
	if items["ScriptParrot_Sonoff3_up"] == OFF:
		events.sendCommand("Sonoffmini3_Alive", "OFF")

@rule("Tube_Lamp", description="Tube_Lamp switch", tags=["Switch", "Tube_Lamp"])
@when("Item Tube_Lamp changed")
def tubelamp_state(event):
	if event.itemState == OFF:
		#events.postUpdate(ir.getItem("Irbridge_IRSend"), (TubeLamp_irraw))
		#events.sendCommand(ir.getItem("Irbridge_IRSend"), (TubeLamp_irraw))
		#postUpdateCheckFirst("Irbridge_IRSend", "irsend 0,9325,4520,595,555,595,555,595,555,595,555,590,555,595,555,590,560,595,555,595,1665,590,1670,595,1670,590,1670,595,555,590,1670,590,1670,570,1690,590,1670,590,1670,590,555,590,555,590,560,590,555,570,580,570,580,590,555,595,555,590,1670,590,1670,595,1670,595,1670,590,1670,590,1670,595,41130,9270,2250,590")
		events.sendCommand("Irbridge_IRSend", "irsend 0,9325,4520,595,555,595,555,595,555,595,555,590,555,595,555,590,560,595,555,595,1665,590,1670,595,1670,590,1670,595,555,590,1670,590,1670,570,1690,590,1670,590,1670,590,555,590,555,590,560,590,555,570,580,570,580,590,555,595,555,590,1670,590,1670,595,1670,595,1670,590,1670,590,1670,595,41130,9270,2250,590")
	if event.itemState == ON:
		#events.postUpdate(ir.getItem("Irbridge_IRSend"), (TubeLamp_irraw))
		#events.sendCommand(ir.getItem("Irbridge_IRSend"), (TubeLamp_irraw))
		#postUpdateCheckFirst("Irbridge_IRSend", "irsend 0,9325,4520,595,555,595,555,595,555,595,555,590,555,595,555,590,560,595,555,595,1665,590,1670,595,1670,590,1670,595,555,590,1670,590,1670,570,1690,590,1670,590,1670,590,555,590,555,590,560,590,555,570,580,570,580,590,555,595,555,590,1670,590,1670,595,1670,595,1670,590,1670,590,1670,595,41130,9270,2250,590")
		events.sendCommand("Irbridge_IRSend", "irsend 0,9325,4520,595,555,595,555,595,555,595,555,590,555,595,555,590,560,595,555,595,1665,590,1670,595,1670,590,1670,595,555,590,1670,590,1670,570,1690,590,1670,590,1670,590,555,590,555,590,560,590,555,570,580,570,580,590,555,595,555,590,1670,590,1670,595,1670,595,1670,590,1670,590,1670,595,41130,9270,2250,590")

def timer_priza8():
	events.sendCommand("Priza8_Power", "OFF")
	events.sendCommand("Priza11_Power", "OFF") # nou din data de 13.01.2024 # Priza10 se transorma in Priza11 din 01.12.2025
	if priza8TimerOff is not None:  # FIX 2026-06-20: Guard against None timer
		priza8TimerOff.cancel()

@rule("Priza8_Power TOD", description="Priza8_Power ON", tags=["cron", "Priza8_Power"])
@when("Item vTimeOfDay changed")
def priza8_tod_state(event):
	global priza8TimerOff
	day = "DAY"
	night = "NIGHT"
	bed = "BED"
	evening = "EVENING"
	winter = "Winter"
	now = DateTime.now()
	month = now.getMonthOfYear()
	day_of_month = now.getDayOfMonth()
	if event.itemState == StringType(evening):
		if items["HomePresence"] == ON:
			events.sendCommand("Priza8_Power", "ON")
			# Priza11_Power (balcony LED) not started at evening — controlled only by 082_tomato_led.py
	elif event.itemState == StringType(night):
		events.sendCommand("Pi_fireplace", "OFF")
		if priza8TimerOff is None or priza8TimerOff.hasTerminated():
			priza8TimerOff = ScriptExecution.createTimer(DateTime.now().plusSeconds(60), timer_priza8)
	elif event.itemState == StringType(bed):
		events.sendCommand("Pi_fireplace", "OFF")
		#if items["Sufra2_Light_Illuminance"] >= QuantityType(u"3.0 lx"):
			#events.sendCommand("Tube_Lamp", "OFF")
		if priza8TimerOff is None or priza8TimerOff.hasTerminated():
			priza8TimerOff = ScriptExecution.createTimer(DateTime.now().plusSeconds(60), timer_priza8)

def timer_fireplace():
	events.sendCommand("Fireplace", "OFF")
	LogAction.logInfo("fireplace_cinema", "Fireplace is off due to Cinema off")
	if Fireplacetimer is not None:  # FIX 2026-06-20: Guard against None timer
		Fireplacetimer.cancel()

@rule("Cinema changed", description="Cinema changed", tags=["Cinema", "Sufra"])
@when("Item Cinema changed")
def fireplace_cinema(event):
	global Fireplacetimer
	bed = "BED"
	evening = "EVENING"
	winter = "Winter"
	if items["vTimeOfDay"] == StringType(evening):
		if event.itemState == OFF:
			if Fireplacetimer is None or Fireplacetimer.hasTerminated():
				Fireplacetimer = ScriptExecution.createTimer(DateTime.now().plusMinutes(10), timer_fireplace)
		elif event.itemState == ON:
			events.sendCommand("Priza8_Power", "ON")
			#Fireplacetimer = ScriptExecution.createTimer("FireplaceTimerOff", DateTime.now().plusMinutes(10), timer_fireplace)
			if Fireplacetimer is not None and not Fireplacetimer.hasTerminated():
				Fireplacetimer.cancel()

@rule("Priza9_Power TOD", description="Priza9_Power ON/OFF based on TimeOfDay", tags=["cron", "Priza9_Power"])
@when("Item vTimeOfDay changed")
@when("Item HomePresence changed")
def priza9_tod_hp_state(event):
	if items["HomePresence"] == ON:
		if items["vTimeOfDay"] == StringType(day) or items["vTimeOfDay"] == StringType(afternoon):
			if items["Eco_Power_Switch"] == ON:
				events.sendCommand("Priza9_Power", "ON")
		elif items["vTimeOfDay"] == StringType(evening):
			events.sendCommand("Priza9_Power", "OFF")
	else:
		if items["vTimeOfDay"] == StringType(evening):
			events.sendCommand("Priza9_Power", "OFF")

@rule("Priza9_Power Cron Jobs", description="Priza9_Power ON/OFF based on cron schedule", tags=["cron", "Priza9_Power"])
@when("Time cron 0 55 7 * * ?")
@when("Time cron 0 30 8 * * ?")
@when("Time cron 0 55 15 * * ?")
@when("Time cron 0 30 16 * * ?")
def priza9_power_cron_jobs(event):
	if event is not None and event.trigger in ["Time cron 0 55 7 * * ?", "Time cron 0 55 15 * * ?"]:
		if items["Priza9_Power"] != OFF:
			events.sendCommand("Priza9_Power", "OFF")
	elif event is not None and event.trigger in ["Time cron 0 30 8 * * ?", "Time cron 0 30 16 * * ?"]:
		if items["HomePresence"] == ON and items["Priza9_Power"] != ON and items["Eco_Power_Switch"] == ON:
			events.sendCommand("Priza9_Power", "ON")

@rule("ECO Guard: Auto-OFF Priza3/7 when powered ON during ECO management", description="Force OFF if ECO is managing power", tags=["ECO", "Guard"])
@when("Item Priza3_Power changed")
@when("Item Priza7_Power changed")
def eco_guard_priza_power(event):
	"""When Priza3/7 power turns ON while ECO is managing, immediately turn OFF"""
	if str(event.itemState).upper() == "ON" and items["PWRConsumption"] == ON:
		dev_name = event.itemName
		logger.info("ECO_GUARD", "{} turned ON during ECO management - forcing OFF", dev_name)
		events.sendCommand(dev_name, "OFF")

@rule("Priza7_Power OFF state cronjob", description="Priza7_Power OFF2 state", tags=["cron", "Priza7_Power"])
@when("Time cron 0 0 22 * * ?")
def priza7_power_off2_state(event):
	events.sendCommand("OffFlag7", "ON")
	if items["Priza7_Power"] not in [NULL, UNDEF] and items["Priza7_Power"] != OFF:
		events.sendCommand("Priza7_Power", "OFF")
	#	events.sendCommand("OffFlag7", "ON")

#@rule("Priza7_Power ON state cronjob weekend", description="Priza7_Power ON1 state", tags=["cron", "Priza7_Power"])
#@when("Time cron 0 30 8 ? * SAT,SUN *")
#def priza7_power_on1_state(event):
#	events.sendCommand("OffFlag7", "OFF")
#	if items["HomePresence"] == ON:
#		if items["Priza7_Power"] != ON:
#			events.sendCommand("Priza7_Power", "ON")
#		#	events.sendCommand("OffFlag7", "OFF")	#nou pe data 21.01.2024

#@rule("Priza7_Power ON state cronjob weekday", description="Priza7_Power ON weekday state", tags=["cron", "Priza7_Power"])
#@when("Time cron 0 0 7 ? * MON,TUE,WED,THU,FRI *")
#def priza7_power_on_weekday_state(event):
#	events.sendCommand("OffFlag7", "OFF")
#	if items["HomePresence"] == ON:
#		if items["Priza7_Power"] != ON:
#			events.sendCommand("Priza7_Power", "ON")
		#	events.sendCommand("OffFlag7", "OFF")	#nou pe data 21.01.2024

#@rule("Priza10_Power ON state cronjob", description="Priza10_Power ON state", tags=["cron", "Priza10_Power"])
#@when("Time cron 0 45 5 * * ?")
#def priza10_power_on_state(event):
#	if items["Priza10_Power"] != ON:
#		events.sendCommand("Priza10_Power", "ON")

@rule("Priza11_Power OFF state cronjob", description="Priza11_Power OFF state", tags=["cron", "Priza11_Power"]) # Priza10 se transorma in Priza11 din 01.12.2025
@when("Time cron 0 30 22 * * ?")
def priza11_power_off_state(event):
	if items["Priza11_Power"] != OFF:
		events.sendCommand("Priza11_Power", "OFF")

@rule("Switch weekend on", description="Sensors reset and other functions using cron", tags=["cron", "Schedule"])
@when("Time cron 0 0 0 ? * SAT,SUN *")
def weekend_swon(event):
	if items["Weekend"] != ON:
		events.sendCommand("Weekend", "ON")
		events.sendCommand("Clock_alarm", "OFF")

@rule("Switch weekend off", description="Sensors reset and other functions using cron", tags=["cron", "Schedule"])
@when("Time cron 0 0 0 ? * MON,TUE,WED,THU,FRI *")
def weekend_swoff(event):
	if items["Weekend"] != OFF:
		events.sendCommand("Weekend", "OFF")
		events.sendCommand("Clock_alarm", "OFF")

@rule("Backup_rrd4j activate", description="Activate Backup_rrd4j", tags=["cron", "Backup_rrd4j"])
@when("Time cron 0 0 0 * * ? *")
def backup_rrd4j_on(event):
	events.sendCommand("Backup_rrd4j", "ON")

@rule("Backup_rrd4j deactivate", description="Deactivate Backup_rrd4j", tags=["cron", "Backup_rrd4j"])
@when("Time cron 0 5 0 * * ? *")
def backup_rrd4j_off(event):
	events.sendCommand("Backup_rrd4j", "OFF")

@rule("Start HMSmqtt", description="Start HMS mqtt container", tags=["cron", "Container Docker"])
@when("Time cron 0 0 * * * ? *")
@when("Time cron 0 15 * * * ? *")
@when("Time cron 0 30 * * * ? *")
@when("Time cron 0 45 * * * ? *")
def start_hmsmqtt(event):
	if items["DaylightPhilips_Dark"] != ON:
		events.sendCommand("HMS2mqtt", "ON")

@rule("Stop HMSmqtt", description="Stop HMS mqtt container", tags=["cron", "Container Docker"])
@when("Time cron 0 13 * * * ? *")
@when("Time cron 0 28 * * * ? *")
@when("Time cron 0 43 * * * ? *")
@when("Time cron 0 58 * * * ? *")
def stop_hmsmqtt(event):
	events.sendCommand("HMS2mqtt", "OFF")

# DISABLED 2026-06-30: Log deletion script replaced with persistent logging
# Logs will no longer be truncated daily; use proper logrotate configuration instead
# @rule("Delete large log files", description="Mosquitto & linux log", tags=["Mosquitto", "Log"])
# @when("Time cron 0 0 0 * * ? *")
# def large_log(event):
# 	large_log = Exec.executeCommandLine("/etc/openhab2/scripts/delete_logs.sh", 10000)

@rule("Stop Prize", description="Stop prize", tags=["cron", "Prize"])
@when("Time cron 0 0 0 * * ? *")
@when("Time cron 0 0 12 * * ? *")
def stop_prize(event):
	# FIX-A: getattr(event, "trigger") always returns None for cron events in OH 2.5
	# JSR223. Use DateTime.now().getHourOfDay() to distinguish midnight (0) from noon (12).
	# Midnight: clear full latch first, then outlet — single rule so order is deterministic.
	if DateTime.now().getHourOfDay() == 0:
		logger.info("SCHEDULE", "Midnight: Stopping Priza1, clearing BatteryFull")
		if items["Priza1_BatteryFull"] != OFF:
			events.sendCommand("Priza1_BatteryFull", "OFF")
			LogAction.logInfo("Priza1", "Priza1_BatteryFull OFF — end of day (midnight)")
	else:
		logger.info("SCHEDULE", "Noon: Stopping Priza1")
	events.sendCommand("Priza1_Power", "OFF")
#	events.sendCommand("Priza2_Power", "OFF")
#	events.sendCommand("Priza3_Power", "OFF")
#	events.sendCommand("Priza4_Power", "OFF")
#	events.sendCommand("Priza7_Power", "OFF")

@rule("Start Prize", description="Start prize", tags=["cron", "Prize"])
@when("Time cron 15 0 0 * * ? *")
@when("Time cron 15 0 12 * * ? *")
def start_prize(event):
	logger.info("SCHEDULE", "Starting devices on schedule (Priza2, Priza3)")
	#events.sendCommand("Priza1_Power", "ON") ###18.10.2025### A fost transformata Priza1 pentru E-Bike
	events.sendCommand("Priza2_Power", "ON")
	# Guard: Don't turn ON Priza3 if ECO is managing power
	if items["PWRConsumption"] != OnOffType.ON:
		events.sendCommand("Priza3_Power", "ON")
	#events.sendCommand("Priza4_Power", "ON")
#	events.sendCommand("Priza7_Power", "ON")

@rule("Daily reset Priza1_BatteryFull", description="Reset BatteryFull flag at 05:00 to prevent stuck state", tags=["cron", "Priza1", "safety"])
@when("Time cron 0 0 5 * * ? *")
def reset_priza1_battery_full(event):
	"""
	Daily safety reset of Priza1_BatteryFull at 05:00 AM.
	Prevents circular dependency if flag gets stuck ON:
	- Flag stuck ON → auto charging blocked
	- Charging blocked → can't turn socket ON
	- Socket can't turn ON → flag can't reset (only resets when socket turns ON)

	This rule breaks the cycle by forcing a reset every morning before charging windows.
	Harmless if flag is already OFF; ensures charging can proceed.
	"""
	priza1_full = str(items["Priza1_BatteryFull"]).strip()
	if priza1_full == "ON":
		events.sendCommand("Priza1_BatteryFull", "OFF")
		LogAction.logInfo("Priza1", "Daily safety reset: Priza1_BatteryFull OFF (05:00)")
		logger.info("BATTERY", "Priza1_BatteryFull daily reset at 05:00")
	else:
		logger.info("BATTERY", "Priza1_BatteryFull already OFF at 05:00 (normal)")

# NOTE: eco_timer_on/off block and eco_power_switch_state rule removed 2026-03-07.
# Device sequencing on Eco_Power_Switch changes is now handled entirely by
# 080_Power. Eco_Power_Switch is still a valid manual override — 080_Power
# watches it directly via an Item changed trigger.
