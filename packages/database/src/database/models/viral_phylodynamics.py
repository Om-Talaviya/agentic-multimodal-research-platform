"""
Phase 132: Global Pandemic Biosurveillance & Multi-Strain Viral Lineage Phylodynamics Models.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBViralSurveillanceStudy(Base):
    """Represents a global viral genomic surveillance & phylodynamics study."""

    __tablename__ = "viral_surveillance_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(String(100), nullable=True)
    pathogen_name = Column(String(200), nullable=False, index=True)
    genome_type = Column(String(100), nullable=False, default="ssRNA(+)")
    geographic_regions = Column(JSON, nullable=False, default=list)  # list of regions/continents
    total_genomes_sequenced = Column(Integer, default=50000, nullable=False)
    effective_reproduction_number_rt = Column(Float, default=1.35, nullable=False)
    transmission_fitness_gain_pct = Column(Float, default=24.5, nullable=False)
    metadata_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    lineages = relationship(
        "DBPhylodynamicLineage",
        back_populates="study",
        cascade="all, delete-orphan",
        order_by="DBPhylodynamicLineage.created_at",
    )
    fitness_profiles = relationship(
        "DBStrainTransmissionFitness",
        back_populates="study",
        cascade="all, delete-orphan",
        order_by="DBStrainTransmissionFitness.created_at",
    )


class DBPhylodynamicLineage(Base):
    """Represents a phylogenetic clade / lineage under active epidemiological tracking."""

    __tablename__ = "phylodynamic_lineages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("viral_surveillance_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    lineage_clade = Column(String(100), nullable=False)
    pangolin_designation = Column(String(100), nullable=False)  # e.g., "JN.1.11.1" or "BA.2.86"
    who_label = Column(String(100), nullable=True)  # e.g., "Omicron" or "Variant Under Monitoring"
    defining_mutations = Column(JSON, nullable=False, default=list)  # list of amino acid mutations e.g., ["S:L455S", "S:F456L"]
    growth_advantage_daily = Column(Float, default=0.08, nullable=False)
    immune_evasion_score = Column(Float, default=0.88, nullable=False)
    global_prevalence_pct = Column(Float, default=42.5, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    study = relationship("DBViralSurveillanceStudy", back_populates="lineages")


class DBStrainTransmissionFitness(Base):
    """Represents transmission dynamics and cross-neutralization resistance measurements."""

    __tablename__ = "strain_transmission_fitness"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("viral_surveillance_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    clade_name = Column(String(100), nullable=False)
    basic_reproduction_number_r0 = Column(Float, default=3.2, nullable=False)
    serial_interval_days = Column(Float, default=3.8, nullable=False)
    ace2_binding_affinity_shift = Column(Float, default=1.45, nullable=False)  # fold change vs ancestral
    cross_neutralization_titer_fold_drop = Column(Float, default=12.5, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    study = relationship("DBViralSurveillanceStudy", back_populates="fitness_profiles")
