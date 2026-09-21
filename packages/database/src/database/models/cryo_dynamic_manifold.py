"""Cryo Manifold Models (Phase 117)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBCryoManifoldDataset(Base):
    __tablename__ = "cryo_manifold_datasets"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    target_complex_name = Column(String(100), nullable=False)
    latent_dimensions = Column(Integer, default=10, nullable=False)
    total_particles_aligned = Column(Integer, default=145000, nullable=False)
    manifold_energy_barrier_kcal = Column(Float, default=4.25, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    manifold_states = relationship("DBConformationalManifoldState", back_populates="dataset", cascade="all, delete-orphan")

class DBConformationalManifoldState(Base):
    __tablename__ = "cryo_manifold_states"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(GUID(), ForeignKey("cryo_manifold_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    state_label = Column(String(100), nullable=False)
    rmsd_from_ground_state = Column(Float, nullable=False)
    relative_population_percentage = Column(Float, nullable=False)
    free_energy_delta_kcal = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    dataset = relationship("DBCryoManifoldDataset", back_populates="manifold_states")
