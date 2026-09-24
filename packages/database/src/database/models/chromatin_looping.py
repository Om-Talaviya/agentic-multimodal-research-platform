"""Phase 152: High-Resolution Hi-C Chromatin Loop Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBHiCChromatinLoopStudy(Base):
    """Hi-C 3D chromatin conformation and enhancer-promoter loop study."""

    __tablename__ = "hic_chromatin_loop_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    cell_line_name = Column(String(120), nullable=False)
    chromosome = Column(String(32), default="chr8")
    genomic_resolution_bp = Column(Integer, default=5000, nullable=False)
    total_loops_detected = Column(Integer, default=0, nullable=False)
    tad_count = Column(Integer, default=0, nullable=False)
    mean_insulation_score = Column(Float, default=0.0)
    mean_loop_span_kb = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    contact_edges = relationship("DBEnhancerPromoterContactEdge", back_populates="study", cascade="all, delete-orphan")
    tad_boundaries = relationship("DBTADBoundaryRegion", back_populates="study", cascade="all, delete-orphan")


class DBEnhancerPromoterContactEdge(Base):
    """Specific enhancer-promoter interaction loop with contact frequency."""

    __tablename__ = "enhancer_promoter_contact_edges"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("hic_chromatin_loop_studies.id", ondelete="CASCADE"), nullable=False)
    enhancer_locus = Column(String(120), nullable=False)
    target_gene = Column(String(64), nullable=False)
    contact_frequency = Column(Float, nullable=False)
    loop_span_bp = Column(Integer, nullable=False)
    ctcf_convergent_motif = Column(Boolean, default=True)
    activation_log2fc = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBHiCChromatinLoopStudy", back_populates="contact_edges")


class DBTADBoundaryRegion(Base):
    """Topologically Associating Domain boundary coordinates and insulation."""

    __tablename__ = "tad_boundary_regions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("hic_chromatin_loop_studies.id", ondelete="CASCADE"), nullable=False)
    start_bp = Column(Integer, nullable=False)
    end_bp = Column(Integer, nullable=False)
    insulation_score = Column(Float, nullable=False)
    ctcf_occupancy_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBHiCChromatinLoopStudy", back_populates="tad_boundaries")
