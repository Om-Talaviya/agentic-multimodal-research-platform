"""SQLAlchemy models for Synthetic Instruction Dataset Generation & Active Learning Engine."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from database.connection import Base
from database.models.memory import GUID

JSONType = JSON().with_variant(JSONB, "postgresql")


class DBSyntheticDataset(Base):
    """Represents a curated synthetic instruction tuning dataset."""

    __tablename__ = "synthetic_datasets"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True, index=True)
    workspace_id = Column(GUID(), nullable=True, index=True)
    project_id = Column(GUID(), nullable=True, index=True)
    research_job_id = Column(GUID(), nullable=True, index=True)

    name = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    dataset_format = Column(String(64), default="alpaca_sft", nullable=False)
    # alpaca_sft, sharegpt, dpo_preference, rl_trajectory, cot_reasoning

    domain_field = Column(String(128), default="general_science", nullable=False)
    target_model_family = Column(String(128), default="llama_3", nullable=False)
    total_samples = Column(Integer, default=0, nullable=False)
    quality_filter_threshold = Column(Float, default=0.80, nullable=False)
    status = Column(String(64), default="draft", nullable=False, index=True)
    # draft, synthesizing, curated, exported, archived

    stats_metadata = Column(JSONType, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    samples = relationship("DBInstructionSample", back_populates="dataset", cascade="all, delete-orphan", order_by="DBInstructionSample.sample_index")
    exports = relationship("DBAlignmentExport", back_populates="dataset", cascade="all, delete-orphan", order_by="DBAlignmentExport.exported_at")


class DBInstructionSample(Base):
    """Represents a single synthesized instruction-response sample or preference pair."""

    __tablename__ = "instruction_samples"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(GUID(), ForeignKey("synthetic_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    sample_index = Column(Integer, default=0, nullable=False)

    system_prompt = Column(Text, nullable=True)
    instruction = Column(Text, nullable=False)
    input_context = Column(Text, nullable=True)
    chosen_response = Column(Text, nullable=False)
    rejected_response = Column(Text, nullable=True)  # Populated for DPO preference pairs
    cot_reasoning_trace = Column(Text, nullable=True)

    evolution_strategy = Column(String(64), default="direct_synthesis", nullable=False)
    # direct_synthesis, in_depth_expansion, in_breadth_variation, constraint_hardening, adversarial_redteaming, cot_decomposition

    quality_score = Column(Float, default=0.88, nullable=False)
    toxicity_score = Column(Float, default=0.01, nullable=False)
    hallucination_risk = Column(Float, default=0.05, nullable=False)
    dedup_hash = Column(String(64), nullable=True, index=True)
    curation_verdict = Column(String(64), default="accepted", nullable=False)
    # accepted, rejected, edited

    metadata_json = Column(JSONType, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    dataset = relationship("DBSyntheticDataset", back_populates="samples")


class DBAlignmentExport(Base):
    """Represents an exported dataset snapshot in standardized fine-tuning formats."""

    __tablename__ = "alignment_exports"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(GUID(), ForeignKey("synthetic_datasets.id", ondelete="CASCADE"), nullable=False, index=True)

    export_format = Column(String(64), default="jsonl", nullable=False)
    # jsonl, parquet, huggingface_arrow, csv
    export_path = Column(String(512), nullable=True)
    sample_count = Column(Integer, default=0, nullable=False)
    file_size_bytes = Column(Integer, default=0, nullable=False)
    exported_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    dataset = relationship("DBSyntheticDataset", back_populates="exports")
