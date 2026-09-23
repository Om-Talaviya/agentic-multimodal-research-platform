"""
Phase 137: CAR-Macrophage (CAR-M) Solid Tumor Phagocytosis & TME Matrix Degradation Database Models.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBCARMacrophageDesign(Base):
    __tablename__ = "car_macrophage_designs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, nullable=True, index=True)
    construct_name = Column(String(255), nullable=False, index=True)
    target_tumor_antigen = Column(String(100), nullable=False, default="HER2 / ERBB2")
    scfv_domain = Column(String(255), nullable=False, default="Trastuzumab-derived 4D5")
    intracellular_signaling_domain = Column(String(100), nullable=False, default="Megf10 / FcR-gamma / CD3zeta")
    macrophage_subtype = Column(String(50), nullable=False, default="M1-Polarized Pro-Inflammatory")
    matrix_degradation_mmp_score = Column(Float, nullable=False, default=8.4)
    target_phagocytosis_efficiency_percent = Column(Float, nullable=False, default=78.5)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    phagocytosis_records = relationship(
        "DBPhagocytosisKinetics",
        back_populates="design",
        cascade="all, delete-orphan",
    )
    tme_profiles = relationship(
        "DBTMERepolarizationProfile",
        back_populates="design",
        cascade="all, delete-orphan",
    )


class DBPhagocytosisKinetics(Base):
    __tablename__ = "phagocytosis_kinetics"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    design_id = Column(GUID, ForeignKey("car_macrophage_designs.id", ondelete="CASCADE"), nullable=False, index=True)
    target_cell_line = Column(String(100), nullable=False)  # "SK-BR-3 (HER2+ Breast Cancer)"
    effector_to_target_ratio = Column(String(20), nullable=False, default="2:1")
    trogocytosis_rate_percent = Column(Float, nullable=False, default=12.4)
    whole_cell_engulfment_rate_percent = Column(Float, nullable=False, default=66.1)
    antigen_cross_presentation_index = Column(Float, nullable=False, default=0.88)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    design = relationship("DBCARMacrophageDesign", back_populates="phagocytosis_records")


class DBTMERepolarizationProfile(Base):
    __tablename__ = "tme_repolarization_profiles"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    design_id = Column(GUID, ForeignKey("car_macrophage_designs.id", ondelete="CASCADE"), nullable=False, index=True)
    tnf_alpha_secretion_pg_ml = Column(Float, nullable=False)
    il12_secretion_pg_ml = Column(Float, nullable=False)
    il10_immunosuppression_fold_reduction = Column(Float, nullable=False)
    collagen_matrix_clearance_percent = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    design = relationship("DBCARMacrophageDesign", back_populates="tme_profiles")
