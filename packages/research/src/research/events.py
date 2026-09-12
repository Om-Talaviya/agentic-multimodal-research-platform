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
    PLAN_DECOMPOSED = "plan_decomposed"
    TASKS_CREATED = "tasks_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_SPAWNED = "task_spawned"
    DAG_REPLANNED = "dag_replanned"
    SOURCES_ADDED = "sources_added"
    EVIDENCE_ADDED = "evidence_added"
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_COMPLETED = "verification_completed"
    DEEP_RESEARCH_STARTED = "deep_research_started"
    RESEARCH_ITERATION_STARTED = "research_iteration_started"
    HYPOTHESIS_FORMULATED = "hypothesis_formulated"
    RESEARCH_ITERATION_COMPLETED = "research_iteration_completed"
    DEEP_RESEARCH_CONVERGED = "deep_research_converged"
    DEEP_RESEARCH_TERMINATED = "deep_research_terminated"
    REPORT_STARTED = "report_started"
    REPORT_GENERATED = "report_generated"
    MEMORY_RECALLED = "memory_recalled"
    MEMORY_STORED = "memory_stored"
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


import threading


class ResearchEventBus:
    """Bounded async pub/sub grouped by research job ID."""

    def __init__(self, max_queue_size: int = 100) -> None:
        self.max_queue_size = max_queue_size
        self._subscribers: dict[str, set[asyncio.Queue[ResearchEvent]]] = defaultdict(set)
        self._lock = threading.Lock()
        self._sequence = 0

    async def publish(self, event: ResearchEvent) -> ResearchEvent:
        with self._lock:
            self._sequence += 1
            event.sequence = self._sequence
            subscribers = list(self._subscribers.get(event.job_id, set()))

        for queue in subscribers:
            try:
                loop = getattr(queue, "_loop", None)
                curr_loop = None
                try:
                    curr_loop = asyncio.get_running_loop()
                except RuntimeError:
                    pass

                def _do_put(q: asyncio.Queue[ResearchEvent], ev: ResearchEvent) -> None:
                    try:
                        q.put_nowait(ev)
                    except asyncio.QueueFull:
                        try:
                            q.get_nowait()
                        except asyncio.QueueEmpty:
                            pass
                        try:
                            q.put_nowait(ev)
                        except asyncio.QueueFull:
                            pass

                if loop and loop.is_running() and loop != curr_loop:
                    loop.call_soon_threadsafe(_do_put, queue, event)
                else:
                    _do_put(queue, event)
            except Exception:
                pass

        return event

    @asynccontextmanager
    async def subscribe(self, job_id: str) -> AsyncIterator[asyncio.Queue[ResearchEvent]]:
        queue: asyncio.Queue[ResearchEvent] = asyncio.Queue(maxsize=self.max_queue_size)
        with self._lock:
            self._subscribers[job_id].add(queue)

        try:
            yield queue
        finally:
            with self._lock:
                subscribers = self._subscribers.get(job_id)
                if subscribers is not None:
                    subscribers.discard(queue)
                    if not subscribers:
                        self._subscribers.pop(job_id, None)

    async def subscriber_count(self, job_id: str) -> int:
        with self._lock:
            return len(self._subscribers.get(job_id, set()))


research_event_bus = ResearchEventBus()
