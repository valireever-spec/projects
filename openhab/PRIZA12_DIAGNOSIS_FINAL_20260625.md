# Priza12 Diagnosis - Final Report (2026-06-25)

## Summary
**Priza12 is configured in OpenHAB but NOT communicating.**

---

## Finding 1: Device IS Configured
✅ Priza12 Thing exists in OpenHAB:
```
UID: mqtt:topic:priza12
Label: Priza12
Status: ONLINE
Bridge: mqtt:systemBroker:mosquitto
Location: Prize
```

---

## Finding 2: Correct Item Linking
✅ Items are correctly linked to MQTT channels:

**Power Channel:**
- Thing: `mqtt:topic:priza12`
- Channel: `Power` 
- Linked Item: `Priza12_Power`
- MQTT Topics:
  - State: `stat/priza12/POWER`
  - Command: `cmnd/priza12/POWER`

**Teleperiod Channel:**
- Thing: `mqtt:topic:priza12`
- Channel: `Teleperiod`
- Linked Item: `Priza12_TelePeriod`
- MQTT Topics:
  - State: `stat/priza12/TelePeriod`
  - Command: `cmnd/priza12/TelePeriod`

---

## Finding 3: Device NOT Publishing
❌ **Items are NULL — Device Never Published State**

| Item | Type | State | LastUpdate | Issue |
|------|------|-------|-----------|-------|
| Priza12_Power | Switch | NULL | null | No MQTT message on `stat/priza12/POWER` |
| Priza12_TelePeriod | Number | NULL | null | No MQTT message on `stat/priza12/TelePeriod` |

**Evidence:**
- Thing status: ONLINE (can receive commands)
- Items state: NULL (never received updates)
- Logs: No Priza12 messages in last 5000 log lines
- **Conclusion:** Device is connected to broker but not sending telemetry

---

## Finding 4: Device Has No Current Sensor
✅ Confirmed: Priza12 has NO power current sensor

**Available channels:**
- Power (ON/OFF switch) 
- Teleperiod (telemetry interval)

**NOT available:**
- Current, Voltage, Apparent Power, Power Factor
- (This matches Tasmota devices without INA219 or similar)

---

## Finding 5: Device Controls Working (One-Way)
✅ Automation CAN control Priza12

The 017_Prize script can send commands:
- Command topic: `cmnd/priza12/POWER` → Will turn device ON/OFF
- AutoControl logic: Ownership-based (AUTO vs EXTERNAL)

**BUT:** Feedback fails because device doesn't publish state back.

---

## Root Cause

**Priza12 (Tasmota device) is NOT publishing its telemetry.**

Likely causes:
1. **WiFi signal too weak** — Device connected but not stable
2. **MQTT subscribe misconfigured** — Device not subscribed to broker  
3. **Tasmota Topic mismatch** — Device publishes to different topic (e.g., `tele/` instead of `stat/`)
4. **Device idle/asleep** — Configured to not send periodic telemetry
5. **Broker firewall/ACL issue** — Device blocked from publishing

---

## Verification Steps

### Step 1: Check Device Connectivity
```bash
# SSH into OpenHAB system
ssh openhabian@192.168.3.25

# Check if device sends any MQTT messages
mosquitto_sub -h 127.0.0.1 -t 'stat/priza12/#' -W 5
mosquitto_sub -h 127.0.0.1 -t 'tele/priza12/#' -W 5  # Alternative topic

# If nothing appears in 5 seconds, device is not sending
```

### Step 2: Check Device Web Interface
- Access Priza12 web interface directly (check its IP)
- Verify WiFi signal strength
- Check MQTT broker settings
- Confirm TelePeriod is not too long (should be 60-120s)

### Step 3: Force Device to Publish
```bash
# Send MQTT command to force status update
mosquitto_pub -h 127.0.0.1 -t 'cmnd/priza12/Status' -m '0'

# Should see response on stat/priza12/STATUS
mosquitto_sub -h 127.0.0.1 -t 'stat/priza12/+' -C 1
```

### Step 4: Check Tasmota Logs
- Connect to device web console
- Check WiFi signal (RSSI)
- Check MQTT connection status
- Look for publish errors

---

## Solutions

### Option A: Reconnect Device (Quick Fix)
1. Power off Priza12 for 10 seconds
2. Power back on
3. Wait 1-2 minutes for telemetry
4. Check if items update

### Option B: Fix WiFi Issue
1. Check signal strength on device web UI
2. Reduce distance to WiFi AP
3. Check for interference
4. If weak, consider WiFi extender or device relocation

### Option C: Reconfigure MQTT
1. Verify MQTT broker IP in Tasmota
2. Verify authentication credentials
3. Check broker ACL/firewall rules
4. Restart device

### Option D: Disable Priza12 (If Not Needed)
If Priza12 doesn't work and you don't need it:

**Remove from automation** (080_Power_rev20260312.py):
```python
# Line 133: Remove from devices_on
devices_on = [
    # "Priza12_Power_auto",  ← Delete this line
    "Priza7_Power",
    ...
]

# Line 615: Remove from seasonal device list
return [
    # "Priza12_Power_auto",  ← Delete this line
    "Priza7_Power",
    ...
]
```

Then redeploy the script.

---

## Current Impact

**Priza12 Status in Automation:**
- ✅ Can receive ON/OFF commands from automation
- ❌ Cannot confirm its state (feedback missing)
- ❌ Charging sequence spends 3 seconds checking a device with no feedback
- ⚠️ Ownership logic works but can't verify if command succeeded

**Safety:** Low risk (other devices still charge normally)

---

## Recommendation

**Try Option A first** (reconnect device):
1. Physically power-cycle Priza12
2. Wait 2 minutes
3. Check if `Priza12_Power` updates from NULL to ON/OFF

If it still doesn't work, check the device's web interface or consider disabling it from the automation.

Would you like me to help with any of these options?
