"""
Background job for auto-importing requirements from all projects.
Runs on a schedule to keep tracker in sync with project files.
"""

import logging
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from .models import Project, Requirement
from .database import SessionLocal
from .requirement_parser import load_and_parse_project_requirements
from .project_board_sync import ProjectBoardSyncer
import json

logger = logging.getLogger(__name__)

class RequirementsAutoImporter:
    """Auto-imports requirements from all projects on schedule."""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.last_sync_times = {}  # Track last sync per project
        self.sync_count = 0

    def start(self):
        """Start the background scheduler."""
        if not self.scheduler.running:
            # Import every 5 minutes
            self.scheduler.add_job(
                self.sync_all_projects,
                'interval',
                minutes=5,
                id='auto_import_requirements',
                name='Auto-import requirements from all projects',
                max_instances=1  # Prevent concurrent runs
            )
            self.scheduler.start()
            logger.info("✅ Background requirement sync scheduler started (every 5 minutes)")

    def stop(self):
        """Stop the background scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("⏹️  Background requirement sync scheduler stopped")

    def sync_all_projects(self):
        """Sync requirements from projects AND export tracker data back to projects."""
        db = SessionLocal()
        try:
            projects = db.query(Project).all()
            total_imported = 0
            total_updated = 0
            projects_with_changes = []

            # Step 1: Import requirements FROM projects
            for project in projects:
                if not project.path:
                    continue

                imported, updated = self.sync_project_requirements(db, project)
                total_imported += imported
                total_updated += updated

                if imported > 0 or updated > 0:
                    projects_with_changes.append({
                        "name": project.name,
                        "imported": imported,
                        "updated": updated
                    })

                self.last_sync_times[project.id] = datetime.now()

            # Step 2: Export tracker data back TO all projects (V-Model boards)
            export_result = ProjectBoardSyncer.sync_all_projects(db)
            projects_exported = export_result["synced"]

            self.sync_count += 1

            if projects_with_changes:
                logger.info(
                    f"✅ Auto-sync #{self.sync_count}: "
                    f"IMPORT: {total_imported} new, {total_updated} updated | "
                    f"EXPORT: {projects_exported} project boards updated"
                )
            else:
                logger.debug(
                    f"✓ Auto-sync #{self.sync_count}: "
                    f"No changes to import | {projects_exported} boards updated"
                )

        except Exception as e:
            logger.error(f"❌ Error during auto-sync: {e}", exc_info=True)
        finally:
            db.close()

    def sync_project_requirements(self, db: Session, project: Project) -> tuple:
        """
        Sync requirements for a single project.
        Returns: (imported_count, updated_count)
        """
        try:
            parsed = load_and_parse_project_requirements(project.path)
        except Exception as e:
            logger.warning(f"⚠️  Could not parse requirements for {project.name}: {e}")
            return 0, 0

        imported_count = 0
        updated_count = 0

        # Process functional requirements
        for fr in parsed.get("functional", []):
            existing = db.query(Requirement).filter(
                Requirement.project_id == project.id,
                Requirement.req_id == fr.req_id
            ).first()

            acceptance_criteria = json.dumps([
                {"id": c["id"], "description": c["description"]}
                for c in fr.acceptance_criteria
            ])
            test_cases = json.dumps(fr.test_cases)

            description = f"Actor: {fr.actor}\n\nUse Case:\n{fr.use_case}"

            if existing:
                # Update if changed
                if (existing.title != fr.title or
                    existing.description != description or
                    existing.acceptance_criteria != acceptance_criteria):
                    existing.title = fr.title
                    existing.description = description
                    existing.category = fr.category
                    existing.acceptance_criteria = acceptance_criteria
                    existing.test_case = test_cases
                    db.commit()
                    updated_count += 1
            else:
                # Create new requirement
                db_req = Requirement(
                    project_id=project.id,
                    req_id=fr.req_id,
                    req_type="Functional",
                    category=fr.category,
                    title=fr.title,
                    description=description,
                    acceptance_criteria=acceptance_criteria,
                    test_case=test_cases,
                    measurement_method=None,
                    target=None,
                    status="Proposed"
                )
                db.add(db_req)
                db.commit()
                imported_count += 1

        # Process non-functional requirements
        for nfr in parsed.get("nonfunctional", []):
            existing = db.query(Requirement).filter(
                Requirement.project_id == project.id,
                Requirement.req_id == nfr.req_id
            ).first()

            if existing:
                # Update if changed
                if (existing.title != nfr.title or
                    existing.description != nfr.specification or
                    existing.measurement_method != nfr.measurement_method or
                    existing.target != nfr.target):
                    existing.title = nfr.title
                    existing.description = nfr.specification
                    existing.category = nfr.category
                    existing.measurement_method = nfr.measurement_method
                    existing.target = nfr.target
                    existing.test_case = nfr.test_case
                    db.commit()
                    updated_count += 1
            else:
                # Create new requirement
                db_req = Requirement(
                    project_id=project.id,
                    req_id=nfr.req_id,
                    req_type="Non-Functional",
                    category=nfr.category,
                    title=nfr.title,
                    description=nfr.specification,
                    acceptance_criteria=None,
                    test_case=nfr.test_case,
                    measurement_method=nfr.measurement_method,
                    target=nfr.target,
                    status="Proposed"
                )
                db.add(db_req)
                db.commit()
                imported_count += 1

        return imported_count, updated_count

    def get_status(self) -> dict:
        """Get current auto-import status."""
        return {
            "running": self.scheduler.running,
            "sync_count": self.sync_count,
            "last_sync_times": {
                pid: time.isoformat() for pid, time in self.last_sync_times.items()
            },
            "next_run": str(self.scheduler.get_job('auto_import_requirements').next_run_time)
            if self.scheduler.running else None
        }


# Global instance
importer = RequirementsAutoImporter()
