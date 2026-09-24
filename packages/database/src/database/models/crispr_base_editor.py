"""
SQLAlchemy Models for Phase 164: CRISPR Base Editing Bystander Mutation Risk & Nucleotide Transition Forecaster.
"""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from database.connection import Base
from database.models.memory import GUID
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBCRISPRBaseEditorStudy(Base):
    __tablename__ = "crispr_base_editor_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), nullable=True, index=True)
    target_gene = Column(String(100), nullable=False)
    editor_type = Column(String(50), default="ABE8e")  # ABE, CBE, dual-BE
    protospacer_sequence = Column(String(50), nullable=False)
    pam_sequence = Column(String(10), default="NGG")
    on_target_conversion_efficiency = Column(Float, nullable=False)
    bystander_purity_score = Column(Float, nullable=False)
    indel_frequency_percent = Column(Float, default=0.05)
    created_at = Column(DateTime, default=utc_now)

    transitions = relationship(
        "DBTargetNucleotideTransition",
        back_populates="study",
        cascade="all, delete-orphan",
    )
    bystander_windows = relationship(
        "DBBystanderEditingWindow",
        back_populates="study",
        cascade="all, delete-orphan",
    )


class DBTargetNucleotideTransition(Base):
    __tablename__ = "target_nucleotide_transitions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("crispr_base_editor_studies.id"), nullable=False, index=True)
    protospacer_position = Column(Integer, nullable=False)
    initial_base = Column(String(5), nullable=False)
    target_base = Column(String(5), nullable=False)
    transition_efficiency = Column(Float, nullable=False)
    amino_acid_consequence = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    study = relationship("DBCRISPRBaseEditorStudy", back_populates="transitions")


class DBBystanderEditingWindow(Base):
    __tablename__ = "bystander_editing_windows"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("crispr_base_editor_studies.id"), nullable=False, index=True)
    window_range = Column(String(20), default="Positions 4-8")
    bystander_count = Column(Integer, default=0)
    unintended_mutation_risk_percent = Column(Float, default=0.0)
    mitigation_strategy = Column(String(255), default="Use narrow-window deaminase variant (e.g., evoCDA-narrow)")
    created_at = Column(DateTime, default=utc_now)

    study = relationship("DBCRISPRBaseEditorStudy", back_populates="bystander_windows")
