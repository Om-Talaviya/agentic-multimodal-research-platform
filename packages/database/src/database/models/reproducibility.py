"""Database models for In-Silico Experimentation, Computational Reproducibility, and Claim Verification."""

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


class DBExperimentProtocol(Base):
    """Represents an extracted or authored computational experiment protocol."""

    __tablename__ = "experiment_protocols"

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

    name = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    source_paper_title = Column(String(500), nullable=True)
    source_doi = Column(String(200), nullable=True)

    runtime_language = Column(String(50), nullable=False, default="python3")  # python3, julia, r
    executable_code = Column(Text, nullable=False)
    parameters = Column(JSONType, nullable=False, default=dict)  # {param_name: default_value}
    dependencies = Column(JSONType, nullable=False, default=list)  # ['numpy', 'scipy', 'math']
    claimed_metrics = Column(JSONType, nullable=False, default=dict)  # {metric_name: claimed_value}

    verification_status = Column(
        String(50),
        nullable=False,
        default="unverified",
        index=True,
    )  # unverified, fully_reproduced, partially_reproduced, discrepant, failed

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
    runs = relationship(
        "DBReproducibilityRun",
        back_populates="protocol",
        cascade="all, delete-orphan",
        order_by="DBReproducibilityRun.created_at.desc()",
    )
    verification_traces = relationship(
        "DBClaimVerificationTrace",
        back_populates="protocol",
        cascade="all, delete-orphan",
        order_by="DBClaimVerificationTrace.created_at.desc()",
    )


class DBReproducibilityRun(Base):
    """Represents a computational execution run of an experiment protocol."""

    __tablename__ = "reproducibility_runs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(
        GUID(),
        ForeignKey("experiment_protocols.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    executed_by = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )  # pending, running, succeeded, failed, timeout

    execution_time_ms = Column(Float, nullable=False, default=0.0)
    memory_peak_mb = Column(Float, nullable=False, default=0.0)
    reproduced_metrics = Column(JSONType, nullable=False, default=dict)  # {metric_name: actual_value}
    runtime_logs = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    reproducibility_score = Column(Float, nullable=False, default=0.0)  # 0.0 to 1.0 (1.0 = exact match)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    protocol = relationship("DBExperimentProtocol", back_populates="runs")


class DBClaimVerificationTrace(Base):
    """Represents a granular comparison between a claimed scientific metric and reproduced metric."""

    __tablename__ = "claim_verification_traces"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(
        GUID(),
        ForeignKey("experiment_protocols.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_id = Column(
        GUID(),
        ForeignKey("reproducibility_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    claim_statement = Column(String(500), nullable=False)
    metric_name = Column(String(100), nullable=False)
    claimed_value = Column(Float, nullable=False)
    reproduced_value = Column(Float, nullable=False)
    delta_relative_error = Column(Float, nullable=False, default=0.0)  # |claimed - actual| / max(|claimed|, 1e-6)
    tolerance_threshold = Column(Float, nullable=False, default=0.05)  # 5% tolerance default

    verdict = Column(
        String(50),
        nullable=False,
        default="reproduced",
        index=True,
    )  # reproduced, discrepant, refuted, inconclusive

    analysis_notes = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    protocol = relationship("DBExperimentProtocol", back_populates="verification_traces")
