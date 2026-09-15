"""Autonomous Synthetic Biology & CRISPR Gene Editing Guide RNA Models (Phase 40)."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from database.models.memory import GUID, JSONType


class DBCRISPRDesign(Base):
    """Master CRISPR targeting campaign and target gene specification."""

    __tablename__ = "crispr_designs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)

    target_gene: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    genomic_locus: Mapped[str] = mapped_column(String(150), nullable=False, default="Chr1:55039447-55064852")
    organism: Mapped[str] = mapped_column(String(100), nullable=False, default="Homo sapiens")
    cas_enzyme: Mapped[str] = mapped_column(String(50), nullable=False, default="SpCas9")
    pam_motif: Mapped[str] = mapped_column(String(20), nullable=False, default="NGG")
    target_strand: Mapped[str] = mapped_column(String(20), nullable=False, default="both")
    editing_modality: Mapped[str] = mapped_column(String(50), nullable=False, default="knockout_cleavage")
    target_sequence_fasta: Mapped[str] = mapped_column(Text, nullable=False)
    design_summary_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    guide_rnas: Mapped[list["DBGuideRNA"]] = relationship("DBGuideRNA", back_populates="design", cascade="all, delete-orphan", lazy="selectin")


class DBGuideRNA(Base):
    """Specific candidate gRNA guide spacer with on-target and off-target ratings."""

    __tablename__ = "crispr_guide_rnas"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    design_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("crispr_designs.id", ondelete="CASCADE"), nullable=False, index=True)

    guide_name: Mapped[str] = mapped_column(String(100), nullable=False)
    spacer_sequence_20nt: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    pam_sequence: Mapped[str] = mapped_column(String(10), nullable=False)
    genomic_position: Mapped[int] = mapped_column(Integer, nullable=False)
    strand: Mapped[str] = mapped_column(String(5), nullable=False, default="+")
    cut_position_rel: Mapped[int] = mapped_column(Integer, nullable=False, default=17)
    on_target_efficiency_score: Mapped[float] = mapped_column(Float, nullable=False, default=85.0)
    off_target_cfd_score: Mapped[float] = mapped_column(Float, nullable=False, default=95.0)
    gc_content_pct: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    secondary_structure_delta_g: Mapped[float] = mapped_column(Float, nullable=False, default=-2.4)
    recommendation_tier: Mapped[str] = mapped_column(String(20), nullable=False, default="optimal")
    oligo_forward_top: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    oligo_reverse_bottom: Mapped[str] = mapped_column(String(50), nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    design: Mapped["DBCRISPRDesign"] = relationship("DBCRISPRDesign", back_populates="guide_rnas")
    off_target_sites: Mapped[list["DBOffTargetSite"]] = relationship("DBOffTargetSite", back_populates="guide", cascade="all, delete-orphan", lazy="selectin")
    base_editing_profiles: Mapped[list["DBBaseEditingProfile"]] = relationship("DBBaseEditingProfile", back_populates="guide", cascade="all, delete-orphan", lazy="selectin")


class DBOffTargetSite(Base):
    """Genome-wide predicted off-target mismatch cleavage locus."""

    __tablename__ = "crispr_off_targets"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    guide_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("crispr_guide_rnas.id", ondelete="CASCADE"), nullable=False, index=True)

    chromosome: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    genomic_coordinate: Mapped[int] = mapped_column(Integer, nullable=False)
    mismatched_sequence: Mapped[str] = mapped_column(String(30), nullable=False)
    mismatch_count: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    mismatch_positions_json: Mapped[list] = mapped_column(JSONType, nullable=False, default=list)
    cfd_cleavage_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.045)
    gene_annotation: Mapped[str] = mapped_column(String(100), nullable=False, default="Intergenic")
    is_exonic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    guide: Mapped["DBGuideRNA"] = relationship("DBGuideRNA", back_populates="off_target_sites")


class DBBaseEditingProfile(Base):
    """Base editing window (ABE/CBE) activity and bystander deamination evaluation."""

    __tablename__ = "crispr_base_editing_profiles"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    guide_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("crispr_guide_rnas.id", ondelete="CASCADE"), nullable=False, index=True)

    editing_type: Mapped[str] = mapped_column(String(30), nullable=False, default="ABE_A_to_G")
    target_base: Mapped[str] = mapped_column(String(5), nullable=False, default="A")
    editing_window_start: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    editing_window_end: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    expected_product_sequence: Mapped[str] = mapped_column(String(30), nullable=False)
    bystander_bases_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    purity_score_pct: Mapped[float] = mapped_column(Float, nullable=False, default=92.5)
    activity_score_pct: Mapped[float] = mapped_column(Float, nullable=False, default=78.0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    guide: Mapped["DBGuideRNA"] = relationship("DBGuideRNA", back_populates="base_editing_profiles")
