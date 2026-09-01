"""Tests for research event bus and event models."""

import asyncio
import pytest
from research.events import ResearchEvent, ResearchEventBus, ResearchEventType


@pytest.mark.asyncio
async def test_event_bus_publish_and_subscribe():
    bus = ResearchEventBus(max_queue_size=10)
    job_id = "test-job-1"

    async with bus.subscribe(job_id) as queue:
        assert await bus.subscriber_count(job_id) == 1

        event = ResearchEvent(
            job_id=job_id,
            type=ResearchEventType.JOB_STARTED,
            message="Job started",
            data={"status": "running"},
        )
        published = await bus.publish(event)
        assert published.sequence == 1

        received = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert received.id == event.id
        assert received.type == ResearchEventType.JOB_STARTED
        assert received.sequence == 1
        assert received.data["status"] == "running"

    # Verify unsubscription cleanup
    assert await bus.subscriber_count(job_id) == 0


@pytest.mark.asyncio
async def test_event_bus_job_isolation():
    bus = ResearchEventBus(max_queue_size=10)
    job_a = "job-a"
    job_b = "job-b"

    async with bus.subscribe(job_a) as queue_a, bus.subscribe(job_b) as queue_b:
        event_a = ResearchEvent(
            job_id=job_a,
            type=ResearchEventType.TASK_STARTED,
            data={"task_id": "t1"},
        )
        await bus.publish(event_a)

        received_a = await asyncio.wait_for(queue_a.get(), timeout=1.0)
        assert received_a.job_id == job_a

        # Queue B should not receive Job A's event
        assert queue_b.empty()


@pytest.mark.asyncio
async def test_event_bus_multi_subscriber_fan_out():
    bus = ResearchEventBus(max_queue_size=10)
    job_id = "job-fan-out"

    async with bus.subscribe(job_id) as q1, bus.subscribe(job_id) as q2:
        assert await bus.subscriber_count(job_id) == 2

        event = ResearchEvent(
            job_id=job_id,
            type=ResearchEventType.PLANNING_COMPLETED,
            data={"step_count": 3},
        )
        await bus.publish(event)

        r1 = await asyncio.wait_for(q1.get(), timeout=1.0)
        r2 = await asyncio.wait_for(q2.get(), timeout=1.0)

        assert r1.id == event.id
        assert r2.id == event.id
        assert r1.sequence == r2.sequence


@pytest.mark.asyncio
async def test_event_bus_bounded_queue_backpressure():
    # Bounded queue with maxsize=2
    bus = ResearchEventBus(max_queue_size=2)
    job_id = "job-backpressure"

    async with bus.subscribe(job_id) as queue:
        # Publish 3 events without reading
        for i in range(1, 4):
            await bus.publish(
                ResearchEvent(
                    job_id=job_id,
                    type=ResearchEventType.TASK_COMPLETED,
                    data={"index": i},
                )
            )

        # The oldest event should have been dropped to accommodate the newest without crashing
        assert queue.qsize() == 2
        r1 = await queue.get()
        r2 = await queue.get()
        assert r1.data["index"] == 2
        assert r2.data["index"] == 3
