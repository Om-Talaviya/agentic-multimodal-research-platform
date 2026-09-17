"""Liquid Biopsy ctDNA Fragmentomics & MRD Detection Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base


class DBLiquidBiopsySample(Base):
    """Liquid biopsy cfDNA sample record for fragmentomics and MRD detection."""
    __tablename__ = "liquid_biopsy_samples"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(64), nullable=False, index=True)
    sample_barcode = Column(String(64), nullable=False, unique=True, index=True)
    cancer_type = Column(String(128), nullable=False)
    sampling_timepoint = Column(String(64), nullable=False)  # BASELINE, POST_SURGERY, CYCLE_3, SURVEILLANCE
    total_cfdna_ng_ml = Column(Float, nullable=False, default=15.0)
    tumor_fraction_pct = Column(Float, nullable=False, default=1.0)
    mrd_status = Column(String(32), nullable=False)  # MRD_POSITIVE, MRD_NEGATIVE, INDETERMINATE
    fragment_short_ratio = Column(Float, nullable=False, default=0.25)
    median_fragment_length_bp = Column(Integer, nullable=False, default=167)
    sample_metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    size_distributions = relationship("DBFragmentSizeDistribution", back_populates="sample", cascade="all, delete-orphan")
    end_motifs = relationship("DBEndMotifProfile", back_populates="sample", cascade="all, delete-orphan")


class DBFragmentSizeDistribution(Base):
    """Fragment length profile binned across base pair ranges."""
    __tablename__ = "fragment_size_distributions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sample_id = Column(String(36), ForeignKey("liquid_biopsy_samples.id", ondelete="CASCADE"), nullable=False)
    bin_start_bp = Column(Integer, nullable=False)
    bin_end_bp = Column(Integer, nullable=False)
    fragment_count = Column(Integer, nullable=False)
    fragment_frequency_pct = Column(Float, nullable=False)

    sample = relationship("DBLiquidBiopsySample", back_populates="size_distributions")


class DBEndMotifProfile(Base):
    """4-mer fragment end-motif frequency metrics."""
    __tablename__ = "fragment_end_motifs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sample_id = Column(String(36), ForeignKey("liquid_biopsy_samples.id", ondelete="CASCADE"), nullable=False)
    motif_sequence_4mer = Column(String(8), nullable=False)
    observed_frequency = Column(Float, nullable=False)
    reference_frequency = Column(Float, nullable=False, default=0.0625)
    motif_diversity_score = Column(Float, nullable=False, default=1.0)

    sample = relationship("DBLiquidBiopsySample", back_populates="end_motifs")
