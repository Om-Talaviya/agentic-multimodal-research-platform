"""Unit tests for Agent Runtime foundation."""

import asyncio
import pytest
from agents.runtime.events import (
    AgentCancelledEvent,
    AgentCompletedEvent,
    AgentCreatedEvent,
    AgentFailedEvent,
    AgentStartedEvent,
    AgentTimedOutEvent,
    AgentWaitingForApprovalEvent,
    EventEmitter,
    ModelRequestStartedEvent,
    ModelResponseReceivedEvent,
    ToolCallCompletedEvent,
    ToolCallFailedEvent,
    ToolCallRequestedEvent,
    ToolCallStartedEvent,
)
from agents.runtime.runtime import AgentExecutionResult, AgentRuntime
from agents.runtime.state import AgentState, AgentStateMachine, InvalidStateTransitionError
from agents.runtime.task import AgentTask
from agents.runtime.tools import ToolExecutionResult, ToolExecutor
from ai.gateway.model_gateway import ModelGateway
from ai.providers.router import ModelRouter
from ai.registry.model_registry import ModelDefinition, ModelRegistry
from ai.registry.provider_registry import ProviderRegistry
from ai.schemas import (
    LLMMessage,
    LLMRequest,
    LLMResponse,
    MessageRole,
    ModelCapability,
    ProviderHealth,
)
from tools.base import Permission, Tool, ToolParameter, ToolSchema
from tools.registry import ToolRegistry


# ---------------------------------------------------------------------------
# Test Mocks & Helpers
# ---------------------------------------------------------------------------

class FakeTool(Tool):
    """Test tool."""

    schema = ToolSchema(
        name="test_calculator",
        description="Add two numbers",
        parameters=[
            ToolParameter(name="a", type="integer", description="first"),
            ToolParameter(name="b", type="integer", description="second"),
        ],
        returns="sum",
        permissions=[Permission.CODE_EXECUTION],
    )

    async def execute(self, a: int = 0, b: int = 0) -> int:
        return a + b


class SlowTool(Tool):
    """Tool that hangs for testing timeouts."""

    schema = ToolSchema(
        name="slow_tool",
        description="Slow hanging tool",
        parameters=[],
        returns="none",
        permissions=[],
    )

    async def execute(self) -> str:
        await asyncio.sleep(10.0)
        return "done"


class FailingTool(Tool):
    """Tool that throws an exception."""

    schema = ToolSchema(
        name="failing_tool",
        description="Tool that always fails",
        parameters=[],
        returns="none",
        permissions=[],
    )

    async def execute(self) -> str:
        raise ValueError("Simulated tool crash")


class MockLLMProvider:
    """Mock LLM Provider for runtime tests."""

    def __init__(self, responses: list[LLMResponse]) -> None:
        self.name = "mock_provider"
        self.is_local = True
        self.capabilities = {
            ModelCapability.REASONING,
            ModelCapability.SUMMARIZATION,
            ModelCapability.TOOL_USE,
        }
        self.models = ["mock-model"]
        self._responses = list(responses)
        self.call_count = 0

    async def complete(self, request: LLMRequest) -> LLMResponse:
        self.call_count += 1
        if not self._responses:
            return LLMResponse(content="Final default response", model="mock-model")
        return self._responses.pop(0)

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(provider=self.name, healthy=True)


def build_test_runtime(responses: list[LLMResponse], tools: list[Tool] = None, approval_hook=None) -> AgentRuntime:
    """Construct mock runtime with controlled gateway and tool responses."""
    tool_reg = ToolRegistry()
    if tools:
        for t in tools:
            tool_reg.register(t)

    mock_provider = MockLLMProvider(responses)
    prov_reg = ProviderRegistry()
    prov_reg.register_llm(mock_provider)

    model_reg = ModelRegistry()
    model_reg.register(
        ModelDefinition(
            model_id="mock-model",
            provider_name="mock_provider",
            capabilities=set(mock_provider.capabilities),
            priority=10,
        )
    )

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(router=router, model_registry=model_reg, provider_registry=prov_reg)

    return AgentRuntime(
        gateway=gateway,
        tool_registry=tool_reg,
        event_emitter=EventEmitter(),
        approval_hook=approval_hook,
    )


# ---------------------------------------------------------------------------
# Unit Tests
# ---------------------------------------------------------------------------

def test_state_machine_valid_transitions():
    """Test allowed state transitions in AgentStateMachine."""
    sm = AgentStateMachine(AgentState.CREATED)
    assert sm.state == AgentState.CREATED
    assert sm.is_terminal is False

    sm.transition_to(AgentState.RUNNING)
    assert sm.state == AgentState.RUNNING

    sm.transition_to(AgentState.WAITING_FOR_TOOL)
    assert sm.state == AgentState.WAITING_FOR_TOOL

    sm.transition_to(AgentState.RUNNING)
    sm.transition_to(AgentState.COMPLETED)
    assert sm.state == AgentState.COMPLETED
    assert sm.is_terminal is True


def test_state_machine_invalid_transitions():
    """Test that invalid state transitions raise InvalidStateTransitionError."""
    sm = AgentStateMachine(AgentState.CREATED)
    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to(AgentState.COMPLETED)

    sm.transition_to(AgentState.RUNNING)
    sm.transition_to(AgentState.COMPLETED)

    # Terminal state cannot transition anywhere
    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to(AgentState.RUNNING)


def test_task_model_validation():
    """Test AgentTask schema and defaults."""
    task = AgentTask(
        task_id="t-1",
        description="Compute sum",
        input={"a": 10, "b": 20},
        timeout_seconds=30.0,
        max_iterations=5,
    )
    assert task.task_id == "t-1"
    assert task.timeout_seconds == 30.0
    assert task.max_iterations == 5
    assert task.priority == 5


@pytest.mark.asyncio
async def test_runtime_simple_execution():
    """Test single iteration completion without tool calls."""
    responses = [
        LLMResponse(content="The answer is 42", model="mock-model"),
    ]
    runtime = build_test_runtime(responses)

    task = AgentTask(task_id="task-100", description="What is the answer?")
    result = await runtime.execute(task=task)

    assert result.success is True
    assert result.state == AgentState.COMPLETED
    assert result.output == "The answer is 42"
    assert result.iterations == 1
    assert len(result.errors) == 0
    assert result.telemetry["model_used"] == "mock-model"

    # Verify event stream
    event_types = [e.event_type for e in result.events]
    assert "AgentCreated" in event_types
    assert "AgentStarted" in event_types
    assert "ModelRequestStarted" in event_types
    assert "ModelResponseReceived" in event_types
    assert "AgentCompleted" in event_types


@pytest.mark.asyncio
async def test_runtime_tool_execution_loop():
    """Test multi-step execution with a tool call and final answer."""
    calc_tool = FakeTool()
    responses = [
        # Iteration 1: Model calls test_calculator
        LLMResponse(
            content="",
            model="mock-model",
            tool_calls=[
                {
                    "id": "call-1",
                    "function": {"name": "test_calculator", "arguments": '{"a": 15, "b": 25}'},
                }
            ],
        ),
        # Iteration 2: Model gives final answer based on tool output
        LLMResponse(content="The calculated sum is 40", model="mock-model"),
    ]
    runtime = build_test_runtime(responses, tools=[calc_tool])

    task = AgentTask(task_id="calc-task", description="Calculate 15 + 25")
    result = await runtime.execute(
        task=task,
        allowed_tools=["test_calculator"],
        allowed_permissions={Permission.CODE_EXECUTION},
    )

    assert result.success is True
    assert result.state == AgentState.COMPLETED
    assert result.output == "The calculated sum is 40"
    assert result.iterations == 2
    assert result.total_tool_calls == 1

    event_types = [e.event_type for e in result.events]
    assert "ToolCallRequested" in event_types
    assert "ToolCallStarted" in event_types
    assert "ToolCallCompleted" in event_types


@pytest.mark.asyncio
async def test_runtime_tool_permission_denied():
    """Test that tool calls lacking required permission fail safely."""
    calc_tool = FakeTool()
    responses = [
        LLMResponse(
            content="",
            model="mock-model",
            tool_calls=[
                {
                    "id": "call-perm",
                    "function": {"name": "test_calculator", "arguments": '{"a": 1, "b": 2}'},
                }
            ],
        ),
        LLMResponse(content="Could not calculate due to missing permission", model="mock-model"),
    ]
    # Do NOT grant CODE_EXECUTION permission
    runtime = build_test_runtime(responses, tools=[calc_tool])

    task = AgentTask(task_id="t-perm", description="Calculate")
    result = await runtime.execute(
        task=task,
        allowed_tools=["test_calculator"],
        allowed_permissions=set(),  # empty permissions
    )

    assert result.success is True
    assert "missing permission" in result.output
    event_types = [e.event_type for e in result.events]
    assert "ToolCallFailed" in event_types


@pytest.mark.asyncio
async def test_runtime_tool_timeout():
    """Test that a hanging tool call times out gracefully without crashing."""
    slow_tool = SlowTool()
    executor = ToolExecutor(tool_registry=ToolRegistry())
    executor.tool_registry.register(slow_tool)

    res = await executor.execute_tool_call(
        tool_name="slow_tool",
        arguments={},
        tool_call_id="call-timeout",
        timeout_seconds=0.05,
    )
    assert res.success is False
    assert "timed out" in res.error


@pytest.mark.asyncio
async def test_runtime_tool_crash_handled():
    """Test that an exception inside a tool is handled gracefully."""
    failing_tool = FailingTool()
    executor = ToolExecutor(tool_registry=ToolRegistry())
    executor.tool_registry.register(failing_tool)

    res = await executor.execute_tool_call(
        tool_name="failing_tool",
        arguments={},
        tool_call_id="call-fail",
    )
    assert res.success is False
    assert "Simulated tool crash" in res.error


@pytest.mark.asyncio
async def test_runtime_iteration_limit():
    """Test that exceeding max_iterations terminates and transitions to FAILED."""
    # Endless tool calls
    responses = [
        LLMResponse(
            content="",
            model="mock-model",
            tool_calls=[
                {
                    "id": f"call-{i}",
                    "function": {"name": "test_calculator", "arguments": '{"a": 1, "b": 1}'},
                }
            ],
        )
        for i in range(10)
    ]
    calc_tool = FakeTool()
    runtime = build_test_runtime(responses, tools=[calc_tool])

    task = AgentTask(task_id="t-loop", description="Loop task", max_iterations=3)
    result = await runtime.execute(
        task=task,
        allowed_tools=["test_calculator"],
        allowed_permissions={Permission.CODE_EXECUTION},
    )

    assert result.success is False
    assert result.state == AgentState.FAILED
    assert result.iterations == 3
    assert any("Iteration limit reached" in err for err in result.errors)


@pytest.mark.asyncio
async def test_runtime_cancellation():
    """Test agent cancellation during execution."""
    calc_tool = FakeTool()
    responses = [
        LLMResponse(
            content="",
            model="mock-model",
            tool_calls=[
                {
                    "id": "call-1",
                    "function": {"name": "test_calculator", "arguments": '{"a": 1, "b": 1}'},
                }
            ],
        ),
        LLMResponse(content="Should not reach here", model="mock-model"),
    ]
    runtime = build_test_runtime(responses, tools=[calc_tool])

    # Hook subscription to cancel agent on first iteration
    def on_iteration(event):
        if event.event_type == "AgentIterationCompleted":
            runtime.cancel(event.agent_id, reason="User test cancellation")

    runtime.event_emitter.subscribe(on_iteration)

    task = AgentTask(task_id="t-cancel", description="Cancel task", max_iterations=5)
    result = await runtime.execute(
        task=task,
        allowed_tools=["test_calculator"],
        allowed_permissions={Permission.CODE_EXECUTION},
    )

    assert result.success is False
    assert result.state == AgentState.CANCELLED
    event_types = [e.event_type for e in result.events]
    assert "AgentCancelled" in event_types


@pytest.mark.asyncio
async def test_runtime_human_approval_pause_and_resume():
    """Test pausing for human approval and resuming after approval."""
    calc_tool = FakeTool()
    responses = [
        LLMResponse(
            content="",
            model="mock-model",
            tool_calls=[
                {
                    "id": "call-approval",
                    "function": {"name": "test_calculator", "arguments": '{"a": 5, "b": 5}'},
                }
            ],
        ),
        LLMResponse(content="Result after approval is 10", model="mock-model"),
    ]

    def require_approval_hook(agent_id: str, tool_name: str, args: dict) -> bool:
        return tool_name == "test_calculator"

    runtime = build_test_runtime(responses, tools=[calc_tool], approval_hook=require_approval_hook)

    def auto_approver(event):
        if event.event_type == "AgentWaitingForApproval":
            runtime.approve(event.agent_id, event.tool_call_id)

    runtime.event_emitter.subscribe(auto_approver)

    task = AgentTask(task_id="t-approve", description="Calculate with approval")
    result = await runtime.execute(
        task=task,
        allowed_tools=["test_calculator"],
        allowed_permissions={Permission.CODE_EXECUTION},
    )

    assert result.success is True
    assert result.output == "Result after approval is 10"
    event_types = [e.event_type for e in result.events]
    assert "AgentWaitingForApproval" in event_types
    assert "ToolCallCompleted" in event_types
