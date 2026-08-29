"""Unit tests for AgentOrchestrator resilience and coordination."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from agents.base import Agent, AgentContext, AgentResult
from agents.memory import AgentMemory
from agents.orchestrator import AgentOrchestrator
from agents.registry import AgentRegistry
from tools.registry import ToolRegistry
from research.models import ResearchTask


class MockFailingAgent(Agent):
    name = "mock_failing"
    description = "Mock agent that fails on first attempt and succeeds on second"
    attempts = 0

    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        MockFailingAgent.attempts += 1
        if MockFailingAgent.attempts == 1:
            raise RuntimeError("Transient network error")
        return AgentResult(success=True, output={"status": "recovered"})


class MockCriticAgent(Agent):
    name = "critic"
    description = "Mock critic agent"

    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            output={
                "verifications": [{"evidence_id": "ev_1", "verification_status": "verified"}],
                "quality_score": 0.95,
            }
        )


@pytest.mark.asyncio
async def test_orchestrator_retry_recovery():
    MockFailingAgent.attempts = 0
    agent_registry = AgentRegistry()
    agent_registry.register("mock_failing", MockFailingAgent)

    tool_registry = ToolRegistry()
    mock_router = MagicMock()

    orchestrator = AgentOrchestrator(
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        model_router=mock_router,
        max_retries=2,
        retry_delay_seconds=0.01,
    )

    task = ResearchTask(
        id="task_fail_1",
        job_id="job_1",
        type="mock_failing",
        objective="Test retry mechanism",
        agent="mock_failing",
    )

    context = orchestrator.create_context(job_id="job_1", task_id="task_fail_1", request_id="req_1")

    with patch("database.connection.get_session"):
        result = await orchestrator.run_agent("mock_failing", task, context)

    assert result.success is True
    assert result.output["status"] == "recovered"
    assert MockFailingAgent.attempts == 2


@pytest.mark.asyncio
async def test_orchestrator_parallel_execution():
    agent_registry = AgentRegistry()
    agent_registry.register("critic", MockCriticAgent)

    tool_registry = ToolRegistry()
    mock_router = MagicMock()

    orchestrator = AgentOrchestrator(
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        model_router=mock_router,
    )

    task1 = ResearchTask(id="task_p1", job_id="job_p", type="critic", objective="Task 1", agent="critic")
    task2 = ResearchTask(id="task_p2", job_id="job_p", type="critic", objective="Task 2", agent="critic")

    context = orchestrator.create_context(job_id="job_p", task_id="task_root", request_id="req_p")

    with patch("database.connection.get_session"):
        results = await orchestrator.run_parallel(
            [("critic", task1), ("critic", task2)],
            context,
        )

    assert len(results) == 2
    assert all(r.success for r in results if isinstance(r, AgentResult))


@pytest.mark.asyncio
async def test_orchestrator_run_critic_helper():
    agent_registry = AgentRegistry()
    agent_registry.register("critic", MockCriticAgent)

    tool_registry = ToolRegistry()
    mock_router = MagicMock()

    orchestrator = AgentOrchestrator(
        agent_registry=agent_registry,
        tool_registry=tool_registry,
        model_router=mock_router,
    )

    with patch("database.connection.get_session"):
        result = await orchestrator.run_critic(
            evidence=[{"id": "ev_1", "claim": "Test claim"}],
            question="What is the claim?",
            job_id="job_critic_test",
            request_id="req_critic_test",
        )

    assert result.success is True
    assert result.output["quality_score"] == 0.95
