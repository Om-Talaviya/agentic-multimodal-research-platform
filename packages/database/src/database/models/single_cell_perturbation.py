"""
SQLAlchemy Models for Phase 167: Single-Cell Multi-Omics Perturbation Screening & Causal GRN Inversion Engine.
"""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from database.connection import Base
from database.models.memory import GUID
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBSingleCellPerturbationStudy(Base):
    __tablename__ = "single_cell_perturbation_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), nullable=True, index=True)
    study_name = Column(String(255), nullable=False)
    perturbation_modality = Column(String(100), default="CRISPRi-PerturbSeq")
    total_cells_profiled = Column(Integer, default=0)
    target_genes_count = Column(Integer, default=0)
    energy_distance_shift = Column(Float, nullable=False)
    causal_network_density = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)

    target_effects = relationship(
        "DBPerturbationTargetEffect",
        back_populates="study",
        cascade="all, delete-orphan",
    )
    grn_edges = relationship(
        "DBCausalGRNEdge",
        back_populates="study",
        cascade="all, delete-orphan",
    )


class DBPerturbationTargetEffect(Base):
    __tablename__ = "perturbation_target_effects"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("single_cell_perturbation_studies.id"), nullable=False, index=True)
    guide_target_gene = Column(String(100), nullable=False)
    knockdown_efficiency_percent = Column(Float, nullable=False)
    differentially_expressed_genes_count = Column(Integer, nullable=False)
    phenotypic_dispersion_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    study = relationship("DBSingleCellPerturbationStudy", back_populates="target_effects")


class DBCausalGRNEdge(Base):
    __tablename__ = "causal_grn_edges"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("single_cell_perturbation_studies.id"), nullable=False, index=True)
    source_regulator_gene = Column(String(100), nullable=False)
    target_effector_gene = Column(String(100), nullable=False)
    causal_weight_beta = Column(Float, nullable=False)
    p_value_fdr = Column(Float, nullable=False)
    regulation_sign = Column(String(20), default="Activation")
    created_at = Column(DateTime, default=utc_now)

    study = relationship("DBSingleCellPerturbationStudy", back_populates="grn_edges")
