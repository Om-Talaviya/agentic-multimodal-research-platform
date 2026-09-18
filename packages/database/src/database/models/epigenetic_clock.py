"""Epigenetic Clock & DNA Methylation Database Models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBEpigeneticSample(Base):
    __tablename__ = "epigenetic_samples"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    sample_name = Column(String(255), nullable=False)
    tissue_type = Column(String(100), default="Whole Blood", nullable=False)
    chronological_age = Column(Float, nullable=False)
    gender = Column(String(50), default="unknown", nullable=False)
    platform = Column(String(100), default="Illumina EPIC 850k", nullable=False)
    total_cpgs_profiled = Column(Integer, default=0, nullable=False)
    sample_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    clock_results = relationship("DBMethylationClockResult", back_populates="sample", cascade="all, delete-orphan")


class DBMethylationClockResult(Base):
    __tablename__ = "methylation_clock_results"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    sample_id = Column(GUID(), ForeignKey("epigenetic_samples.id", ondelete="CASCADE"), nullable=False, index=True)
    clock_model = Column(String(100), default="Horvath Multi-Tissue", nullable=False)  # Horvath, Hannum, PhenoAge, GrimAge
    predicted_epigenetic_age = Column(Float, nullable=False)
    age_acceleration = Column(Float, nullable=False)  # predicted_age - chronological_age
    confidence_interval_low = Column(Float, default=0.0, nullable=False)
    confidence_interval_high = Column(Float, default=0.0, nullable=False)
    mortality_risk_percentile = Column(Float, default=50.0, nullable=False)
    model_r_squared = Column(Float, default=0.92, nullable=False)
    cpgs_utilized = Column(Integer, default=353, nullable=False)
    pace_of_aging = Column(Float, default=1.0, nullable=False)  # DuneDInPACE metric
    analysis_details = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sample = relationship("DBEpigeneticSample", back_populates="clock_results")
    cpg_markers = relationship("DBCpGMarkerScore", back_populates="clock_result", cascade="all, delete-orphan")


class DBCpGMarkerScore(Base):
    __tablename__ = "cpg_marker_scores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    clock_result_id = Column(GUID(), ForeignKey("methylation_clock_results.id", ondelete="CASCADE"), nullable=False, index=True)
    cpg_id = Column(String(100), nullable=False, index=True)  # e.g., cg00075967
    gene_symbol = Column(String(100), nullable=True)
    chromosome = Column(String(20), nullable=True)
    genomic_coordinate = Column(Integer, nullable=True)
    beta_value = Column(Float, nullable=False)  # 0.0 to 1.0 methylation degree
    model_weight = Column(Float, nullable=False)
    contribution_to_age = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    clock_result = relationship("DBMethylationClockResult", back_populates="cpg_markers")
