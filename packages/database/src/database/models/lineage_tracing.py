"""Lineage Models (Phase 114)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBLineageBarcodeExperiment(Base):
    __tablename__ = "lineage_experiments"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    experiment_title = Column(String(200), nullable=False)
    barcoding_technology = Column(String(100), default="CRISPR-Cas9 Scarring (GESTALT)", nullable=False)
    total_unique_clones = Column(Integer, default=1250, nullable=False)
    shannon_entropy_diversity = Column(Float, default=4.82, nullable=False)
    dominant_clone_fraction = Column(Float, default=0.28, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    trajectories = relationship("DBClonalLineageTrajectory", back_populates="experiment", cascade="all, delete-orphan")

class DBClonalLineageTrajectory(Base):
    __tablename__ = "lineage_trajectories"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID(), ForeignKey("lineage_experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    clone_barcode_id = Column(String(100), nullable=False)
    initial_frequency = Column(Float, nullable=False)
    post_selection_frequency = Column(Float, nullable=False)
    relative_fitness_coefficient = Column(Float, default=1.45, nullable=False)
    resistance_conferring_driver = Column(String(100), default="KRAS-G12D Amplification", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    experiment = relationship("DBLineageBarcodeExperiment", back_populates="trajectories")
