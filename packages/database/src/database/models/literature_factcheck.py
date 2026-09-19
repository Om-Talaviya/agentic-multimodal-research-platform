"""Literature Discrepancy & Hallucination Fact-Checking Database Models (Phase 103)."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBLiteratureFactCheck(Base):
    __tablename__ = "literature_fact_checks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    paper_title = Column(String(255), nullable=False)
    doi_or_pmid = Column(String(100), nullable=False)
    factcheck_verdict = Column(String(50), default="VERIFIED_CONSISTENT", nullable=False)  # VERIFIED_CONSISTENT, MINOR_DISCREPANCY, CONFLICTING_CLAIMS, POTENTIAL_HALLUCINATION
    overall_truthfulness_score = Column(Float, default=94.5, nullable=False)  # 0 to 100
    total_claims_extracted = Column(Integer, default=18, nullable=False)
    corroborated_claims_count = Column(Integer, default=16, nullable=False)
    discrepant_claims_count = Column(Integer, default=2, nullable=False)
    analysis_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    claims = relationship("DBDiscrepancyClaim", back_populates="factcheck", cascade="all, delete-orphan")
    citations = relationship("DBCitationIntegrityMetric", back_populates="factcheck", cascade="all, delete-orphan")


class DBDiscrepancyClaim(Base):
    __tablename__ = "literature_discrepancy_claims"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    factcheck_id = Column(GUID(), ForeignKey("literature_fact_checks.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    claimed_finding = Column(String(255), nullable=False)
    literature_consensus_finding = Column(String(255), nullable=False)
    contradiction_severity = Column(String(50), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, RETRACTION_RISK
    supporting_evidence_count = Column(Integer, default=8, nullable=False)
    refuting_evidence_count = Column(Integer, default=12, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    factcheck = relationship("DBLiteratureFactCheck", back_populates="claims")


class DBCitationIntegrityMetric(Base):
    __tablename__ = "citation_integrity_metrics"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    factcheck_id = Column(GUID(), ForeignKey("literature_fact_checks.id", ondelete="CASCADE"), nullable=False, index=True)
    cited_doi = Column(String(100), nullable=False)
    cited_paper_title = Column(String(255), nullable=False)
    citation_context_match = Column(String(50), default="FAITHFUL_CITATION", nullable=False)  # FAITHFUL_CITATION, CITATION_EXAGGERATION, PHANTOM_CITATION
    integrity_confidence = Column(Float, default=0.96, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    factcheck = relationship("DBLiteratureFactCheck", back_populates="citations")
