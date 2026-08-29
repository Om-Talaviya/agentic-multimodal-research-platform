"""Agent orchestrator for multi-agent coordination."""

import asyncio
import time
from uuid import uuid4
from typing import Any
from agents.base import Agent, AgentContext, AgentResult, AgentMemory
from agents.registry import AgentRegistry
from tools.registry import ToolRegistry
from ai.providers.router import ModelRouter
from shared.logging import get_logger

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
    
    def create_context(
        self,
        job_id: str,
        task_id: str,
        request_id: str,
        permissions: set[str] | None = None,
    ) -> AgentContext:
        return AgentContext(
            research_job_id=job_id,
            task_id=task_id,
            request_id=request_id,
            tools={t.schema.name: t for t in self.tools.get_all()},
            memory=AgentMemory(),
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
        agent_class = self.agents.get(agent_name)
        if not agent_class:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        agent = agent_class()
        start_time = time.time()
        
        # Create agent run record - lazy import
        from database.connection import get_session
        from database.repositories import AgentRunRepository
        from database.models import AgentRun
        
        async with get_session() as session:
            run_repo = AgentRunRepository(session)
            agent_run = AgentRun(
                id=str(uuid4()),
                job_id=context.research_job_id,
                task_id=context.task_id,
                agent_name=agent_name,
                request_id=context.request_id,
                input={"task_objective": task.objective, "task_type": task.type},
            )
            await run_repo.create(agent_run)
            run_id = agent_run.id
        
        await agent.on_start(task, context)
        
        try:
            result = await agent.run(task, context)
            duration_ms = int((time.time() - start_time) * 1000)
            
            await agent.on_complete(result, context)
            
            # Update agent run
            async with get_session() as session:
                run_repo = AgentRunRepository(session)
                await run_repo.complete(
                    run_id,
                    success=result.success,
                    output=result.output,
                    errors=result.errors,
                    duration_ms=duration_ms,
                )
            
            return result
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            await agent.on_error(e, context)
            
            # Update agent run with error
            async with get_session() as session:
                run_repo = AgentRunRepository(session)
                await run_repo.complete(
                    run_id,
                    success=False,
                    errors=[str(e)],
                    duration_ms=duration_ms,
                )
            
            logger.error("Agent run failed", agent=agent_name, task_id=context.task_id, error=str(e))
            raise
    
    async def run_parallel(
        self,
        agent_tasks: list[tuple[str, "ResearchTask"]],
        context: AgentContext,
    ) -> list[AgentResult | Exception]:
        """Run multiple agents in parallel."""
        tasks = [
            self.run_agent(agent_name, task, context)
            for agent_name, task in agent_tasks
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)