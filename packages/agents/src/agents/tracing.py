"""Agent observability and execution tracing framework."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4
from shared.logging import get_logger

logger = get_logger(__name__)


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class ToolCallTrace:
    """Trace record for an individual tool execution."""

    tool_name: str
    arguments: Dict[str, Any]
    output: Any = None
    success: bool = True
    error: Optional[str] = None
    duration_ms: int = 0
    timestamp: datetime = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "output": str(self.output)[:1000] if self.output is not None else None,
            "success": self.success,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ModelCallTrace:
    """Trace record for an individual model API call."""

    provider: str
    model: str
    request_type: str = "complete"  # complete, stream, vision, embed
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    success: bool = True
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "request_type": self.request_type,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class AgentTrace:
    """Execution trace for an agent run session."""

    agent_name: str
    task_id: str
    job_id: str
    request_id: str
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: datetime = field(default_factory=utc_now)
    completed_at: Optional[datetime] = None
    success: bool = False
    input: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    tool_calls: List[ToolCallTrace] = field(default_factory=list)
    model_calls: List[ModelCallTrace] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: int = 0

    def add_tool_call(self, tool_call: ToolCallTrace) -> None:
        """Append a tool call trace."""
        self.tool_calls.append(tool_call)

    def add_model_call(self, model_call: ModelCallTrace) -> None:
        """Append a model call trace."""
        self.model_calls.append(model_call)

    def complete(self, success: bool, output: Optional[Dict[str, Any]] = None, errors: Optional[List[str]] = None) -> None:
        """Mark the trace as finished and compute total duration."""
        self.completed_at = utc_now()
        self.success = success
        if output is not None:
            self.output = output
        if errors:
            self.errors.extend(errors)
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "agent_name": self.agent_name,
            "task_id": self.task_id,
            "job_id": self.job_id,
            "request_id": self.request_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "success": self.success,
            "input": self.input,
            "output": self.output,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "model_calls": [mc.to_dict() for mc in self.model_calls],
            "errors": self.errors,
            "duration_ms": self.duration_ms,
        }
