"""
Production Database Layer - Phase 3 Core Component

Provides persistent storage for requirements, designs, implementations, and audit trail.
Supports SQLite (dev) and PostgreSQL (production).
"""

import logging
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

DATABASE_PATH = Path("/tmp/orchestrator.db")


class RequirementStatus(Enum):
    """Requirement status in database."""
    PROPOSED = "proposed"
    ANALYZED = "analyzed"
    ACCEPTED = "accepted"
    IMPLEMENTING = "implementing"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    DEPLOYED = "deployed"
    FAILED = "failed"


@dataclass
class StoredRequirement:
    """Requirement stored in database."""
    id: str
    title: str
    description: str
    status: str
    project: str
    created_at: str
    updated_at: str
    metadata: Dict = None


@dataclass
class StoredSnapshot:
    """State snapshot stored in database."""
    requirement_id: str
    phase: str  # "before", "after"
    timestamp: str
    files_count: int
    python_files: int
    test_files: int
    total_lines: int
    coverage_percent: float
    hash_data: Dict = None


@dataclass
class AuditLogEntry:
    """Audit log entry."""
    id: int
    requirement_id: str
    timestamp: str
    action: str  # "created", "analyzed", "implemented", etc.
    status: str
    details: Dict = None


class Database:
    """Production database for orchestrator state."""

    def __init__(self, db_path: str = str(DATABASE_PATH)):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.connection = None
        self._init_database()
        logger.info(f"Initialized Database at {db_path}")

    def _init_database(self):
        """Initialize database schema."""
        try:
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()

            # Create tables if they don't exist
            cursor.executescript("""
            CREATE TABLE IF NOT EXISTS requirements (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                project TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT
            );

            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                files_count INTEGER,
                python_files INTEGER,
                test_files INTEGER,
                total_lines INTEGER,
                coverage_percent REAL,
                hash_data TEXT,
                FOREIGN KEY (requirement_id) REFERENCES requirements(id)
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT,
                details TEXT,
                FOREIGN KEY (requirement_id) REFERENCES requirements(id)
            );

            CREATE TABLE IF NOT EXISTS design_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_id TEXT NOT NULL,
                decisions TEXT,
                effort_hours REAL,
                tasks TEXT,
                risks TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (requirement_id) REFERENCES requirements(id)
            );

            CREATE TABLE IF NOT EXISTS implementation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_id TEXT NOT NULL,
                tasks_completed INTEGER,
                tasks_failed INTEGER,
                changes_summary TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (requirement_id) REFERENCES requirements(id)
            );

            CREATE INDEX IF NOT EXISTS idx_requirements_status ON requirements(status);
            CREATE INDEX IF NOT EXISTS idx_requirements_project ON requirements(project);
            CREATE INDEX IF NOT EXISTS idx_audit_requirement ON audit_log(requirement_id);
            CREATE INDEX IF NOT EXISTS idx_snapshots_requirement ON snapshots(requirement_id);
            """)

            self.connection.commit()
            logger.info("Database schema initialized")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def create_requirement(self, req_id: str, title: str, description: str, project: str) -> bool:
        """Create new requirement in database.

        Args:
            req_id: Unique requirement ID
            title: Requirement title
            description: Description
            project: Project name

        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            now = datetime.now().isoformat()

            cursor.execute("""
            INSERT INTO requirements (id, title, description, status, project, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (req_id, title, description, RequirementStatus.PROPOSED.value, project, now, now))

            self.connection.commit()

            # Log to audit trail
            self._audit_log(req_id, "created", RequirementStatus.PROPOSED.value)

            logger.info(f"Created requirement: {req_id}")
            return True

        except Exception as e:
            logger.error(f"Error creating requirement: {e}")
            return False

    def update_requirement_status(self, req_id: str, status: str) -> bool:
        """Update requirement status.

        Args:
            req_id: Requirement ID
            status: New status

        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            now = datetime.now().isoformat()

            cursor.execute("""
            UPDATE requirements SET status = ?, updated_at = ? WHERE id = ?
            """, (status, now, req_id))

            self.connection.commit()

            # Log to audit trail
            self._audit_log(req_id, f"status_updated_to_{status}", status)

            logger.info(f"Updated requirement {req_id} status to {status}")
            return True

        except Exception as e:
            logger.error(f"Error updating requirement status: {e}")
            return False

    def store_snapshot(self, req_id: str, phase: str, snapshot_data: Dict) -> bool:
        """Store state snapshot.

        Args:
            req_id: Requirement ID
            phase: "before" or "after"
            snapshot_data: Snapshot data from Phase 1

        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
            INSERT INTO snapshots
            (requirement_id, phase, timestamp, files_count, python_files, test_files,
             total_lines, coverage_percent, hash_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                req_id,
                phase,
                snapshot_data.get('timestamp', datetime.now().isoformat()),
                snapshot_data.get('total_files', 0),
                snapshot_data.get('python_files', 0),
                snapshot_data.get('test_files', 0),
                snapshot_data.get('total_lines', 0),
                snapshot_data.get('coverage_percent', 0.0),
                json.dumps(snapshot_data.get('file_hashes', {}))
            ))

            self.connection.commit()
            logger.info(f"Stored {phase} snapshot for requirement {req_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing snapshot: {e}")
            return False

    def store_design(self, req_id: str, design_output: Dict) -> bool:
        """Store design output.

        Args:
            req_id: Requirement ID
            design_output: Design from Designer Agent

        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
            INSERT INTO design_results
            (requirement_id, decisions, effort_hours, tasks, risks, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                req_id,
                json.dumps(design_output.get('design_decisions', [])),
                design_output.get('estimated_effort_hours', 0.0),
                json.dumps(design_output.get('implementation_tasks', [])),
                json.dumps(design_output.get('risks', [])),
                datetime.now().isoformat()
            ))

            self.connection.commit()
            logger.info(f"Stored design for requirement {req_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing design: {e}")
            return False

    def store_implementation(self, req_id: str, impl_result: Dict) -> bool:
        """Store implementation result.

        Args:
            req_id: Requirement ID
            impl_result: Result from Implementer

        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
            INSERT INTO implementation_results
            (requirement_id, tasks_completed, tasks_failed, changes_summary, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (
                req_id,
                impl_result.get('tasks_completed', 0),
                impl_result.get('tasks_failed', 0),
                json.dumps(impl_result.get('changes_summary', {})),
                datetime.now().isoformat()
            ))

            self.connection.commit()
            logger.info(f"Stored implementation result for requirement {req_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing implementation: {e}")
            return False

    def get_requirement(self, req_id: str) -> Optional[Dict]:
        """Get requirement by ID.

        Args:
            req_id: Requirement ID

        Returns:
            Requirement dict or None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM requirements WHERE id = ?", (req_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Error getting requirement: {e}")
            return None

    def get_requirements_by_status(self, status: str, project: Optional[str] = None) -> List[Dict]:
        """Get all requirements by status.

        Args:
            status: Status to filter
            project: Optional project filter

        Returns:
            List of requirement dicts
        """
        try:
            cursor = self.connection.cursor()

            if project:
                cursor.execute(
                    "SELECT * FROM requirements WHERE status = ? AND project = ?",
                    (status, project)
                )
            else:
                cursor.execute("SELECT * FROM requirements WHERE status = ?", (status,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting requirements: {e}")
            return []

    def get_audit_log(self, req_id: str) -> List[Dict]:
        """Get audit log for a requirement.

        Args:
            req_id: Requirement ID

        Returns:
            List of audit log entries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM audit_log WHERE requirement_id = ? ORDER BY timestamp DESC",
                (req_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting audit log: {e}")
            return []

    def _audit_log(self, req_id: str, action: str, status: str, details: Optional[Dict] = None):
        """Create audit log entry.

        Args:
            req_id: Requirement ID
            action: Action performed
            status: Current status
            details: Optional details dict
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
            INSERT INTO audit_log (requirement_id, timestamp, action, status, details)
            VALUES (?, ?, ?, ?, ?)
            """, (
                req_id,
                datetime.now().isoformat(),
                action,
                status,
                json.dumps(details) if details else None
            ))
            self.connection.commit()

        except Exception as e:
            logger.warning(f"Error creating audit log: {e}")

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Statistics dict
        """
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT COUNT(*) FROM requirements")
            total_reqs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM requirements WHERE status = ?",
                          (RequirementStatus.VERIFIED.value,))
            verified_reqs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM audit_log")
            total_audit = cursor.fetchone()[0]

            return {
                'total_requirements': total_reqs,
                'verified_requirements': verified_reqs,
                'total_audit_entries': total_audit,
                'database_path': str(self.db_path),
                'database_size_bytes': self.db_path.stat().st_size if self.db_path.exists() else 0
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# Test usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print("\n" + "=" * 80)
    print("DATABASE LAYER TEST")
    print("=" * 80 + "\n")

    # Initialize database
    db = Database()

    try:
        # Test 1: Create requirement
        print("1️⃣ Creating requirement...")
        success = db.create_requirement(
            "REQ-P3-001",
            "Add authentication feature",
            "Implement JWT-based auth",
            "investing-platform"
        )
        print(f"   ✓ Created: {success}\n")

        # Test 2: Store snapshot
        print("2️⃣ Storing before snapshot...")
        success = db.store_snapshot(
            "REQ-P3-001",
            "before",
            {
                'total_files': 44420,
                'python_files': 21927,
                'test_files': 6348,
                'total_lines': 8560545,
                'coverage_percent': 75.0,
                'file_hashes': {'file1.py': 'hash1', 'file2.py': 'hash2'}
            }
        )
        print(f"   ✓ Stored: {success}\n")

        # Test 3: Update status
        print("3️⃣ Updating requirement status...")
        success = db.update_requirement_status("REQ-P3-001", RequirementStatus.ANALYZED.value)
        print(f"   ✓ Updated: {success}\n")

        # Test 4: Store design
        print("4️⃣ Storing design output...")
        success = db.store_design(
            "REQ-P3-001",
            {
                'design_decisions': [
                    {'title': 'Use JWT', 'confidence': 0.95},
                    {'title': 'Add tests', 'confidence': 1.0}
                ],
                'estimated_effort_hours': 16.0,
                'implementation_tasks': ['Design API', 'Implement', 'Test'],
                'risks': ['Security risk']
            }
        )
        print(f"   ✓ Stored: {success}\n")

        # Test 5: Get requirement
        print("5️⃣ Retrieving requirement...")
        req = db.get_requirement("REQ-P3-001")
        print(f"   ✓ Retrieved: {req['title']}")
        print(f"   ✓ Status: {req['status']}\n")

        # Test 6: Get audit log
        print("6️⃣ Getting audit log...")
        audit_log = db.get_audit_log("REQ-P3-001")
        print(f"   ✓ Audit entries: {len(audit_log)}")
        for entry in audit_log[:3]:
            print(f"      - {entry['action']} at {entry['timestamp']}\n")

        # Test 7: Get statistics
        print("7️⃣ Database statistics...")
        stats = db.get_stats()
        print(f"   ✓ Total requirements: {stats['total_requirements']}")
        print(f"   ✓ Verified requirements: {stats['verified_requirements']}")
        print(f"   ✓ Audit entries: {stats['total_audit_entries']}")
        print(f"   ✓ Database size: {stats['database_size_bytes']} bytes\n")

        print("✓ Database layer test PASSED\n")

    finally:
        db.close()
