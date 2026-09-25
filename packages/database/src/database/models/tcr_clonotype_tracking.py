"""TCR/BCR Clonotype Tracking & Lineage Dynamics Model."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


class DBTCRClonotypeStudy(Base):
    """Database model for single-cell TCR/BCR repertoire studies."""

    __tablename__ = "tcr_clonotype_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_name = Column(String(255), nullable=False, index=True)
    sample_source = Column(String(255), nullable=False, default="PBMC")
    repertoire_type = Column(String(64), nullable=False, default="TCR_alpha_beta")
    cell_count = Column(Integer, nullable=False, default=5000)
    shannon_entropy = Column(Float, nullable=False, default=4.52)
    gini_simpson_index = Column(Float, nullable=False, default=0.88)
    clonality_score = Column(Float, nullable=False, default=0.35)
    summary_metrics = Column(JSON, nullable=True)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )
    updated_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    clonotypes = relationship(
        "DBClonotypeLineageNode",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    diversity_metrics = relationship(
        "DBImmuneRepertoireDiversityMetric",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class DBClonotypeLineageNode(Base):
    """Database model for individual TCR/BCR clonotype nodes."""

    __tablename__ = "tcr_clonotype_lineage_nodes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("tcr_clonotype_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    cdr3_amino_acid = Column(String(128), nullable=False)
    v_gene = Column(String(64), nullable=False)
    j_gene = Column(String(64), nullable=False)
    d_gene = Column(String(64), nullable=True)
    clone_frequency = Column(Float, nullable=False)
    expansion_status = Column(String(64), nullable=False, default="hyperexpanded")
    antigen_specificity = Column(String(128), nullable=True)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBTCRClonotypeStudy", back_populates="clonotypes")


class DBImmuneRepertoireDiversityMetric(Base):
    """Database model for sample-level diversity and V-J segment distribution metrics."""

    __tablename__ = "tcr_diversity_metrics"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("tcr_clonotype_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name = Column(String(128), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_category = Column(String(64), nullable=False, default="entropy")
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBTCRClonotypeStudy", back_populates="diversity_metrics")
