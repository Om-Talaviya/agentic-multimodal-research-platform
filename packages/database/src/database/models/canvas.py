"""SQLAlchemy models for Real-Time Multi-Agent Collaborative Research Canvas & Visual Ideation Studio."""

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


class DBCanvasBoard(Base):
    """Represents an infinite 2D research canvas for visual node ideation and evidence linking."""

    __tablename__ = "canvas_boards"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True, index=True)
    workspace_id = Column(GUID(), nullable=True, index=True)
    project_id = Column(GUID(), nullable=True, index=True)
    research_job_id = Column(GUID(), nullable=True, index=True)

    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    viewport_state = Column(JSONType, default=lambda: {"zoom": 1.0, "pan_x": 0.0, "pan_y": 0.0}, nullable=False)
    background_grid = Column(String(64), default="dots", nullable=False)  # dots, lines, crosses, clean
    status = Column(String(64), default="active", nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    nodes = relationship("DBCanvasNode", back_populates="canvas", cascade="all, delete-orphan", order_by="DBCanvasNode.created_at")
    edges = relationship("DBCanvasEdge", back_populates="canvas", cascade="all, delete-orphan", order_by="DBCanvasEdge.created_at")


class DBCanvasNode(Base):
    """Represents a visual research node (Hypothesis, Evidence, Paper, Agent Thought, Conclusion)."""

    __tablename__ = "canvas_nodes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    canvas_id = Column(GUID(), ForeignKey("canvas_boards.id", ondelete="CASCADE"), nullable=False, index=True)

    node_type = Column(String(64), default="hypothesis", nullable=False)
    # hypothesis, evidence, paper, agent_thought, data_series, conclusion, counter_claim

    title = Column(String(512), nullable=False)
    content = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.85, nullable=False)
    status = Column(String(64), default="verified", nullable=False)  # draft, verified, disputed, inconclusive

    position_x = Column(Float, default=0.0, nullable=False)
    position_y = Column(Float, default=0.0, nullable=False)
    width = Column(Float, default=280.0, nullable=False)
    height = Column(Float, default=160.0, nullable=False)

    color_accent = Column(String(64), default="#3b82f6", nullable=False)
    metadata_json = Column(JSONType, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    canvas = relationship("DBCanvasBoard", back_populates="nodes")


class DBCanvasEdge(Base):
    """Represents a directed or bidirectional relational link between canvas nodes."""

    __tablename__ = "canvas_edges"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    canvas_id = Column(GUID(), ForeignKey("canvas_boards.id", ondelete="CASCADE"), nullable=False, index=True)

    source_node_id = Column(GUID(), ForeignKey("canvas_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_node_id = Column(GUID(), ForeignKey("canvas_nodes.id", ondelete="CASCADE"), nullable=False, index=True)

    relation_type = Column(String(64), default="supports", nullable=False)
    # supports, refutes, derives_from, correlates_with, branches_to, questions

    label = Column(String(256), nullable=True)
    weight = Column(Float, default=1.0, nullable=False)
    metadata_json = Column(JSONType, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    canvas = relationship("DBCanvasBoard", back_populates="edges")
