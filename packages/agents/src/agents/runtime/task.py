"""Task model definitions for agent execution."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field
from shared.types import JSONDict


class AgentTask(BaseModel):
    """Structured task definition executed by the Agent Runtime."""

    model_config = ConfigDict(protected_namespaces=())

    task_id: str
    description: str
    input: Dict[str, Any] = Field(default_factory=dict)
    requested_capability: Optional[str] = None
    requested_model: Optional[str] = None
    timeout_seconds: float = 60.0
    max_iterations: int = 10
    max_tool_calls: int = 20
    priority: int = 5
    metadata: JSONDict = Field(default_factory=dict)
