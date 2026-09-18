"""Next-Generation Sequencing (NGS) Long-Read Structural Variant & Telomere Calling Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.connection import Base


class DBLongReadSequencingRun(Base):
    __tablename__ = "long_read_sequencing_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sample_name = Column(String(255), nullable=False)
    platform = Column(String(64), default="PACBIO_HIFI")
    flowcell_type = Column(String(128), default="PromethION_R10.4.1")
    mean_read_length_bp = Column(Float, default=18500.0)
    total_gigabases = Column(Float, default=45.2)
    n50_length_bp = Column(Integer, default=21400)
    mean_phred_quality = Column(Float, default=31.5)
    run_metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    structural_variants = relationship("DBStructuralVariantCall", back_populates="run", cascade="all, delete-orphan")
    telomeric_profiles = relationship("DBTelomericRepeatProfile", back_populates="run", cascade="all, delete-orphan")


class DBStructuralVariantCall(Base):
    __tablename__ = "long_read_structural_variants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("long_read_sequencing_runs.id", ondelete="CASCADE"), nullable=False)
    chromosome = Column(String(32), nullable=False)
    start_pos = Column(Integer, nullable=False)
    end_pos = Column(Integer, nullable=False)
    sv_type = Column(String(32), default="DELETION")
    sv_length_bp = Column(Integer, default=1250)
    genotype = Column(String(16), default="0/1")
    support_reads = Column(Integer, default=28)
    filter_status = Column(String(32), default="PASS")
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("DBLongReadSequencingRun", back_populates="structural_variants")


class DBTelomericRepeatProfile(Base):
    __tablename__ = "long_read_telomere_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("long_read_sequencing_runs.id", ondelete="CASCADE"), nullable=False)
    chromosome_arm = Column(String(32), nullable=False)  # chr1p, chr1q, chr2p...
    hexamer_motif = Column(String(16), default="TTAGGG")
    repeat_count = Column(Integer, default=1450)
    telomere_length_kbp = Column(Float, default=8.7)
    erosion_hazard_level = Column(String(32), default="LOW")
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("DBLongReadSequencingRun", back_populates="telomeric_profiles")
