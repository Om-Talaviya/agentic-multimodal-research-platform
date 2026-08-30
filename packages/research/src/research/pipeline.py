"""Main research pipeline orchestration."""

from uuid import uuid4
from datetime import datetime
from research.models import ResearchRequest, ResearchJob, ResearchPlan, ResearchTask, Source, Evidence
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

    async def run_report_generation(self, job: ResearchJob) -> None:
        """Run report agent to synthesize verified evidence into a report and persist it."""
        from uuid import UUID
        from database.connection import get_session
        from database.repositories import EvidenceRepository, SourceRepository, ReportRepository
        from database.models import Report as ReportModel

        try:
            job_uuid = UUID(str(job.id))

            # Get verified evidence and sources
            async with get_session() as session:
                evidence_repo = EvidenceRepository(session)
                source_repo = SourceRepository(session)
                evidence_list = await evidence_repo.get_by_job(job_uuid)
                sources = await source_repo.get_by_job(job_uuid)

            if not evidence_list:
                logger.info("No evidence to generate report for job", job_id=job.id)
                # Still create a minimal report
                evidence_list = []
                sources = []

            # Convert SQLAlchemy models to dict for the agent
            evidence_dicts = []
            for ev in evidence_list:
                evidence_dicts.append({
                    "id": str(ev.id),
                    "claim": ev.claim,
                    "supporting_text": ev.supporting_text,
                    "confidence": ev.confidence,
                    "verification_status": ev.verification_status,
                    "verification_notes": ev.verification_notes,
                })

            source_dicts = []
            for src in sources:
                source_dicts.append({
                    "id": str(src.id),
                    "type": src.type,
                    "url": src.url,
                    "title": src.title,
                })

            # Create report generation task
            report_task = ResearchTask(
                id=str(uuid4()),
                job_id=job.id,
                type="report",
                objective=f"Generate research report for: {job.question}",
                agent="report",
                inputs={
                    "evidence": evidence_dicts,
                    "sources": source_dicts,
                    "question": job.question,
                },
            )

            # Run ReportAgent through orchestrator
            context = self.orchestrator.create_context(job.id, report_task.id, job.request_id)
            report_result = await self.orchestrator.run_agent("report", report_task, context)

            if not report_result.success:
                raise ValueError(f"Report generation failed: {report_result.errors}")

            # Persist the report
            report_data = report_result.output
            report_model = ReportModel(
                job_id=job_uuid,
                title=report_data.get("title", f"Research Report: {job.question}"),
                executive_summary=report_data.get("executive_summary", ""),
                methodology=report_data.get("methodology", ""),
                findings=report_data.get("findings", []),
                evidence_ids=report_data.get("evidence_ids", []),
                source_ids=report_data.get("source_ids", []),
                conclusions=report_data.get("conclusions", []),
                limitations=report_data.get("limitations", []),
            )

            async with get_session() as session:
                report_repo = ReportRepository(session)
                await report_repo.create(report_model)

            logger.info("Report generated and persisted", job_id=job.id, report_id=str(report_model.id))

        except Exception as report_err:
            logger.error("Report generation step encountered error", job_id=job.id, error=str(report_err))
            raise

    async def run(self, request: ResearchRequest) -> ResearchJob:
        """Run full research pipeline."""
        job = await self.create_job(request)
        await self.run_job(job.id)
        return job

    async def run_job(self, job_id: str) -> ResearchJob:
        """Run full research pipeline on an existing job."""
        from database.connection import get_session
        from database.repositories import ResearchJobRepository
        from shared.types import JobStatus
        from uuid import UUID

        # Load the job
        async with get_session() as session:
            repo = ResearchJobRepository(session)
            job = await repo.get(UUID(job_id))
            if not job:
                raise ValueError(f"Job not found: {job_id}")
        
        try:
            async with get_session() as session:
                repo = ResearchJobRepository(session)
                await repo.update_status(job.id, JobStatus.RUNNING)
            
            # Planning
            plan = await self.run_planning(job)
            
            # Execution
            await self.execute_plan(job, plan)
            
            # Verification using Critic Agent
            await self.run_verification(job)
            
            # Report generation
            await self.run_report_generation(job)

            async with get_session() as session:
                repo = ResearchJobRepository(session)
                await repo.update_status(job.id, JobStatus.COMPLETED)
            
        except Exception as e:
            logger.error("Research pipeline failed", job_id=job.id, error=str(e))
            async with get_session() as session:
                repo = ResearchJobRepository(session)
                await repo.update_status(job.id, JobStatus.FAILED, str(e))
            raise
        
        return job