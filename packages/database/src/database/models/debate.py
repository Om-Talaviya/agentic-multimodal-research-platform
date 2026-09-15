"""Database models for Adversarial Multi-Agent Debate and Consensus Synthesis."""

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


class DBAgentDebate(Base):
    """Represents an adversarial multi-agent research debate session."""

    __tablename__ = "agent_debates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
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

    topic = Column(String(500), nullable=False)
    initial_thesis = Column(Text, nullable=False)
    counter_thesis = Column(Text, nullable=True)

    status = Column(
        String(50),
        nullable=False,
        default="active",
        index=True,
    )  # active, concluded, deadlocked, paused

    max_rounds = Column(Integer, nullable=False, default=3)
    current_round = Column(Integer, nullable=False, default=0)

    proposer_model = Column(String(100), nullable=False, default="gemini-2.5-pro")
    opposer_model = Column(String(100), nullable=False, default="gemini-2.5-pro")
    arbiter_model = Column(String(100), nullable=False, default="gemini-2.5-pro")

    proposer_elo = Column(Float, nullable=False, default=1500.0)
    opposer_elo = Column(Float, nullable=False, default=1500.0)

    config_json = Column(JSONType, nullable=False, default=dict)
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
    rounds = relationship(
        "DBDebateRound",
        back_populates="debate",
        cascade="all, delete-orphan",
        order_by="DBDebateRound.round_number.asc()",
    )
    consensus = relationship(
        "DBDebateConsensus",
        back_populates="debate",
        uselist=False,
        cascade="all, delete-orphan",
    )


class DBDebateRound(Base):
    """Represents a single round of adversarial argument and rebuttal."""

    __tablename__ = "debate_rounds"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    debate_id = Column(
        GUID(),
        ForeignKey("agent_debates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    round_number = Column(Integer, nullable=False, index=True)

    # Proposer turn
    proposer_argument = Column(Text, nullable=False)
    proposer_citations = Column(JSONType, nullable=False, default=list)
    proposer_score = Column(Float, nullable=False, default=0.0)

    # Opposer rebuttal
    opposer_argument = Column(Text, nullable=False)
    opposer_citations = Column(JSONType, nullable=False, default=list)
    opposer_score = Column(Float, nullable=False, default=0.0)

    # Arbiter round evaluation
    arbiter_critique = Column(Text, nullable=True)
    round_winner = Column(String(50), nullable=True)  # proposer, opposer, draw
    elo_delta = Column(Float, nullable=False, default=0.0)
    round_telemetry = Column(JSONType, nullable=False, default=dict)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    debate = relationship("DBAgentDebate", back_populates="rounds")


class DBDebateConsensus(Base):
    """Represents the dialectical consensus synthesized by the arbiter."""

    __tablename__ = "debate_consensus"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    debate_id = Column(
        GUID(),
        ForeignKey("agent_debates.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    consensus_statement = Column(Text, nullable=False)
    accepted_claims = Column(JSONType, nullable=False, default=list)
    refuted_claims = Column(JSONType, nullable=False, default=list)
    concessions = Column(JSONType, nullable=False, default=list)
    remaining_uncertainties = Column(JSONType, nullable=False, default=list)

    overall_confidence = Column(Float, nullable=False, default=0.0)
    winner_overall = Column(String(50), nullable=False, default="balanced_consensus")
    final_proposer_elo = Column(Float, nullable=False, default=1500.0)
    final_opposer_elo = Column(Float, nullable=False, default=1500.0)

    synthesis_metadata = Column(JSONType, nullable=False, default=dict)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    debate = relationship("DBAgentDebate", back_populates="consensus")
