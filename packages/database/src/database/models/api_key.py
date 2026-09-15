"""
Developer API Key Database Model (Phase 25).
Supports granular scopes, tier-based rate limiting, and SHA-256 hashed storage.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base
from database.models.memory import GUID, JSONType


class DBApiKey(Base):
    """
    Developer API Key for public programmatic access to the AI Research OS.
    Stores only the SHA-256 hash and a safe prefix for UI masking.
    """
    __tablename__ = "api_keys"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id: Mapped[Optional[UUID]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # e.g. "amrp_live_a1b2"
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)   # SHA-256 of raw secret
    
    scopes: Mapped[List[str]] = mapped_column(JSONType, nullable=False, default=lambda: ["research:read", "research:write", "documents:read"])
    rate_limit_tier: Mapped[str] = mapped_column(String(50), nullable=False, default="free")  # free, pro, enterprise
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "name": self.name,
            "key_prefix": self.key_prefix,
            "masked_key": f"{self.key_prefix}...{self.key_hash[-4:]}",
            "scopes": self.scopes,
            "rate_limit_tier": self.rate_limit_tier,
            "rate_limit_rpm": self.rate_limit_rpm,
            "is_active": self.is_active,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
