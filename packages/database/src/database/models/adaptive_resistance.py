"""SQLAlchemy models for Phase 130: Precision Oncology Adaptive Chemotherapy Resistance & Clonal Fitness Dynamics Simulator."""

from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBAdaptiveResistanceStudy(Base):
    """Represents an adaptive chemotherapy resistance and clonal fitness study."""

    __tablename__ = "adaptive_resistance_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    cancer_type = Column(String(100), nullable=False, index=True)
    patient_id = Column(String(100), nullable=True)
    description = Column(String(1000), nullable=True)
    chemo_regimen = Column(JSON, nullable=False, default=list)  # list of drug regimen configs
    total_cycles = Column(Integer, default=10, nullable=False)
    status = Column(String(50), default="COMPLETED", nullable=False)
    summary_metrics = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    clonal_lineages = relationship(
        "DBClonalFitnessLineage",
        back_populates="study",
        cascade="all, delete-orphan",
        order_by="DBClonalFitnessLineage.created_at",
    )
    resistance_trajectories = relationship(
        "DBDrugResistanceTrajectory",
        back_populates="study",
        cascade="all, delete-orphan",
        order_by="DBDrugResistanceTrajectory.time_step",
    )


class DBClonalFitnessLineage(Base):
    """Represents a specific subclonal lineage with distinct drug fitness & mutations."""

    __tablename__ = "clonal_fitness_lineages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("adaptive_resistance_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    clone_name = Column(String(100), nullable=False)
    driver_mutations = Column(JSON, nullable=False, default=list)  # list of mutated genes/variants
    initial_frequency = Column(Float, nullable=False, default=0.1)
    final_frequency = Column(Float, nullable=False, default=0.1)
    intrinsic_fitness = Column(Float, nullable=False, default=1.0)
    drug_ic50_shifts = Column(JSON, nullable=False, default=dict)  # drug -> fold shift in IC50
    phenotype = Column(String(100), default="SENSITIVE", nullable=False)  # SENSITIVE, TOLERANT, MULTI_DRUG_RESISTANT
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    study = relationship("DBAdaptiveResistanceStudy", back_populates="clonal_lineages")


class DBDrugResistanceTrajectory(Base):
    """Represents longitudinal tumor burden, clonal frequency, and dosing schedule trajectory."""

    __tablename__ = "drug_resistance_trajectories"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("adaptive_resistance_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    time_step = Column(Integer, nullable=False)  # e.g., week / day index
    drug_concentration = Column(Float, nullable=False, default=0.0)
    tumor_burden = Column(Float, nullable=False, default=1.0)  # relative tumor volume/burden
    clone_abundances = Column(JSON, nullable=False, default=dict)  # clone_name -> fraction
    resistance_index = Column(Float, nullable=False, default=0.0)  # weighted resistance score 0.0 - 1.0
    adaptive_recommendation = Column(String(255), nullable=True)  # CONTINUE, DOSE_MODULATE, DRUG_HOLIDAY, SWITCH_REGIMEN
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    study = relationship("DBAdaptiveResistanceStudy", back_populates="resistance_trajectories")
