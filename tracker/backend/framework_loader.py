import re
from pathlib import Path

FRAMEWORK_PATH = Path("/home/vali/projects/project-designer/FRAMEWORK.md")
PLAYBOOKS_PATH = Path("/home/vali/projects/project-designer/PLAYBOOKS.md")
CHECKLIST_PATH = Path("/home/vali/projects/project-designer/CHECKLIST.md")

PILLARS = [
    "Architecture Discipline & Traceability",
    "Build Quality In / Error-Proofing",
    "Verification & Validation",
    "Continuous Integration & Safe Delivery",
    "Root-Cause Driven Improvement",
    "Security & Privacy by Design",
    "Observability & Telemetry",
    "Maintainability & Sustainable Pace"
]

def load_rules():
    try:
        content = FRAMEWORK_PATH.read_text()
        rules = {"pillars": {}}

        for pillar in PILLARS:
            rules["pillars"][pillar] = {
                "name": pillar,
                "rules": []
            }

        lines = content.split('\n')
        current_pillar = None
        current_rule = None

        for i, line in enumerate(lines):
            for pillar in PILLARS:
                if pillar.lower() in line.lower() and '#' in line:
                    current_pillar = pillar
                    break

            if line.startswith('### Rule'):
                match = re.search(r'### Rule (\d+\.\d+)', line)
                if match:
                    rule_id = match.group(1)
                    rule_title = line.replace(f'### Rule {rule_id}', '').strip()
                    current_rule = {
                        "id": rule_id,
                        "title": rule_title,
                        "content": ""
                    }
                    if current_pillar:
                        rules["pillars"][current_pillar]["rules"].append(current_rule)
            elif current_rule and line.strip() and not line.startswith('#'):
                current_rule["content"] += line + "\n"

        return rules
    except FileNotFoundError:
        return {"status": "not_found", "message": "FRAMEWORK.md not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def load_playbooks():
    try:
        content = PLAYBOOKS_PATH.read_text()
        playbooks = {}

        lines = content.split('\n')
        current_playbook = None

        for line in lines:
            if line.startswith('## '):
                title = line.replace('## ', '').strip()
                current_playbook = {
                    "title": title,
                    "content": ""
                }
                playbooks[title] = current_playbook
            elif current_playbook:
                current_playbook["content"] += line + "\n"

        return {"playbooks": playbooks, "count": len(playbooks)}
    except FileNotFoundError:
        return {"status": "not_found", "message": "PLAYBOOKS.md not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def load_checklist():
    try:
        content = CHECKLIST_PATH.read_text()
        return {
            "status": "loaded",
            "lines": len(content.split('\n')),
            "content": content
        }
    except FileNotFoundError:
        return {"status": "not_found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
