"""SQLAlchemy models for Autonomous Patent Landscape Analysis & Prior Art Search Engine."""

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


class DBPatentCorpus(Base):
    """Represents a patent landscape corpus and prior-art search repository."""

    __tablename__ = "patent_corpora"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True, index=True)
    workspace_id = Column(GUID(), nullable=True, index=True)
    project_id = Column(GUID(), nullable=True, index=True)
    research_job_id = Column(GUID(), nullable=True, index=True)

    title = Column(String(512), nullable=False)
    technology_domain = Column(String(128), default="artificial_intelligence", nullable=False)
    cpc_classification = Column(String(128), default="G06N 10/00", nullable=False)
    jurisdiction = Column(String(64), default="GLOBAL", nullable=False)  # USPTO, EPO, WIPO, JPO, CNIPA, GLOBAL
    status = Column(String(64), default="active", nullable=False, index=True)  # active, analyzing, completed, archived

    total_patents_indexed = Column(Integer, default=0, nullable=False)
    freedom_to_operate_verdict = Column(String(64), default="clear", nullable=False)  # clear, caution, high_risk, blocked
    metadata_json = Column(JSONType, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    patents = relationship("DBPatentDocument", back_populates="corpus", cascade="all, delete-orphan", order_by="DBPatentDocument.publication_date")
    evaluations = relationship("DBPriorArtEvaluation", back_populates="corpus", cascade="all, delete-orphan", order_by="DBPriorArtEvaluation.created_at")
    fto_reports = relationship("DBFreedomToOperateReport", back_populates="corpus", cascade="all, delete-orphan", order_by="DBFreedomToOperateReport.created_at")


class DBPatentDocument(Base):
    """Represents an individual patent specification asset."""

    __tablename__ = "patent_documents"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    corpus_id = Column(GUID(), ForeignKey("patent_corpora.id", ondelete="CASCADE"), nullable=False, index=True)

    patent_number = Column(String(128), nullable=False, index=True)  # e.g., US-11823901-B2
    title = Column(String(512), nullable=False)
    abstract = Column(Text, nullable=True)
    assignee = Column(String(256), nullable=False)
    filing_date = Column(String(64), nullable=True)
    publication_date = Column(String(64), nullable=True)
    cpc_classes = Column(JSONType, default=list, nullable=False)
    status = Column(String(64), default="granted", nullable=False)  # granted, pending, expired
    claims_count = Column(Integer, default=0, nullable=False)
    citations_count = Column(Integer, default=0, nullable=False)
    full_text_url = Column(String(512), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    corpus = relationship("DBPatentCorpus", back_populates="patents")
    claims = relationship("DBPatentClaim", back_populates="patent", cascade="all, delete-orphan", order_by="DBPatentClaim.claim_number")


class DBPatentClaim(Base):
    """Represents a granular independent or dependent patent claim."""

    __tablename__ = "patent_claims"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    patent_id = Column(GUID(), ForeignKey("patent_documents.id", ondelete="CASCADE"), nullable=False, index=True)

    claim_number = Column(Integer, default=1, nullable=False)
    claim_type = Column(String(64), default="independent", nullable=False)  # independent, dependent
    parent_claim_number = Column(Integer, nullable=True)
    claim_text = Column(Text, nullable=False)
    parsed_elements_json = Column(JSONType, default=list, nullable=False)
    infringement_risk_score = Column(Float, default=0.0, nullable=False)

    patent = relationship("DBPatentDocument", back_populates="claims")


class DBPriorArtEvaluation(Base):
    """Represents a 35 U.S.C. 102/103 novelty and non-obviousness claim evaluation."""

    __tablename__ = "prior_art_evaluations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    corpus_id = Column(GUID(), ForeignKey("patent_corpora.id", ondelete="CASCADE"), nullable=False, index=True)
    prior_art_patent_id = Column(GUID(), ForeignKey("patent_documents.id", ondelete="SET NULL"), nullable=True, index=True)

    target_invention_claim = Column(Text, nullable=False)
    novelty_score = Column(Float, default=0.85, nullable=False)
    obviousness_score = Column(Float, default=0.20, nullable=False)
    overlap_ratio = Column(Float, default=0.15, nullable=False)
    verdict = Column(String(64), default="distinguishable", nullable=False)
    # anticipates_102, obvious_103, distinguishable, non_infringing

    detailed_rationale = Column(Text, nullable=False)
    mitigation_strategy = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    corpus = relationship("DBPatentCorpus", back_populates="evaluations")
    prior_art_patent = relationship("DBPatentDocument")


class DBFreedomToOperateReport(Base):
    """Represents a Freedom to Operate (FTO) clearance dossier and white-space opportunity map."""

    __tablename__ = "fto_reports"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    corpus_id = Column(GUID(), ForeignKey("patent_corpora.id", ondelete="CASCADE"), nullable=False, index=True)

    total_examined_patents = Column(Integer, default=0, nullable=False)
    high_risk_claims_count = Column(Integer, default=0, nullable=False)
    medium_risk_claims_count = Column(Integer, default=0, nullable=False)
    fto_clearance_percentage = Column(Float, default=100.0, nullable=False)

    summary_assessment = Column(Text, nullable=False)
    white_space_opportunities = Column(JSONType, default=list, nullable=False)
    claim_chart_matrices = Column(JSONType, default=list, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    corpus = relationship("DBPatentCorpus", back_populates="fto_reports")
