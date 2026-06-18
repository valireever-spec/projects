import json
import os
from pathlib import Path

PROJECTS_ROOT = Path("/home/vali/projects")

def scan_for_projects():
    """Scan projects directory for tracker.json files"""
    projects = []

    for item in PROJECTS_ROOT.iterdir():
        if not item.is_dir() or item.name.startswith('.'):
            continue
        if item.name in ['tracker', 'project-designer', '__pycache__', 'venv']:
            continue

        tracker_file = item / "tracker.json"
        if tracker_file.exists():
            try:
                with open(tracker_file, 'r') as f:
                    config = json.load(f)
                config['path'] = str(item)
                projects.append(config)
            except Exception as e:
                print(f"Error reading {tracker_file}: {e}")

    return projects

def get_tracker_config(project_path):
    """Get tracker.json for a specific project"""
    tracker_file = Path(project_path) / "tracker.json"
    if tracker_file.exists():
        with open(tracker_file, 'r') as f:
            return json.load(f)
    return None

def create_default_tracker_config(name, description="", tech_stack=""):
    """Create default tracker.json template"""
    return {
        "name": name,
        "description": description,
        "tech_stack": tech_stack,
        "tracked": True
    }
