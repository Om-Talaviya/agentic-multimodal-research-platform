"""
Phase 50: Autonomous AI Scientist Self-Evolving Research Agent & Nobel-Turing Discovery Engine Models.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID, JSONType


class DBAutonomousScientistProgram(Base):
    __tablename__ = "ai_scientist_programs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(500), nullable=False)
    research_domain = Column(String(255), default="Oncology Systems Immunology")
    goal_statement = Column(Text, nullable=False)
    exploration_mode = Column(String(50), default="EXPLOIT_FRONTIER") # EXPLOIT_FRONTIER, ADVERSARIAL_EXPLORATION, PARADIGM_SHIFT
    max_cycles = Column(Integer, default=5)
    current_cycle = Column(Integer, default=5)
    overall_novelty_score = Column(Float, default=0.94)
    status = Column(String(50), default="BREAKTHROUGH_ACHIEVED") # RUNNING, CONVERGED, BREAKTHROUGH_ACHIEVED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    iteration_cycles = relationship("DBResearchIterationCycle", back_populates="program", cascade="all, delete-orphan")
    breakthroughs = relationship("DBDiscoveryBreakthrough", back_populates="program", cascade="all, delete-orphan")


class DBResearchIterationCycle(Base):
    __tablename__ = "ai_scientist_iteration_cycles"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    program_id = Column(GUID, ForeignKey("ai_scientist_programs.id", ondelete="CASCADE"), nullable=False)
    cycle_index = Column(Integer, nullable=False)
    hypothesis = Column(Text, nullable=False)
    experimental_protocol = Column(Text, nullable=False)
    simulation_metrics = Column(JSONType, default=dict)
    metacognitive_reflection = Column(Text, nullable=False)
    cycle_novelty_delta = Column(Float, default=0.15)
    created_at = Column(DateTime, default=datetime.utcnow)

    program = relationship("DBAutonomousScientistProgram", back_populates="iteration_cycles")


class DBDiscoveryBreakthrough(Base):
    __tablename__ = "ai_scientist_breakthroughs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    program_id = Column(GUID, ForeignKey("ai_scientist_programs.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    breakthrough_class = Column(String(100), default="NOBEL_TURING_CLASS") # NOBEL_TURING_CLASS, MAJOR_DISCOVERY, NOVEL_INSIGHT
    novelty_score = Column(Float, default=0.96)
    empirical_validity_score = Column(Float, default=0.92)
    falsifiability_index = Column(Float, default=0.88)
    formal_conclusion = Column(Text, nullable=False)
    whitepaper_summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    program = relationship("DBAutonomousScientistProgram", back_populates="breakthroughs")
