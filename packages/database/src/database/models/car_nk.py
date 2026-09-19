"""CAR-NK & Immuno-Oncology SynNotch Cell Circuit Database Models (Phase 96)."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBCarNkDesign(Base):
    __tablename__ = "car_nk_designs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    construct_name = Column(String(255), nullable=False)
    primary_target = Column(String(100), nullable=False)  # e.g., CD19, Mesothelin, EGFRvIII
    costimulatory_domain = Column(String(100), default="2B4_plus_41BB", nullable=False)  # 2B4 (CD244), DNAM-1, 4-1BB, DAP12
    signaling_domain = Column(String(100), default="CD3zeta", nullable=False)
    cytotoxicity_score = Column(Float, default=88.5, nullable=False)  # 0 to 100
    persistence_index = Column(Float, default=82.0, nullable=False)  # 0 to 100
    exhaustion_resistance_score = Column(Float, default=91.4, nullable=False)
    off_tumor_safety_margin = Column(Float, default=94.0, nullable=False)
    design_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    synnotch_gates = relationship("DBSynNotchGate", back_populates="car_nk", cascade="all, delete-orphan")
    cytokines = relationship("DBCytokineSecretionProfile", back_populates="car_nk", cascade="all, delete-orphan")


class DBSynNotchGate(Base):
    __tablename__ = "synnotch_gates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    car_nk_id = Column(GUID(), ForeignKey("car_nk_designs.id", ondelete="CASCADE"), nullable=False, index=True)
    gate_type = Column(String(50), default="AND_GATE", nullable=False)  # AND_GATE, NOT_GATE, OR_GATE
    sensor_antigen = Column(String(100), nullable=False)  # e.g., EpCAM, ROR1
    actuator_payload = Column(String(100), nullable=False)  # CAR-Mesothelin Expression, IL-15 Secretion
    specificity_enrichment = Column(Float, default=14.5, nullable=False)  # Fold increase vs single antigen
    leaky_expression_pct = Column(Float, default=1.8, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    car_nk = relationship("DBCarNkDesign", back_populates="synnotch_gates")


class DBCytokineSecretionProfile(Base):
    __tablename__ = "car_nk_cytokine_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    car_nk_id = Column(GUID(), ForeignKey("car_nk_designs.id", ondelete="CASCADE"), nullable=False, index=True)
    cytokine_name = Column(String(50), nullable=False)  # IL-15, IL-21, IFNg, TNFa, Granzyme-B
    secretion_level_pg_ml = Column(Float, nullable=False)
    is_armored_payload = Column(String(50), default="AUTONOMOUS_SECRETION", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    car_nk = relationship("DBCarNkDesign", back_populates="cytokines")
