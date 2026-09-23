"""
Phase 136: Epigenetic Histone Acetylation Dynamics & HAT/HDAC Chromatin Remodeling Database Models.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBHistoneAcetylationModel(Base):
    __tablename__ = "histone_acetylation_models"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, nullable=True, index=True)
    locus_name = Column(String(255), nullable=False, index=True)
    genomic_coordinates = Column(String(255), nullable=False)
    cell_line_or_tissue = Column(String(255), nullable=False)
    initial_h3k27ac_enrichment = Column(Float, nullable=False, default=12.4)
    hdac_inhibitor_name = Column(String(100), nullable=True, default="Vorinostat (SAHA)")
    predicted_enhancer_activation_fold = Column(Float, nullable=False, default=4.8)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    enzyme_kinetics = relationship(
        "DBHATHDACKinetics",
        back_populates="model",
        cascade="all, delete-orphan",
    )
    chromatin_profiles = relationship(
        "DBChromatinOpennessProfile",
        back_populates="model",
        cascade="all, delete-orphan",
    )


class DBHATHDACKinetics(Base):
    __tablename__ = "hat_hdac_kinetics"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    model_id = Column(GUID, ForeignKey("histone_acetylation_models.id", ondelete="CASCADE"), nullable=False, index=True)
    enzyme_type = Column(String(50), nullable=False)  # "HAT (p300/CBP)", "HDAC1/2", "HDAC6"
    catalytic_rate_kcat = Column(Float, nullable=False)  # s^-1
    michaelis_constant_km_um = Column(Float, nullable=False)  # uM
    inhibition_constant_ki_nm = Column(Float, nullable=True)  # nM
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    model = relationship("DBHistoneAcetylationModel", back_populates="enzyme_kinetics")


class DBChromatinOpennessProfile(Base):
    __tablename__ = "chromatin_openness_profiles"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    model_id = Column(GUID, ForeignKey("histone_acetylation_models.id", ondelete="CASCADE"), nullable=False, index=True)
    time_point_hours = Column(Float, nullable=False)
    nucleosome_occupancy_percent = Column(Float, nullable=False)
    atac_seq_peak_intensity_rpm = Column(Float, nullable=False)
    brd4_bromodomain_recruitment = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    model = relationship("DBHistoneAcetylationModel", back_populates="chromatin_profiles")
