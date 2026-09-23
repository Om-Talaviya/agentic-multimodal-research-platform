"""
Phase 138: High-Throughput Lipid Nanoparticle (LNP) Formulation & mRNA Encapsulation Efficiency Database Models.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBLNPFormulationScreen(Base):
    __tablename__ = "lnp_formulation_screens"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, nullable=True, index=True)
    formulation_tag = Column(String(255), nullable=False, index=True)
    mrna_payload_name = Column(String(255), nullable=False, default="EGFP Reporter / Antigen mRNA")
    flow_rate_ratio_aqueous_to_organic = Column(Float, nullable=False, default=3.0)
    total_flow_rate_ml_min = Column(Float, nullable=False, default=12.0)
    nitrogen_to_phosphate_np_ratio = Column(Float, nullable=False, default=6.0)
    hydrodynamic_diameter_pdi = Column(Float, nullable=False, default=0.08)
    particle_size_z_avg_nm = Column(Float, nullable=False, default=74.5)
    encapsulation_efficiency_percent = Column(Float, nullable=False, default=94.2)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lipid_components = relationship(
        "DBLipidRatioComponent",
        back_populates="formulation",
        cascade="all, delete-orphan",
    )
    efficiency_metrics = relationship(
        "DBEncapsulationEfficiencyMetric",
        back_populates="formulation",
        cascade="all, delete-orphan",
    )


class DBLipidRatioComponent(Base):
    __tablename__ = "lipid_ratio_components"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    formulation_id = Column(GUID, ForeignKey("lnp_formulation_screens.id", ondelete="CASCADE"), nullable=False, index=True)
    lipid_type = Column(String(100), nullable=False)  # "Ionizable Lipid (SM-102 / ALC-0315)", "Helper Lipid (DSPC)", "Cholesterol", "PEG-Lipid"
    mol_percent = Column(Float, nullable=False)  # e.g. 50.0, 10.0, 38.5, 1.5
    pka_apparent = Column(Float, nullable=True)  # e.g. 6.68
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    formulation = relationship("DBLNPFormulationScreen", back_populates="lipid_components")


class DBEncapsulationEfficiencyMetric(Base):
    __tablename__ = "encapsulation_efficiency_metrics"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    formulation_id = Column(GUID, ForeignKey("lnp_formulation_screens.id", ondelete="CASCADE"), nullable=False, index=True)
    ribogreen_free_rna_fluorescence = Column(Float, nullable=False)
    ribogreen_total_rna_fluorescence = Column(Float, nullable=False)
    calculated_encapsulation_percent = Column(Float, nullable=False)
    cryo_tem_morphology = Column(String(100), nullable=False, default="Homogeneous Electron-Dense Core")
    in_vivo_transfection_potency_fold = Column(Float, nullable=False, default=8.2)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    formulation = relationship("DBLNPFormulationScreen", back_populates="efficiency_metrics")
