"""Usage record model for telemetry and cost tracking."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class UsageRecord(Base):
    """Granular model API usage telemetry and cost record."""

    __tablename__ = "usage_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    job_id = Column(GUID(), ForeignKey("research_jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    request_type = Column(String(50), nullable=False, default="complete")
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    cost_usd = Column(Float, nullable=False, default=0.0)
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
