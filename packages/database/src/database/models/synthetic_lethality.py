import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class DBSyntheticLethalScreen(Base):
    __tablename__ = "synthetic_lethal_screens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screen_name = Column(String(255), nullable=False)
    primary_target_gene = Column(String(100), nullable=False)  # e.g., BRCA1, KRAS, TP53, ARID1A, VHL
    tumor_indication = Column(String(100), nullable=False, default="Ovarian Carcinoma")
    ceres_dependency_threshold = Column(Float, nullable=False, default=-0.5)  # < -0.5 indicates essentiality
    sample_cell_lines_count = Column(Integer, nullable=False, default=320)
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    partners = relationship("DBSyntheticLethalPartner", back_populates="screen", cascade="all, delete-orphan")
    dependency_scores = relationship("DBCRISPRDependencyScore", back_populates="screen", cascade="all, delete-orphan")

class DBSyntheticLethalPartner(Base):
    __tablename__ = "synthetic_lethal_partners"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screen_id = Column(String(36), ForeignKey("synthetic_lethal_screens.id", ondelete="CASCADE"), nullable=False)
    partner_gene = Column(String(100), nullable=False)  # e.g., PARP1, POLQ, SMARCA2, PRMT5
    interaction_type = Column(String(100), nullable=False, default="DNA Repair Compensation")  # Paralog, DNA Repair, Pathway Bypass
    ceres_depmap_delta_score = Column(Float, nullable=False)  # Delta CERES score between mutant and wildtype
    synthetic_lethal_p_value = Column(Float, nullable=False)  # Adjusted p-value (Benjamini-Hochberg)
    is_validated_druggable = Column(Boolean, default=True)
    confidence_tier = Column(String(50), nullable=False, default="HIGH")  # HIGH, MODERATE, LOW
    created_at = Column(DateTime, default=datetime.utcnow)

    screen = relationship("DBSyntheticLethalScreen", back_populates="partners")

class DBCRISPRDependencyScore(Base):
    __tablename__ = "crispr_dependency_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screen_id = Column(String(36), ForeignKey("synthetic_lethal_screens.id", ondelete="CASCADE"), nullable=False)
    cell_line_name = Column(String(100), nullable=False)  # MDA-MB-436, OVCAR-8, HCT116
    lineage = Column(String(100), nullable=False, default="Ovary")
    primary_gene_dependency_score = Column(Float, nullable=False)  # CERES score
    partner_gene_dependency_score = Column(Float, nullable=False)  # CERES score
    co_essentiality_correlation = Column(Float, nullable=False, default=0.68)  # Pearson r
    created_at = Column(DateTime, default=datetime.utcnow)

    screen = relationship("DBSyntheticLethalScreen", back_populates="dependency_scores")
