from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .models import Base, Project, ScorecardEntry, Gap, Review, Requirement
from .database import engine, get_db
from .schemas import ProjectCreate, Project as ProjectSchema, ScorecardEntryCreate, GapCreate, Gap as GapSchema
from typing import List
import os
from dotenv import load_dotenv
from .project_scanner import scan_for_projects
from .requirement_parser import load_and_parse_project_requirements
from .requirement_sync import sync_requirements_to_files, RequirementSyncManager
from .requirement_linking import RequirementLinker
from .portfolio_analytics import PortfolioAnalytics
from .background_sync import importer
from .project_board_sync import ProjectBoardSyncer
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Design & Bug Tracker")

# Background sync events
@app.on_event("startup")
async def startup_event():
    """Start background requirement sync on app startup."""
    importer.start()
    logger.info("🚀 Application started with auto-import enabled")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background requirement sync on app shutdown."""
    importer.stop()
    logger.info("🛑 Application shutting down, auto-import stopped")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/projects", response_model=List[dict])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    result = []
    for p in projects:
        scorecard = db.query(ScorecardEntry).filter(ScorecardEntry.project_id == p.id).all()
        pillar_status = {}
        for s in scorecard:
            pillar_status[s.pillar] = s.status

        gap_count = db.query(Gap).filter(Gap.project_id == p.id).count()

        maturity = calculate_maturity(scorecard)

        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "tech_stack": p.tech_stack,
            "path": p.path,
            "maturity_score": maturity,
            "pillar_status": pillar_status,
            "gap_count": gap_count,
            "created_at": p.created_at.isoformat(),
        })
    return result

@app.post("/api/projects", response_model=dict)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    existing = db.query(Project).filter(Project.name == project.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project already exists")

    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return {"id": db_project.id, "name": db_project.name}

@app.get("/api/projects/{project_id}", response_model=dict)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    scorecard = db.query(ScorecardEntry).filter(ScorecardEntry.project_id == project_id).all()
    gaps = db.query(Gap).filter(Gap.project_id == project_id).all()
    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
    reviews = db.query(Review).filter(Review.project_id == project_id).all()

    pillar_status = {}
    for s in scorecard:
        pillar_status[s.pillar] = {"status": s.status, "evidence": s.evidence}

    maturity = calculate_maturity(scorecard)

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "tech_stack": project.tech_stack,
        "path": project.path,
        "maturity_score": maturity,
        "scorecard": pillar_status,
        "requirements": [{"id": r.id, "req_id": r.req_id, "description": r.description, "status": r.status, "req_type": r.req_type, "category": r.category, "gap_count": len([g for g in gaps if g.requirement_id == r.id])} for r in requirements],
        "gaps": [{"id": g.id, "pillar": g.pillar, "title": g.title, "status": g.status, "severity": g.severity, "effort": g.effort, "requirement_id": g.requirement_id, "description": g.description} for g in gaps],
        "review_count": len(reviews),
    }

@app.put("/api/projects/{project_id}/scorecard", response_model=dict)
def update_scorecard(project_id: int, entries: List[ScorecardEntryCreate], db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.query(ScorecardEntry).filter(ScorecardEntry.project_id == project_id).delete()

    for entry in entries:
        db_entry = ScorecardEntry(project_id=project_id, **entry.dict())
        db.add(db_entry)

    db.commit()
    return {"status": "updated"}

@app.post("/api/projects/{project_id}/gaps", response_model=dict)
def create_gap(project_id: int, gap: GapCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_gap = Gap(project_id=project_id, **gap.dict())
    db.add(db_gap)
    db.commit()
    db.refresh(db_gap)
    return {"id": db_gap.id, "status": "created"}

@app.put("/api/projects/{project_id}/gaps/{gap_id}", response_model=dict)
def update_gap(project_id: int, gap_id: int, gap: GapCreate, db: Session = Depends(get_db)):
    db_gap = db.query(Gap).filter(Gap.id == gap_id, Gap.project_id == project_id).first()
    if not db_gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    for key, value in gap.dict().items():
        setattr(db_gap, key, value)

    db.commit()
    return {"status": "updated"}

@app.patch("/api/projects/{project_id}/gaps/{gap_id}", response_model=dict)
def patch_gap(project_id: int, gap_id: int, gap_update: dict, db: Session = Depends(get_db)):
    """Partially update a gap (used by tracker_client for status/solution updates)."""
    db_gap = db.query(Gap).filter(Gap.id == gap_id, Gap.project_id == project_id).first()
    if not db_gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    for key, value in gap_update.items():
        if hasattr(db_gap, key) and value is not None:
            setattr(db_gap, key, value)

    db.commit()
    db.refresh(db_gap)
    return {"status": "updated", "gap_id": gap_id}

@app.delete("/api/projects/{project_id}/gaps/{gap_id}", response_model=dict)
def delete_gap(project_id: int, gap_id: int, db: Session = Depends(get_db)):
    db_gap = db.query(Gap).filter(Gap.id == gap_id, Gap.project_id == project_id).first()
    if not db_gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    db.delete(db_gap)
    db.commit()
    return {"status": "deleted"}

@app.get("/api/projects/{project_id}/gaps/{gap_id}/suggest-requirements", response_model=list)
def suggest_requirements_for_gap(project_id: int, gap_id: int, db: Session = Depends(get_db)):
    """Suggest requirements that might be violated by this gap."""
    gap = db.query(Gap).filter(Gap.id == gap_id, Gap.project_id == project_id).first()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

    req_list = []
    for r in requirements:
        req_list.append({
            "id": r.id,
            "req_id": r.req_id,
            "title": r.title,
            "req_type": r.req_type,
            "category": r.category,
            "description": r.description,
            "acceptance_criteria": r.acceptance_criteria,
            "test_case": r.test_case
        })

    suggestions = RequirementLinker.suggest_requirements(gap.title, gap.description, req_list)
    return suggestions

@app.put("/api/projects/{project_id}/gaps/{gap_id}/link-requirement", response_model=dict)
def link_requirement_to_gap(project_id: int, gap_id: int, link_data: dict, db: Session = Depends(get_db)):
    """Link a gap to a requirement it violates."""
    gap = db.query(Gap).filter(Gap.id == gap_id, Gap.project_id == project_id).first()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    requirement_id = link_data.get('requirement_id')
    acceptance_criterion_id = link_data.get('acceptance_criterion_id')  # Optional: specific CR-XXX

    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    # Link the gap to the requirement
    gap.requirement_id = requirement_id
    gap.violation_type = requirement.req_type
    gap.acceptance_criterion_id = acceptance_criterion_id

    db.commit()

    return {
        "status": "linked",
        "gap_id": gap_id,
        "requirement_id": requirement_id,
        "requirement_req_id": requirement.req_id
    }

@app.get("/api/projects/{project_id}/gaps/{gap_id}/traceability", response_model=dict)
def get_gap_traceability(project_id: int, gap_id: int, db: Session = Depends(get_db)):
    """Get complete traceability chain: Gap → Requirement → Solution."""
    gap = db.query(Gap).filter(Gap.id == gap_id, Gap.project_id == project_id).first()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    # Build traceability object
    traceability = {
        "gap": {
            "id": gap.id,
            "title": gap.title,
            "description": gap.description,
            "status": gap.status,
            "severity": gap.severity,
            "effort": gap.effort,
            "pillar": gap.pillar,
            "created_at": gap.created_at.isoformat() if gap.created_at else None,
        },
        "requirement": None,
        "solution": None
    }

    # Get linked requirement if exists
    if gap.requirement_id:
        req = db.query(Requirement).filter(Requirement.id == gap.requirement_id).first()
        if req:
            traceability["requirement"] = {
                "id": req.id,
                "req_id": req.req_id,
                "title": req.title,
                "req_type": req.req_type,
                "status": req.status,
                "category": req.category,
                "description": req.description[:100] if req.description else None,
            }

    # Get solution if gap is fixed
    if gap.solution_summary or gap.fixed_commit_hash:
        traceability["solution"] = {
            "summary": gap.solution_summary,
            "code_file": gap.fixed_code_file,
            "commit_hash": gap.fixed_commit_hash,
            "fixed_at": gap.fixed_at.isoformat() if gap.fixed_at else None,
            "fixed_by": gap.fixed_by,
        }

    return traceability

@app.get("/api/projects/{project_id}/requirements/{requirement_id}/linked-gaps", response_model=list)
def get_gaps_for_requirement(project_id: int, requirement_id: int, db: Session = Depends(get_db)):
    """Get all gaps that violate a specific requirement."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    gaps = db.query(Gap).filter(
        Gap.requirement_id == requirement_id,
        Gap.project_id == project_id
    ).all()

    result = []
    for gap in gaps:
        result.append({
            "id": gap.id,
            "title": gap.title,
            "description": gap.description,
            "status": gap.status,
            "severity": gap.severity,
            "effort": gap.effort,
            "acceptance_criterion_id": gap.acceptance_criterion_id,
            "pillar": gap.pillar
        })

    return result

@app.get("/api/projects/{project_id}/requirement-health", response_model=list)
def get_requirement_health(project_id: int, db: Session = Depends(get_db)):
    """Get health status of all requirements (how many gaps violate each)."""
    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

    result = []
    for req in requirements:
        related_gaps = db.query(Gap).filter(
            Gap.requirement_id == req.id,
            Gap.project_id == project_id
        ).all()

        req_dict = {
            "id": req.id,
            "req_id": req.req_id,
            "title": req.title,
            "req_type": req.req_type,
            "category": req.category,
            "status": req.status,
            "description": req.description,
            "acceptance_criteria": req.acceptance_criteria,
            "test_case": req.test_case
        }

        health = RequirementLinker.analyze_requirement_health(req_dict, [g.__dict__ for g in related_gaps])
        result.append(health)

    return result

@app.get("/api/rules", response_model=dict)
def get_rules():
    rules = load_framework_rules()
    return rules

@app.get("/api/playbooks", response_model=dict)
def get_playbooks():
    playbooks = load_framework_playbooks()
    return playbooks

@app.get("/api/auto-import-status", response_model=dict)
def get_auto_import_status():
    """Get status of background requirement auto-import."""
    return importer.get_status()

@app.get("/api/projects/{project_id}/board", response_model=dict)
def get_project_board(project_id: int, db: Session = Depends(get_db)):
    """Get the V-Model board for a project (markdown content)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    board_content = ProjectBoardSyncer.generate_project_board(db, project)
    return {
        "project_id": project_id,
        "project_name": project.name,
        "board": board_content
    }

@app.post("/api/projects/{project_id}/sync-board", response_model=dict)
def sync_project_board(project_id: int, db: Session = Depends(get_db)):
    """Manually sync V-Model board for a project to its local file."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    board_content = ProjectBoardSyncer.generate_project_board(db, project)
    success = ProjectBoardSyncer.write_project_board(project, board_content)

    if success:
        return {
            "status": "synced",
            "project": project.name,
            "file_path": str(project.path) + "/V_MODEL_BOARD.md"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to write board file")

@app.post("/api/import-projects", response_model=dict)
def import_projects(db: Session = Depends(get_db)):
    """Scan /home/vali/projects/ for tracker.json and import projects"""
    scanned = scan_for_projects()
    imported = 0
    skipped = 0

    for project_data in scanned:
        existing = db.query(Project).filter(Project.name == project_data['name']).first()
        if existing:
            skipped += 1
            continue

        db_project = Project(
            name=project_data['name'],
            description=project_data.get('description'),
            tech_stack=project_data.get('tech_stack'),
            path=project_data.get('path')
        )
        db.add(db_project)
        imported += 1

    db.commit()
    return {"imported": imported, "skipped": skipped, "projects": [p['name'] for p in scanned]}

@app.post("/api/projects/{project_id}/requirements", response_model=dict)
def create_requirement(project_id: int, req_data: dict, db: Session = Depends(get_db)):
    """Create a new requirement (functional or non-functional)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_req = Requirement(
        project_id=project_id,
        req_id=req_data.get('req_id'),
        req_type=req_data.get('req_type'),
        category=req_data.get('category'),
        title=req_data.get('title'),
        description=req_data.get('description'),
        acceptance_criteria=req_data.get('acceptance_criteria'),
        measurement_method=req_data.get('measurement_method'),
        target=req_data.get('target'),
        test_case=req_data.get('test_case')
    )
    db.add(db_req)
    db.commit()
    db.refresh(db_req)
    return {"id": db_req.id, "req_id": db_req.req_id, "status": "created"}

@app.get("/api/projects/{project_id}/requirements", response_model=list)
def get_requirements(project_id: int, db: Session = Depends(get_db)):
    """Get all requirements for a project"""
    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()
    result = []
    for r in requirements:
        gap_count = db.query(Gap).filter(Gap.requirement_id == r.id).count()

        # Parse JSON fields if they are strings
        acceptance_criteria = r.acceptance_criteria
        if acceptance_criteria and isinstance(acceptance_criteria, str):
            try:
                acceptance_criteria = json.loads(acceptance_criteria)
            except:
                acceptance_criteria = [{"description": acceptance_criteria}]

        test_case = r.test_case
        if test_case and isinstance(test_case, str):
            try:
                test_case = json.loads(test_case)
            except:
                test_case = [test_case]

        result.append({
            "id": r.id,
            "req_id": r.req_id,
            "title": r.title,
            "description": r.description,
            "req_type": r.req_type,
            "category": r.category,
            "status": r.status,
            "acceptance_criteria": acceptance_criteria,
            "measurement_method": r.measurement_method,
            "target": r.target,
            "test_case": test_case,
            "gap_count": gap_count
        })
    return result

@app.get("/api/projects/{project_id}/requirements/{requirement_id}", response_model=dict)
def get_requirement(project_id: int, requirement_id: int, db: Session = Depends(get_db)):
    """Get a single requirement by ID"""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    gap_count = db.query(Gap).filter(Gap.requirement_id == requirement.id).count()

    acceptance_criteria = requirement.acceptance_criteria
    if acceptance_criteria and isinstance(acceptance_criteria, str):
        try:
            acceptance_criteria = json.loads(acceptance_criteria)
        except:
            acceptance_criteria = [{"description": acceptance_criteria}]

    test_case = requirement.test_case
    if test_case and isinstance(test_case, str):
        try:
            test_case = json.loads(test_case)
        except:
            test_case = [test_case]

    return {
        "id": requirement.id,
        "req_id": requirement.req_id,
        "title": requirement.title,
        "description": requirement.description,
        "req_type": requirement.req_type,
        "category": requirement.category,
        "status": requirement.status,
        "acceptance_criteria": acceptance_criteria,
        "measurement_method": requirement.measurement_method,
        "target": requirement.target,
        "test_case": test_case,
        "gap_count": gap_count
    }

@app.get("/api/projects/{project_id}/gaps/{gap_id}", response_model=dict)
def get_gap(project_id: int, gap_id: int, db: Session = Depends(get_db)):
    """Get a single gap by ID"""
    gap = db.query(Gap).filter(
        Gap.id == gap_id,
        Gap.project_id == project_id
    ).first()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    return {
        "id": gap.id,
        "project_id": gap.project_id,
        "pillar": gap.pillar,
        "title": gap.title,
        "description": gap.description,
        "severity": gap.severity,
        "status": gap.status,
        "effort": gap.effort,
        "requirement_id": gap.requirement_id,
    }

@app.post("/api/projects/{project_id}/import-requirements", response_model=dict)
def import_requirements_from_project(project_id: int, project_path: str = None, db: Session = Depends(get_db)):
    """Import requirements from project files into tracker database"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Use provided path or the project's path from database
    path_to_scan = project_path or project.path
    if not path_to_scan:
        raise HTTPException(status_code=400, detail="No project path available")

    # Parse requirements from project files
    parsed = load_and_parse_project_requirements(path_to_scan)

    # Clear existing requirements for this project
    db.query(Requirement).filter(Requirement.project_id == project_id).delete()

    imported_count = 0

    # Import functional requirements
    for fr in parsed.get("functional", []):
        acceptance_criteria = json.dumps([
            {"id": c["id"], "description": c["description"]}
            for c in fr.acceptance_criteria
        ])
        test_cases = json.dumps(fr.test_cases)
        components = json.dumps(fr.components)

        db_req = Requirement(
            project_id=project_id,
            req_id=fr.req_id,
            req_type="Functional",
            category=fr.category,
            title=fr.title,
            description=f"Actor: {fr.actor}\n\nUse Case:\n{fr.use_case}",
            acceptance_criteria=acceptance_criteria,
            test_case=test_cases,
            measurement_method=None,
            target=None,
            status="Proposed"
        )
        db.add(db_req)
        imported_count += 1

    # Import non-functional requirements
    for nfr in parsed.get("nonfunctional", []):
        db_req = Requirement(
            project_id=project_id,
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
        imported_count += 1

    db.commit()

    return {
        "status": "imported",
        "imported_count": imported_count,
        "functional_count": len(parsed.get("functional", [])),
        "nonfunctional_count": len(parsed.get("nonfunctional", [])),
        "errors": parsed.get("errors", [])
    }

@app.patch("/api/projects/{project_id}/requirements/{requirement_id}", response_model=dict)
def patch_requirement(project_id: int, requirement_id: int, req_data: dict, db: Session = Depends(get_db)):
    """Partially update a requirement (used by tracker_client for status updates)."""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    if 'status' in req_data:
        requirement.status = req_data['status']
    if 'description' in req_data:
        requirement.description = req_data['description']

    db.commit()
    db.refresh(requirement)
    return {"status": "updated", "requirement_id": requirement_id}

@app.put("/api/projects/{project_id}/requirements/{requirement_id}", response_model=dict)
def update_requirement(project_id: int, requirement_id: int, req_data: dict, db: Session = Depends(get_db)):
    """Update a requirement in the tracker"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    # Update fields
    if 'title' in req_data:
        requirement.title = req_data['title']
    if 'description' in req_data:
        requirement.description = req_data['description']
    if 'req_type' in req_data:
        requirement.req_type = req_data['req_type']
    if 'category' in req_data:
        requirement.category = req_data['category']
    if 'status' in req_data:
        requirement.status = req_data['status']
    if 'acceptance_criteria' in req_data:
        criteria = req_data['acceptance_criteria']
        requirement.acceptance_criteria = json.dumps(criteria) if not isinstance(criteria, str) else criteria
    if 'test_case' in req_data:
        test = req_data['test_case']
        requirement.test_case = json.dumps(test) if isinstance(test, list) else test
    if 'measurement_method' in req_data:
        requirement.measurement_method = req_data['measurement_method']
    if 'target' in req_data:
        requirement.target = req_data['target']

    db.commit()
    db.refresh(requirement)

    return {
        "id": requirement.id,
        "req_id": requirement.req_id,
        "status": "updated"
    }

@app.delete("/api/projects/{project_id}/requirements/{requirement_id}", response_model=dict)
def delete_requirement(project_id: int, requirement_id: int, db: Session = Depends(get_db)):
    """Delete a requirement"""
    requirement = db.query(Requirement).filter(
        Requirement.id == requirement_id,
        Requirement.project_id == project_id
    ).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    # Also delete any gaps linked to this requirement
    db.query(Gap).filter(Gap.requirement_id == requirement_id).delete()

    db.delete(requirement)
    db.commit()

    return {"status": "deleted", "requirement_id": requirement_id}

@app.post("/api/projects/{project_id}/sync-requirements", response_model=dict)
def sync_requirements_to_project_files(project_id: int, db: Session = Depends(get_db)):
    """Sync requirements from tracker back to project files"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.path:
        raise HTTPException(status_code=400, detail="No project path available")

    # Get all requirements from tracker
    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

    req_list = []
    for r in requirements:
        # Parse JSON fields
        acceptance_criteria = r.acceptance_criteria
        if acceptance_criteria and isinstance(acceptance_criteria, str):
            try:
                acceptance_criteria = json.loads(acceptance_criteria)
            except:
                acceptance_criteria = []

        test_case = r.test_case
        if test_case and isinstance(test_case, str):
            try:
                test_case = json.loads(test_case)
            except:
                test_case = [test_case]

        req_list.append({
            "req_id": r.req_id,
            "req_type": r.req_type,
            "title": r.title,
            "category": r.category,
            "description": r.description,
            "acceptance_criteria": acceptance_criteria,
            "test_case": test_case,
            "measurement_method": r.measurement_method,
            "target": r.target,
            "status": r.status
        })

    # Write to files
    result = sync_requirements_to_files(project.path, req_list)

    return {
        "status": result["status"],
        "message": "Requirements synced to project files",
        "functional": result.get("functional"),
        "nonfunctional": result.get("nonfunctional"),
        "errors": result.get("errors", [])
    }

@app.get("/api/projects/{project_id}/sync-status", response_model=dict)
def get_sync_status(project_id: int, db: Session = Depends(get_db)):
    """Get sync status between tracker and project files"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.path:
        raise HTTPException(status_code=400, detail="No project path available")

    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

    req_list = [
        {
            "req_id": r.req_id,
            "req_type": r.req_type,
            "title": r.title
        }
        for r in requirements
    ]

    manager = RequirementSyncManager(project.path)
    status = manager.get_sync_status(req_list)

    return status

@app.get("/api/projects/{project_id}/requirements-coverage", response_model=dict)
def get_requirements_coverage(project_id: int, db: Session = Depends(get_db)):
    """Get requirement coverage report (which requirements are met vs. gaps)"""
    requirements = db.query(Requirement).filter(Requirement.project_id == project_id).all()

    functional = [r for r in requirements if r.req_type == "Functional"]
    nonfunctional = [r for r in requirements if r.req_type == "Non-Functional"]

    functional_met = sum(1 for r in functional if r.status == "Validated")
    nonfunctional_met = sum(1 for r in nonfunctional if r.status == "Validated")

    return {
        "functional_total": len(functional),
        "functional_met": functional_met,
        "functional_coverage": f"{int((functional_met / len(functional) * 100)) if functional else 0}%" if functional else "N/A",
        "nonfunctional_total": len(nonfunctional),
        "nonfunctional_met": nonfunctional_met,
        "nonfunctional_coverage": f"{int((nonfunctional_met / len(nonfunctional) * 100)) if nonfunctional else 0}%" if nonfunctional else "N/A",
        "total_requirements": len(requirements),
        "total_met": functional_met + nonfunctional_met,
        "overall_coverage": f"{int(((functional_met + nonfunctional_met) / len(requirements) * 100)) if requirements else 0}%" if requirements else "N/A"
    }

@app.get("/api/portfolio/health", response_model=dict)
def get_portfolio_health(db: Session = Depends(get_db)):
    """Get aggregate requirement health across all projects."""
    projects = db.query(Project).all()

    projects_health = {}

    for project in projects:
        requirements = db.query(Requirement).filter(Requirement.project_id == project.id).all()
        health_data = []

        for req in requirements:
            related_gaps = db.query(Gap).filter(
                Gap.requirement_id == req.id,
                Gap.project_id == project.id
            ).all()

            req_dict = {
                "id": req.id,
                "req_id": req.req_id,
                "title": req.title,
                "req_type": req.req_type,
                "category": req.category,
                "status": req.status,
                "description": req.description
            }

            health = RequirementLinker.analyze_requirement_health(req_dict, [g.__dict__ for g in related_gaps])
            health_data.append(health)

        if health_data:
            projects_health[str(project.id)] = health_data

    # Aggregate metrics
    metrics = PortfolioAnalytics.aggregate_requirement_health(projects_health)
    score = PortfolioAnalytics.calculate_portfolio_health_score(metrics)

    return {
        "portfolio_score": score,
        "total_requirements": metrics["total_requirements"],
        "healthy": metrics["healthy"],
        "at_risk": metrics["at_risk"],
        "unvalidated": metrics["unvalidated"],
        "coverage_percent": metrics["coverage_percent"],
        "at_risk_percent": metrics["at_risk_percent"],
        "total_gaps": metrics["total_gaps"],
        "critical_risk_count": metrics["critical_risk_count"]
    }

@app.get("/api/portfolio/by-project", response_model=list)
def get_portfolio_by_project(db: Session = Depends(get_db)):
    """Get requirement health summary per project."""
    projects = db.query(Project).all()

    projects_health = {}

    for project in projects:
        requirements = db.query(Requirement).filter(Requirement.project_id == project.id).all()
        health_data = []

        for req in requirements:
            related_gaps = db.query(Gap).filter(
                Gap.requirement_id == req.id,
                Gap.project_id == project.id
            ).all()

            req_dict = {
                "id": req.id,
                "req_id": req.req_id,
                "title": req.title,
                "req_type": req.req_type,
                "category": req.category,
                "status": req.status
            }

            health = RequirementLinker.analyze_requirement_health(req_dict, [g.__dict__ for g in related_gaps])
            health_data.append(health)

        if health_data:
            projects_health[str(project.id)] = health_data

    summary = PortfolioAnalytics.get_by_project_summary(projects_health)

    # Add project names
    project_map = {str(p.id): p.name for p in projects}
    for item in summary:
        item["project_name"] = project_map.get(item["project_id"], "Unknown")

    return summary

@app.get("/api/portfolio/at-risk", response_model=list)
def get_portfolio_at_risk(db: Session = Depends(get_db), limit: int = 20):
    """Get most at-risk requirements across portfolio."""
    projects = db.query(Project).all()

    projects_health = {}

    for project in projects:
        requirements = db.query(Requirement).filter(Requirement.project_id == project.id).all()
        health_data = []

        for req in requirements:
            related_gaps = db.query(Gap).filter(
                Gap.requirement_id == req.id,
                Gap.project_id == project.id
            ).all()

            req_dict = {
                "id": req.id,
                "req_id": req.req_id,
                "title": req.title,
                "req_type": req.req_type,
                "category": req.category,
                "status": req.status
            }

            health = RequirementLinker.analyze_requirement_health(req_dict, [g.__dict__ for g in related_gaps])
            health_data.append(health)

        if health_data:
            projects_health[str(project.id)] = health_data

    metrics = PortfolioAnalytics.aggregate_requirement_health(projects_health)
    at_risk = PortfolioAnalytics.get_top_at_risk_requirements(metrics, limit)

    # Add project names
    project_map = {str(p.id): p.name for p in projects}
    for item in at_risk:
        item["project_name"] = project_map.get(item["project_id"], "Unknown")

    return at_risk

@app.get("/api/portfolio/category-breakdown", response_model=dict)
def get_portfolio_category_breakdown(db: Session = Depends(get_db)):
    """Get requirement breakdown by category across portfolio."""
    projects = db.query(Project).all()

    projects_health = {}

    for project in projects:
        requirements = db.query(Requirement).filter(Requirement.project_id == project.id).all()
        health_data = []

        for req in requirements:
            related_gaps = db.query(Gap).filter(
                Gap.requirement_id == req.id,
                Gap.project_id == project.id
            ).all()

            req_dict = {
                "id": req.id,
                "req_id": req.req_id,
                "title": req.title,
                "req_type": req.req_type,
                "category": req.category,
                "status": req.status
            }

            health = RequirementLinker.analyze_requirement_health(req_dict, [g.__dict__ for g in related_gaps])
            health_data.append(health)

        if health_data:
            projects_health[str(project.id)] = health_data

    metrics = PortfolioAnalytics.aggregate_requirement_health(projects_health)
    return PortfolioAnalytics.get_requirement_category_breakdown(metrics["all_requirements"])

@app.get("/api/portfolio/type-breakdown", response_model=dict)
def get_portfolio_type_breakdown(db: Session = Depends(get_db)):
    """Get requirement breakdown by type (Functional vs Non-Functional)."""
    projects = db.query(Project).all()

    projects_health = {}

    for project in projects:
        requirements = db.query(Requirement).filter(Requirement.project_id == project.id).all()
        health_data = []

        for req in requirements:
            related_gaps = db.query(Gap).filter(
                Gap.requirement_id == req.id,
                Gap.project_id == project.id
            ).all()

            req_dict = {
                "id": req.id,
                "req_id": req.req_id,
                "title": req.title,
                "req_type": req.req_type,
                "category": req.category,
                "status": req.status
            }

            health = RequirementLinker.analyze_requirement_health(req_dict, [g.__dict__ for g in related_gaps])
            health_data.append(health)

        if health_data:
            projects_health[str(project.id)] = health_data

    metrics = PortfolioAnalytics.aggregate_requirement_health(projects_health)
    return PortfolioAnalytics.get_requirement_type_breakdown(metrics["all_requirements"])

def calculate_maturity(scorecard):
    if not scorecard:
        return 0
    met = sum(1 for s in scorecard if s.status == "✅")
    return int((met / len(scorecard)) * 100) if scorecard else 0

def load_framework_rules():
    from .framework_loader import load_rules
    return load_rules()

def load_framework_playbooks():
    from .framework_loader import load_playbooks
    return load_playbooks()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
