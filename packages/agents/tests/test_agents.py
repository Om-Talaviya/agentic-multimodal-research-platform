"""Tests for agents package."""

import pytest
from agents.base import Agent, AgentContext, AgentResult, AgentMemory
from agents.registry import AgentRegistry
from ai.providers.router import ModelRouter
from ai.schemas import ModelCapabilities
from research.models import ResearchTask


class MockAgent(Agent):
    """Mock agent for testing."""
    
    name = "mock_agent"
    description = "Mock agent for testing"
    capabilities = {"testing"}
    
    def __init__(self, should_succeed: bool = True, result_output: any = "success"):
        super().__init__()
        self.should_succeed = should_succeed
        self.result_output = result_output
        self.run_called = False
    
    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        self.run_called = True
        if self.should_succeed:
            return AgentResult(success=True, output=self.result_output)
        return AgentResult(success=False, errors=["Mock error"])


def test_agent_memory():
    """Test AgentMemory."""
    memory = AgentMemory()
    
    # Short term
    memory.add_short_term("item1")
    memory.add_short_term("item2")
    assert memory.get_short_term(1) == ["item2"]
    assert memory.get_short_term(5) == ["item1", "item2"]
    
    # Long term
    memory.set_long_term("key1", "value1")
    assert memory.get_long_term("key1") == "value1"
    assert memory.get_long_term("missing", "default") == "default"
    
    # Working
    memory.set_working("work1", "data1")
    assert memory.get_working("work1") == "data1"
    memory.clear_working()
    assert memory.get_working("work1") is None


def test_agent_context():
    """Test AgentContext creation."""
    from ai.providers.router import ModelRouter
    from tools.registry import ToolRegistry
    
    router = ModelRouter([], [], [], [])
    tool_reg = ToolRegistry()
    memory = AgentMemory()
    
    context = AgentContext(
        research_job_id="job-1",
        task_id="task-1",
        request_id="req-1",
        tools={},
        memory=memory,
        model_router=router,
        config={"test": "value"},
    )
    
    assert context.research_job_id == "job-1"
    assert context.task_id == "task-1"
    assert context.config["test"] == "value"


def test_agent_registry():
    """Test AgentRegistry."""
    registry = AgentRegistry()
    
    registry.register("mock", MockAgent)
    
    agent_class = registry.get("mock")
    assert agent_class == MockAgent
    
    agent = registry.create("mock")
    assert isinstance(agent, MockAgent)
    assert agent.name == "mock_agent"
    
    agents = registry.list_agents()
    assert len(agents) == 1
    assert agents[0]["name"] == "mock"
    
    # get returns None for unknown agent
    assert registry.get("unknown") is None
    
    # create raises ValueError for unknown agent
    with pytest.raises(ValueError):
        registry.create("unknown")


@pytest.mark.asyncio
async def test_mock_agent_success():
    """Test mock agent successful execution."""
    agent = MockAgent(should_succeed=True, result_output={"data": "test"})
    
    task = ResearchTask(
        id="task-1",
        job_id="job-1",
        type="test",
        objective="Test objective",
        agent="mock_agent",
    )
    
    from ai.providers.router import ModelRouter
    from tools.registry import ToolRegistry
    
    router = ModelRouter([], [], [], [])
    tool_reg = ToolRegistry()
    memory = AgentMemory()
    
    context = AgentContext(
        research_job_id="job-1",
        task_id="task-1",
        request_id="req-1",
        tools={},
        memory=memory,
        model_router=router,
    )
    
    result = await agent.run(task, context)
    
    assert result.success is True
    assert result.output == {"data": "test"}
    assert agent.run_called is True


@pytest.mark.asyncio
async def test_mock_agent_failure():
    """Test mock agent failure."""
    agent = MockAgent(should_succeed=False)
    
    task = ResearchTask(
        id="task-1",
        job_id="job-1",
        type="test",
        objective="Test",
        agent="mock_agent",
    )
    
    from ai.providers.router import ModelRouter
    from tools.registry import ToolRegistry
    
    router = ModelRouter([], [], [], [])
    tool_reg = ToolRegistry()
    memory = AgentMemory()
    
    context = AgentContext(
        research_job_id="job-1",
        task_id="task-1",
        request_id="req-1",
        tools={},
        memory=memory,
        model_router=router,
    )
    
    result = await agent.run(task, context)
    
    assert result.success is False
    assert "Mock error" in result.errors