"""
Phase 48: Autonomous Multi-Omics Pathway Perturbation & Causal Signaling Simulator Models.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID, JSONType


class DBMultiOmicsExperiment(Base):
    __tablename__ = "pathway_multiomics_experiments"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(500), nullable=False)
    cell_line = Column(String(100), default="A549 (Lung Adenocarcinoma)")
    perturbation_type = Column(String(100), default="CRISPR_KO") # CRISPR_KO, SMALL_MOLECULE, SIRNA, RADIOTHERAPY
    omics_layers = Column(JSONType, default=lambda: ["Transcriptomics", "Phospho-Proteomics", "Metabolomics"])
    status = Column(String(50), default="SIMULATED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cascades = relationship("DBPathwayCascade", back_populates="experiment", cascade="all, delete-orphan")
    simulations = relationship("DBPerturbationSimulation", back_populates="experiment", cascade="all, delete-orphan")


class DBPathwayCascade(Base):
    __tablename__ = "pathway_signaling_cascades"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID, ForeignKey("pathway_multiomics_experiments.id", ondelete="CASCADE"), nullable=False)
    pathway_name = Column(String(255), nullable=False) # MAPK/ERK, PI3K/AKT/mTOR, JAK/STAT
    node_count = Column(Integer, default=18)
    feedback_loops_count = Column(Integer, default=3)
    steady_state_activation = Column(Float, default=0.74) # 0.0 to 1.0
    cascade_topology = Column(JSONType, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("DBMultiOmicsExperiment", back_populates="cascades")


class DBPerturbationSimulation(Base):
    __tablename__ = "pathway_perturbation_simulations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID, ForeignKey("pathway_multiomics_experiments.id", ondelete="CASCADE"), nullable=False)
    target_node = Column(String(100), nullable=False) # e.g. KRAS_G12C, EGFR, BRAF_V600E
    inhibition_efficiency_pct = Column(Float, default=92.5)
    downstream_phospho_delta_pct = Column(Float, default=-78.4)
    metabolic_flux_shift_pct = Column(Float, default=-44.2)
    time_course_hours = Column(Integer, default=48)
    time_series_trajectories = Column(JSONType, default=list) # ODE points
    bypass_resistance_mechanisms = Column(JSONType, default=list) # [{pathway: 'PI3K', upregulation_pct: 35.2}]
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("DBMultiOmicsExperiment", back_populates="simulations")
