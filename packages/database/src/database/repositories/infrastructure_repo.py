"""Repository for Worker Node cluster telemetry and Storage Object catalog (Phase 24)."""
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy import desc, func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.infrastructure import DBStorageObject, DBWorkerNode
from shared.logging import get_logger

logger = get_logger(__name__)


class InfrastructureRepository:
    """Async repository for distributed worker nodes and blob storage metadata."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # =========================================================================
    # Worker Node Telemetry & Heartbeats
    # =========================================================================

    async def register_or_heartbeat_worker(
        self,
        worker_id: str,
        hostname: str = "node.cluster.local",
        concurrency: int = 4,
        active_tasks: Optional[List[str]] = None,
        cpu_percent: float = 0.0,
        memory_mb: float = 0.0,
        status: str = "HEALTHY",
    ) -> DBWorkerNode:
        """Register a worker node or update its heartbeat pulse."""
        stmt = select(DBWorkerNode).where(DBWorkerNode.worker_id == worker_id)
        result = await self.session.execute(stmt)
        node = result.scalars().first()

        now = datetime.now(UTC)
        tasks = active_tasks or []

        if node:
            node.hostname = hostname
            node.concurrency = concurrency
            node.active_tasks = tasks
            node.cpu_percent = cpu_percent
            node.memory_mb = memory_mb
            node.status = "BUSY" if len(tasks) >= concurrency else status
            node.last_heartbeat = now
        else:
            node = DBWorkerNode(
                worker_id=worker_id,
                hostname=hostname,
                concurrency=concurrency,
                active_tasks=tasks,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                status="BUSY" if len(tasks) >= concurrency else status,
                last_heartbeat=now,
                created_at=now,
            )
            self.session.add(node)

        await self.session.flush()
        return node

    async def list_workers(self, include_offline: bool = True) -> List[DBWorkerNode]:
        """List cluster worker nodes."""
        stmt = select(DBWorkerNode).order_by(desc(DBWorkerNode.last_heartbeat))
        if not include_offline:
            stmt = stmt.where(DBWorkerNode.status != "OFFLINE")

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def sweep_stale_workers(self, timeout_seconds: int = 60) -> int:
        """Mark workers without recent heartbeats as OFFLINE."""
        stale_threshold = datetime.now(UTC) - timedelta(seconds=timeout_seconds)
        stmt = (
            update(DBWorkerNode)
            .where(DBWorkerNode.last_heartbeat < stale_threshold, DBWorkerNode.status != "OFFLINE")
            .values(status="OFFLINE")
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    # =========================================================================
    # Storage Object Catalog
    # =========================================================================

    async def record_storage_object(
        self,
        bucket: str,
        object_key: str,
        size_bytes: int,
        etag: str,
        md5_hash: str,
        sha256_hash: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, Any]] = None,
        workspace_id: Optional[UUID] = None,
        uploader_id: Optional[UUID] = None,
    ) -> DBStorageObject:
        """Catalog an S3/MinIO stored object."""
        stmt = select(DBStorageObject).where(
            DBStorageObject.bucket == bucket,
            DBStorageObject.object_key == object_key,
        )
        result = await self.session.execute(stmt)
        obj = result.scalars().first()

        now = datetime.now(UTC)
        if obj:
            obj.size_bytes = size_bytes
            obj.etag = etag
            obj.md5_hash = md5_hash
            obj.sha256_hash = sha256_hash
            obj.content_type = content_type
            obj.metadata_json = metadata or {}
            obj.workspace_id = workspace_id or obj.workspace_id
            obj.uploader_id = uploader_id or obj.uploader_id
        else:
            obj = DBStorageObject(
                bucket=bucket,
                object_key=object_key,
                content_type=content_type,
                size_bytes=size_bytes,
                etag=etag,
                md5_hash=md5_hash,
                sha256_hash=sha256_hash,
                metadata_json=metadata or {},
                workspace_id=workspace_id,
                uploader_id=uploader_id,
                created_at=now,
            )
            self.session.add(obj)

        await self.session.flush()
        return obj

    async def list_storage_objects(
        self,
        workspace_id: Optional[UUID] = None,
        bucket: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DBStorageObject]:
        """Query cataloged storage objects with optional workspace filtering."""
        stmt = select(DBStorageObject)
        if workspace_id:
            stmt = stmt.where(DBStorageObject.workspace_id == workspace_id)
        if bucket:
            stmt = stmt.where(DBStorageObject.bucket == bucket)

        stmt = stmt.order_by(desc(DBStorageObject.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_storage_object_by_id(self, object_id: UUID) -> Optional[DBStorageObject]:
        stmt = select(DBStorageObject).where(DBStorageObject.id == object_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete_storage_object_record(self, object_id: UUID) -> bool:
        obj = await self.get_storage_object_by_id(object_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def get_storage_usage_summary(self, workspace_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Aggregate total storage usage in bytes and count."""
        stmt = select(
            func.count(DBStorageObject.id).label("total_objects"),
            func.coalesce(func.sum(DBStorageObject.size_bytes), 0).label("total_bytes"),
        )
        if workspace_id:
            stmt = stmt.where(DBStorageObject.workspace_id == workspace_id)

        result = await self.session.execute(stmt)
        row = result.first()
        total_objects = row.total_objects if row else 0
        total_bytes = int(row.total_bytes) if row and row.total_bytes is not None else 0

        return {
            "workspace_id": str(workspace_id) if workspace_id else None,
            "total_objects": total_objects,
            "total_bytes": total_bytes,
            "total_mb": round(total_bytes / (1024 * 1024), 2),
            "total_gb": round(total_bytes / (1024 * 1024 * 1024), 4),
        }
