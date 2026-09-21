"""DDR Models (Phase 119)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBDDRPathwayProfile(Base):
    __tablename__ = "ddr_profiles"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    cancer_type = Column(String(100), nullable=False)
    primary_ddr_defect = Column(String(100), nullable=False)
    hrd_genomic_scar_score = Column(Float, default=58.5, nullable=False)
    replication_stress_index = Column(Float, default=0.82, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    synthetic_interactions = relationship("DBSyntheticViabilityInteraction", back_populates="ddr_profile", cascade="all, delete-orphan")

class DBSyntheticViabilityInteraction(Base):
    __tablename__ = "ddr_synthetic_interactions"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    ddr_profile_id = Column(GUID(), ForeignKey("ddr_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    therapeutic_target_gene = Column(String(100), nullable=False)
    synthetic_lethal_potency_score = Column(Float, nullable=False)
    recommended_inhibitor_class = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ddr_profile = relationship("DBDDRPathwayProfile", back_populates="synthetic_interactions")
