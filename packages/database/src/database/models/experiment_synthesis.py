"""Autonomous AI Lab Co-Pilot & Centennial Synthesis Core Database Models (Phase 100)."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBAutonomousExperimentSynthesis(Base):
    __tablename__ = "autonomous_experiment_syntheses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    campaign_title = Column(String(255), nullable=False)
    scientific_domain = Column(String(100), nullable=False)  # e.g., Synthetic Biology, Targeted Therapeutics, Material Informatics
    autonomous_state = Column(String(50), default="COMPLETED", nullable=False)  # PLANNING, SIMULATING, EXECUTING_ROBOTICS, VERIFYING, PUBLISHING, COMPLETED
    overall_confidence_score = Column(Float, default=96.5, nullable=False)  # 0 to 100
    total_pipeline_stages = Column(Integer, default=5, nullable=False)
    completed_stages_count = Column(Integer, default=5, nullable=False)
    hypothesis_statement = Column(Text, nullable=False)
    synthesis_summary = Column(Text, nullable=False)
    synthesis_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    action_steps = relationship("DBAutonomousActionStep", back_populates="synthesis", cascade="all, delete-orphan")
    verifications = relationship("DBClosedLoopVerificationRecord", back_populates="synthesis", cascade="all, delete-orphan")


class DBAutonomousActionStep(Base):
    __tablename__ = "autonomous_action_steps"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    synthesis_id = Column(GUID(), ForeignKey("autonomous_experiment_syntheses.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    stage_name = Column(String(100), nullable=False)  # Hypothesis Formulation, In-Silico Docking, OT-2 Liquid Dispense, Spectrophotometry Readout, LaTeX Preprint Generation
    agent_persona = Column(String(100), nullable=False)  # Lead Scientist, Simulation Engine, Robotics Dispatcher, QA Validator, Publication Synthesizer
    execution_status = Column(String(50), default="SUCCESS", nullable=False)
    latency_seconds = Column(Float, default=1.85, nullable=False)
    output_summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    synthesis = relationship("DBAutonomousExperimentSynthesis", back_populates="action_steps")


class DBClosedLoopVerificationRecord(Base):
    __tablename__ = "closed_loop_verifications"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    synthesis_id = Column(GUID(), ForeignKey("autonomous_experiment_syntheses.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False)  # Simulated vs Empirical Correlation R^2, Protocol GxP Audit Integrity, Statistical Significance p-value
    expected_value = Column(Float, nullable=False)
    observed_value = Column(Float, nullable=False)
    deviation_pct = Column(Float, default=1.2, nullable=False)
    verification_passed = Column(String(50), default="PASSED", nullable=False)  # PASSED, FAILED, WARNING
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    synthesis = relationship("DBAutonomousExperimentSynthesis", back_populates="verifications")
