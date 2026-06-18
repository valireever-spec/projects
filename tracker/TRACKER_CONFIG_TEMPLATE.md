# tracker.json Template

Each project can have a `tracker.json` file that defines its metadata for the Design & Bug Tracker.

## Location
Place this file in the project root:
```
/home/vali/projects/my-project/
├── README.md
├── tracker.json          ← Add this
└── ... (project files)
```

## Example

```json
{
  "name": "investing-platform",
  "description": "Portfolio investment platform with real-time analytics",
  "tech_stack": "Python, FastAPI, React",
  "tracked": true
}
```

## Fields

- **name** (required) — Project name (unique)
- **description** (optional) — What the project does
- **tech_stack** (optional) — Technologies used (e.g., "Python, FastAPI, React")
- **tracked** (optional, default: true) — Whether to include in tracker

## Minimal

```json
{
  "name": "my-project"
}
```

## Full Example

```json
{
  "name": "business-dev-platform",
  "description": "Internal business development tools for deal analysis",
  "tech_stack": "Python, Django, PostgreSQL, React",
  "tracked": true
}
```

## Auto-Import

Once you add `tracker.json` to a project, the tracker will:
1. Auto-discover it when you click "Import Projects" in the dashboard
2. Create a project record with the metadata
3. Initialize it as a new project ready for review

## For All Projects

Add this to each portfolio project:

```bash
cat > tracker.json << 'EOF'
{
  "name": "project-name",
  "description": "Brief description",
  "tech_stack": "Tech list"
}
EOF
```

Then in the tracker dashboard, click "Import Projects" to bulk-load all discovered projects.
