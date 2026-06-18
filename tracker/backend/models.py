from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    tech_stack = Column(String, nullable=True)
    path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scorecard_entries = relationship("ScorecardEntry", back_populates="project")
    gaps = relationship("Gap", back_populates="project")
    reviews = relationship("Review", back_populates="project")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    reviewed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    maturity_score = Column(Integer, nullable=True)

    project = relationship("Project", back_populates="reviews")

class ScorecardEntry(Base):
    __tablename__ = "scorecard_entries"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    pillar = Column(String)
    status = Column(String)
    evidence = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="scorecard_entries")

class Gap(Base):
    __tablename__ = "gaps"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    pillar = Column(String)
    rule_id = Column(String, nullable=True)
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="Discovered")
    severity = Column(String, nullable=True)
    effort = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="gaps")
