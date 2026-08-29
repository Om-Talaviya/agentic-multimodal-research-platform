"""Main research pipeline orchestration."""

from uuid import uuid4
from datetime import datetime
from research.models import ResearchRequest, ResearchJob, ResearchPlan, ResearchTask
from agents.orchestrator import AgentOrchestrator
from agents.registry import AgentRegistry
from tools.registry import ToolRegistry
from ai.providers.router import ModelRouter
from shared.logging import get_logger

logger = get_logger(__name__)


class ResearchPipeline:
    """Orchestrates the full research pipeline."""
    
    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        agent_registry: AgentRegistry,
        tool_registry: ToolRegistry,
        model_router: ModelRouter,
    ):
        self.orchestrator = orchestrator
        self.agent_registry = agent_registry
        self.tool_registry = tool_registry
        self.model_router = model_router
    
    async def create_job(self, request: ResearchRequest) -> ResearchJob:
        """Create a new research job from request."""
        # For now, create a basic job - planner will enhance
        job = ResearchJob(
            request_id=str(uuid4()),
            question=request.question,
            objective=request.question,
            constraints=request.constraints,
        )
        
        from database.connection import get_session
        from database.repositories import ResearchJobRepository
        
        async with get_session() as session:
            repo = ResearchJobRepository(session)
            await repo.create(job)
        
        logger.info("Research job created", job_id=job.id)
        return job
    
    async def run_planning(self, job: ResearchJob) -> ResearchPlan:
        """Run planner agent to create research plan."""
        from agents.planner.planner_agent import PlannerAgent
        
        planner = PlannerAgent()
        task = ResearchTask(
            id=str(uuid4()),
            job_id=job.id,
            type="planning",
            objective=job.objective,
            agent="planner",
            context={
                "domain": job.domain,
                "scope": job.scope,
                "constraints": job.constraints,
            },
        )
        
        context = self.orchestrator.create_context(job.id, task.id, job.request_id)
        result = await planner.run(task, context)
        
        if not result.success:
            raise ValueError(f"Planning failed: {result.errors}")
        
        return result.output
    
    async def execute_plan(self, job: ResearchJob, plan: ResearchPlan) -> None:
        """Execute research plan tasks."""
        # Build task DAG
        step_map = {step.id: step for step in plan.steps}
        tasks = {}
        for step in plan.steps:
            tasks[step.id] = ResearchTask(
                id=str(uuid4()),
                job_id=job.id,
                type=step.agent,
                objective=step.description,
                agent=step.agent,
                inputs=step.inputs,
                depends_on=step.depends_on,
                priority=step.priority,
            )
        
        from database.connection import get_session
        from database.repositories import TaskRepository, SourceRepository, EvidenceRepository
        from shared.types import TaskStatus, JobStatus
        
        async with get_session() as session:
            task_repo = TaskRepository(session)
            await task_repo.create_batch(list(tasks.values()))
        
        completed = set()
        
        while len(completed) < len(tasks):
            # Find ready tasks
            ready = [
                t for t in tasks.values()
                if t.id not in completed
                and all(dep in completed for dep in t.depends_on)
            ]
            
            if not ready:
                raise ValueError("Circular dependency or no ready tasks")
            
            # Execute ready tasks
            contexts = [
                self.orchestrator.create_context(job.id, t.id, job.request_id)
                for t in ready
            ]
            
            agent_tasks = [(t.agent, t) for t in ready]
            results = await self.orchestrator.run_parallel(agent_tasks, contexts[0])
            
            # Process results
            async with get_session() as session:
                task_repo = TaskRepository(session)
                source_repo = SourceRepository(session)
                evidence_repo = EvidenceRepository(session)
                
                for task, result in zip(ready, results):
                    if isinstance(result, Exception):
                        await task_repo.update_status(task.id, TaskStatus.FAILED, str(result))
                        logger.error("Task failed", task_id=task.id, error=str(result))
                    else:
                        await task_repo.update_status(task.id, TaskStatus.COMPLETED, result=result.output)
                        
                        # Store sources and evidence
                        if result.output and isinstance(result.output, dict):
                            if "sources" in result.output:
                                await source_repo.create_batch(result.output["sources"])
                            if "evidence" in result.output:
                                for ev in result.output["evidence"]:
                                    ev.job_id = job.id
                                await evidence_repo.create_batch(result.output["evidence"])
                        
                    completed.add(task.id)
    
    async def run_verification(self, job: ResearchJob) -> None:
        """Run critic agent to evaluate and verify collected evidence."""
        from uuid import UUID
        from database.connection import get_session
        from database.repositories import EvidenceRepository

        try:
            job_uuid = UUID(str(job.id))
            async with get_session() as session:
                evidence_repo = EvidenceRepository(session)
                evidence_list = await evidence_repo.get_by_job(job_uuid)

            if not evidence_list:
                logger.info("No evidence to verify for job", job_id=job.id)
                return

            critic_result = await self.orchestrator.run_critic(
                evidence=evidence_list,
                question=job.question,
                job_id=str(job.id),
                request_id=str(job.request_id),
            )

            if critic_result.success and isinstance(critic_result.output, dict):
                verifications = critic_result.output.get("verifications", [])
                async with get_session() as session:
                    evidence_repo = EvidenceRepository(session)
                    for item in verifications:
                        ev_id = item.get("evidence_id")
                        if ev_id:
                            try:
                                await evidence_repo.update_verification(
                                    evidence_id=UUID(str(ev_id)),
                                    status=item.get("verification_status", "verified"),
                                    confidence=item.get("confidence"),
                                    notes=item.get("verification_notes"),
                                )
                            except Exception as update_err:
                                logger.warning("Could not update verification for evidence", evidence_id=ev_id, error=str(update_err))
        except Exception as verif_err:
            logger.warning("Evidence verification step encountered error", job_id=job.id, error=str(verif_err))

    async def run(self, request: ResearchRequest) -> ResearchJob:
        """Run full research pipeline."""
        job = await self.create_job(request)
        
        try:
            from database.connection import get_session
            from database.repositories import ResearchJobRepository
            from shared.types import JobStatus
            
            async with get_session() as session:
                repo = ResearchJobRepository(session)
                await repo.update_status(job.id, JobStatus.RUNNING)
            
            # Planning
            plan = await self.run_planning(job)
            
            # Execution
            await self.execute_plan(job, plan)
            
            # Verification using Critic Agent
            await self.run_verification(job)
            
            async with get_session() as session:
                repo = ResearchJobRepository(session)
                await repo.update_status(job.id, JobStatus.COMPLETED)
            
        except Exception as e:
            logger.error("Research pipeline failed", job_id=job.id, error=str(e))
            from database.connection import get_session
            from database.repositories import ResearchJobRepository
            from shared.types import JobStatus
            async with get_session() as session:
                repo = ResearchJobRepository(session)
                await repo.update_status(job.id, JobStatus.FAILED, str(e))
            raise
        
        return job