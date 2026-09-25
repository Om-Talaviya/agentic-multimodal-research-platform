"""Cryo-ET Subtomogram Averaging & In-Situ Macromolecular Structure Model."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


class DBCryoETTomogramStudy(Base):
    """Database model for 3D Cryo-ET subtomogram averaging reconstructions."""

    __tablename__ = "cryoet_tomography_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_name = Column(String(255), nullable=False, index=True)
    cellular_context = Column(String(128), nullable=False, default="Intact Neuronal Synapse (In-Situ)")
    target_complex_name = Column(String(128), nullable=False, default="AMPAR-TARP Ion Channel Complex")
    particles_picked_count = Column(Integer, nullable=False, default=4)
    final_fsc_resolution_angstrom = Column(Float, nullable=False, default=3.42)
    angular_search_step_deg = Column(Float, nullable=False, default=3.75)
    summary_metrics = Column(JSON, nullable=True)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )
    updated_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    particles = relationship(
        "DBCryoETSubtomogramParticle",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    classes = relationship(
        "DBCryoETResolutionClass",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class DBCryoETSubtomogramParticle(Base):
    """Database model for individual subtomogram 3D volume extractions."""

    __tablename__ = "cryoet_tomography_particles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("cryoet_tomography_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    particle_id_str = Column(String(64), nullable=False)
    x_vox = Column(Float, nullable=False)
    y_vox = Column(Float, nullable=False)
    z_vox = Column(Float, nullable=False)
    euler_rot_deg = Column(Float, nullable=False)
    euler_tilt_deg = Column(Float, nullable=False)
    euler_psi_deg = Column(Float, nullable=False)
    cross_correlation_score = Column(Float, nullable=False)
    conformational_state = Column(String(32), nullable=False, default="Resting Closed")
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBCryoETTomogramStudy", back_populates="particles")


class DBCryoETResolutionClass(Base):
    """Database model for 3D class averages and FSC gold-standard resolution curves."""

    __tablename__ = "cryoet_tomography_classes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("cryoet_tomography_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    class_number = Column(Integer, nullable=False)
    class_name = Column(String(64), nullable=False)
    particle_occupancy_pct = Column(Float, nullable=False)
    resolution_angstrom = Column(Float, nullable=False)
    fsc_cutoff_type = Column(String(32), nullable=False, default="FSC_0.143_GoldStandard")
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBCryoETTomogramStudy", back_populates="classes")
