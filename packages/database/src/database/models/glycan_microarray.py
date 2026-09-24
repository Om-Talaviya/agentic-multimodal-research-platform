"""Phase 148: Glycomics Microarray & Lectin Specificity Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBGlycanMicroarrayScreen(Base):
    """Glycan microarray screen campaign."""

    __tablename__ = "glycan_microarray_screens"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    target_lectin_name = Column(String(255), nullable=False)
    organism_source = Column(String(120), default="Homo sapiens")
    array_spots_count = Column(Integer, default=0, nullable=False)
    mean_signal_to_noise = Column(Float, default=0.0)
    primary_epitope_motif = Column(String(255), nullable=False)
    kd_apparent_nM = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    spot_records = relationship("DBGlycanSpotBindingRecord", back_populates="screen", cascade="all, delete-orphan")
    specificity_profiles = relationship("DBLectinSpecificityProfile", back_populates="screen", cascade="all, delete-orphan")


class DBGlycanSpotBindingRecord(Base):
    """Individual glycan spot binding intensity record."""

    __tablename__ = "glycan_spot_binding_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    screen_id = Column(GUID(), ForeignKey("glycan_microarray_screens.id", ondelete="CASCADE"), nullable=False)
    glycan_iupac = Column(String(255), nullable=False)
    spot_index = Column(Integer, nullable=False)
    fluorescence_rfu = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False)
    relative_affinity = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    screen = relationship("DBGlycanMicroarrayScreen", back_populates="spot_records")


class DBLectinSpecificityProfile(Base):
    """Epitope motif enrichment and Kd profile."""

    __tablename__ = "lectin_specificity_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    screen_id = Column(GUID(), ForeignKey("glycan_microarray_screens.id", ondelete="CASCADE"), nullable=False)
    glycan_motif = Column(String(120), nullable=False)
    enrichment_fold = Column(Float, nullable=False)
    p_value_log10 = Column(Float, nullable=False)
    selectivity_index = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    screen = relationship("DBGlycanMicroarrayScreen", back_populates="specificity_profiles")
