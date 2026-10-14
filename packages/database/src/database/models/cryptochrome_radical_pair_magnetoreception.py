"""SQLAlchemy models for Phase 493: Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CryptochromeRadicalPairMagnetoreceptionStudy(Base):
    """Study record for Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator."""

    __tablename__ = "p493_cryptochrome_radical_pair_magnetoreception_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Purified Migratory Avian Cryptochrome-4 (ErCry4) Flavin-Tryptophan Photoreduced Radical Pair")
    analytical_modality = Column(String(100), nullable=False, default="quantum-radical-pair-magnetoreception")
    singlet_triplet_yield_anisotropy_ratio = Column(Float, nullable=False, default=1.48)
    radical_pair_quantum_coherence_time_us = Column(Float, nullable=False, default=4.85)
    geomagnetic_field_inclination_sensitivity_nT = Column(Float, nullable=False, default=25.0)
    spin_state_entanglement_fidelity = Column(Float, nullable=False, default=0.982)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CryptochromeRadicalPairMagnetoreceptionItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CryptochromeRadicalPairMagnetoreceptionMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CryptochromeRadicalPairMagnetoreceptionItemProfile(Base):
    """Detailed item profile for Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator."""

    __tablename__ = "p493_cryptochrome_radical_pair_magnetoreception_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p493_cryptochrome_radical_pair_magnetoreception_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryptochromeRadicalPairMagnetoreceptionStudy", back_populates="item_profiles")


class CryptochromeRadicalPairMagnetoreceptionMetricTrace(Base):
    """Metric trace for Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator."""

    __tablename__ = "p493_cryptochrome_radical_pair_magnetoreception_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p493_cryptochrome_radical_pair_magnetoreception_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryptochromeRadicalPairMagnetoreceptionStudy", back_populates="metric_traces")
