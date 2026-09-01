"""In-process research event bus for real-time job progress updates."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from enum import Enum
from typing import Any, AsyncIterator
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class ResearchEventType(str, Enum):
    JOB_CREATED = "job_created"
    JOB_STARTED = "job_started"
    PLANNING_STARTED = "planning_started"
    PLANNING_COMPLETED = "planning_completed"
    TASKS_CREATED = "tasks_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    SOURCES_ADDED = "sources_added"
    EVIDENCE_ADDED = "evidence_added"
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_COMPLETED = "verification_completed"
    REPORT_STARTED = "report_started"
    REPORT_GENERATED = "report_generated"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"


class ResearchEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    type: ResearchEventType
    sequence: int = 0
    timestamp: datetime = Field(default_factory=utc_now)
    message: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class ResearchEventBus:
    """Bounded async pub/sub grouped by research job ID."""

    def __init__(self, max_queue_size: int = 100) -> None:
        self.max_queue_size = max_queue_size
        self._subscribers: dict[str, set[asyncio.Queue[ResearchEvent]]] = defaultdict(set)
        self._lock = asyncio.Lock()
        self._sequence = 0

    async def publish(self, event: ResearchEvent) -> ResearchEvent:
        async with self._lock:
            self._sequence += 1
            event.sequence = self._sequence
            subscribers = list(self._subscribers.get(event.job_id, set()))

        for queue in subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    pass

        return event

    @asynccontextmanager
    async def subscribe(self, job_id: str) -> AsyncIterator[asyncio.Queue[ResearchEvent]]:
        queue: asyncio.Queue[ResearchEvent] = asyncio.Queue(maxsize=self.max_queue_size)
        async with self._lock:
            self._subscribers[job_id].add(queue)

        try:
            yield queue
        finally:
            async with self._lock:
                subscribers = self._subscribers.get(job_id)
                if subscribers is not None:
                    subscribers.discard(queue)
                    if not subscribers:
                        self._subscribers.pop(job_id, None)

    async def subscriber_count(self, job_id: str) -> int:
        async with self._lock:
            return len(self._subscribers.get(job_id, set()))


research_event_bus = ResearchEventBus()
