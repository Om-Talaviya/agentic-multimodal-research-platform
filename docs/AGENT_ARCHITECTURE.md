# Agent Architecture

## Overview

The agent framework provides a lightweight, extensible foundation for building specialized research agents. It emphasizes:
- Clear separation of agent logic from orchestration
- Tool use with permission boundaries
- Structured memory (short-term context, long-term knowledge)
- Observable execution traces
- Testability with deterministic mocks

## Core Components

### Agent Base Class

```python
# packages/agents/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from packages.ai.schemas import LLMMessage
from packages.tools.base import Tool
from packages.shared.types import JSONDict

@dataclass
class AgentContext:
    """Shared context passed to agents during execution."""
    research_job_id: str
    task_id: str
    request_id: str
    tools: dict[str, Tool]           # Available tools
    memory: "AgentMemory"            # Agent memory
    model_router: "ModelRouter"      # For model selection
    config: dict[str, Any]           # Agent-specific config
    metadata: JSONDict = field(default_factory=dict)

@dataclass
class AgentResult:
    """Result of agent execution."""
    success: bool
    output: Any = None
    evidence: list["Evidence"] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: JSONDict = field(default_factory=dict)

class Agent(ABC):
    """Base class for all agents."""
    
    name: str
    description: str
    capabilities: set[str] = field(default_factory=set)
    
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
    
    @abstractmethod
    async def run(self, task: "ResearchTask", context: AgentContext) -> AgentResult:
        """Execute the agent on a task."""
        pass
    
    async def on_start(self, task: "ResearchTask", context: AgentContext) -> None:
        """Hook called before run()."""
        pass
    
    async def on_complete(self, result: AgentResult, context: AgentContext) -> None:
        """Hook called after successful run()."""
        pass
    
    async def on_error(self, error: Exception, context: AgentContext) -> None:
        """Hook called on error."""
        pass
```

### Agent Registry

```python
# packages/agents/registry.py
from packages.agents.base import Agent
from typing import Type

class AgentRegistry:
    """Registry for agent discovery and instantiation."""
    
    def __init__(self):
        self._agents: dict[str, Type[Agent]] = {}
    
    def register(self, name: str, agent_class: Type[Agent]) -> None:
        self._agents[name] = agent_class
    
    def get(self, name: str) -> Type[Agent] | None:
        return self._agents.get(name)
    
    def create(self, name: str, config: dict | None = None) -> Agent:
        agent_class = self.get(name)
        if not agent_class:
            raise ValueError(f"Unknown agent: {name}")
        return agent_class(config)
    
    def list_agents(self) -> list[dict]:
        return [
            {"name": name, "description": cls.description, "capabilities": cls.capabilities}
            for name, cls in self._agents.items()
        ]

# Global registry instance
registry = AgentRegistry()
```

### Tool System

```python
# packages/tools/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any

class ToolParameter(BaseModel):
    """JSON Schema for tool parameter."""
    name: str
    type: str
    description: str
    required: bool = True
    enum: list[Any] | None = None

class ToolSchema(BaseModel):
    """Tool definition for model consumption."""
    name: str
    description: str
    parameters: list[ToolParameter]
    returns: str

class Tool(ABC):
    """Base class for tools."""
    
    schema: ToolSchema
    permissions: list[str] = []  # Required permissions
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool."""
        pass
    
    def to_openai_format(self) -> dict:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.schema.name,
                "description": self.schema.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        p.name: {"type": p.type, "description": p.description}
                        for p in self.schema.parameters
                    },
                    "required": [p.name for p in self.schema.parameters if p.required],
                },
            },
        }
```

### Tool Registry

```python
# packages/tools/registry.py
from packages.tools.base import Tool

class ToolRegistry:
    """Registry for tool discovery and execution."""
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        self._tools[tool.schema.name] = tool
    
    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)
    
    def get_all(self) -> list[Tool]:
        return list(self._tools.values())
    
    def get_schemas(self) -> list[dict]:
        return [tool.to_openai_format() for tool in self._tools.values()]
    
    async def execute(self, name: str, **kwargs) -> Any:
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        return await tool.execute(**kwargs)

# Global registry
tool_registry = ToolRegistry()
```

### Built-in Tools

```python
# packages/tools/definitions/web_search.py
from packages.tools.base import Tool, ToolSchema, ToolParameter
import httpx
from packages.shared.config import settings

class WebSearchTool(Tool):
    """Search the web using a search API."""
    
    schema = ToolSchema(
        name="web_search",
        description="Search the web for information",
        parameters=[
            ToolParameter(name="query", type="string", description="Search query"),
            ToolParameter(name="max_results", type="integer", description="Max results", required=False),
        ],
        returns="List of search results with title, url, snippet",
    )
    permissions = ["web_access"]
    
    async def execute(self, query: str, max_results: int = 10) -> list[dict]:
        # Implementation uses configured search API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.search_api_url}/search",
                json={"query": query, "max_results": max_results},
                headers={"Authorization": f"Bearer {settings.search_api_key}"},
            )
            response.raise_for_status()
            return response.json()["results"]

# packages/tools/definitions/web_fetch.py
class WebFetchTool(Tool):
    """Fetch and extract content from a URL."""
    
    schema = ToolSchema(
        name="web_fetch",
        description="Fetch and extract readable content from a URL",
        parameters=[
            ToolParameter(name="url", type="string", description="URL to fetch"),
            ToolParameter(name="max_length", type="integer", description="Max content length", required=False),
        ],
        returns="Extracted text content",
    )
    permissions = ["web_access"]
    
    async def execute(self, url: str, max_length: int = 50000) -> str:
        # Implementation with readability extraction
        pass

# packages/tools/definitions/document_read.py
class DocumentReadTool(Tool):
    """Read content from an uploaded document."""
    
    schema = ToolSchema(
        name="document_read",
        description="Read content from an uploaded document by ID",
        parameters=[
            ToolParameter(name="document_id", type="string", description="Document ID"),
            ToolParameter(name="section", type="string", description="Section to read", required=False),
        ],
        returns="Document content",
    )
    permissions = ["document_access"]
    
    async def execute(self, document_id: str, section: str | None = None) -> str:
        # Implementation reads from document store
        pass
```

## Agent Memory

```python
# packages/agents/memory.py
from dataclasses import dataclass, field
from typing import Any
from collections import deque

@dataclass
class AgentMemory:
    """Agent memory with short-term and long-term storage."""
    
    # Short-term: recent conversation/context (bounded)
    short_term: deque = field(default_factory=lambda: deque(maxlen=20))
    
    # Long-term: key facts, findings (persisted)
    long_term: dict[str, Any] = field(default_factory=dict)
    
    # Working memory: current task state
    working: dict[str, Any] = field(default_factory=dict)
    
    def add_short_term(self, item: Any) -> None:
        self.short_term.append(item)
    
    def get_short_term(self, n: int = 10) -> list[Any]:
        return list(self.short_term)[-n:]
    
    def set_long_term(self, key: str, value: Any) -> None:
        self.long_term[key] = value
    
    def get_long_term(self, key: str, default: Any = None) -> Any:
        return self.long_term.get(key, default)
    
    def set_working(self, key: str, value: Any) -> None:
        self.working[key] = value
    
    def get_working(self, key: str, default: Any = None) -> Any:
        return self.working.get(key, default)
    
    def clear_working(self) -> None:
        self.working.clear()
```

## Orchestrator

```python
# packages/agents/orchestrator.py
from packages.agents.base import Agent, AgentContext, AgentResult
from packages.agents.registry import AgentRegistry
from packages.tools.registry import ToolRegistry
from packages.ai.providers.router import ModelRouter
from packages.research.models import ResearchTask
from packages.shared.logging import get_logger

logger = get_logger(__name__)

class AgentOrchestrator:
    """Orchestrates multi-agent research workflows."""
    
    def __init__(
        self,
        agent_registry: AgentRegistry,
        tool_registry: ToolRegistry,
        model_router: ModelRouter,
    ):
        self.agents = agent_registry
        self.tools = tool_registry
        self.router = model_router
    
    def create_context(self, job_id: str, task_id: str, request_id: str) -> AgentContext:
        return AgentContext(
            research_job_id=job_id,
            task_id=task_id,
            request_id=request_id,
            tools={t.schema.name: t for t in self.tools.get_all()},
            memory=AgentMemory(),
            model_router=self.router,
            config={},
        )
    
    async def run_agent(
        self,
        agent_name: str,
        task: ResearchTask,
        context: AgentContext,
    ) -> AgentResult:
        agent_class = self.agents.get(agent_name)
        if not agent_class:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        agent = agent_class()
        context.tools = {t.schema.name: t for t in self.tools.get_all()}
        context.model_router = self.router
        
        await agent.on_start(task, context)
        try:
            result = await agent.run(task, context)
            await agent.on_complete(result, context)
            return result
        except Exception as e:
            await agent.on_error(e, context)
            raise
    
    async def run_parallel(
        self,
        agent_tasks: list[tuple[str, ResearchTask]],
        context: AgentContext,
    ) -> list[AgentResult]:
        """Run multiple agents in parallel."""
        import asyncio
        tasks = [
            self.run_agent(agent_name, task, context)
            for agent_name, task in agent_tasks
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

## Initial Agent Implementations

### Planner Agent

```python
# packages/agents/planner/planner_agent.py
from packages.agents.base import Agent, AgentContext, AgentResult
from packages.research.models import ResearchTask, ResearchPlan, ResearchStep
from packages.ai.schemas import LLMRequest, LLMMessage
from packages.ai.providers.router import ModelRouter
from packages.ai.schemas import ModelCapabilities, ModelCapability
import json

class PlannerAgent(Agent):
    """Decomposes research requests into executable plans."""
    
    name = "planner"
    description = "Creates research plans from user requests"
    capabilities = {"planning", "task_decomposition"}
    
    SYSTEM_PROMPT = """You are a research planner. Given a research question, create a structured
    research plan as a JSON object with the following schema:
    {
        "objective": "Clear statement of research goal",
        "steps": [
            {
                "id": "step_1",
                "name": "Descriptive name",
                "description": "What this step accomplishes",
                "agent": "agent_name",
                "inputs": {"key": "value"},
                "depends_on": ["step_id"],
                "priority": 1
            }
        ],
        "expected_outputs": ["output_type1", "output_type2"]
    }
    
    Available agents: web_research, document_analysis, data_analysis, synthesis, report
    """
    
    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        router: ModelRouter = context.model_router
        llm = router.select_llm(ModelCapabilities.for_task("planning"))
        
        response = await llm.complete(LLMRequest(
            messages=[
                LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                LLMMessage(role="user", content=f"Research request: {task.objective}\n\nContext: {task.context}"),
            ],
            temperature=0.3,
            json_mode=True,
        ))
        
        try:
            plan_data = json.loads(response.content)
            plan = ResearchPlan(**plan_data)
            return AgentResult(
                success=True,
                output=plan,
                metadata={"model": response.model, "tokens": response.usage},
            )
        except Exception as e:
            return AgentResult(
                success=False,
                errors=[f"Failed to parse plan: {e}"],
            )
```

### Web Research Agent

```python
# packages/agents/research/web_agent.py
from packages.agents.base import Agent, AgentContext, AgentResult
from packages.research.models import ResearchTask, Evidence, Source
from packages.ai.schemas import LLMRequest, LLMMessage
from packages.ai.providers.router import ModelRouter
from packages.ai.schemas import ModelCapabilities
from packages.tools.registry import tool_registry
import uuid

class WebResearchAgent(Agent):
    """Searches and extracts information from the web."""
    
    name = "web_research"
    description = "Searches the web and extracts relevant information"
    capabilities = {"web_search", "content_extraction", "fact_finding"}
    
    SYSTEM_PROMPT = """You are a web research agent. Your task is to find relevant information
    for the given research question. Use the web_search tool to find sources, then web_fetch
    to retrieve content. Extract key facts, citations, and evidence.
    
    Always cite your sources with URLs. Be specific and factual.
    """
    
    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        router: ModelRouter = context.model_router
        llm = router.select_llm(ModelCapabilities.for_task("research"))
        
        # Get tools
        search_tool = tool_registry.get("web_search")
        fetch_tool = tool_registry.get("web_fetch")
        
        if not search_tool or not fetch_tool:
            return AgentResult(success=False, errors=["Required tools not available"])
        
        # Search
        search_results = await search_tool.execute(query=task.objective, max_results=10)
        
        evidence = []
        sources = []
        
        for result in search_results[:5]:  # Limit for MVP
            try:
                content = await fetch_tool.execute(url=result["url"])
                
                # Extract evidence using LLM
                extract_response = await llm.complete(LLMRequest(
                    messages=[
                        LLMMessage(role="system", content="Extract key facts from this content relevant to the research question. Return JSON array of {claim, evidence, confidence}."),
                        LLMMessage(role="user", content=f"Question: {task.objective}\n\nContent: {content[:10000]}"),
                    ],
                    temperature=0.2,
                    json_mode=True,
                ))
                
                # Parse and create evidence objects
                import json
                facts = json.loads(extract_response.content)
                
                source = Source(
                    id=str(uuid.uuid4()),
                    type="web",
                    url=result["url"],
                    title=result["title"],
                    metadata={"snippet": result.get("snippet")},
                )
                sources.append(source)
                
                for fact in facts:
                    evidence.append(Evidence(
                        id=str(uuid.uuid4()),
                        source_id=source.id,
                        claim=fact["claim"],
                        supporting_text=fact["evidence"],
                        confidence=fact.get("confidence", 0.7),
                    ))
                    
            except Exception as e:
                logger.warning(f"Failed to process {result['url']}: {e}")
                continue
        
        return AgentResult(
            success=True,
            output={"sources": sources, "evidence": evidence},
            evidence=evidence,
            metadata={"sources_found": len(sources), "evidence_count": len(evidence)},
        )
```

## Agent Execution Trace

For observability, every agent run produces a trace:

```python
# packages/agents/tracing.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class AgentTrace:
    """Execution trace for an agent run."""
    agent_name: str
    task_id: str
    job_id: str
    request_id: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    success: bool = False
    input: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    tool_calls: list[dict] = field(default_factory=list)
    model_calls: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    duration_ms: int = 0
    
    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "task_id": self.task_id,
            "job_id": self.job_id,
            "request_id": self.request_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "success": self.success,
            "input": self.input,
            "output": self.output,
            "tool_calls": self.tool_calls,
            "model_calls": self.model_calls,
            "errors": self.errors,
            "duration_ms": self.duration_ms,
        }
```

---

*Agent framework is designed for testability - all external dependencies (tools, models) are injected via context.*