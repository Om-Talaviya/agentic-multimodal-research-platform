"""SQLAlchemy models for Phase 575: Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CryoEtSubtomogramMembraneCoatAssemblerStudy(Base):
    """Study record for Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler."""

    __tablename__ = "p575_cryo_et_subtomogram_membrane_coat_assembler_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Vitrified Saccharomyces cerevisiae Budding Vesicle Donor Sites with COP-II Polyhedral Lattice Outer Shell")
    analytical_modality = Column(String(100), nullable=False, default="cryoet-subtomogram-coat-assembly")
    subtomogram_resolution_fsc0143_a = Column(Float, nullable=False, default=4.15)
    cage_polyhedral_symmetry_index = Column(Float, nullable=False, default=0.945)
    membrane_curvature_coupling_energy_kbt = Column(Float, nullable=False, default=24.8)
    angular_orientation_precision_deg = Column(Float, nullable=False, default=1.85)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CryoEtSubtomogramMembraneCoatAssemblerItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CryoEtSubtomogramMembraneCoatAssemblerMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CryoEtSubtomogramMembraneCoatAssemblerItemProfile(Base):
    """Detailed item profile for Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler."""

    __tablename__ = "p575_cryo_et_subtomogram_membrane_coat_assembler_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p575_cryo_et_subtomogram_membrane_coat_assembler_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoEtSubtomogramMembraneCoatAssemblerStudy", back_populates="item_profiles")


class CryoEtSubtomogramMembraneCoatAssemblerMetricTrace(Base):
    """Metric trace for Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler."""

    __tablename__ = "p575_cryo_et_subtomogram_membrane_coat_assembler_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p575_cryo_et_subtomogram_membrane_coat_assembler_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoEtSubtomogramMembraneCoatAssemblerStudy", back_populates="metric_traces")
