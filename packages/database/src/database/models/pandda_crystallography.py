"""
Phase 129: Autonomous High-Throughput Crystallography Fragment Screening & Pan-Dataset Density Analysis (PanDDA) Models.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBCrystallographyFragmentScreen(Base):
    __tablename__ = "pandda_fragment_screens"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(String(100), nullable=True)
    campaign_name = Column(String(200), nullable=False)
    target_protein = Column(String(200), nullable=False)
    crystal_space_group = Column(String(50), nullable=False, default="P 21 21 21")
    high_resolution_cutoff_angstrom = Column(Float, nullable=False, default=1.45)
    total_crystals_soaked = Column(Integer, nullable=False, default=320)
    pandda_events_detected = Column(Integer, nullable=False, default=14)
    background_model_r_free = Column(Float, nullable=False, default=0.185)
    metadata_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hits = relationship("DBFragmentHit", back_populates="screen", cascade="all, delete-orphan")
    density_maps = relationship("DBPanDDABackgroundDensityMap", back_populates="screen", cascade="all, delete-orphan")


class DBFragmentHit(Base):
    __tablename__ = "pandda_fragment_hits"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    screen_id = Column(GUID(), ForeignKey("pandda_fragment_screens.id", ondelete="CASCADE"), nullable=False)
    hit_id = Column(String(100), nullable=False)
    fragment_smiles = Column(String(500), nullable=False)
    binding_site_name = Column(String(100), nullable=False)  # Catalytic Pocket, Cryptic Allosteric Site
    event_b_factor = Column(Float, nullable=False, default=24.5)
    event_occupancy = Column(Float, nullable=False, default=0.78)
    z_peak_score = Column(Float, nullable=False, default=6.45)
    ligand_efficiency_le = Column(Float, nullable=False, default=0.48)
    created_at = Column(DateTime, default=datetime.utcnow)

    screen = relationship("DBCrystallographyFragmentScreen", back_populates="hits")


class DBPanDDABackgroundDensityMap(Base):
    __tablename__ = "pandda_density_maps"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    screen_id = Column(GUID(), ForeignKey("pandda_fragment_screens.id", ondelete="CASCADE"), nullable=False)
    map_id = Column(String(100), nullable=False)
    resolution_angstrom = Column(Float, nullable=False, default=1.45)
    statistical_outlier_noise_sigma = Column(Float, nullable=False, default=0.12)
    mean_density_value = Column(Float, nullable=False, default=0.98)
    created_at = Column(DateTime, default=datetime.utcnow)

    screen = relationship("DBCrystallographyFragmentScreen", back_populates="density_maps")
