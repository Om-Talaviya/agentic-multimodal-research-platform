"""AlphaFold Multimeric Complex & Co-Evolutionary Contact Model."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


class DBAlphaFoldComplexStudy(Base):
    """Database model for AlphaFold-Multimer docking and interface contact predictions."""

    __tablename__ = "alphafold_complex_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_name = Column(String(255), nullable=False, index=True)
    target_complex_name = Column(String(128), nullable=False, default="PD-1 / PD-L1 Complex")
    chain_a_name = Column(String(64), nullable=False, default="PDCD1_HUMAN (Chain A)")
    chain_b_name = Column(String(64), nullable=False, default="CD274_HUMAN (Chain B)")
    mean_iptm_score = Column(Float, nullable=False, default=0.88)
    mean_plddt_interface = Column(Float, nullable=False, default=89.4)
    buried_surface_area_angstrom2 = Column(Float, nullable=False, default=1840.5)
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

    contacts = relationship(
        "DBInterfaceContactResidue",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    energy_metrics = relationship(
        "DBInterfaceEnergyMetric",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class DBInterfaceContactResidue(Base):
    """Database model for interface residue-residue contacts and PAE values."""

    __tablename__ = "interface_contact_residues"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("alphafold_complex_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    chain_a_residue = Column(String(32), nullable=False)
    chain_b_residue = Column(String(32), nullable=False)
    inter_residue_distance_angstrom = Column(Float, nullable=False)
    predicted_aligned_error_angstrom = Column(Float, nullable=False)
    interaction_type = Column(String(32), nullable=False, default="hydrogen_bond")
    contact_plddt = Column(Float, nullable=False, default=91.2)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBAlphaFoldComplexStudy", back_populates="contacts")


class DBInterfaceEnergyMetric(Base):
    """Database model for interface binding free energy and solvation decomposition."""

    __tablename__ = "interface_energy_metrics"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("alphafold_complex_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    energy_component = Column(String(64), nullable=False)
    value_kcal_mol = Column(Float, nullable=False)
    favorable_flag = Column(String(16), nullable=False, default="FAVORABLE")
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBAlphaFoldComplexStudy", back_populates="energy_metrics")
