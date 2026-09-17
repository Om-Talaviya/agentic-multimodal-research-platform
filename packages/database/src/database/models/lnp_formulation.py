"""Synthetic Cell Membrane Dynamics & LNP Formulation Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class DBLNPFormulationStudy(Base):
    __tablename__ = "lnp_formulation_studies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    formulation_name = Column(String(255), nullable=False)
    cargo_type = Column(String(64), default="mRNA")
    ionizable_lipid_name = Column(String(128), default="ALC-0315")
    lipid_ratio_molar_json = Column(JSON, default=dict)
    np_ratio = Column(Float, default=6.0)
    encapsulation_efficiency_pct = Column(Float, default=94.5)
    mean_diameter_nm = Column(Float, default=78.2)
    pdi_polydispersity_index = Column(Float, default=0.12)
    zeta_potential_mv = Column(Float, default=2.4)
    apparent_pka = Column(Float, default=6.45)
    simulation_metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    components = relationship("DBLNPLipidComponent", back_populates="formulation", cascade="all, delete-orphan")
    membrane_profiles = relationship("DBMembraneDynamicsProfile", back_populates="formulation", cascade="all, delete-orphan")


class DBLNPLipidComponent(Base):
    __tablename__ = "lnp_lipid_components"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    formulation_id = Column(String(36), ForeignKey("lnp_formulation_studies.id", ondelete="CASCADE"), nullable=False)
    component_name = Column(String(128), nullable=False)
    lipid_category = Column(String(64), nullable=False)
    molar_percentage = Column(Float, default=50.0)
    molecular_weight_g_mol = Column(Float, default=700.0)
    charge_at_ph7 = Column(Float, default=0.0)

    formulation = relationship("DBLNPFormulationStudy", back_populates="components")


class DBMembraneDynamicsProfile(Base):
    __tablename__ = "lnp_membrane_dynamics_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    formulation_id = Column(String(36), ForeignKey("lnp_formulation_studies.id", ondelete="CASCADE"), nullable=False)
    membrane_thickness_angstrom = Column(Float, default=39.5)
    area_per_lipid_angstrom2 = Column(Float, default=62.4)
    order_parameter_s2 = Column(Float, default=0.22)
    bending_modulus_kc_kbt = Column(Float, default=24.5)
    endosomal_escape_efficiency_pct = Column(Float, default=18.5)
    cytotoxicity_score = Column(Float, default=0.15)

    formulation = relationship("DBLNPFormulationStudy", back_populates="membrane_profiles")
