from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import Base, Project, ScorecardEntry, Gap, Review, Requirement
from database import engine, get_db
from schemas import ProjectCreate, Project as ProjectSchema, ScorecardEntryCreate, GapCreate, Gap as GapSchema
from typing import List
import os
from dotenv import load_dotenv
from project_scanner import scan_for_projects

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Design & Bug Tracker")

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
        "gaps": [{"id": g.id, "pillar": g.pillar, "title": g.title, "status": g.status, "severity": g.severity, "effort": g.effort} for g in gaps],
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

@app.delete("/api/projects/{project_id}/gaps/{gap_id}", response_model=dict)
def delete_gap(project_id: int, gap_id: int, db: Session = Depends(get_db)):
    db_gap = db.query(Gap).filter(Gap.id == gap_id, Gap.project_id == project_id).first()
    if not db_gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    db.delete(db_gap)
    db.commit()
    return {"status": "deleted"}

@app.get("/api/rules", response_model=dict)
def get_rules():
    rules = load_framework_rules()
    return rules

@app.get("/api/playbooks", response_model=dict)
def get_playbooks():
    playbooks = load_framework_playbooks()
    return playbooks

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
        result.append({
            "id": r.id,
            "req_id": r.req_id,
            "title": r.title,
            "req_type": r.req_type,
            "category": r.category,
            "status": r.status,
            "acceptance_criteria": r.acceptance_criteria,
            "measurement_method": r.measurement_method,
            "target": r.target,
            "test_case": r.test_case,
            "gap_count": gap_count
        })
    return result

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

def calculate_maturity(scorecard):
    if not scorecard:
        return 0
    met = sum(1 for s in scorecard if s.status == "✅")
    return int((met / len(scorecard)) * 100) if scorecard else 0

def load_framework_rules():
    from framework_loader import load_rules
    return load_rules()

def load_framework_playbooks():
    from framework_loader import load_playbooks
    return load_playbooks()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
