"""Database models for Multimodal Scientific Presentation and Executive Podcasting Briefing generation."""

from datetime import datetime, timezone
from typing import Optional, List
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from database.connection import Base
from database.models.memory import GUID

JSONType = JSON().with_variant(JSONB, "postgresql")


class DBSynthesisPresentation(Base):
    """Represents a generated slide deck presentation from research findings."""

    __tablename__ = "synthesis_presentations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    research_job_id = Column(
        GUID(),
        ForeignKey("research_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    workspace_id = Column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    project_id = Column(
        GUID(),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title = Column(String(500), nullable=False)
    subtitle = Column(String(500), nullable=True)
    target_audience = Column(String(100), nullable=False, default="executive")  # executive, scientific, technical, general
    theme = Column(String(50), nullable=False, default="midnight_slate")  # midnight_slate, obsidian_glow, modern_clean
    estimated_duration_min = Column(Integer, nullable=False, default=15)
    total_slides = Column(Integer, nullable=False, default=0)

    metadata_json = Column(JSONType, nullable=False, default=dict)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    slides = relationship(
        "DBPresentationSlide",
        back_populates="presentation",
        cascade="all, delete-orphan",
        order_by="DBPresentationSlide.slide_number.asc()",
    )


class DBPresentationSlide(Base):
    """Represents an individual slide within a presentation deck."""

    __tablename__ = "presentation_slides"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    presentation_id = Column(
        GUID(),
        ForeignKey("synthesis_presentations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    slide_number = Column(Integer, nullable=False, default=1)
    layout_type = Column(String(50), nullable=False, default="bullet_points")  # title, bullet_points, two_column, chart_comparison, callout_quote
    headline = Column(String(300), nullable=False)
    bullet_points = Column(JSONType, nullable=False, default=list)  # List of strings / structured cards
    speaker_notes = Column(Text, nullable=True)
    visual_metadata = Column(JSONType, nullable=False, default=dict)  # {chart_type, citation_ref, badge_text}

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    presentation = relationship("DBSynthesisPresentation", back_populates="slides")


class DBPodcastBriefing(Base):
    """Represents a multi-speaker scientific audio briefing / podcast dialogue."""

    __tablename__ = "podcast_briefings"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    research_job_id = Column(
        GUID(),
        ForeignKey("research_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    workspace_id = Column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    project_id = Column(
        GUID(),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title = Column(String(500), nullable=False)
    episode_topic = Column(Text, nullable=False)
    host_name = Column(String(100), nullable=False, default="Dr. Elena Vance (Host)")
    expert_name = Column(String(100), nullable=False, default="Prof. Marcus Sterling (Specialist)")
    
    total_duration_sec = Column(Float, nullable=False, default=0.0)
    total_dialogue_turns = Column(Integer, nullable=False, default=0)

    # Chronological dialogue lines: [{speaker, text, audio_cue, timestamp_start_sec, timestamp_end_sec}]
    dialogue_transcript_json = Column(JSONType, nullable=False, default=list)
    audio_url = Column(String(1000), nullable=True)
    status = Column(String(50), nullable=False, default="synthesized")  # synthesized, rendered, failed

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

