"""Agent base classes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID
from tools.registry import ToolRegistry
from ai.providers.router import ModelRouter
from shared.types import JSONDict, UUIDStr


@dataclass
class AgentMemory:
    """Agent memory with short-term and long-term storage."""
    
    short_term: list[Any] = field(default_factory=list)
    long_term: dict[str, Any] = field(default_factory=dict)
    working: dict[str, Any] = field(default_factory=dict)
    
    def add_short_term(self, item: Any) -> None:
        self.short_term.append(item)
        # Keep last 20 items
        if len(self.short_term) > 20:
            self.short_term = self.short_term[-20:]
    
    def get_short_term(self, n: int = 10) -> list[Any]:
        return self.short_term[-n:]
    
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


@dataclass
class AgentContext:
    """Shared context passed to agents during execution."""
    research_job_id: UUIDStr = "default-job"
    task_id: UUIDStr = "default-task"
    request_id: UUIDStr = "default-req"
    tools: dict[str, Any] = field(default_factory=dict)
    memory: AgentMemory = field(default_factory=AgentMemory)
    model_router: Optional[ModelRouter] = None
    model_gateway: Optional[Any] = None
    config: dict[str, Any] = field(default_factory=dict)
    metadata: JSONDict = field(default_factory=dict)
    permissions: set[str] = field(default_factory=set)
    user_id: Optional[Any] = None
    workspace_id: Optional[Any] = None
    project_id: Optional[Any] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert context summary to dictionary for logging and model dispatch."""
        uid = self.user_id or self.metadata.get("user_id")
        return {
            "research_job_id": str(self.research_job_id),
            "task_id": str(self.task_id),
            "request_id": str(self.request_id),
            "user_id": str(uid) if uid else None,
            "workspace_id": str(self.workspace_id) if self.workspace_id else None,
            "project_id": str(self.project_id) if self.project_id else None,
            "config": self.config,
            "metadata": self.metadata,
        }

    async def complete_llm(
        self,
        request: Any,
        task: Optional[str] = None,
    ) -> Any:
        """Helper to invoke completion via gateway (with telemetry & user_id) or fallback to router."""
        req_meta = dict(getattr(request, "metadata", {}) or {})
        uid = self.user_id or self.metadata.get("user_id")
        if "user_id" not in req_meta and uid:
            req_meta["user_id"] = str(uid)
        if "job_id" not in req_meta:
            req_meta["job_id"] = str(self.research_job_id)
        if "task_id" not in req_meta:
            req_meta["task_id"] = str(self.task_id)

        current_req = request.model_copy(update={"metadata": req_meta}) if hasattr(request, "model_copy") else request

        if self.model_gateway:
            return await self.model_gateway.complete(current_req, task=task)
        elif self.model_router:
            from ai.schemas import ModelCapabilities
            caps = ModelCapabilities.for_task(task or "research") if task else None
            llm = self.model_router.select_llm(caps)
            return await llm.complete(current_req)
        else:
            raise ValueError("Neither model_gateway nor model_router is configured on AgentContext")


@dataclass
class AgentResult:
    """Result of agent execution."""
    success: bool
    output: Any = None
    evidence: list[Any] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: JSONDict = field(default_factory=dict)
    task_id: Optional[str] = None
    agent_name: Optional[str] = None


class Agent(ABC):
    """Base class for all agents."""
    
    name: str
    description: str = ""
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


# Forward reference
class ResearchTask:
    pass