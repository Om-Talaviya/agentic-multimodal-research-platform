"""Distributed Task Queue and Worker Cluster Management Subsystem (Phase 24)."""
import asyncio
from datetime import UTC, datetime
from enum import Enum
import heapq
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Tuple
import uuid
from pydantic import BaseModel, ConfigDict, Field
from shared.logging import get_logger

logger = get_logger(__name__)


class QueuePriority(str, Enum):
    LOW = "LOW"
    DEFAULT = "DEFAULT"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Priority weighting for heap ordering (lower number = higher priority)
_PRIORITY_WEIGHTS = {
    QueuePriority.CRITICAL: 1,
    QueuePriority.HIGH: 2,
    QueuePriority.DEFAULT: 3,
    QueuePriority.LOW: 4,
}


class QueuedTask(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: Optional[str] = None
    task_type: str = Field(..., description="research_dag, multimodal_ingest, model_eval, memory_consolidation")
    priority: QueuePriority = QueuePriority.DEFAULT
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    max_retries: int = 3
    retry_count: int = 0
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED, RETRYING
    assigned_worker_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "job_id": self.job_id,
            "task_type": self.task_type,
            "priority": self.priority.value if hasattr(self.priority, "value") else str(self.priority),
            "payload": self.payload,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "status": self.status,
            "assigned_worker_id": self.assigned_worker_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
        }


class AsyncTaskQueue:
    """In-Memory and Redis-compatible priority task queue for background workers."""

    def __init__(self) -> None:
        self._heap: List[Tuple[int, float, str]] = []  # (priority_weight, timestamp, task_id)
        self._tasks: Dict[str, QueuedTask] = {}
        self._lock = asyncio.Lock()
        self._counter = 0

    async def enqueue(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: QueuePriority = QueuePriority.DEFAULT,
        job_id: Optional[str] = None,
        max_retries: int = 3,
    ) -> QueuedTask:
        """Enqueue a new task into the priority queue."""
        async with self._lock:
            task = QueuedTask(
                task_type=task_type,
                payload=payload,
                priority=priority,
                job_id=job_id,
                max_retries=max_retries,
            )
            self._tasks[task.task_id] = task
            weight = _PRIORITY_WEIGHTS.get(priority, 3)
            ts = task.created_at.timestamp()
            self._counter += 1
            heapq.heappush(self._heap, (weight, ts, task.task_id))
            
            logger.info("Task enqueued", task_id=task.task_id, task_type=task_type, priority=priority.value)
            return task

    async def dequeue(self, worker_id: str) -> Optional[QueuedTask]:
        """Pop the highest priority available pending task."""
        async with self._lock:
            while self._heap:
                _, _, task_id = heapq.heappop(self._heap)
                task = self._tasks.get(task_id)
                if task and task.status in ("PENDING", "RETRYING"):
                    task.status = "RUNNING"
                    task.assigned_worker_id = worker_id
                    task.started_at = datetime.now(UTC)
                    return task
            return None

    async def complete_task(self, task_id: str, result: Dict[str, Any]) -> Optional[QueuedTask]:
        """Mark task as successfully completed."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.status = "COMPLETED"
                task.result = result
                task.completed_at = datetime.now(UTC)
                logger.info("Task completed", task_id=task_id, worker_id=task.assigned_worker_id)
            return task

    async def fail_task(self, task_id: str, error: str) -> Optional[QueuedTask]:
        """Mark task as failed or requeue if retries remain."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return None

            task.error = error
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = "RETRYING"
                weight = _PRIORITY_WEIGHTS.get(task.priority, 3)
                heapq.heappush(self._heap, (weight, datetime.now(UTC).timestamp(), task.task_id))
                logger.warning("Task failed, scheduled for retry", task_id=task_id, retry=task.retry_count)
            else:
                task.status = "FAILED"
                task.completed_at = datetime.now(UTC)
                logger.error("Task permanently failed after max retries", task_id=task_id, error=error)

            return task

    async def get_task(self, task_id: str) -> Optional[QueuedTask]:
        async with self._lock:
            return self._tasks.get(task_id)

    async def get_queue_metrics(self) -> Dict[str, Any]:
        """Get aggregate queue metrics."""
        async with self._lock:
            pending = sum(1 for t in self._tasks.values() if t.status == "PENDING")
            running = sum(1 for t in self._tasks.values() if t.status == "RUNNING")
            completed = sum(1 for t in self._tasks.values() if t.status == "COMPLETED")
            failed = sum(1 for t in self._tasks.values() if t.status == "FAILED")
            retrying = sum(1 for t in self._tasks.values() if t.status == "RETRYING")

            return {
                "total_tasks": len(self._tasks),
                "pending_tasks": pending,
                "running_tasks": running,
                "completed_tasks": completed,
                "failed_tasks": failed,
                "retrying_tasks": retrying,
                "queue_depth": len(self._heap),
            }


class WorkerNode:
    """Represents an active async execution worker node."""

    def __init__(
        self,
        worker_id: Optional[str] = None,
        hostname: str = "node-1.cluster.local",
        concurrency: int = 4,
    ) -> None:
        self.worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        self.hostname = hostname
        self.concurrency = concurrency
        self.active_tasks: Set[str] = set()
        self.total_completed: int = 0
        self.total_failed: int = 0
        self.status: str = "HEALTHY"  # HEALTHY, BUSY, OFFLINE
        self.last_heartbeat = datetime.now(UTC)
        self.cpu_percent: float = 12.5
        self.memory_mb: float = 245.0

    def record_heartbeat(self, cpu_percent: float = 15.0, memory_mb: float = 250.0) -> None:
        self.last_heartbeat = datetime.now(UTC)
        self.cpu_percent = cpu_percent
        self.memory_mb = memory_mb
        self.status = "BUSY" if len(self.active_tasks) >= self.concurrency else "HEALTHY"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "hostname": self.hostname,
            "concurrency": self.concurrency,
            "active_tasks_count": len(self.active_tasks),
            "active_tasks": list(self.active_tasks),
            "total_completed": self.total_completed,
            "total_failed": self.total_failed,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_mb": self.memory_mb,
        }


# Global singleton queue instance for the research application
global_task_queue = AsyncTaskQueue()
