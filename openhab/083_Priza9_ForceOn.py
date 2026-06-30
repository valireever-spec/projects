# 083_Priza9_ForceOn.py
# Priza9ForceOn override handler - prevents other scripts from turning off Priza9_Power

from core.rules import rule
from core.triggers import when
from core.jsr223.scope import events, items
from core.actions import LogAction
from org.eclipse.smarthome.core.library.types import OnOffType

ON = OnOffType.ON
OFF = OnOffType.OFF

def is_state(item_state, target_state):
    """Safe state comparison using string conversion. Handles Java State objects reliably."""
    return str(item_state).strip() == str(target_state).strip()


@rule("Priza9ForceOn activation", description="Turn on Priza9_Power when Priza9ForceOn is activated", tags=["Priza9_Power", "Force"])
@when("Item Priza9ForceOn changed to ON")
def priza9_force_on_activated(event):
	if not is_state(items["Priza9_Power"], ON):
		events.sendCommand("Priza9_Power", "ON")
		LogAction.logInfo("Priza9ForceOn", "Priza9_Power forced ON")

@rule("Priza9ForceOn deactivation", description="Log when Priza9ForceOn is deactivated", tags=["Priza9_Power", "Force"])
@when("Item Priza9ForceOn changed to OFF")
def priza9_force_on_deactivated(event):
	LogAction.logInfo("Priza9ForceOn", "Priza9_Power force override deactivated - normal automation rules resume")
