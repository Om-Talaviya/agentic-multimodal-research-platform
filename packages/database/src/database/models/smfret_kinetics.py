"""Single-Molecule FRET (smFRET) Kinetics & Conformational Transition Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base


class DBSmFRETExperiment(Base):
    """Single-molecule FRET experiment record."""
    __tablename__ = "smfret_experiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_title = Column(String(255), nullable=False)
    macromolecule_name = Column(String(128), nullable=False, index=True)
    donor_fluorophore = Column(String(32), nullable=False, default="Cy3")
    acceptor_fluorophore = Column(String(32), nullable=False, default="Cy5")
    forster_radius_angstrom = Column(Float, nullable=False, default=54.0)
    acquisition_rate_hz = Column(Float, nullable=False, default=100.0)
    total_molecules_recorded = Column(Integer, nullable=False, default=1)
    state_count = Column(Integer, nullable=False, default=3)
    experiment_metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    traces = relationship("DBSmFRETMoleculeTrace", back_populates="experiment", cascade="all, delete-orphan")
    states = relationship("DBConformationalState", back_populates="experiment", cascade="all, delete-orphan")


class DBSmFRETMoleculeTrace(Base):
    """Individual single-molecule time-series fluorescence and FRET trace."""
    __tablename__ = "smfret_molecule_traces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String(36), ForeignKey("smfret_experiments.id", ondelete="CASCADE"), nullable=False)
    molecule_index = Column(Integer, nullable=False)
    total_frames = Column(Integer, nullable=False, default=500)
    mean_fret_efficiency = Column(Float, nullable=False, default=0.5)
    photobleaching_frame = Column(Integer, nullable=True)
    trace_data_json = Column(JSON, default=list)  # [{time_sec, donor_int, acceptor_int, fret_eff, hmm_state, distance_angstrom}]

    experiment = relationship("DBSmFRETExperiment", back_populates="traces")


class DBConformationalState(Base):
    """Hidden Markov Model (HMM) conformational state and kinetic rates."""
    __tablename__ = "smfret_conformational_states"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String(36), ForeignKey("smfret_experiments.id", ondelete="CASCADE"), nullable=False)
    state_index = Column(Integer, nullable=False)
    state_name = Column(String(64), nullable=False)  # OPEN, INTERMEDIATE, CLOSED
    mean_efficiency = Column(Float, nullable=False)
    occupancy_fraction = Column(Float, nullable=False)
    mean_dwell_time_ms = Column(Float, nullable=False)
    transition_rates_json = Column(JSON, default=dict)  # {to_state_idx: rate_per_sec}

    experiment = relationship("DBSmFRETExperiment", back_populates="states")
