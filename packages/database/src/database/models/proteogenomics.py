"""Proteogenomics & Mass Spectrometry Peptide Spectral Library Database Models (Phase 95)."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBProteogenomicExperiment(Base):
    __tablename__ = "proteogenomic_experiments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    sample_id = Column(String(255), nullable=False)
    organism = Column(String(100), default="Homo sapiens", nullable=False)
    instrument_type = Column(String(100), default="Orbitrap Exploris 480", nullable=False)  # Orbitrap, timsTOF Pro, Q-Exactive
    search_database = Column(String(100), default="UniProtKB + Ribo-Seq Novel ORFs", nullable=False)
    fdr_threshold = Column(Float, default=0.01, nullable=False)
    total_spectra_analyzed = Column(Integer, default=50000, nullable=False)
    identified_peptides_count = Column(Integer, default=12400, nullable=False)
    novel_noncanonical_orfs_count = Column(Integer, default=38, nullable=False)
    analysis_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    psm_matches = relationship("DBPeptideSpectrumMatch", back_populates="experiment", cascade="all, delete-orphan")
    novel_junctions = relationship("DBNovelSpliceJunction", back_populates="experiment", cascade="all, delete-orphan")


class DBPeptideSpectrumMatch(Base):
    __tablename__ = "peptide_spectrum_matches"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID(), ForeignKey("proteogenomic_experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_number = Column(Integer, nullable=False)
    peptide_sequence = Column(String(255), nullable=False)
    protein_accession = Column(String(100), nullable=False)
    charge_state = Column(Integer, default=2, nullable=False)
    precursor_mz = Column(Float, nullable=False)
    calculated_mz = Column(Float, nullable=False)
    hyperscore = Column(Float, default=45.2, nullable=False)
    posterior_error_prob = Column(Float, default=0.002, nullable=False)
    is_novel_variant = Column(String(50), default="CANONICAL", nullable=False)  # CANONICAL, NON_CANONICAL_ORF, VARIANT_MUTATION
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    experiment = relationship("DBProteogenomicExperiment", back_populates="psm_matches")


class DBNovelSpliceJunction(Base):
    __tablename__ = "novel_splice_junctions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID(), ForeignKey("proteogenomic_experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    chromosome = Column(String(20), nullable=False)
    junction_start = Column(Integer, nullable=False)
    junction_end = Column(Integer, nullable=False)
    supporting_reads_count = Column(Integer, default=14, nullable=False)
    peptide_evidence = Column(String(255), nullable=False)
    frameshift_flag = Column(String(50), default="IN_FRAME", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    experiment = relationship("DBProteogenomicExperiment", back_populates="novel_junctions")
