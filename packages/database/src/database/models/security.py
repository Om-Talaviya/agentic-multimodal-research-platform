"""SQLAlchemy database models for Enterprise Security, KMS Secrets, and Audit Logs (Phase 23)."""
from datetime import UTC, datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from database.models.memory import GUID, JSONType


class DBSecurityAuditLog(Base):
    """Immutable, tamper-evident security audit log with cryptographic SHA-256 hash chaining."""

    __tablename__ = "security_audit_logs"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    sequence_id: Mapped[Optional[int]] = mapped_column(Integer, autoincrement=True, nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default="INFO")  # INFO, WARNING, CRITICAL
    actor_id: Mapped[Optional[UUID]] = mapped_column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    workspace_id: Mapped[Optional[UUID]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[Dict[str, Any]] = mapped_column(JSONType, nullable=False, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "event_type": self.event_type,
            "severity": self.severity,
            "actor_id": str(self.actor_id) if self.actor_id else None,
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "action": self.action,
            "details": self.details or {},
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
            "created_at": self.created_at.isoformat(),
        }


class DBEncryptedSecret(Base):
    """Encrypted credential vault using KMS AES-256-GCM envelope encryption."""

    __tablename__ = "encrypted_secrets"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    secret_type: Mapped[str] = mapped_column(String(50), nullable=False)  # api_key, oauth_token, database_uri
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # gemini, openai, anthropic, custom
    key_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1-aes256gcm")
    encrypted_payload: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_dek: Mapped[str] = mapped_column(Text, nullable=False)
    masked_preview: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "sk-...a1b2"
    workspace_id: Mapped[Optional[UUID]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True, index=True)
    created_by: Mapped[Optional[UUID]] = mapped_column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "secret_type": self.secret_type,
            "provider": self.provider,
            "key_version": self.key_version,
            "masked_preview": self.masked_preview,
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "created_by": str(self.created_by) if self.created_by else None,
            "is_revoked": self.is_revoked,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class DBSecurityPolicy(Base):
    """Workspace-level security, compliance, retention, and access control policies."""

    __tablename__ = "security_policies"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True, nullable=False)
    retention_days: Mapped[int] = mapped_column(Integer, nullable=False, default=365)  # 0 = indefinite
    enforce_mfa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ip_whitelist: Mapped[Dict[str, Any]] = mapped_column(JSONType, nullable=False, default=dict)  # {"allowed_cidrs": []}
    allowed_providers: Mapped[Dict[str, Any]] = mapped_column(JSONType, nullable=False, default=dict)  # {"providers": ["gemini", "ollama"]}
    gdpr_anonymize_on_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    data_classification: Mapped[str] = mapped_column(String(50), nullable=False, default="CONFIDENTIAL")  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "workspace_id": str(self.workspace_id),
            "retention_days": self.retention_days,
            "enforce_mfa": self.enforce_mfa,
            "ip_whitelist": self.ip_whitelist or {},
            "allowed_providers": self.allowed_providers or {},
            "gdpr_anonymize_on_delete": self.gdpr_anonymize_on_delete,
            "data_classification": self.data_classification,
            "updated_at": self.updated_at.isoformat(),
        }
