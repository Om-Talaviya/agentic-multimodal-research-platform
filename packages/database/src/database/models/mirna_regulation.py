"""miRNA Models (Phase 115)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBMiRNARegulatoryNetwork(Base):
    __tablename__ = "mirna_networks"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    mirna_id = Column(String(50), nullable=False)
    seed_sequence = Column(String(20), nullable=False)
    disease_context = Column(String(100), nullable=False)
    total_predicted_targets = Column(Integer, default=450, nullable=False)
    network_density = Column(Float, default=0.64, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    target_repressions = relationship("DBMiRNATargetRepression", back_populates="network", cascade="all, delete-orphan")

class DBMiRNATargetRepression(Base):
    __tablename__ = "mirna_target_repressions"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    network_id = Column(GUID(), ForeignKey("mirna_networks.id", ondelete="CASCADE"), nullable=False, index=True)
    target_gene = Column(String(100), nullable=False)
    seed_match_type = Column(String(50), default="8mer Canonical", nullable=False)
    binding_free_energy_kcal_mol = Column(Float, nullable=False)
    predicted_repression_fold = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    network = relationship("DBMiRNARegulatoryNetwork", back_populates="target_repressions")
