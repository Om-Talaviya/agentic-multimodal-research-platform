"""HDX-MS Conformational Dynamics & Epitope Mapping Model."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


class DBHDXMSEpitopeStudy(Base):
    """Database model for HDX-MS conformational dynamics and conformational epitope mapping."""

    __tablename__ = "hdx_ms_epitope_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_name = Column(String(255), nullable=False, index=True)
    target_protein_name = Column(String(128), nullable=False, default="Spike RBD / Neutralizing mAb")
    peptides_monitored_count = Column(Integer, nullable=False, default=4)
    mean_deuteration_protection_pct = Column(Float, nullable=False, default=42.8)
    epitope_region_identified = Column(String(128), nullable=False, default="Residues 470-492 (RBD Receptor Binding Loop)")
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

    peptides = relationship(
        "DBPeptideDeuterationProfile",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    hotspots = relationship(
        "DBEpitopeProtectionHotspot",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class DBPeptideDeuterationProfile(Base):
    """Database model for individual peptic fragments across HDX timepoints."""

    __tablename__ = "peptide_deuteration_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("hdx_ms_epitope_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    peptide_sequence = Column(String(64), nullable=False)
    start_residue = Column(Integer, nullable=False)
    end_residue = Column(Integer, nullable=False)
    deuterium_uptake_apo_pct = Column(Float, nullable=False)
    deuterium_uptake_bound_pct = Column(Float, nullable=False)
    delta_deuterium_protection_pct = Column(Float, nullable=False)
    confidence_p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBHDXMSEpitopeStudy", back_populates="peptides")


class DBEpitopeProtectionHotspot(Base):
    """Database model for consolidated conformational epitope binding residues."""

    __tablename__ = "epitope_protection_hotspots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("hdx_ms_epitope_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    residue_name = Column(String(32), nullable=False)
    protection_factor_log2 = Column(Float, nullable=False)
    solvent_accessibility_change = Column(String(32), nullable=False, default="buried_upon_binding")
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBHDXMSEpitopeStudy", back_populates="hotspots")
