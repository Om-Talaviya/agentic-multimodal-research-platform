"""
Phase 47: Autonomous Cryo-EM Density Map Fitting & Macromolecular Complex Modeling Models.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID, JSONType


class DBCryoEMDensityMap(Base):
    __tablename__ = "cryoem_density_maps"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(500), nullable=False)
    emdb_id = Column(String(50), default="EMD-30452")
    nominal_resolution_angstrom = Column(Float, default=2.4)
    voxel_size_angstrom = Column(Float, default=0.82)
    box_dimensions = Column(String(50), default="256x256x256")
    contour_level = Column(Float, default=0.035)
    fsc_resolution_threshold = Column(Float, default=2.35)
    fsc_curve_data = Column(JSONType, default=list)
    status = Column(String(50), default="FITTED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    fittings = relationship("DBDensityMapFitting", back_populates="density_map", cascade="all, delete-orphan")
    complexes = relationship("DBMacromolecularComplex", back_populates="density_map", cascade="all, delete-orphan")


class DBDensityMapFitting(Base):
    __tablename__ = "cryoem_map_fittings"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    density_map_id = Column(GUID, ForeignKey("cryoem_density_maps.id", ondelete="CASCADE"), nullable=False)
    pdb_model_id = Column(String(50), default="7KRR")
    cross_correlation_coefficient = Column(Float, default=0.885)
    molprobity_clashscore = Column(Float, default=2.1)
    ramachandran_favored_pct = Column(Float, default=97.8)
    rotamer_outliers_pct = Column(Float, default=0.4)
    alpha_helices_count = Column(Integer, default=24)
    beta_sheets_count = Column(Integer, default=18)
    fitting_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    density_map = relationship("DBCryoEMDensityMap", back_populates="fittings")


class DBMacromolecularComplex(Base):
    __tablename__ = "cryoem_macromolecular_complexes"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    density_map_id = Column(GUID, ForeignKey("cryoem_density_maps.id", ondelete="CASCADE"), nullable=False)
    complex_name = Column(String(255), nullable=False)
    stoichiometry = Column(String(100), default="A2B2C1")
    buried_surface_area_angstrom2 = Column(Float, default=3450.0)
    binding_free_energy_delta_g = Column(Float, default=-14.2)
    interface_residue_count = Column(Integer, default=64)
    interaction_hotspots = Column(JSONType, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    density_map = relationship("DBCryoEMDensityMap", back_populates="complexes")
