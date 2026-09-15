"""SQLAlchemy database models for Production Infrastructure, Worker Nodes, and Storage Blobs (Phase 24)."""
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base
from database.models.memory import GUID, JSONType


class DBWorkerNode(Base):
    """Tracks background async execution worker nodes, resource loads, and heartbeats."""

    __tablename__ = "worker_nodes"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    worker_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False, default="node.cluster.local")
    concurrency: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    active_tasks: Mapped[List[str]] = mapped_column(JSONType, nullable=False, default=list)
    total_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="HEALTHY")  # HEALTHY, BUSY, OFFLINE
    cpu_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    memory_mb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_heartbeat: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "worker_id": self.worker_id,
            "hostname": self.hostname,
            "concurrency": self.concurrency,
            "active_tasks_count": len(self.active_tasks) if isinstance(self.active_tasks, list) else 0,
            "active_tasks": self.active_tasks if isinstance(self.active_tasks, list) else [],
            "total_completed": self.total_completed,
            "total_failed": self.total_failed,
            "status": self.status,
            "cpu_percent": self.cpu_percent,
            "memory_mb": self.memory_mb,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DBStorageObject(Base):
    """Metadata catalog for S3/MinIO/Local stored blob objects and datasets."""

    __tablename__ = "storage_objects"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    bucket: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    object_key: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False, default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    etag: Mapped[str] = mapped_column(String(100), nullable=False)
    md5_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONType, nullable=False, default=dict)
    workspace_id: Mapped[Optional[UUID]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True)
    uploader_id: Mapped[Optional[UUID]] = mapped_column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), index=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "bucket": self.bucket,
            "object_key": self.object_key,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
            "size_mb": round(self.size_bytes / (1024 * 1024), 3),
            "etag": self.etag,
            "md5_hash": self.md5_hash,
            "sha256_hash": self.sha256_hash,
            "metadata": self.metadata_json or {},
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "uploader_id": str(self.uploader_id) if self.uploader_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
