"""SQLAlchemy database models for Workspace Invitations, Report Annotations, and Workspace Activities."""

from datetime import UTC, datetime, timedelta
import secrets
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID, JSONType


def utc_now() -> datetime:
    return datetime.now(UTC)


def generate_invite_token() -> str:
    """Generate a secure URL-safe invitation token."""
    return secrets.token_urlsafe(32)


class DBWorkspaceInvite(Base):
    """Pending or accepted workspace email/token invitation."""

    __tablename__ = "workspace_invites"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False, default="researcher", index=True)  # admin, researcher, analyst, reviewer, viewer
    token = Column(String(128), unique=True, nullable=False, default=generate_invite_token, index=True)
    invited_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_accepted = Column(Boolean, nullable=False, default=False, index=True)
    expires_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC) + timedelta(days=7),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    workspace = relationship("DBWorkspace", foreign_keys=[workspace_id])
    inviter = relationship("User", foreign_keys=[invited_by])

    __table_args__ = (
        Index("ix_workspace_invites_ws_email", "workspace_id", "email"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "workspace_id": str(self.workspace_id),
            "email": self.email,
            "role": self.role,
            "token": self.token,
            "invited_by": str(self.invited_by) if self.invited_by else None,
            "is_accepted": self.is_accepted,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DBReportAnnotation(Base):
    """Threaded inline comment or annotation on a synthesized research report."""

    __tablename__ = "report_annotations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    report_id = Column(GUID, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    section_index = Column(Integer, nullable=True)  # Index of findings section or paragraph
    selected_text = Column(Text, nullable=True)     # Quoted or highlighted snippet
    comment_text = Column(Text, nullable=False)      # The reviewer/collaborator note
    status = Column(String(50), nullable=False, default="open", index=True)  # open, resolved
    
    resolved_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    author = relationship("User", foreign_keys=[user_id])
    resolver = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index("ix_report_annotations_report_status", "report_id", "status"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "report_id": str(self.report_id),
            "user_id": str(self.user_id),
            "author_username": self.author.username if self.author else None,
            "section_index": self.section_index,
            "selected_text": self.selected_text,
            "comment_text": self.comment_text,
            "status": self.status,
            "resolved_by": str(self.resolved_by) if self.resolved_by else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DBWorkspaceActivity(Base):
    """Audit activity feed item logging collaborative events within a workspace."""

    __tablename__ = "workspace_activities"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(GUID, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action = Column(String(100), nullable=False, index=True)  # job_created, job_completed, doc_uploaded, annotation_added, member_joined
    entity_id = Column(GUID, nullable=True)
    details_json = Column(JSONType, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_ws_activities_ws_created", "workspace_id", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "workspace_id": str(self.workspace_id),
            "project_id": str(self.project_id) if self.project_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "username": self.user.username if self.user else "System",
            "action": self.action,
            "entity_id": str(self.entity_id) if self.entity_id else None,
            "details": self.details_json or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
