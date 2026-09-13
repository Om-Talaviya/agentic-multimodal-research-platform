"""Unit tests for distributed AsyncTaskQueue and WorkerNode (Phase 24)."""
import asyncio
import pytest
from research.workers.task_queue import AsyncTaskQueue, QueuePriority, QueuedTask, WorkerNode

@pytest.mark.asyncio
async def test_task_queue_priority_ordering():
    queue = AsyncTaskQueue()

    # Enqueue tasks in random priority order
    t_low = await queue.enqueue("task_low", {"msg": "low"}, priority=QueuePriority.LOW)
    t_critical = await queue.enqueue("task_crit", {"msg": "crit"}, priority=QueuePriority.CRITICAL)
    t_default = await queue.enqueue("task_def", {"msg": "def"}, priority=QueuePriority.DEFAULT)
    t_high = await queue.enqueue("task_high", {"msg": "high"}, priority=QueuePriority.HIGH)

    # Dequeue must pop in priority order: CRITICAL -> HIGH -> DEFAULT -> LOW
    p1 = await queue.dequeue("worker-1")
    assert p1.task_id == t_critical.task_id
    assert p1.status == "RUNNING"
    assert p1.assigned_worker_id == "worker-1"

    p2 = await queue.dequeue("worker-1")
    assert p2.task_id == t_high.task_id

    p3 = await queue.dequeue("worker-1")
    assert p3.task_id == t_default.task_id

    p4 = await queue.dequeue("worker-1")
    assert p4.task_id == t_low.task_id

    # Queue should now be empty
    p5 = await queue.dequeue("worker-1")
    assert p5 is None

@pytest.mark.asyncio
async def test_task_queue_retry_and_fail():
    queue = AsyncTaskQueue()
    task = await queue.enqueue("flaky_job", {"attempt": 1}, max_retries=2)

    # First attempt: dequeue and fail
    d1 = await queue.dequeue("worker-1")
    assert d1.task_id == task.task_id
    await queue.fail_task(task.task_id, "Temporary network timeout")

    # Should be retrying and re-enqueued
    assert task.status == "RETRYING"
    assert task.retry_count == 1

    # Second attempt
    d2 = await queue.dequeue("worker-2")
    assert d2.task_id == task.task_id
    await queue.fail_task(task.task_id, "Another timeout")
    assert task.retry_count == 2
    assert task.status == "RETRYING"

    # Third attempt exceeds max_retries
    d3 = await queue.dequeue("worker-3")
    assert d3.task_id == task.task_id
    await queue.fail_task(task.task_id, "Fatal crash")
    assert task.status == "FAILED"

@pytest.mark.asyncio
async def test_worker_node_lifecycle():
    worker = WorkerNode(worker_id="test-worker-alpha", hostname="host-01", concurrency=2)
    assert worker.status == "HEALTHY"

    # Add active tasks
    worker.active_tasks.add("task-1")
    worker.active_tasks.add("task-2")
    worker.record_heartbeat(cpu_percent=45.0, memory_mb=512.0)

    assert worker.status == "BUSY"
    assert worker.cpu_percent == 45.0

    d = worker.to_dict()
    assert d["worker_id"] == "test-worker-alpha"
    assert d["active_tasks_count"] == 2
