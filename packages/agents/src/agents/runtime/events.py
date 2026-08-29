"""Structured execution events for agent observability and streaming."""

import asyncio
import inspect
import time
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from shared.types import JSONDict


class AgentEvent(BaseModel):
    """Base class for all agent execution events."""

    model_config = ConfigDict(protected_namespaces=())

    event_type: str
    agent_id: str
    task_id: str
    timestamp: float = Field(default_factory=time.time)
    data: JSONDict = Field(default_factory=dict)


class AgentCreatedEvent(AgentEvent):
    event_type: str = "AgentCreated"


class AgentStartedEvent(AgentEvent):
    event_type: str = "AgentStarted"


class ModelRequestStartedEvent(AgentEvent):
    event_type: str = "ModelRequestStarted"
    model: Optional[str] = None
    prompt_tokens_est: Optional[int] = None


class ModelResponseReceivedEvent(AgentEvent):
    event_type: str = "ModelResponseReceived"
    model: Optional[str] = None
    latency_ms: Optional[int] = None
    tool_calls_requested: int = 0


class ToolCallRequestedEvent(AgentEvent):
    event_type: str = "ToolCallRequested"
    tool_name: str
    tool_call_id: str


class ToolCallStartedEvent(AgentEvent):
    event_type: str = "ToolCallStarted"
    tool_name: str
    tool_call_id: str


class ToolCallCompletedEvent(AgentEvent):
    event_type: str = "ToolCallCompleted"
    tool_name: str
    tool_call_id: str
    duration_ms: Optional[int] = None


class ToolCallFailedEvent(AgentEvent):
    event_type: str = "ToolCallFailed"
    tool_name: str
    tool_call_id: str
    error: str
    duration_ms: Optional[int] = None


class AgentIterationCompletedEvent(AgentEvent):
    event_type: str = "AgentIterationCompleted"
    iteration: int


class AgentWaitingForApprovalEvent(AgentEvent):
    event_type: str = "AgentWaitingForApproval"
    tool_name: str
    tool_call_id: str
    reason: Optional[str] = None


class AgentCompletedEvent(AgentEvent):
    event_type: str = "AgentCompleted"
    iterations: int = 1
    total_duration_ms: Optional[int] = None


class AgentFailedEvent(AgentEvent):
    event_type: str = "AgentFailed"
    error: str
    iterations: int = 1


class AgentCancelledEvent(AgentEvent):
    event_type: str = "AgentCancelled"
    reason: Optional[str] = None


class AgentTimedOutEvent(AgentEvent):
    event_type: str = "AgentTimedOut"
    timeout_seconds: float


class EventEmitter:
    """Dispatches execution events to registered subscribers."""

    def __init__(self) -> None:
        self._handlers: List[Callable[[AgentEvent], Any]] = []
        self._history: List[AgentEvent] = []

    def subscribe(self, handler: Callable[[AgentEvent], Any]) -> None:
        """Register a synchronous or asynchronous event callback."""
        if handler not in self._handlers:
            self._handlers.append(handler)

    def unsubscribe(self, handler: Callable[[AgentEvent], Any]) -> None:
        """Remove a callback."""
        if handler in self._handlers:
            self._handlers.remove(handler)

    async def emit(self, event: AgentEvent) -> None:
        """Record and broadcast event to all subscribers."""
        self._history.append(event)
        for handler in self._handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception:
                pass  # Handler errors do not interrupt agent execution

    @property
    def history(self) -> List[AgentEvent]:
        """Return event history."""
        return list(self._history)

    def clear(self) -> None:
        """Clear registered handlers and history."""
        self._handlers.clear()
        self._history.clear()
