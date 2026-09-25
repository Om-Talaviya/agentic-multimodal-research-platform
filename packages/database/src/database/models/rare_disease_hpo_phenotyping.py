"""SQLAlchemy models for Phase 181: Rare Disease Deep Phenotyping & HPO-OMIM Semantic Matcher."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class RDDeepHPOStudy(Base):
    """Study record for rare disease patient clinical phenotyping and semantic ontology matching."""

    __tablename__ = "rd_deep_hpo_phenotyping_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    patient_cohort_id = Column(String(100), nullable=False)
    primary_clinical_presentation = Column(String(255), nullable=False)
    extracted_hpo_count = Column(Integer, nullable=False, default=6)
    top_omim_disease_candidate = Column(String(255), nullable=False)
    semantic_similarity_resnik_score = Column(Float, nullable=False, default=0.875)
    diagnostic_prioritization_rank = Column(Integer, nullable=False, default=1)
    causal_gene_symbol = Column(String(100), nullable=False, default="FBN1")
    inheritance_mode = Column(String(100), nullable=False, default="Autosomal dominant")
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    hpo_terms = relationship("RDDeepHPOTerm", back_populates="study", cascade="all, delete-orphan")
    omim_matches = relationship("RDDeepOMIMMatch", back_populates="study", cascade="all, delete-orphan")


class RDDeepHPOTerm(Base):
    """Extracted Human Phenotype Ontology terms."""

    __tablename__ = "rd_deep_hpo_terms"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("rd_deep_hpo_phenotyping_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    hpo_id = Column(String(50), nullable=False)
    hpo_label = Column(String(200), nullable=False)
    information_content_score = Column(Float, nullable=False, default=6.45)
    clinical_severity_weight = Column(Float, nullable=False, default=1.0)
    organ_system_category = Column(String(100), nullable=False, default="Skeletal system")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("RDDeepHPOStudy", back_populates="hpo_terms")


class RDDeepOMIMMatch(Base):
    """Ranked OMIM / Orphanet candidate diseases."""

    __tablename__ = "rd_deep_omim_matches"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("rd_deep_hpo_phenotyping_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    omim_id = Column(String(50), nullable=False)
    disease_name = Column(String(255), nullable=False)
    causal_genes = Column(String(200), nullable=False)
    phenomizer_p_value = Column(Float, nullable=False, default=0.00012)
    jaccard_similarity_score = Column(Float, nullable=False, default=0.78)
    matching_terms_count = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("RDDeepHPOStudy", back_populates="omim_matches")