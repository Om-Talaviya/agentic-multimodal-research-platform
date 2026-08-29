"""Agent Runtime execution engine managing loops, timeouts, cancellation, and events."""

import asyncio
import time
from typing import Any, Callable, Dict, List, Optional, Set, Union
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field

from agents.base import AgentMemory
from agents.runtime.events import (
    AgentCancelledEvent,
    AgentCompletedEvent,
    AgentCreatedEvent,
    AgentEvent,
    AgentFailedEvent,
    AgentIterationCompletedEvent,
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
from agents.runtime.state import AgentState, AgentStateMachine, InvalidStateTransitionError
from agents.runtime.task import AgentTask
from agents.runtime.tools import ToolExecutionResult, ToolExecutor
from ai.gateway.model_gateway import ModelGateway
from ai.schemas import LLMMessage, LLMRequest, MessageRole
from shared.exceptions import ProviderError, ProviderUnavailableError
from shared.logging import get_logger
from shared.types import JSONDict
from tools.base import Permission
from tools.registry import ToolRegistry, tool_registry as default_tool_registry

logger = get_logger(__name__)


class AgentExecutionResult(BaseModel):
    """Complete result from an AgentRuntime execution."""

    model_config = ConfigDict(protected_namespaces=())

    agent_id: str
    task_id: str
    success: bool
    state: AgentState
    output: Any = None
    iterations: int = 0
    total_tool_calls: int = 0
    errors: List[str] = Field(default_factory=list)
    duration_ms: int = 0
    telemetry: JSONDict = Field(default_factory=dict)
    events: List[AgentEvent] = Field(default_factory=list)


class AgentRuntime:
    """Execution engine for safe, provider-agnostic agents."""

    def __init__(
        self,
        gateway: ModelGateway,
        tool_registry: Optional[ToolRegistry] = None,
        event_emitter: Optional[EventEmitter] = None,
        approval_hook: Optional[Callable[[str, str, Dict[str, Any]], bool]] = None,
    ) -> None:
        self.gateway = gateway
        self.tool_registry = tool_registry or default_tool_registry
        self.event_emitter = event_emitter or EventEmitter()
        self.approval_hook = approval_hook  # returns True if approval required: hook(agent_id, tool_name, args)
        self._cancellation_flags: Dict[str, bool] = {}
        self._pending_approvals: Dict[str, asyncio.Event] = {}
        self._approval_decisions: Dict[str, bool] = {}

    def cancel(self, agent_id: str, reason: Optional[str] = None) -> None:
        """Signal cancellation for a running agent."""
        self._cancellation_flags[agent_id] = True
        logger.info("Cancellation requested for agent", agent_id=agent_id, reason=reason)

    def is_cancelled(self, agent_id: str) -> bool:
        """Check if an agent has been cancelled."""
        return self._cancellation_flags.get(agent_id, False)

    def approve(self, agent_id: str, tool_call_id: str) -> None:
        """Approve a paused tool call."""
        key = f"{agent_id}:{tool_call_id}"
        self._approval_decisions[key] = True
        if key in self._pending_approvals:
            self._pending_approvals[key].set()

    def reject(self, agent_id: str, tool_call_id: str) -> None:
        """Reject a paused tool call."""
        key = f"{agent_id}:{tool_call_id}"
        self._approval_decisions[key] = False
        if key in self._pending_approvals:
            self._pending_approvals[key].set()

    async def execute(
        self,
        task: AgentTask,
        agent_id: Optional[str] = None,
        agent_name: str = "general_agent",
        allowed_tools: Optional[List[str]] = None,
        allowed_permissions: Optional[Set[Union[Permission, str]]] = None,
        system_prompt: Optional[str] = None,
        custom_memory: Optional[AgentMemory] = None,
        auto_approve: bool = False,
    ) -> AgentExecutionResult:
        """Run the bounded agent execution loop for a task."""
        agent_id = agent_id or str(uuid4())
        start_time = time.perf_counter()
        state_machine = AgentStateMachine(AgentState.CREATED)
        self._cancellation_flags[agent_id] = False
        memory = custom_memory or AgentMemory()

        # Tool executor for this agent
        tool_executor = ToolExecutor(
            tool_registry=self.tool_registry,
            allowed_tools=allowed_tools,
            allowed_permissions=allowed_permissions,
        )
        tool_schemas = tool_executor.get_allowed_tool_schemas()

        # Emit AgentCreated
        await self.event_emitter.emit(
            AgentCreatedEvent(
                agent_id=agent_id,
                task_id=task.task_id,
                data={"agent_name": agent_name, "priority": task.priority},
            )
        )

        # Transition to RUNNING
        state_machine.transition_to(AgentState.RUNNING)
        await self.event_emitter.emit(
            AgentStartedEvent(
                agent_id=agent_id,
                task_id=task.task_id,
                data={"task_description": task.description},
            )
        )

        # Build initial message history
        messages: List[LLMMessage] = []
        if system_prompt:
            messages.append(LLMMessage(role=MessageRole.SYSTEM, content=system_prompt))
        else:
            messages.append(
                LLMMessage(
                    role=MessageRole.SYSTEM,
                    content=f"You are an AI research assistant ({agent_name}). Complete the task accurately.",
                )
            )

        # Initial user task message
        user_content = f"Task: {task.description}"
        if task.input:
            user_content += f"\nInput data: {task.input}"
        messages.append(LLMMessage(role=MessageRole.USER, content=user_content))

        iteration = 0
        final_output: Any = None
        errors: List[str] = []
        last_model_used: Optional[str] = None
        last_provider_used: Optional[str] = None

        try:
            while iteration < task.max_iterations:
                iteration += 1

                # 1. Check Cancellation
                if self.is_cancelled(agent_id):
                    state_machine.transition_to(AgentState.CANCELLED)
                    await self.event_emitter.emit(
                        AgentCancelledEvent(agent_id=agent_id, task_id=task.task_id, reason="User cancelled")
                    )
                    break

                # 2. Check Execution Timeout
                elapsed = time.perf_counter() - start_time
                if elapsed > task.timeout_seconds:
                    state_machine.transition_to(AgentState.TIMED_OUT)
                    await self.event_emitter.emit(
                        AgentTimedOutEvent(
                            agent_id=agent_id,
                            task_id=task.task_id,
                            timeout_seconds=task.timeout_seconds,
                        )
                    )
                    errors.append(f"Agent execution timed out after {task.timeout_seconds}s")
                    break

                # 3. Call Model Gateway
                llm_req = LLMRequest(
                    messages=messages,
                    model=task.requested_model,
                    tools=tool_schemas if tool_schemas else None,
                    tool_choice="auto" if tool_schemas else "none",
                )

                await self.event_emitter.emit(
                    ModelRequestStartedEvent(
                        agent_id=agent_id,
                        task_id=task.task_id,
                        model=task.requested_model,
                    )
                )

                try:
                    remaining_timeout = max(5.0, task.timeout_seconds - elapsed)
                    model_res = await asyncio.wait_for(
                        self.gateway.complete(
                            request=llm_req,
                            task=task.requested_capability,
                            fallback_enabled=True,
                        ),
                        timeout=remaining_timeout,
                    )
                except asyncio.TimeoutError:
                    state_machine.transition_to(AgentState.TIMED_OUT)
                    await self.event_emitter.emit(
                        AgentTimedOutEvent(
                            agent_id=agent_id,
                            task_id=task.task_id,
                            timeout_seconds=task.timeout_seconds,
                        )
                    )
                    errors.append("Model call timed out")
                    break
                except Exception as e:
                    logger.error("Model Gateway error during agent run", agent_id=agent_id, error=str(e))
                    errors.append(f"Model error: {str(e)}")
                    state_machine.transition_to(AgentState.FAILED)
                    await self.event_emitter.emit(
                        AgentFailedEvent(agent_id=agent_id, task_id=task.task_id, error=str(e), iterations=iteration)
                    )
                    break

                last_model_used = model_res.model
                last_provider_used = model_res.metadata.get("provider")
                telemetry_data = model_res.metadata.get("telemetry", {})
                latency_ms = telemetry_data.get("latency_ms")

                await self.event_emitter.emit(
                    ModelResponseReceivedEvent(
                        agent_id=agent_id,
                        task_id=task.task_id,
                        model=model_res.model,
                        latency_ms=latency_ms,
                        tool_calls_requested=len(model_res.tool_calls) if model_res.tool_calls else 0,
                    )
                )

                # Append assistant response to messages and memory
                assistant_msg = LLMMessage(
                    role=MessageRole.ASSISTANT,
                    content=model_res.content or "",
                    tool_calls=model_res.tool_calls,
                )
                messages.append(assistant_msg)
                memory.add_short_term(assistant_msg)

                # 4. Handle Tool Calls if requested
                if model_res.tool_calls and len(model_res.tool_calls) > 0:
                    if tool_executor.total_calls >= task.max_tool_calls:
                        errors.append(f"Maximum tool calls limit ({task.max_tool_calls}) reached")
                        state_machine.transition_to(AgentState.FAILED)
                        await self.event_emitter.emit(
                            AgentFailedEvent(
                                agent_id=agent_id,
                                task_id=task.task_id,
                                error="Tool call limit exceeded",
                                iterations=iteration,
                            )
                        )
                        break

                    for tool_call in model_res.tool_calls:
                        tool_call_id = tool_call.get("id") or str(uuid4())
                        func_info = tool_call.get("function", {})
                        t_name = func_info.get("name", "")
                        t_args = func_info.get("arguments", {})

                        await self.event_emitter.emit(
                            ToolCallRequestedEvent(
                                agent_id=agent_id,
                                task_id=task.task_id,
                                tool_name=t_name,
                                tool_call_id=tool_call_id,
                            )
                        )

                        # Check human approval hook
                        requires_approval = False
                        if self.approval_hook and not auto_approve:
                            requires_approval = self.approval_hook(agent_id, t_name, t_args if isinstance(t_args, dict) else {})

                        if requires_approval:
                            approval_key = f"{agent_id}:{tool_call_id}"
                            event_obj = asyncio.Event()
                            self._pending_approvals[approval_key] = event_obj

                            state_machine.transition_to(AgentState.WAITING_FOR_APPROVAL)
                            await self.event_emitter.emit(
                                AgentWaitingForApprovalEvent(
                                    agent_id=agent_id,
                                    task_id=task.task_id,
                                    tool_name=t_name,
                                    tool_call_id=tool_call_id,
                                )
                            )
                            
                            # Wait for approval signal or timeout if not already decided
                            if approval_key not in self._approval_decisions:
                                try:
                                    await asyncio.wait_for(event_obj.wait(), timeout=10.0)
                                except asyncio.TimeoutError:
                                    pass

                            approved = self._approval_decisions.get(approval_key, False)
                            state_machine.transition_to(AgentState.RUNNING)

                            if not approved:
                                # Tool call rejected
                                tool_res = ToolExecutionResult(
                                    success=False,
                                    tool_name=t_name,
                                    tool_call_id=tool_call_id,
                                    error="Tool execution rejected by human operator",
                                )
                                tool_msg = LLMMessage(
                                    role=MessageRole.TOOL,
                                    content=f"Error: {tool_res.error}",
                                    tool_call_id=tool_call_id,
                                    name=t_name,
                                )
                                messages.append(tool_msg)
                                memory.add_short_term(tool_msg)
                                continue

                        # Execute tool
                        state_machine.transition_to(AgentState.WAITING_FOR_TOOL)
                        await self.event_emitter.emit(
                            ToolCallStartedEvent(
                                agent_id=agent_id,
                                task_id=task.task_id,
                                tool_name=t_name,
                                tool_call_id=tool_call_id,
                            )
                        )

                        tool_res = await tool_executor.execute_tool_call(
                            tool_name=t_name,
                            arguments=t_args,
                            tool_call_id=tool_call_id,
                        )

                        state_machine.transition_to(AgentState.RUNNING)

                        if tool_res.success:
                            await self.event_emitter.emit(
                                ToolCallCompletedEvent(
                                    agent_id=agent_id,
                                    task_id=task.task_id,
                                    tool_name=t_name,
                                    tool_call_id=tool_call_id,
                                    duration_ms=tool_res.duration_ms,
                                )
                            )
                            tool_content = str(tool_res.output)
                        else:
                            await self.event_emitter.emit(
                                ToolCallFailedEvent(
                                    agent_id=agent_id,
                                    task_id=task.task_id,
                                    tool_name=t_name,
                                    tool_call_id=tool_call_id,
                                    error=tool_res.error or "Unknown tool error",
                                    duration_ms=tool_res.duration_ms,
                                )
                            )
                            tool_content = f"Error: {tool_res.error}"

                        tool_msg = LLMMessage(
                            role=MessageRole.TOOL,
                            content=tool_content,
                            tool_call_id=tool_call_id,
                            name=t_name,
                        )
                        messages.append(tool_msg)
                        memory.add_short_term(tool_msg)

                    await self.event_emitter.emit(
                        AgentIterationCompletedEvent(
                            agent_id=agent_id,
                            task_id=task.task_id,
                            iteration=iteration,
                        )
                    )
                    continue

                # 5. Model provided text output without tool calls -> Task Complete!
                final_output = model_res.content
                state_machine.transition_to(AgentState.COMPLETED)
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                await self.event_emitter.emit(
                    AgentCompletedEvent(
                        agent_id=agent_id,
                        task_id=task.task_id,
                        iterations=iteration,
                        total_duration_ms=duration_ms,
                    )
                )
                break

            # If loop finished without terminal state, iteration limit was reached
            if not state_machine.is_terminal:
                state_machine.transition_to(AgentState.FAILED)
                errors.append(f"Iteration limit reached ({task.max_iterations}) without final answer")
                await self.event_emitter.emit(
                    AgentFailedEvent(
                        agent_id=agent_id,
                        task_id=task.task_id,
                        error="Iteration limit exceeded",
                        iterations=iteration,
                    )
                )

        except Exception as e:
            logger.exception("Unexpected error in agent execution loop", agent_id=agent_id)
            if not state_machine.is_terminal:
                state_machine.transition_to(AgentState.FAILED)
            errors.append(str(e))
            await self.event_emitter.emit(
                AgentFailedEvent(
                    agent_id=agent_id,
                    task_id=task.task_id,
                    error=str(e),
                    iterations=iteration,
                )
            )

        duration_ms = int((time.perf_counter() - start_time) * 1000)
        success = state_machine.state == AgentState.COMPLETED

        telemetry = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "task_id": task.task_id,
            "state": state_machine.state.value,
            "iterations": iteration,
            "total_tool_calls": tool_executor.total_calls,
            "duration_ms": duration_ms,
            "model_used": last_model_used,
            "provider_used": last_provider_used,
            "success": success,
        }

        return AgentExecutionResult(
            agent_id=agent_id,
            task_id=task.task_id,
            success=success,
            state=state_machine.state,
            output=final_output,
            iterations=iteration,
            total_tool_calls=tool_executor.total_calls,
            errors=errors,
            duration_ms=duration_ms,
            telemetry=telemetry,
            events=self.event_emitter.history,
        )
