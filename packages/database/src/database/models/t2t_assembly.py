"""
Phase 126: Autonomous Whole-Genome Long-Read Telomere-to-Telomere Structural Variant & Phase Assembly Models.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBT2TAssembly(Base):
    __tablename__ = "t2t_assemblies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(String(100), nullable=True)
    sample_name = Column(String(200), nullable=False)
    sequencing_technology = Column(String(100), nullable=False, default="PacBio-HiFi+ONT-UltraLong")
    total_contig_length_bp = Column(Integer, nullable=False, default=3117275501)
    n50_length_kbp = Column(Float, nullable=False, default=145200.5)
    qv_consensus_accuracy = Column(Float, nullable=False, default=62.4)
    kmer_completeness_pct = Column(Float, nullable=False, default=99.98)
    telomere_telomere_closed_chromosomes = Column(Integer, nullable=False, default=24)
    metadata_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    variants = relationship("DBT2TStructuralVariantCall", back_populates="assembly", cascade="all, delete-orphan")
    haplotypes = relationship("DBPhasedHaplotypeBlock", back_populates="assembly", cascade="all, delete-orphan")


class DBT2TStructuralVariantCall(Base):
    __tablename__ = "t2t_structural_variants"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    assembly_id = Column(GUID(), ForeignKey("t2t_assemblies.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(String(100), nullable=False)
    chromosome = Column(String(50), nullable=False)
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    sv_type = Column(String(50), nullable=False)  # DELETION, INSERTION, INVERSION, TRANSLOCATION, DUP
    sv_length_bp = Column(Integer, nullable=False)
    genotype_quality = Column(Float, nullable=False, default=99.0)
    supporting_reads_count = Column(Integer, nullable=False, default=45)
    flanking_repeat_motif = Column(String(200), nullable=True)
    functional_impact_score = Column(Float, nullable=False, default=0.75)
    created_at = Column(DateTime, default=datetime.utcnow)

    assembly = relationship("DBT2TAssembly", back_populates="variants")


class DBPhasedHaplotypeBlock(Base):
    __tablename__ = "t2t_phased_haplotypes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    assembly_id = Column(GUID(), ForeignKey("t2t_assemblies.id", ondelete="CASCADE"), nullable=False)
    chromosome = Column(String(50), nullable=False)
    block_start_bp = Column(Integer, nullable=False)
    block_end_bp = Column(Integer, nullable=False)
    phase_switch_error_rate = Column(Float, nullable=False, default=0.0012)
    maternal_markers_count = Column(Integer, nullable=False, default=12400)
    paternal_markers_count = Column(Integer, nullable=False, default=11980)
    created_at = Column(DateTime, default=datetime.utcnow)

    assembly = relationship("DBT2TAssembly", back_populates="haplotypes")
