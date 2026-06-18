from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import Base, Project, ScorecardEntry, Gap, Review
from database import engine, get_db
from schemas import ProjectCreate, Project as ProjectSchema, ScorecardEntryCreate, GapCreate, Gap as GapSchema
from typing import List
import os
from dotenv import load_dotenv

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
