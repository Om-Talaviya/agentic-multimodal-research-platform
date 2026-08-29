"""Safe tool executor enforcing permissions, timeouts, validation, and error boundaries."""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Set, Union
from pydantic import BaseModel, ConfigDict, Field

from tools.base import Permission, Tool
from tools.registry import ToolRegistry
from shared.logging import get_logger

logger = get_logger(__name__)


class ToolExecutionResult(BaseModel):
    """Structured result of a tool execution attempt."""

    model_config = ConfigDict(protected_namespaces=())

    success: bool
    tool_name: str
    tool_call_id: str
    output: Any = None
    error: Optional[str] = None
    duration_ms: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolPermissionDeniedError(Exception):
    """Raised when an agent attempts to execute a tool without required permissions."""

    pass


class ToolNotFoundError(Exception):
    """Raised when a requested tool does not exist."""

    pass


class ToolExecutor:
    """Safely executes tools with input validation, timeout boundaries, and permission checking."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        allowed_tools: Optional[List[str]] = None,
        allowed_permissions: Optional[Set[Union[Permission, str]]] = None,
        default_timeout_seconds: float = 30.0,
    ) -> None:
        self.tool_registry = tool_registry
        self.allowed_tools = set(allowed_tools) if allowed_tools is not None else None
        self.allowed_permissions = set(allowed_permissions or set())
        self.default_timeout_seconds = default_timeout_seconds
        self._tool_call_count = 0

    @property
    def total_calls(self) -> int:
        return self._tool_call_count

    def get_allowed_tool_schemas(self) -> List[dict]:
        """Return OpenAI-formatted function schemas for tools allowed to this agent."""
        all_tools = self.tool_registry.get_all()
        schemas = []
        for t in all_tools:
            name = t.schema.name
            if self.allowed_tools is not None and name not in self.allowed_tools:
                continue
            if t.schema.permissions:
                has_perms = all(
                    (p in self.allowed_permissions or (hasattr(p, "value") and p.value in self.allowed_permissions) or str(p) in self.allowed_permissions)
                    for p in t.schema.permissions
                )
                if not has_perms:
                    continue
            schemas.append(t.to_openai_format())
        return schemas

    async def execute_tool_call(
        self,
        tool_name: str,
        arguments: Union[Dict[str, Any], str],
        tool_call_id: str,
        timeout_seconds: Optional[float] = None,
    ) -> ToolExecutionResult:
        """Execute a tool call safely within permission, validation, and timeout boundaries."""
        self._tool_call_count += 1
        start_time = time.perf_counter()
        timeout = timeout_seconds or self.default_timeout_seconds

        # 1. Check if tool is allowed
        if self.allowed_tools is not None and tool_name not in self.allowed_tools:
            return ToolExecutionResult(
                success=False,
                tool_name=tool_name,
                tool_call_id=tool_call_id,
                error=f"Permission denied: tool '{tool_name}' is not in the allowed tool set",
                duration_ms=int((time.perf_counter() - start_time) * 1000),
            )

        # 2. Get tool instance
        tool = self.tool_registry.get(tool_name)
        if not tool:
            return ToolExecutionResult(
                success=False,
                tool_name=tool_name,
                tool_call_id=tool_call_id,
                error=f"Tool not found: '{tool_name}'",
                duration_ms=int((time.perf_counter() - start_time) * 1000),
            )

        # 3. Check tool permissions
        if tool.schema.permissions:
            for required_perm in tool.schema.permissions:
                perm_val = required_perm.value if hasattr(required_perm, "value") else str(required_perm)
                if required_perm not in self.allowed_permissions and perm_val not in self.allowed_permissions:
                    return ToolExecutionResult(
                        success=False,
                        tool_name=tool_name,
                        tool_call_id=tool_call_id,
                        error=f"Permission denied: missing required permission '{perm_val}' for tool '{tool_name}'",
                        duration_ms=int((time.perf_counter() - start_time) * 1000),
                    )

        # 4. Parse and validate arguments
        parsed_args: Dict[str, Any] = {}
        if isinstance(arguments, str):
            try:
                parsed_args = json.loads(arguments) if arguments.strip() else {}
            except json.JSONDecodeError as e:
                return ToolExecutionResult(
                    success=False,
                    tool_name=tool_name,
                    tool_call_id=tool_call_id,
                    error=f"Invalid JSON arguments: {str(e)}",
                    duration_ms=int((time.perf_counter() - start_time) * 1000),
                )
        elif isinstance(arguments, dict):
            parsed_args = arguments

        # 5. Execute with timeout
        try:
            output = await asyncio.wait_for(
                tool.execute(**parsed_args),
                timeout=timeout,
            )
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            return ToolExecutionResult(
                success=True,
                tool_name=tool_name,
                tool_call_id=tool_call_id,
                output=output,
                duration_ms=duration_ms,
            )
        except asyncio.TimeoutError:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            return ToolExecutionResult(
                success=False,
                tool_name=tool_name,
                tool_call_id=tool_call_id,
                error=f"Tool '{tool_name}' execution timed out after {timeout}s",
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.warning("Tool execution error", tool=tool_name, error=str(e))
            return ToolExecutionResult(
                success=False,
                tool_name=tool_name,
                tool_call_id=tool_call_id,
                error=f"Tool error: {str(e)}",
                duration_ms=duration_ms,
            )
