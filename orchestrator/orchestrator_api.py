"""
Orchestrator REST API - Production Deployment Component

FastAPI-based REST endpoints for orchestrator management and execution.
"""

import logging
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
import uvicorn

# Add orchestrator to path
sys.path.insert(0, '/home/vali/projects/orchestrator')

from database_layer import Database, RequirementStatus
from orchestrator_workflow import Orchestrator, WorkflowResult
from tracker_integration import TrackerIntegration
from claude_api_integration import ClaudeIntegration
from designer_agent import Requirement, RequirementType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CreateRequirementRequest(BaseModel):
    """Request to create a requirement."""
    title: str
    description: str
    project: str
    acceptance_criteria: str = ""
    requirement_type: str = "feature"


class UpdateRequirementStatusRequest(BaseModel):
    """Request to update requirement status."""
    status: str


class RequirementResponse(BaseModel):
    """Requirement response."""
    id: str
    title: str
    description: str
    status: str
    project: str
    created_at: str


class WorkflowResponse(BaseModel):
    """Workflow execution response."""
    requirement_id: str
    status: str
    success: bool
    duration_seconds: float
    design_decisions: int
    tasks_completed: int
    tasks_failed: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    components: Dict[str, bool]


class StatsResponse(BaseModel):
    """Statistics response."""
    total_requirements: int
    verified_requirements: int
    total_audit_entries: int
    database_path: str
    database_size_bytes: int
    uptime_seconds: float


# ============================================================================
# ORCHESTRATOR API
# ============================================================================

class OrchestratorAPI:
    """REST API for orchestrator."""

    def __init__(self, db_path: str = "/tmp/orchestrator.db",
                 project_root: str = "/home/vali/projects/investing-platform",
                 tracker_url: str = "http://localhost:8000"):
        """Initialize orchestrator API.

        Args:
            db_path: Path to SQLite database
            project_root: Root path for project analysis
            tracker_url: Tracker API URL
        """
        self.db = Database(db_path)
        self.orchestrator = Orchestrator(project_root)
        self.tracker = TrackerIntegration(tracker_url)
        self.claude = ClaudeIntegration(use_real_api=True)
        self.start_time = datetime.now()
        self.active_workflows = {}

        logger.info("Initialized OrchestratorAPI")

    def health_check(self) -> HealthResponse:
        """Check API and component health.

        Returns:
            HealthResponse with component status
        """
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            components={
                'database': True,
                'tracker': self.tracker.is_available(),
                'claude': self.claude.is_available(),
                'orchestrator': True
            }
        )

    def create_requirement(self, req: CreateRequirementRequest) -> RequirementResponse:
        """Create a new requirement.

        Args:
            req: Create requirement request

        Returns:
            RequirementResponse with created requirement
        """
        req_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Store in database
        self.db.create_requirement(
            req_id, req.title, req.description, req.project
        )

        # Sync to tracker
        tracker_result = self.tracker.sync_requirement_to_tracker(
            req.project,
            "/home/vali/projects/" + req.project.lower().replace(" ", "-"),
            req_id,
            req.title,
            req.description,
            req.acceptance_criteria,
            req.requirement_type
        )

        logger.info(f"Created requirement: {req_id}")

        return RequirementResponse(
            id=req_id,
            title=req.title,
            description=req.description,
            status="proposed",
            project=req.project,
            created_at=datetime.now().isoformat()
        )

    def get_requirement(self, requirement_id: str) -> RequirementResponse:
        """Get requirement details.

        Args:
            requirement_id: Requirement ID

        Returns:
            RequirementResponse
        """
        req = self.db.get_requirement(requirement_id)

        if not req:
            raise HTTPException(status_code=404, detail="Requirement not found")

        return RequirementResponse(
            id=req['id'],
            title=req['title'],
            description=req['description'],
            status=req['status'],
            project=req['project'],
            created_at=req['created_at']
        )

    def update_requirement_status(self, requirement_id: str,
                                 status_update: UpdateRequirementStatusRequest) -> RequirementResponse:
        """Update requirement status.

        Args:
            requirement_id: Requirement ID
            status_update: New status

        Returns:
            Updated RequirementResponse
        """
        self.db.update_requirement_status(requirement_id, status_update.status)

        req = self.db.get_requirement(requirement_id)
        return RequirementResponse(
            id=req['id'],
            title=req['title'],
            description=req['description'],
            status=req['status'],
            project=req['project'],
            created_at=req['created_at']
        )

    def execute_workflow(self, requirement_id: str,
                        background_tasks: BackgroundTasks) -> Dict:
        """Execute complete orchestrator workflow for a requirement.

        Args:
            requirement_id: Requirement ID
            background_tasks: FastAPI background tasks

        Returns:
            Workflow execution response
        """
        req = self.db.get_requirement(requirement_id)

        if not req:
            raise HTTPException(status_code=404, detail="Requirement not found")

        # Create requirement object
        requirement = Requirement(
            id=requirement_id,
            title=req['title'],
            description=req['description'],
            type=RequirementType.FEATURE
        )

        # Execute in background
        background_tasks.add_task(
            self._run_workflow,
            requirement
        )

        logger.info(f"Started workflow execution for {requirement_id}")

        return {
            'status': 'started',
            'requirement_id': requirement_id,
            'message': 'Workflow execution started in background'
        }

    def _run_workflow(self, requirement: Requirement):
        """Run workflow in background.

        Args:
            requirement: Requirement to process
        """
        try:
            # Phase 1: Capture before state
            logger.info(f"Workflow: Capturing before state for {requirement.id}")
            self.db.update_requirement_status(requirement.id, "analyzed")

            # Phase 2: Design analysis with real Claude
            logger.info(f"Workflow: Analyzing with Claude for {requirement.id}")
            claude_result = self.claude.analyze_requirement(
                requirement.id,
                requirement.title,
                requirement.description,
                "",
                "feature"
            )

            if claude_result:
                self.db.store_design(requirement.id, claude_result)

            # Phase 3: Update status
            self.db.update_requirement_status(requirement.id, "implemented")

            logger.info(f"Workflow: Complete for {requirement.id}")

        except Exception as e:
            logger.error(f"Workflow failed for {requirement.id}: {e}")
            self.db.update_requirement_status(requirement.id, "failed")

    def get_audit_log(self, requirement_id: str) -> List[Dict]:
        """Get audit log for requirement.

        Args:
            requirement_id: Requirement ID

        Returns:
            List of audit entries
        """
        audit_log = self.db.get_audit_log(requirement_id)

        return [
            {
                'timestamp': entry['timestamp'],
                'action': entry['action'],
                'status': entry['status']
            }
            for entry in audit_log
        ]

    def get_requirements(self, status: Optional[str] = None,
                        project: Optional[str] = None) -> List[RequirementResponse]:
        """Get requirements with optional filtering.

        Args:
            status: Filter by status
            project: Filter by project

        Returns:
            List of requirements
        """
        if status:
            reqs = self.db.get_requirements_by_status(status, project)
        else:
            reqs = self.db.get_requirements_by_status("proposed", project) if project else []

        return [
            RequirementResponse(
                id=req['id'],
                title=req['title'],
                description=req['description'],
                status=req['status'],
                project=req['project'],
                created_at=req['created_at']
            )
            for req in reqs
        ]

    def get_stats(self) -> StatsResponse:
        """Get orchestrator statistics.

        Returns:
            Statistics
        """
        stats = self.db.get_stats()
        uptime = (datetime.now() - self.start_time).total_seconds()

        return StatsResponse(
            total_requirements=stats['total_requirements'],
            verified_requirements=stats['verified_requirements'],
            total_audit_entries=stats['total_audit_entries'],
            database_path=stats['database_path'],
            database_size_bytes=stats['database_size_bytes'],
            uptime_seconds=uptime
        )


# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

def create_app(api: OrchestratorAPI) -> FastAPI:
    """Create FastAPI application.

    Args:
        api: OrchestratorAPI instance

    Returns:
        FastAPI app
    """
    app = FastAPI(
        title="Orchestrator API",
        description="REST API for autonomous project orchestration",
        version="1.0.0"
    )

    # ============================================================================
    # ENDPOINTS
    # ============================================================================

    @app.get("/health", response_model=HealthResponse)
    async def health():
        """Health check endpoint."""
        return api.health_check()

    @app.post("/api/requirements", response_model=RequirementResponse)
    async def create_requirement(req: CreateRequirementRequest):
        """Create a new requirement."""
        return api.create_requirement(req)

    @app.get("/api/requirements/{requirement_id}", response_model=RequirementResponse)
    async def get_requirement(requirement_id: str):
        """Get requirement details."""
        return api.get_requirement(requirement_id)

    @app.get("/api/requirements", response_model=List[RequirementResponse])
    async def get_requirements(status: Optional[str] = None, project: Optional[str] = None):
        """Get all requirements with optional filtering."""
        return api.get_requirements(status, project)

    @app.put("/api/requirements/{requirement_id}/status")
    async def update_requirement_status(requirement_id: str,
                                       status_update: UpdateRequirementStatusRequest):
        """Update requirement status."""
        return api.update_requirement_status(requirement_id, status_update)

    @app.post("/api/workflows/{requirement_id}")
    async def execute_workflow(requirement_id: str, background_tasks: BackgroundTasks):
        """Execute workflow for requirement."""
        return api.execute_workflow(requirement_id, background_tasks)

    @app.get("/api/requirements/{requirement_id}/audit")
    async def get_audit_log(requirement_id: str):
        """Get audit log for requirement."""
        return api.get_audit_log(requirement_id)

    @app.get("/api/stats", response_model=StatsResponse)
    async def get_stats():
        """Get orchestrator statistics."""
        return api.get_stats()

    return app


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    api = OrchestratorAPI()
    app = create_app(api)

    print("\n" + "="*80)
    print("ORCHESTRATOR REST API")
    print("="*80 + "\n")

    print("Starting FastAPI server on http://localhost:8001")
    print("API documentation: http://localhost:8001/docs\n")

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
