"""Genomic Variant Pathogenicity & ACMG Classification Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base


class DBVariantClassificationReport(Base):
    """Variant classification report adhering to ACMG/AMP standards."""
    __tablename__ = "variant_classification_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gene_symbol = Column(String(64), nullable=False, index=True)
    hgvs_c = Column(String(128), nullable=False)
    hgvs_p = Column(String(128), nullable=False)
    chromosome = Column(String(16), nullable=False)
    genomic_position = Column(Integer, nullable=False)
    ref_allele = Column(String(64), nullable=False)
    alt_allele = Column(String(64), nullable=False)
    transcript_id = Column(String(64), nullable=False, default="NM_000000.1")
    acmg_class = Column(String(32), nullable=False)  # PATHOGENIC, LIKELY_PATHOGENIC, VUS, LIKELY_BENIGN, BENIGN
    pathogenicity_score = Column(Float, nullable=False, default=0.5)  # 0.0 - 1.0 posterior probability
    total_criteria_met = Column(Integer, nullable=False, default=0)
    clinvar_id = Column(String(64), nullable=True)
    variant_summary_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    criteria = relationship("DBACMGCriterionEvidence", back_populates="report", cascade="all, delete-orphan")
    predictor_scores = relationship("DBInSilicoPredictorScore", back_populates="report", cascade="all, delete-orphan")


class DBACMGCriterionEvidence(Base):
    """Individual ACMG/AMP criterion evaluated for a variant."""
    __tablename__ = "acmg_criterion_evidences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("variant_classification_reports.id", ondelete="CASCADE"), nullable=False)
    criterion_code = Column(String(16), nullable=False)  # e.g., PVS1, PS1, PM2, PP3, BA1, BS1, BP4
    criterion_type = Column(String(32), nullable=False)  # PATHOGENIC_VERY_STRONG, PATHOGENIC_STRONG, etc.
    status = Column(String(32), nullable=False, default="NOT_MET")  # MET, NOT_MET, INDETERMINATE
    weight = Column(Float, nullable=False, default=1.0)
    rationale = Column(Text, nullable=False)
    evidence_source = Column(String(128), nullable=False, default="Algorithmic ACMG Evaluator")

    report = relationship("DBVariantClassificationReport", back_populates="criteria")


class DBInSilicoPredictorScore(Base):
    """In-silico pathogenicity prediction tool scores (AlphaMissense, REVEL, CADD, SpliceAI)."""
    __tablename__ = "insilico_predictor_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("variant_classification_reports.id", ondelete="CASCADE"), nullable=False)
    tool_name = Column(String(64), nullable=False)  # AlphaMissense, REVEL, CADD, SpliceAI, PolyPhen2, SIFT
    score_value = Column(Float, nullable=False)
    score_percentile = Column(Float, nullable=False, default=50.0)
    prediction_label = Column(String(64), nullable=False)  # Pathogenic, Damaging, Tolerated, Benign

    report = relationship("DBVariantClassificationReport", back_populates="predictor_scores")
