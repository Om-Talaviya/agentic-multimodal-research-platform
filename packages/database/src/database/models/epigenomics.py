"""
SQLAlchemy models for Autonomous Epigenomic Chromatin Accessibility & ATAC-seq Peak Calling Engine (Phase 56).
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from database.connection import Base


class DBEpigenomicExperiment(Base):
    """Represents an epigenomic sequencing experiment (ATAC-seq, ChIP-seq, Cut&Run)."""
    __tablename__ = "epigenomic_experiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sample_id = Column(String(64), nullable=False)
    tissue_type = Column(String(128), nullable=False)
    assay_type = Column(String(32), default="ATAC-seq")  # ATAC-seq, ChIP-seq, Cut&Run
    sequencing_depth_millions = Column(Float, default=45.0)
    total_peaks_called = Column(Integer, default=0)
    status = Column(String(32), default="COMPLETED")
    metadata_info = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    peaks = relationship("DBChromatinPeak", back_populates="experiment", cascade="all, delete-orphan")


class DBChromatinPeak(Base):
    """Represents an accessible open-chromatin peak call."""
    __tablename__ = "epigenomic_chromatin_peaks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String(36), ForeignKey("epigenomic_experiments.id", ondelete="CASCADE"), nullable=False)
    chromosome = Column(String(16), nullable=False)  # e.g., chr1, chr7, chrX
    start_pos = Column(Integer, nullable=False)
    end_pos = Column(Integer, nullable=False)
    peak_score = Column(Float, nullable=False)
    fold_enrichment = Column(Float, nullable=False)
    p_value_neg_log10 = Column(Float, nullable=False)
    genomic_annotation = Column(String(64), default="Promoter")  # Promoter, Enhancer, Intron, Intergenic
    nearest_gene = Column(String(64), nullable=False)
    distance_to_tss = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("DBEpigenomicExperiment", back_populates="peaks")
    motifs = relationship("DBTranscriptionFactorMotif", back_populates="peak", cascade="all, delete-orphan")


class DBTranscriptionFactorMotif(Base):
    """Represents an enriched TF binding motif within an open chromatin peak."""
    __tablename__ = "epigenomic_tf_motifs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    peak_id = Column(String(36), ForeignKey("epigenomic_chromatin_peaks.id", ondelete="CASCADE"), nullable=False)
    motif_name = Column(String(64), nullable=False)  # e.g., CTCF, FOXA1, NFKB1, AP-1
    pwm_match_score = Column(Float, nullable=False)
    motif_p_value = Column(Float, default=1e-5)
    strand = Column(String(4), default="+")
    consensus_sequence = Column(String(32), default="TGACTCA")
    created_at = Column(DateTime, default=datetime.utcnow)

    peak = relationship("DBChromatinPeak", back_populates="motifs")
