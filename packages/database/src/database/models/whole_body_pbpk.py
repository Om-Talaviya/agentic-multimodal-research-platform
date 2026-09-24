"""Whole-Body PBPK Digital Twin & Trans-Organ Pharmacokinetics Model."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


class DBWholeBodyPBPKStudy(Base):
    """Database model for whole-body physiologically-based pharmacokinetic simulation studies."""

    __tablename__ = "whole_body_pbpk_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_name = Column(String(255), nullable=False, index=True)
    drug_candidate_name = Column(String(255), nullable=False, index=True)
    molecular_weight_da = Column(Float, nullable=False, default=450.0)
    logp = Column(Float, nullable=False, default=2.5)
    plasma_protein_unbound_fraction = Column(Float, nullable=False, default=0.08)
    intrinsic_clearance_ml_min_kg = Column(Float, nullable=False, default=15.0)
    species = Column(String(64), nullable=False, default="human")
    administration_route = Column(String(64), nullable=False, default="oral")
    dose_mg_kg = Column(Float, nullable=False, default=10.0)
    simulation_time_hours = Column(Float, nullable=False, default=24.0)
    status = Column(String(64), nullable=False, default="completed")
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

    organ_compartments = relationship(
        "DBOrganTissueCompartment",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    clearance_rates = relationship(
        "DBTransOrganClearanceRate",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class DBOrganTissueCompartment(Base):
    """Database model for organ tissue compartment kinetics."""

    __tablename__ = "pbpk_organ_tissue_compartments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("whole_body_pbpk_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    organ_name = Column(String(64), nullable=False)
    organ_volume_l_kg = Column(Float, nullable=False)
    blood_flow_rate_l_h_kg = Column(Float, nullable=False)
    tissue_plasma_partition_coefficient = Column(Float, nullable=False)
    permeability_surface_area_product = Column(Float, nullable=False)
    computed_cmax_ug_ml = Column(Float, nullable=False)
    computed_auc_ug_h_ml = Column(Float, nullable=False)
    computed_tmax_h = Column(Float, nullable=False)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBWholeBodyPBPKStudy", back_populates="organ_compartments")


class DBTransOrganClearanceRate(Base):
    """Database model for trans-organ metabolic and renal clearance pathways."""

    __tablename__ = "pbpk_trans_organ_clearance_rates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("whole_body_pbpk_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    elimination_pathway = Column(String(128), nullable=False)
    organ_source = Column(String(64), nullable=False)
    clearance_rate_ml_min = Column(Float, nullable=False)
    extraction_ratio = Column(Float, nullable=False)
    fraction_metabolized = Column(Float, nullable=False)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBWholeBodyPBPKStudy", back_populates="clearance_rates")
