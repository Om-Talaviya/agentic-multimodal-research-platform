"""TPD Molecular Glue Models (Phase 121)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBMolecularGlueScreen(Base):
    __tablename__ = "tpd_glue_screens"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    e3_ligase_name = Column(String(50), nullable=False)
    target_neo_substrate = Column(String(100), nullable=False)
    screen_campaign_name = Column(String(100), nullable=False)
    total_screened_glues = Column(Integer, default=4500, nullable=False)
    top_glue_candidate = Column(String(100), default="CC-90009 Derivative", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ternary_affinities = relationship("DBTernaryComplexAffinity", back_populates="screen", cascade="all, delete-orphan")

class DBTernaryComplexAffinity(Base):
    __tablename__ = "tpd_ternary_affinities"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    screen_id = Column(GUID(), ForeignKey("tpd_glue_screens.id", ondelete="CASCADE"), nullable=False, index=True)
    glue_molecule_smiles = Column(String(255), nullable=False)
    cooperativity_factor_alpha = Column(Float, nullable=False)
    ternary_kd_apparent_nm = Column(Float, nullable=False)
    dc50_degradation_potency_nm = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    screen = relationship("DBMolecularGlueScreen", back_populates="ternary_affinities")
