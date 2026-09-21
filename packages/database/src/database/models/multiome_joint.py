"""Multiome Models (Phase 120)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBSingleCellMultiomeDataset(Base):
    __tablename__ = "multiome_datasets"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    sample_identifier = Column(String(100), nullable=False)
    total_joint_cells = Column(Integer, default=12400, nullable=False)
    wnn_modality_weight_rna = Column(Float, default=0.55, nullable=False)
    wnn_modality_weight_atac = Column(Float, default=0.45, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    linkages = relationship("DBCisRegulatoryLinkage", back_populates="dataset", cascade="all, delete-orphan")

class DBCisRegulatoryLinkage(Base):
    __tablename__ = "multiome_linkages"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(GUID(), ForeignKey("multiome_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    target_gene = Column(String(100), nullable=False)
    accessible_peak_locus = Column(String(100), nullable=False)
    peak_to_gene_correlation = Column(Float, nullable=False)
    binding_transcription_factor = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    dataset = relationship("DBSingleCellMultiomeDataset", back_populates="linkages")
