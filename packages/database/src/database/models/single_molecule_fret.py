"""Phase 160: Single-Molecule FRET (smFRET) Conformational Kinetics Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBSingleMoleculeFRETStudy(Base):
    """Single-molecule FRET conformational transition kinetics study."""

    __tablename__ = "single_molecule_fret_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    biomolecule_name = Column(String(255), nullable=False)
    donor_fluorophore = Column(String(64), default="Cy3 (Donor)")
    acceptor_fluorophore = Column(String(64), default="Cy5 (Acceptor)")
    forster_distance_r0_nm = Column(Float, default=5.4)
    molecules_analyzed_count = Column(Integer, default=0, nullable=False)
    mean_fret_efficiency = Column(Float, default=0.0)
    transition_rate_k_open_s = Column(Float, default=0.0)
    transition_rate_k_close_s = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    state_transitions = relationship("DBFRETKineticStateTransition", back_populates="study", cascade="all, delete-orphan")
    trajectories = relationship("DBFluorophorePhotobleachingTrajectory", back_populates="study", cascade="all, delete-orphan")


class DBFRETKineticStateTransition(Base):
    """Hidden Markov Model (HMM) conformational state and transition rate."""

    __tablename__ = "fret_kinetic_state_transitions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("single_molecule_fret_studies.id", ondelete="CASCADE"), nullable=False)
    state_label = Column(String(64), nullable=False)
    fret_efficiency_peak = Column(Float, nullable=False)
    mean_dwell_time_ms = Column(Float, nullable=False)
    state_occupancy_percentage = Column(Float, nullable=False)
    apparent_distance_angstrom = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBSingleMoleculeFRETStudy", back_populates="state_transitions")


class DBFluorophorePhotobleachingTrajectory(Base):
    """Individual single-molecule time-trace photobleaching profile."""

    __tablename__ = "fluorophore_photobleaching_trajectories"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("single_molecule_fret_studies.id", ondelete="CASCADE"), nullable=False)
    molecule_index = Column(Integer, nullable=False)
    donor_lifetime_seconds = Column(Float, nullable=False)
    acceptor_lifetime_seconds = Column(Float, nullable=False)
    total_transitions_observed = Column(Integer, nullable=False)
    single_step_photobleaching = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBSingleMoleculeFRETStudy", back_populates="trajectories")
