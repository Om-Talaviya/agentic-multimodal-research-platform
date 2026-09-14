import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from database.connection import Base
from database.models.memory import GUID

JSONType = JSON().with_variant(JSONB, "postgresql")



class DBPeerReviewManuscript(Base):
    """Represents a scientific research manuscript submitted for peer review and publication."""

    __tablename__ = "peer_review_manuscripts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True, index=True)
    workspace_id = Column(GUID(), nullable=True, index=True)
    project_id = Column(GUID(), nullable=True, index=True)
    research_job_id = Column(GUID(), nullable=True, index=True)

    title = Column(String(512), nullable=False)
    abstract = Column(Text, nullable=False)
    field_of_study = Column(String(128), default="computer_science", nullable=False)
    venue_format = Column(String(64), default="nature", nullable=False)  # nature, ieee, acm, arxiv
    status = Column(String(64), default="submitted", nullable=False, index=True)
    # submitted, under_review, revisions_requested, accepted, rejected, published

    manuscript_content = Column(Text, nullable=True)
    claimed_contributions = Column(JSONType, default=list, nullable=False)
    keywords = Column(JSONType, default=list, nullable=False)


    overall_score = Column(Float, default=0.0, nullable=False)
    camera_ready_doi = Column(String(256), nullable=True)
    published_latex = Column(Text, nullable=True)
    bibtex_citation = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    reports = relationship("DBPeerReviewReport", back_populates="manuscript", cascade="all, delete-orphan", order_by="DBPeerReviewReport.created_at")
    revisions = relationship("DBManuscriptRevision", back_populates="manuscript", cascade="all, delete-orphan", order_by="DBManuscriptRevision.revision_round")


class DBPeerReviewReport(Base):
    """Represents an independent blinded referee evaluation from a specialized agent."""

    __tablename__ = "peer_review_reports"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    manuscript_id = Column(GUID(), ForeignKey("peer_review_manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)

    reviewer_persona = Column(String(64), nullable=False)  # methodology_critic, statistical_auditor, domain_specialist
    reviewer_title = Column(String(128), nullable=False)

    originality_score = Column(Float, default=0.0, nullable=False)  # 0.0 - 10.0
    methodology_score = Column(Float, default=0.0, nullable=False)  # 0.0 - 10.0
    empirical_soundness = Column(Float, default=0.0, nullable=False)  # 0.0 - 10.0
    clarity_score = Column(Float, default=0.0, nullable=False)  # 0.0 - 10.0
    composite_score = Column(Float, default=0.0, nullable=False)  # 0.0 - 10.0

    recommendation = Column(String(64), default="minor_revision", nullable=False)  # accept, minor_revision, major_revision, reject
    summary_verdict = Column(Text, nullable=False)
    strengths = Column(JSONType, default=list, nullable=False)
    weaknesses = Column(JSONType, default=list, nullable=False)
    detailed_critique = Column(Text, nullable=False)
    required_revisions = Column(JSONType, default=list, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    manuscript = relationship("DBPeerReviewManuscript", back_populates="reports")


class DBManuscriptRevision(Base):
    """Represents an author revision round and point-by-point response to reviewers."""

    __tablename__ = "manuscript_revisions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    manuscript_id = Column(GUID(), ForeignKey("peer_review_manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)

    revision_round = Column(Integer, default=1, nullable=False)
    rebuttal_letter = Column(Text, nullable=False)
    diff_summary = Column(Text, nullable=True)
    point_by_point_responses = Column(JSONType, default=list, nullable=False)
    status = Column(String(64), default="submitted", nullable=False)  # submitted, reviewed, approved


    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    manuscript = relationship("DBPeerReviewManuscript", back_populates="revisions")
