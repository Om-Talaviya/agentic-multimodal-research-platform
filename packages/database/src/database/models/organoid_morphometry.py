"""Phase 147: 3D Tumor Organoid High-Content Morphometry Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBOrganoidMorphometryStudy(Base):
    """3D Tumor Organoid morphometry and volumetric profiling study."""

    __tablename__ = "organoid_morphometry_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_name = Column(String(255), nullable=False)
    tumor_type = Column(String(120), nullable=False)
    organoid_count = Column(Integer, default=1, nullable=False)
    mean_diameter_um = Column(Float, default=0.0)
    mean_volume_um3 = Column(Float, default=0.0)
    sphericity_index = Column(Float, default=0.0)
    necrotic_core_ratio = Column(Float, default=0.0)
    hypoxia_gradient_slope = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    z_stacks = relationship("DBOrganoidZStackProfile", back_populates="study", cascade="all, delete-orphan")
    dose_responses = relationship("DBOrganoidDrugDoseResponse", back_populates="study", cascade="all, delete-orphan")


class DBOrganoidZStackProfile(Base):
    """Optical confocal Z-slice cross-section data."""

    __tablename__ = "organoid_z_stack_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("organoid_morphometry_studies.id", ondelete="CASCADE"), nullable=False)
    slice_depth_um = Column(Float, nullable=False)
    cross_sectional_area_um2 = Column(Float, nullable=False)
    circularity = Column(Float, nullable=False)
    fluorescence_intensity = Column(Float, nullable=False)
    live_dead_ratio = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBOrganoidMorphometryStudy", back_populates="z_stacks")


class DBOrganoidDrugDoseResponse(Base):
    """Compound viability and invasion response curve point."""

    __tablename__ = "organoid_drug_dose_responses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("organoid_morphometry_studies.id", ondelete="CASCADE"), nullable=False)
    compound_name = Column(String(120), nullable=False)
    dose_uM = Column(Float, nullable=False)
    viability_pct = Column(Float, nullable=False)
    invasion_inhibition_pct = Column(Float, nullable=False)
    computed_ic50_uM = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBOrganoidMorphometryStudy", back_populates="dose_responses")
