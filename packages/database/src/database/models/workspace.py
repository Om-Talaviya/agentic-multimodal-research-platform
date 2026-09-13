"""SQLAlchemy database models for Workspaces, Workspace Members, and Projects."""

from datetime import UTC, datetime
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID, JSONType


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBWorkspace(Base):
    """A multi-tenant workspace container grouping users, projects, and research artifacts."""

    __tablename__ = "workspaces"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_personal = Column(Boolean, nullable=False, default=False)
    settings_json = Column(JSONType, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("DBWorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    projects = relationship("DBProject", back_populates="workspace", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_workspaces_owner_created", "owner_id", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "owner_id": str(self.owner_id),
            "is_personal": self.is_personal,
            "settings": self.settings_json or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DBWorkspaceMember(Base):
    """Membership join table associating users with workspaces and defining their RBAC role."""

    __tablename__ = "workspace_members"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False, default="member", index=True)  # owner, admin, researcher, member, viewer
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    workspace = relationship("DBWorkspace", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_workspace_members_ws_user", "workspace_id", "user_id", unique=True),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "workspace_id": str(self.workspace_id),
            "user_id": str(self.user_id),
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DBProject(Base):
    """A research project workspace scoping jobs, documents, memories, and knowledge graphs."""

    __tablename__ = "projects"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_by = Column(GUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(50), nullable=False, default="active", index=True)  # active, archived
    settings_json = Column(JSONType, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    workspace = relationship("DBWorkspace", back_populates="projects")
    creator = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        Index("ix_projects_ws_slug", "workspace_id", "slug", unique=True),
        Index("ix_projects_ws_created", "workspace_id", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "workspace_id": str(self.workspace_id),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "created_by": str(self.created_by) if self.created_by else None,
            "status": self.status,
            "settings": self.settings_json or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
