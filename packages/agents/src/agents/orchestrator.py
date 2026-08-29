"""Agent orchestrator for multi-agent coordination, resilient execution, and tracing."""

import asyncio
import time
from typing import Any, List, Optional, Set, Tuple
from uuid import uuid4
from agents.base import Agent, AgentContext, AgentResult
from agents.memory import AgentMemory
from agents.registry import AgentRegistry
from agents.tracing import AgentTrace, ToolCallTrace, ModelCallTrace
from tools.registry import ToolRegistry
from ai.providers.router import ModelRouter
from shared.logging import get_logger

logger = get_logger(__name__)


class AgentOrchestrator:
    """Orchestrates multi-agent research workflows with retries, tracing, and structured memory."""

    def __init__(
        self,
        agent_registry: AgentRegistry,
        tool_registry: ToolRegistry,
        model_router: ModelRouter,
        max_retries: int = 2,
        retry_delay_seconds: float = 1.0,
    ):
        self.agents = agent_registry
        self.tools = tool_registry
        self.router = model_router
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    def create_context(
        self,
        job_id: str,
        task_id: str,
        request_id: str,
        permissions: Optional[Set[str]] = None,
        memory: Optional[AgentMemory] = None,
    ) -> AgentContext:
        """Create execution context with tools, memory, and model routing."""
        return AgentContext(
            research_job_id=job_id,
            task_id=task_id,
            request_id=request_id,
            tools={t.schema.name: t for t in self.tools.get_all()},
            memory=memory or AgentMemory(),
            model_router=self.router,
            config={},
            permissions=permissions or {"web_access", "document_access"},
        )

    async def run_agent(
        self,
        agent_name: str,
        task: "ResearchTask",
        context: AgentContext,
    ) -> AgentResult:
        """Run an agent with tracing, lifecycle hooks, and retry handling."""
        agent_class = self.agents.get(agent_name)
        if not agent_class:
            raise ValueError(f"Unknown agent: {agent_name}")

        agent = agent_class()
        trace = AgentTrace(
            agent_name=agent_name,
            task_id=context.task_id,
            job_id=context.research_job_id,
            request_id=context.request_id,
            input={"task_objective": task.objective, "task_type": getattr(task, "type", agent_name)},
        )

        # Lazy import database models to avoid circular dependencies
        from database.connection import get_session
        from database.repositories import AgentRunRepository
        from database.models import AgentRun

        run_id = str(uuid4())
        try:
            async with get_session() as session:
                run_repo = AgentRunRepository(session)
                agent_run = AgentRun(
                    id=run_id,
                    job_id=context.research_job_id,
                    task_id=context.task_id,
                    agent_name=agent_name,
                    request_id=context.request_id,
                    input=trace.input,
                )
                await run_repo.create(agent_run)
        except Exception as db_init_err:
            logger.warning("Could not persist initial agent run", error=str(db_init_err))

        await agent.on_start(task, context)

        attempts = 0
        last_error: Optional[Exception] = None
        result: Optional[AgentResult] = None

        while attempts <= self.max_retries:
            attempts += 1
            try:
                result = await agent.run(task, context)
                if result.success:
                    break
                else:
                    logger.warning("Agent returned unsuccessful result", agent=agent_name, attempt=attempts, errors=result.errors)
                    if attempts <= self.max_retries:
                        await asyncio.sleep(self.retry_delay_seconds * attempts)
            except Exception as exc:
                last_error = exc
                logger.warning("Agent execution raised exception", agent=agent_name, attempt=attempts, error=str(exc))
                if attempts <= self.max_retries:
                    await asyncio.sleep(self.retry_delay_seconds * attempts)

        # Finalize execution
        if result and result.success:
            trace.complete(success=True, output=result.output if isinstance(result.output, dict) else {"result": str(result.output)})
            await agent.on_complete(result, context)
        else:
            errors = result.errors if result else [str(last_error) if last_error else "Unknown execution error"]
            trace.complete(success=False, errors=errors)
            if last_error:
                await agent.on_error(last_error, context)
            result = result or AgentResult(success=False, errors=errors)

        # Update trace and DB record
        try:
            async with get_session() as session:
                run_repo = AgentRunRepository(session)
                await run_repo.complete(
                    run_id,
                    success=trace.success,
                    output=trace.output,
                    errors=trace.errors,
                    duration_ms=trace.duration_ms,
                )
        except Exception as db_complete_err:
            logger.warning("Could not persist completed agent run", error=str(db_complete_err))

        return result

    async def run_parallel(
        self,
        agent_tasks: List[Tuple[str, "ResearchTask"]],
        context: AgentContext,
    ) -> List[AgentResult | Exception]:
        """Run multiple agents in parallel with error isolation."""
        tasks = [
            self.run_agent(agent_name, task, context)
            for agent_name, task in agent_tasks
        ]
        return list(await asyncio.gather(*tasks, return_exceptions=True))

    async def run_critic(
        self,
        evidence: List[Any],
        question: str,
        job_id: str,
        request_id: str,
    ) -> AgentResult:
        """Helper to invoke CriticAgent on accumulated evidence."""
        from research.models import ResearchTask

        critic_task = ResearchTask(
            id=str(uuid4()),
            job_id=job_id,
            type="critic",
            objective=f"Critique and verify findings for: {question}",
            agent="critic",
            inputs={"evidence": evidence, "question": question},
        )
        context = self.create_context(job_id=job_id, task_id=critic_task.id, request_id=request_id)
        return await self.run_agent("critic", critic_task, context)