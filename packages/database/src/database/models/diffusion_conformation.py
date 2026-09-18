"""Multi-Modal Diffusion 3D Protein-Ligand Complex Conformation Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database.connection import Base


class DBDiffusionComplexJob(Base):
    __tablename__ = "diffusion_complex_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    protein_pdb_id = Column(String(32), nullable=False)
    ligand_smiles = Column(String(512), nullable=False)
    diffusion_model_variant = Column(String(64), default="DiffDock_SE3")
    num_diffusion_timesteps = Column(Integer, default=1000)
    sampling_temperature = Column(Float, default=1.0)
    total_conformations_generated = Column(Integer, default=5)
    best_confidence_score = Column(Float, default=0.942)
    status = Column(String(32), default="COMPLETED")
    job_metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    pocket_conformations = relationship("DBDiffusionPocketConformation", back_populates="job", cascade="all, delete-orphan")
    docking_poses = relationship("DBEquivariantDockingPose", back_populates="job", cascade="all, delete-orphan")


class DBDiffusionPocketConformation(Base):
    __tablename__ = "diffusion_pocket_conformations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("diffusion_complex_jobs.id", ondelete="CASCADE"), nullable=False)
    conformation_rank = Column(Integer, default=1)
    pocket_center_x = Column(Float, default=12.45)
    pocket_center_y = Column(Float, default=-4.20)
    pocket_center_z = Column(Float, default=28.15)
    pocket_volume_angstrom3 = Column(Float, default=485.6)
    cavity_druggability_score = Column(Float, default=0.88)
    clash_penalty_score = Column(Float, default=0.04)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("DBDiffusionComplexJob", back_populates="pocket_conformations")


class DBEquivariantDockingPose(Base):
    __tablename__ = "equivariant_docking_poses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("diffusion_complex_jobs.id", ondelete="CASCADE"), nullable=False)
    pose_rank = Column(Integer, default=1)
    rmsd_to_centroid_angstrom = Column(Float, default=0.82)
    vina_affinity_score = Column(Float, default=-9.45)
    se3_confidence_score = Column(Float, default=0.942)
    num_h_bonds = Column(Integer, default=4)
    contact_surface_area_angstrom2 = Column(Float, default=320.5)
    ligand_coordinates_pdb = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("DBDiffusionComplexJob", back_populates="docking_poses")
