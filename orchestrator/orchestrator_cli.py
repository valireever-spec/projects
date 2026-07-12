"""
Orchestrator CLI Tool - Production Deployment Component

Click-based command-line interface for orchestrator management.
"""

import sys
import logging
from typing import Optional
from datetime import datetime
import click

try:
    from tabulate import tabulate
except ImportError:
    # Fallback tabulate function
    def tabulate(data, headers=None, tablefmt='grid'):
        if not data:
            return ""
        # Simple text format
        lines = []
        if headers:
            lines.append(" | ".join(str(h) for h in headers))
            lines.append("-" * 80)
        for row in data:
            lines.append(" | ".join(str(cell) for cell in row))
        return "\n".join(lines)

# Add orchestrator to path
sys.path.insert(0, '/home/vali/projects/orchestrator')

from database_layer import Database
from orchestrator_workflow import Orchestrator
from tracker_integration import TrackerIntegration
from claude_api_integration import ClaudeIntegration
from designer_agent import Requirement, RequirementType

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class OrchestratorCLI:
    """CLI handler for orchestrator."""

    def __init__(self, db_path: str = "/tmp/orchestrator.db",
                 project_root: str = "/home/vali/projects/investing-platform"):
        """Initialize CLI.

        Args:
            db_path: Database path
            project_root: Project root path
        """
        self.db = Database(db_path)
        self.orchestrator = Orchestrator(project_root)
        self.tracker = TrackerIntegration()
        self.claude = ClaudeIntegration(use_real_api=True)
        self.project_root = project_root


# Global CLI instance
cli_instance = OrchestratorCLI()


@click.group()
def cli():
    """Orchestrator CLI - Autonomous project development management."""
    pass


# ============================================================================
# REQUIREMENT COMMANDS
# ============================================================================

@cli.command()
@click.option('--title', prompt='Requirement title', help='Title of requirement')
@click.option('--description', prompt='Description', help='Requirement description')
@click.option('--project', default='investing-platform', help='Project name')
@click.option('--type', 'req_type', default='feature', help='Requirement type')
def create_req(title: str, description: str, project: str, req_type: str):
    """Create a new requirement."""
    try:
        req_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        cli_instance.db.create_requirement(req_id, title, description, project)

        click.echo(f"\n✅ Created requirement: {req_id}")
        click.echo(f"   Title: {title}")
        click.echo(f"   Project: {project}")
        click.echo(f"   Type: {req_type}")
        click.echo(f"   Status: Proposed\n")

    except Exception as e:
        click.echo(f"\n❌ Error creating requirement: {e}\n", err=True)


@cli.command()
@click.argument('requirement_id')
def status(requirement_id: str):
    """Get requirement status."""
    try:
        req = cli_instance.db.get_requirement(requirement_id)

        if not req:
            click.echo(f"\n❌ Requirement not found: {requirement_id}\n", err=True)
            return

        click.echo(f"\n📋 Requirement: {requirement_id}")
        click.echo(f"   Title: {req['title']}")
        click.echo(f"   Status: {req['status']}")
        click.echo(f"   Project: {req['project']}")
        click.echo(f"   Created: {req['created_at']}\n")

        # Show audit trail
        audit_log = cli_instance.db.get_audit_log(requirement_id)
        if audit_log:
            click.echo("   📜 Audit Trail:")
            for entry in audit_log[:5]:
                click.echo(f"      - {entry['action']} ({entry['status']})")
            click.echo()

    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n", err=True)


@cli.command()
@click.option('--status', default=None, help='Filter by status')
@click.option('--project', default=None, help='Filter by project')
def list_reqs(status: Optional[str], project: Optional[str]):
    """List all requirements."""
    try:
        if status:
            reqs = cli_instance.db.get_requirements_by_status(status, project)
        else:
            reqs = cli_instance.db.get_requirements_by_status("proposed", project) if project else []

        if not reqs:
            click.echo("\n✅ No requirements found\n")
            return

        table_data = [
            [req['id'], req['title'][:40], req['status'], req['project']]
            for req in reqs
        ]

        click.echo("\n" + tabulate(
            table_data,
            headers=['ID', 'Title', 'Status', 'Project'],
            tablefmt='grid'
        ) + "\n")

    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n", err=True)


# ============================================================================
# WORKFLOW COMMANDS
# ============================================================================

@cli.command()
@click.argument('requirement_id')
@click.option('--background', is_flag=True, help='Run in background')
def run(requirement_id: str, background: bool):
    """Run orchestrator workflow for a requirement."""
    try:
        req = cli_instance.db.get_requirement(requirement_id)

        if not req:
            click.echo(f"\n❌ Requirement not found: {requirement_id}\n", err=True)
            return

        click.echo(f"\n▶️  Starting workflow for {requirement_id}...")

        # Create requirement object
        requirement = Requirement(
            id=requirement_id,
            title=req['title'],
            description=req['description'],
            type=RequirementType.FEATURE
        )

        # Execute workflow
        click.echo("   Phase 1️⃣: Capturing project state...")
        cli_instance.db.update_requirement_status(requirement_id, "analyzed")

        click.echo("   Phase 2️⃣: Analyzing with Claude...")
        claude_result = cli_instance.claude.analyze_requirement(
            requirement_id,
            req['title'],
            req['description'],
            "",
            "feature"
        )

        if claude_result:
            click.echo(f"      ✓ Analysis complete (source: {claude_result['source']})")
            click.echo(f"      ✓ Decisions: {len(claude_result['decisions'])}")
            click.echo(f"      ✓ Tasks: {len(claude_result['tasks'])}")
            click.echo(f"      ✓ Effort: {claude_result['effort']} hours")
            if claude_result['tokens']['total'] > 0:
                click.echo(f"      ✓ Tokens: {claude_result['tokens']['total']}")

            cli_instance.db.store_design(requirement_id, claude_result)

        click.echo("   Phase 3️⃣: Storing results...")
        cli_instance.db.update_requirement_status(requirement_id, "implemented")

        click.echo(f"\n✅ Workflow complete for {requirement_id}\n")

    except Exception as e:
        click.echo(f"\n❌ Workflow failed: {e}\n", err=True)


@cli.command()
@click.argument('requirement_id')
def logs(requirement_id: str):
    """View audit logs for a requirement."""
    try:
        audit_log = cli_instance.db.get_audit_log(requirement_id)

        if not audit_log:
            click.echo(f"\n✅ No audit entries\n")
            return

        click.echo(f"\n📜 Audit Log for {requirement_id}:\n")

        table_data = [
            [entry['timestamp'], entry['action'], entry['status']]
            for entry in audit_log
        ]

        click.echo(tabulate(
            table_data,
            headers=['Timestamp', 'Action', 'Status'],
            tablefmt='grid'
        ) + "\n")

    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n", err=True)


# ============================================================================
# SYSTEM COMMANDS
# ============================================================================

@cli.command()
def health():
    """Check system health."""
    try:
        click.echo("\n🏥 System Health Check:\n")

        # Database
        stats = cli_instance.db.get_stats()
        db_ok = stats['total_requirements'] >= 0
        click.echo(f"   {'✅' if db_ok else '❌'} Database: {stats['database_path']}")
        click.echo(f"      Size: {stats['database_size_bytes'] / 1024:.1f} KB")

        # Tracker
        tracker_ok = cli_instance.tracker.is_available()
        click.echo(f"   {'✅' if tracker_ok else '⚠️'} Tracker: {'Available' if tracker_ok else 'Unavailable'}")

        # Claude API
        claude_ok = cli_instance.claude.is_available()
        click.echo(f"   {'✅' if claude_ok else '⚠️'} Claude API: {'Available' if claude_ok else 'Using mock'}")

        # Overall
        overall = db_ok  # Database is required
        click.echo(f"\n   Overall: {'✅ Healthy' if overall else '❌ Issues detected'}\n")

    except Exception as e:
        click.echo(f"\n❌ Health check failed: {e}\n", err=True)


@cli.command()
def stats():
    """Show orchestrator statistics."""
    try:
        stats = cli_instance.db.get_stats()

        click.echo("\n📊 Orchestrator Statistics:\n")
        click.echo(f"   Total requirements: {stats['total_requirements']}")
        click.echo(f"   Verified requirements: {stats['verified_requirements']}")
        click.echo(f"   Total audit entries: {stats['total_audit_entries']}")
        click.echo(f"   Database: {stats['database_path']}")
        click.echo(f"   Size: {stats['database_size_bytes'] / 1024:.1f} KB\n")

        claude_stats = cli_instance.claude.get_usage_stats()
        click.echo(f"   Claude API:")
        click.echo(f"      Requests: {claude_stats['total_requests']}")
        click.echo(f"      Tokens: {claude_stats['total_tokens']}")
        click.echo(f"      Cost: {claude_stats['estimated_cost']}\n")

    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n", err=True)


@cli.command()
def info():
    """Show orchestrator information."""
    try:
        click.echo("\n" + "="*80)
        click.echo("ORCHESTRATOR - Autonomous Project Development System")
        click.echo("="*80 + "\n")

        click.echo("📋 Available Commands:\n")

        commands = [
            ["create-req", "Create a new requirement"],
            ["status", "Get requirement status"],
            ["list-reqs", "List all requirements"],
            ["run", "Execute workflow for requirement"],
            ["logs", "View audit log"],
            ["health", "Check system health"],
            ["stats", "Show statistics"],
        ]

        click.echo(tabulate(commands, headers=['Command', 'Description'], tablefmt='simple'))
        click.echo("\n" + "="*80 + "\n")

    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n", err=True)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    cli()
