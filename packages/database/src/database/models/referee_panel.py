"""
SQLAlchemy models for Scientific Peer-Review Referee Panel & Rebuttal Loop (Phase 64).
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from database.connection import Base


class DBRefereePanelManuscript(Base):
    """Represents a submitted scientific manuscript evaluated by an autonomous referee panel."""
    __tablename__ = "referee_panel_manuscripts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    manuscript_title = Column(String(255), nullable=False)
    research_domain = Column(String(128), default="Computational Immuno-Oncology")
    abstract_text = Column(Text, nullable=False)
    overall_score_out_of_10 = Column(Float, default=8.2)
    editorial_recommendation = Column(String(64), default="Accept with Minor Revisions")
    total_reviews = Column(Integer, default=0)
    status = Column(String(32), default="COMPLETED")
    metadata_info = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("DBRefereePanelReport", back_populates="manuscript", cascade="all, delete-orphan")


class DBRefereePanelReport(Base):
    """Represents an adversarial peer review report from a specialized referee persona."""
    __tablename__ = "referee_panel_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    manuscript_id = Column(String(36), ForeignKey("referee_panel_manuscripts.id", ondelete="CASCADE"), nullable=False)
    referee_persona = Column(String(64), nullable=False)
    score_out_of_10 = Column(Float, nullable=False)
    statistical_rigor_score = Column(Float, default=8.5)
    novelty_score = Column(Float, default=9.0)
    reproducibility_score = Column(Float, default=8.0)
    critique_summary = Column(Text, nullable=False)
    recommendation = Column(String(64), default="Minor Revision")
    created_at = Column(DateTime, default=datetime.utcnow)

    manuscript = relationship("DBRefereePanelManuscript", back_populates="reviews")
    rebuttal_points = relationship("DBRefereeRebuttalPoint", back_populates="review", cascade="all, delete-orphan")


class DBRefereeRebuttalPoint(Base):
    """Represents a structured point-by-point author rebuttal and proposed supplementary verification."""
    __tablename__ = "referee_panel_rebuttals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String(36), ForeignKey("referee_panel_reports.id", ondelete="CASCADE"), nullable=False)
    referee_claim = Column(Text, nullable=False)
    author_rebuttal = Column(Text, nullable=False)
    proposed_supplementary_experiment = Column(Text, nullable=True)
    is_conceded_and_fixed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    review = relationship("DBRefereePanelReport", back_populates="rebuttal_points")
