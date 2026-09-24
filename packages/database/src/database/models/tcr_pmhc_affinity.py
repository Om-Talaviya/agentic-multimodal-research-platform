"""TCR-pMHC Structural Binding Affinity & Cross-Reactivity Models (Phase 145)."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import JSON, GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBTCRpMHCStudy(Base):
    """TCR-pMHC interaction profiling study."""

    __tablename__ = "tcr_pmhc_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tcr_name = Column(String(255), nullable=False)
    cdr3_alpha_seq = Column(String(100), nullable=False)
    cdr3_beta_seq = Column(String(100), nullable=False)
    target_peptide = Column(String(50), nullable=False)
    hla_allele = Column(String(50), nullable=False)
    binding_affinity_kd_um = Column(Float, default=0.0)
    immunogenicity_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    cross_reactivity_records = relationship("DBTCRCrossReactivityRecord", back_populates="study", cascade="all, delete-orphan")


class DBTCRCrossReactivityRecord(Base):
    """Off-target self-peptide cross-reactivity scan."""

    __tablename__ = "tcr_cross_reactivity_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("tcr_pmhc_studies.id", ondelete="CASCADE"), nullable=False)
    self_peptide_seq = Column(String(50), nullable=False)
    tissue_expression = Column(String(100), nullable=False)
    predicted_cross_kd_um = Column(Float, nullable=False)
    off_target_risk_level = Column(String(50), default="Low")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBTCRpMHCStudy", back_populates="cross_reactivity_records")
