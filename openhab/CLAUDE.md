# CLAUDE.md

## Tracker Integration: V-Model & Requirements

This project participates in a portfolio-wide **requirements tracking system**.
All requirements are synced bidirectionally with a central tracker.

**Your Project Files:**
- `./V_MODEL_BOARD.md` — Auto-generated board showing phase progress
  (coverage %, requirements status, linked bugs)
- `./FUNCTIONAL_REQUIREMENTS.md` — Feature specs you maintain
- `./NONFUNCTIONAL_REQUIREMENTS.md` — Performance/reliability specs you maintain

**Workflow:**
1. Edit FUNCTIONAL/NONFUNCTIONAL_REQUIREMENTS.md
2. Tracker auto-imports every 5 minutes
3. Update status in tracker UI as you implement (Proposed → Validated)
4. View your phase progress in V_MODEL_BOARD.md
5. Link bugs to requirements when issues found

**Tracker Dashboard:** http://localhost:5173

**Auto-Sync (every 5 minutes):**
- Requirements imported from your files → Tracker DB
- V_MODEL_BOARD.md exported to your project
- Requirement status updates flow back to your board

See V_MODEL_BOARD.md in your project root for current phase progress.

---

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a working directory for managing automation rules and scripts on a remote **OpenHAB 2** home automation system running at `192.168.3.25` (user: `openhabian` and `claude`).

OpenHAB 2 is a vendor-agnostic, Java-based home automation platform. It manages:
- **Items** (logical devices/sensors)
- **Rules** (automation logic triggered by item state changes)
- **Bindings** (integrations with physical devices and services)
- **Automation scripts** (Python, JavaScript via JSR223 scripting engine)

## System Architecture

The OpenHAB 2 system is deployed remotely with the following structure:

```
/home/openhabian/homeassistant/
├── automations.yaml          # YAML-based automation rules
└── (other config files)

/etc/openhab2/
├── automation/jsr223/python/personal/
│   ├── 082_tomato_led.py     # Python automation scripts
│   └── (other Python scripts)
└── (other OpenHAB configuration)
```

**Access**: SSH key at `~/.ssh/openhab_claude` for user `claude@192.168.3.25`

## Common Commands

### Fetch Automations from Remote

```bash
# Get the current automations.yaml
scp openhabian@192.168.3.25:/home/openhabian/homeassistant/automations.yaml /tmp/automations_current.yaml

# Get a specific Python automation script
scp -i ~/.ssh/openhab_claude claude@192.168.3.25:/etc/openhab2/automation/jsr223/python/personal/082_tomato_led.py /tmp/082_tomato_led.py
```

### Deploy Automations to Remote

```bash
# Upload and replace automations.yaml
# First, edit locally, then:
cat /tmp/automations_current.yaml | ssh openhabian@192.168.3.25 "cat > /home/openhabian/homeassistant/automations.yaml"

# Upload a Python script
scp -i ~/.ssh/openhab_claude /tmp/082_tomato_led.py claude@192.168.3.25:/etc/openhab2/automation/jsr223/python/personal/082_tomato_led.py

# Transfer other files
scp -i ~/.ssh/openhab_claude /tmp/wakeomv.sh claude@192.168.3.25:/tmp/wakeomv.sh
```

### Inspect Remote System

```bash
# SSH into the system
ssh openhabian@192.168.3.25
ssh -i ~/.ssh/openhab_claude claude@192.168.3.25

# Check OpenHAB logs
ssh openhabian@192.168.3.25 "tail -f /var/log/openhab2/openhab.log"

# Verify automation files are in place
ssh -i ~/.ssh/openhab_claude claude@192.168.3.25 "ls -la /etc/openhab2/automation/jsr223/python/personal/"
```

## OpenHAB 2 Concepts

### YAML Automations
- Located in `/home/openhabian/homeassistant/automations.yaml`
- Define trigger → condition → action flows
- Triggers: item state changes, time-based, system events
- Actions: send commands to items, log messages, call scripts

### Python Automation Scripts (JSR223)
- Located in `/etc/openhab2/automation/jsr223/python/personal/`
- Run in the OpenHAB context with access to items, rules engine, logging
- Useful for complex logic, data processing, external API calls
- Scripts are auto-loaded on OpenHAB startup

## Workflow

1. **Fetch** current automations: `scp ... /tmp/automations_current.yaml`
2. **Edit** locally in `/tmp/` (or elsewhere)
3. **Test** by understanding the YAML/Python syntax
4. **Deploy** via `scp` or SSH piping back to the remote system
5. **Verify** with `ssh ... tail -f /var/log/openhab2/openhab.log` to check for errors

## SSH Setup

- **Primary key**: `~/.ssh/openhab_claude` (used for `claude` user)
- **Fallback**: Password auth available for `openhabian` user
- **Hosts**: `openhabian@192.168.3.25` or `claude@192.168.3.25`
