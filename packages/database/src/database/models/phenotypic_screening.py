"""Phenotypic Screening & High-Content Image Morphometry Database Models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBCellPaintingPlate(Base):
    __tablename__ = "cell_painting_plates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    plate_name = Column(String(255), nullable=False)
    format = Column(String(50), default="384-well", nullable=False)  # 96-well, 384-well, 1536-well
    cell_line = Column(String(100), default="U2OS", nullable=False)
    imaging_magnification = Column(String(50), default="20x", nullable=False)
    channels_profiled = Column(JSON, default=list, nullable=False)  # DNA, RNA, ER, AGP, Mito
    total_wells = Column(Integer, default=384, nullable=False)
    plate_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    wells = relationship("DBCellPaintingWell", back_populates="plate", cascade="all, delete-orphan")


class DBCellPaintingWell(Base):
    __tablename__ = "cell_painting_wells"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    plate_id = Column(GUID(), ForeignKey("cell_painting_plates.id", ondelete="CASCADE"), nullable=False, index=True)
    well_position = Column(String(20), nullable=False, index=True)  # e.g. A01, B12
    compound_name = Column(String(255), nullable=False)
    concentration_uM = Column(Float, default=10.0, nullable=False)
    is_control = Column(Boolean, default=False, nullable=False)
    cell_count = Column(Integer, default=1500, nullable=False)
    viability_pct = Column(Float, default=95.0, nullable=False)
    predicted_moa = Column(String(255), default="Unknown", nullable=False)  # Mechanism of Action
    moa_confidence = Column(Float, default=0.85, nullable=False)
    phenotypic_activity_score = Column(Float, default=0.0, nullable=False)  # Mahalanobis distance / induction
    morphological_profile = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    plate = relationship("DBCellPaintingPlate", back_populates="wells")
    single_cells = relationship("DBSingleCellMorphometry", back_populates="well", cascade="all, delete-orphan")


class DBSingleCellMorphometry(Base):
    __tablename__ = "single_cell_morphometry"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    well_id = Column(GUID(), ForeignKey("cell_painting_wells.id", ondelete="CASCADE"), nullable=False, index=True)
    cell_index = Column(Integer, nullable=False)
    nuclear_area = Column(Float, nullable=False)
    nuclear_eccentricity = Column(Float, nullable=False)
    cytoplasm_area = Column(Float, nullable=False)
    er_intensity_mean = Column(Float, nullable=False)
    mito_texture_contrast = Column(Float, nullable=False)
    actin_alignment_index = Column(Float, nullable=False)
    zernike_moment_z20 = Column(Float, default=0.0, nullable=False)
    haralick_homogeneity = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    well = relationship("DBCellPaintingWell", back_populates="single_cells")
