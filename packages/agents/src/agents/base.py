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
    research_job_id: UUIDStr
    task_id: UUIDStr
    request_id: UUIDStr
    tools: dict[str, Any]  # Tool instances
    memory: AgentMemory
    model_router: ModelRouter
    config: dict[str, Any] = field(default_factory=dict)
    metadata: JSONDict = field(default_factory=dict)
    permissions: set[str] = field(default_factory=set)


@dataclass
class AgentResult:
    """Result of agent execution."""
    success: bool
    output: Any = None
    evidence: list[Any] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: JSONDict = field(default_factory=dict)


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