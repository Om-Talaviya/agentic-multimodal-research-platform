"""SQLAlchemy models for Phase 183: CAR-T Cell Exhaustion Epigenetic State Transition Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CARTExhaustionStudy(Base):
    """Study record for CAR-T epigenetic exhaustion trajectories and in-vivo persistence forecasting."""

    __tablename__ = "car_t_exhaustion_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    car_construct_name = Column(String(200), nullable=False)
    costimulatory_domain = Column(String(50), nullable=False, default="4-1BB")
    antigen_density_per_tumor_cell = Column(Float, nullable=False, default=15000.0)
    tonic_signaling_level = Column(String(50), nullable=False, default="low")
    t_stem_cell_memory_pct = Column(Float, nullable=False, default=38.5)
    tox_nr4a_epigenetic_exhaustion_score = Column(Float, nullable=False, default=0.24)
    predicted_persistence_half_life_days = Column(Float, nullable=False, default=185.0)
    in_vivo_antitumor_efficacy_score = Column(Float, nullable=False, default=0.88)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    differentiation_states = relationship("CARTDifferentiationState", back_populates="study", cascade="all, delete-orphan")
    checkpoint_markers = relationship("CARTExhaustionCheckpointMarker", back_populates="study", cascade="all, delete-orphan")


class CARTDifferentiationState(Base):
    """Subpopulation frequencies across Tscm, Tcm, Tem, and Tex state space."""

    __tablename__ = "car_t_differentiation_states"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("car_t_exhaustion_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    state_name = Column(String(50), nullable=False)  # Tscm, Tcm, Tem, Tex_prog, Tex_term
    population_percentage = Column(Float, nullable=False)
    tcf7_expression_level = Column(Float, nullable=False)
    proliferative_capacity_score = Column(Float, nullable=False)
    cytolytic_granzyme_b_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CARTExhaustionStudy", back_populates="differentiation_states")


class CARTExhaustionCheckpointMarker(Base):
    """Inhibitory receptor expression density and exhaustion signature."""

    __tablename__ = "car_t_exhaustion_checkpoint_markers"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("car_t_exhaustion_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    marker_symbol = Column(String(50), nullable=False)  # PD-1, TIM-3, LAG-3, TIGIT, TOX
    surface_density_molecules = Column(Float, nullable=False)
    epigenetic_chromatin_accessibility_score = Column(Float, nullable=False)
    reversibility_potential_pct = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CARTExhaustionStudy", back_populates="checkpoint_markers")