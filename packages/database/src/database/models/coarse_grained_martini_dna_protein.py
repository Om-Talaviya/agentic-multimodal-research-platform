"""SQLAlchemy models for Phase 447: Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CoarseGrainedMartiniDnaProteinStudy(Base):
    """Study record for Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator."""

    __tablename__ = "p447_coarse_grained_martini_dna_protein_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Nucleosome Core Particle Octamer with 147bp Wrapped DNA in 150mM Salt Solvation Box")
    analytical_modality = Column(String(100), nullable=False, default="coarse-grained-martini-dynamics")
    bead_rmsd_convergence_angstrom = Column(Float, nullable=False, default=2.15)
    electrostatic_solvation_free_energy_kcal_mol = Column(Float, nullable=False, default=-342.5)
    conformational_sampling_speedup_factor = Column(Float, nullable=False, default=85.0)
    contact_pair_distribution_g_r = Column(Float, nullable=False, default=1.48)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CoarseGrainedMartiniDnaProteinItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CoarseGrainedMartiniDnaProteinMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CoarseGrainedMartiniDnaProteinItemProfile(Base):
    """Detailed item profile for Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator."""

    __tablename__ = "p447_coarse_grained_martini_dna_protein_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p447_coarse_grained_martini_dna_protein_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CoarseGrainedMartiniDnaProteinStudy", back_populates="item_profiles")


class CoarseGrainedMartiniDnaProteinMetricTrace(Base):
    """Metric trace for Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator."""

    __tablename__ = "p447_coarse_grained_martini_dna_protein_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p447_coarse_grained_martini_dna_protein_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CoarseGrainedMartiniDnaProteinStudy", back_populates="metric_traces")
