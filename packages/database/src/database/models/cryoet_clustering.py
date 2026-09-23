"""
Phase 133: Autonomous Cryo-ET Cellular Subtomogram Deep Clustering & In-Situ Macromolecular Structure Solver Models.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBCryoETSubtomogramStudy(Base):
    """Represents a Cryo-ET subtomogram averaging & deep learning particle clustering study."""

    __tablename__ = "cryoet_subtomogram_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(String(100), nullable=True)
    study_name = Column(String(200), nullable=False, index=True)
    cellular_organism = Column(String(150), nullable=False)
    tilt_series_count = Column(Integer, default=45, nullable=False)
    total_subtomograms_extracted = Column(Integer, default=12500, nullable=False)
    voxel_size_angstrom = Column(Float, default=1.35, nullable=False)
    mean_resolution_angstrom = Column(Float, default=3.2, nullable=False)
    metadata_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    volumes = relationship(
        "DBSubtomogramVolume",
        back_populates="study",
        cascade="all, delete-orphan",
        order_by="DBSubtomogramVolume.created_at",
    )
    clusters = relationship(
        "DBInSituMacromoleculeCluster",
        back_populates="study",
        cascade="all, delete-orphan",
        order_by="DBInSituMacromoleculeCluster.created_at",
    )


class DBSubtomogramVolume(Base):
    """Represents an extracted 3D subtomogram box with 3D coordinates in the cellular tomogram."""

    __tablename__ = "subtomogram_volumes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("cryoet_subtomogram_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    volume_tag = Column(String(100), nullable=False)
    tomogram_id = Column(String(100), nullable=False)
    coord_x = Column(Float, nullable=False)
    coord_y = Column(Float, nullable=False)
    coord_z = Column(Float, nullable=False)
    signal_to_noise_ratio = Column(Float, default=1.85, nullable=False)
    cross_correlation_score = Column(Float, default=0.82, nullable=False)
    assigned_cluster = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    study = relationship("DBCryoETSubtomogramStudy", back_populates="volumes")


class DBInSituMacromoleculeCluster(Base):
    """Represents a discrete macromolecular species identified via 3D deep contrastive embedding."""

    __tablename__ = "insitu_macromolecule_clusters"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("cryoet_subtomogram_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    cluster_label = Column(String(100), nullable=False)
    macromolecule_identity = Column(String(150), nullable=False)  # e.g., "70S Ribosome", "Proteasome 26S", "Nuclear Pore Complex"
    particle_count = Column(Integer, default=1200, nullable=False)
    fsc_resolution_angstrom = Column(Float, default=3.4, nullable=False)
    b_factor_sharpening = Column(Float, default=-85.0, nullable=False)
    conformational_state = Column(String(100), default="Rotational Ground State", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    study = relationship("DBCryoETSubtomogramStudy", back_populates="clusters")
