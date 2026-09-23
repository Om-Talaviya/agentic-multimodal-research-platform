"""
Phase 128: Autonomous Single-Cell Spatial CITE-seq Multi-Modal Surface Protein & mRNA Co-Mapping Models.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBCITEseqDataset(Base):
    __tablename__ = "citeseq_datasets"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(String(100), nullable=True)
    sample_name = Column(String(200), nullable=False)
    tissue_origin = Column(String(150), nullable=False, default="Tumor-Infiltrating Lymphocytes")
    total_cells_profiled = Column(Integer, nullable=False, default=14500)
    adt_panel_size = Column(Integer, nullable=False, default=54)
    rna_features_count = Column(Integer, nullable=False, default=24500)
    dsb_background_ambient_mean = Column(Float, nullable=False, default=1.85)
    wNN_modality_weight_protein = Column(Float, nullable=False, default=0.58)
    wNN_modality_weight_rna = Column(Float, nullable=False, default=0.42)
    metadata_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    antibodies = relationship("DBAntibodyDerivedTag", back_populates="dataset", cascade="all, delete-orphan")
    expressions = relationship("DBCellSurfaceProteinExpression", back_populates="dataset", cascade="all, delete-orphan")


class DBAntibodyDerivedTag(Base):
    __tablename__ = "citeseq_antibody_tags"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(GUID(), ForeignKey("citeseq_datasets.id", ondelete="CASCADE"), nullable=False)
    tag_barcode = Column(String(50), nullable=False)
    marker_name = Column(String(100), nullable=False)  # e.g., "CD3e", "CD4", "CD8a", "PD-1", "CTLA-4"
    clone_id = Column(String(50), nullable=False)
    isotype_control = Column(String(50), nullable=False, default="IgG1-k")
    signal_to_noise_ratio = Column(Float, nullable=False, default=14.8)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("DBCITEseqDataset", back_populates="antibodies")


class DBCellSurfaceProteinExpression(Base):
    __tablename__ = "citeseq_protein_expressions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(GUID(), ForeignKey("citeseq_datasets.id", ondelete="CASCADE"), nullable=False)
    cell_cluster_id = Column(String(100), nullable=False)  # e.g., "Effector_CD8_T_Cells"
    marker_name = Column(String(100), nullable=False)
    dsb_normalized_expression = Column(Float, nullable=False, default=4.82)
    corresponding_rna_tpm = Column(Float, nullable=False, default=128.4)
    concordance_spearman_rho = Column(Float, nullable=False, default=0.78)
    discordance_pvalue = Column(Float, nullable=False, default=0.0001)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("DBCITEseqDataset", back_populates="expressions")
