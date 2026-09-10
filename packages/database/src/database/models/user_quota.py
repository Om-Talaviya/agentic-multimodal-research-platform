"""User quota model for rate limits and cost controls."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class UserQuota(Base):
    """User-specific daily token and cost quota limits."""

    __tablename__ = "user_quotas"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    daily_token_limit = Column(Integer, nullable=True)  # NULL = unlimited
    daily_cost_limit = Column(Float, nullable=True)     # NULL = unlimited
    tokens_used_today = Column(Integer, nullable=False, default=0)
    cost_used_today = Column(Float, nullable=False, default=0.0)
    max_concurrent_jobs = Column(Integer, nullable=True) # NULL = unlimited
    last_reset_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
