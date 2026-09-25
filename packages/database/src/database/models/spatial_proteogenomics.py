"""Spatial Proteogenomics & Subcellular Protein-RNA Co-Localization Model."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


class DBSpatialProteogenomicsStudy(Base):
    """Database model for spatial proteogenomics co-detection studies."""

    __tablename__ = "spatial_proteogenomics_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_name = Column(String(255), nullable=False, index=True)
    tissue_sample_id = Column(String(64), nullable=False, default="GBM_TME_Slice_04")
    total_spots_analyzed = Column(Integer, nullable=False, default=4)
    mean_pearson_colocalization_r = Column(Float, nullable=False, default=0.86)
    subcellular_niche_count = Column(Integer, nullable=False, default=3)
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

    spots = relationship(
        "DBProteinRNACoLocalizationSpot",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    enrichment_metrics = relationship(
        "DBMarkerEnrichmentMetric",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class DBProteinRNACoLocalizationSpot(Base):
    """Database model for individual spatial coordinates with simultaneous protein & mRNA quantification."""

    __tablename__ = "protein_rna_colocalization_spots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("spatial_proteogenomics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    spot_barcode = Column(String(64), nullable=False)
    x_coord = Column(Float, nullable=False)
    y_coord = Column(Float, nullable=False)
    target_mrna_symbol = Column(String(32), nullable=False)
    mrna_normalized_count = Column(Float, nullable=False)
    target_protein_antibody = Column(String(64), nullable=False)
    protein_adt_signal = Column(Float, nullable=False)
    colocalization_pearson_r = Column(Float, nullable=False)
    subcellular_niche = Column(String(64), nullable=False, default="Invasive Tumor Core")
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBSpatialProteogenomicsStudy", back_populates="spots")


class DBMarkerEnrichmentMetric(Base):
    """Database model for niche-specific proteogenomic concordance metrics."""

    __tablename__ = "proteogenomic_enrichment_metrics"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("spatial_proteogenomics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    marker_pair = Column(String(64), nullable=False)
    enrichment_z_score = Column(Float, nullable=False)
    fdr_q_value = Column(Float, nullable=False)
    biological_relevance = Column(String(128), nullable=False)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBSpatialProteogenomicsStudy", back_populates="enrichment_metrics")
