from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4
from datetime import UTC, datetime
from research.models import ResearchRequest, ResearchJob, ResearchPlan, ResearchTask, Source, Evidence
from agents.orchestrator import AgentOrchestrator
from agents.registry import AgentRegistry
from tools.registry import ToolRegistry
from ai.providers.router import ModelRouter
from shared.logging import get_logger
from research.events import ResearchEvent, ResearchEventBus, ResearchEventType, research_event_bus

logger = get_logger(__name__)


def utc_now() -> datetime:
    return datetime.now(UTC)


class ResearchPipeline:
    """Orchestrates the full research pipeline."""
    
    def __init__(
        self,
        orchestrator: AgentOrchestrator,
        agent_registry: AgentRegistry,
        tool_registry: ToolRegistry,
        model_router: ModelRouter,
        event_bus: ResearchEventBus | None = None,
    ):
        self.orchestrator = orchestrator
        self.agent_registry = agent_registry
        self.tool_registry = tool_registry
        self.model_router = model_router
        self.event_bus = event_bus or research_event_bus

    async def _emit(
        self,
        job_id: str,
        event_type: ResearchEventType,
        message: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        try:
            await self.event_bus.publish(
                ResearchEvent(
                    job_id=job_id,
                    type=event_type,
                    message=message,
                    data=data or {},
                )
            )
        except Exception as exc:
            logger.warning(
                "Failed to publish research event",
                job_id=job_id,
                event_type=event_type.value,
                error=str(exc),
            )
    
    async def create_job(self, request: ResearchRequest) -> ResearchJob:
        """Create a new research job from request."""
        from uuid import UUID, uuid4
        from database.connection import get_session
        from database.repositories import ResearchJobRepository
        from database.models import ResearchJob as DBResearchJob
        from shared.types import JobStatus

        job_uuid = uuid4()
        req_uuid = uuid4()

        db_job = DBResearchJob(
            id=job_uuid,
            request_id=req_uuid,
            question=request.question,
            objective=request.question,
            constraints=request.constraints,
            status=JobStatus.PENDING.value,
        )

        async with get_session() as session:
            repo = ResearchJobRepository(session)
            await repo.create(db_job)

        job = ResearchJob(
            id=str(job_uuid),
            request_id=str(req_uuid),
            question=request.question,
            objective=request.question,
            constraints=request.constraints,
            status=JobStatus.PENDING,
        )

        logger.info("Research job created", job_id=job.id)
        await self._emit(
            str(job.id),
            ResearchEventType.JOB_CREATED,
            "Research job created",
            {"status": JobStatus.PENDING.value},
        )
        return job
    
    async def run_planning(self, job: ResearchJob) -> ResearchPlan:
        """Run planner agent to create research plan."""
        from agents.planner.planner_agent import PlannerAgent
        from uuid import uuid4
        
        planner = PlannerAgent()
        job_id_str = str(job.id)
        request_id_str = str(getattr(job, "request_id", uuid4()))

        task = ResearchTask(
            id=str(uuid4()),
            job_id=job_id_str,
            type="planning",
            objective=job.objective,
            agent="planner",
            context={
                "domain": getattr(job, "domain", None),
                "scope": getattr(job, "scope", None),
                "constraints": getattr(job, "constraints", []),
            },
        )
        
        context = self.orchestrator.create_context(job_id_str, task.id, request_id_str)
        await self._emit(
            job_id_str,
            ResearchEventType.PLANNING_STARTED,
            "Research planning started",
            {"task_id": task.id, "agent": task.agent},
        )
        result = await planner.run(task, context)
        
        if not result.success:
            raise ValueError(f"Planning failed: {result.errors}")

        step_count = len(result.output.steps) if result.output else 0
        await self._emit(
            job_id_str,
            ResearchEventType.PLANNING_COMPLETED,
            "Research planning completed",
            {"task_id": task.id, "agent": task.agent, "step_count": step_count},
        )
        return result.output

    @staticmethod
    def _convert_to_db_source(src: Any, job_uuid: "UUID") -> "DBSource":
        from database.models import Source as DBSource
        from uuid import UUID, uuid4

        if isinstance(src, DBSource):
            if not src.job_id:
                src.job_id = job_uuid
            return src

        if isinstance(src, dict):
            s_id = UUID(str(src["id"])) if src.get("id") else uuid4()
            s_type = src.get("type", "web")
            s_url = src.get("url")
            s_title = src.get("title", "Untitled Source")
            s_meta = src.get("metadata") or src.get("source_metadata") or {}
            s_hash = src.get("content_hash")
            s_retrieved = src.get("retrieved_at") or utc_now()
        else:
            s_id = UUID(str(getattr(src, "id", uuid4())))
            s_type = getattr(src, "type", "web")
            s_url = getattr(src, "url", None)
            s_title = getattr(src, "title", "Untitled Source")
            s_meta = getattr(src, "metadata", {}) or getattr(src, "source_metadata", {})
            s_hash = getattr(src, "content_hash", None)
            s_retrieved = getattr(src, "retrieved_at", None) or utc_now()

        return DBSource(
            id=s_id,
            job_id=job_uuid,
            type=s_type,
            url=s_url,
            title=s_title,
            source_metadata=s_meta,
            content_hash=s_hash,
            retrieved_at=s_retrieved,
        )

    @staticmethod
    def _convert_to_db_evidence(ev: Any, job_uuid: "UUID") -> "DBEvidence":
        from database.models import Evidence as DBEvidence
        from uuid import UUID, uuid4

        if isinstance(ev, DBEvidence):
            if not ev.job_id:
                ev.job_id = job_uuid
            return ev

        if isinstance(ev, dict):
            e_id = UUID(str(ev["id"])) if ev.get("id") else uuid4()
            s_id = UUID(str(ev["source_id"])) if ev.get("source_id") else uuid4()
            claim = ev.get("claim", "")
            supporting_text = ev.get("supporting_text", "")
            conf = float(ev.get("confidence", 0.5))
            v_status = ev.get("verification_status", "unverified")
            v_notes = ev.get("verification_notes")
            c_at = ev.get("created_at") or utc_now()
        else:
            e_id = UUID(str(getattr(ev, "id", uuid4())))
            s_id = UUID(str(getattr(ev, "source_id", uuid4())))
            claim = getattr(ev, "claim", "")
            supporting_text = getattr(ev, "supporting_text", "")
            conf = float(getattr(ev, "confidence", 0.5))
            v_status = getattr(ev, "verification_status", "unverified")
            v_notes = getattr(ev, "verification_notes", None)
            c_at = getattr(ev, "created_at", None) or utc_now()

        return DBEvidence(
            id=e_id,
            job_id=job_uuid,
            source_id=s_id,
            claim=claim,
            supporting_text=supporting_text,
            confidence=conf,
            verification_status=v_status,
            verification_notes=v_notes,
            created_at=c_at,
        )

    @staticmethod
    def _serialize_task_result(output: Any) -> Optional[dict]:
        """Serialize task output safely into JSON-compatible dict for database persistence."""
        if output is None:
            return None
        import json
        try:
            if hasattr(output, "model_dump"):
                raw = output.model_dump(mode="json")
            elif isinstance(output, dict):
                raw = {}
                for k, v in output.items():
                    if isinstance(v, list):
                        raw[k] = [
                            item.model_dump(mode="json") if hasattr(item, "model_dump")
                            else item.__dict__ if hasattr(item, "__dict__")
                            else item
                            for item in v
                        ]
                    elif hasattr(v, "model_dump"):
                        raw[k] = v.model_dump(mode="json")
                    else:
                        raw[k] = v
            else:
                raw = {"result": str(output)}

            return json.loads(json.dumps(raw, default=str))
        except Exception:
            return {"result": str(output)}

    async def execute_plan(self, job: ResearchJob, plan: ResearchPlan) -> None:
        """Execute research plan tasks with proper DAG dependency resolution and DB persistence."""
        import asyncio
        from uuid import UUID, uuid4
        from database.connection import get_session
        from database.repositories import TaskRepository, SourceRepository, EvidenceRepository
        from database.models import ResearchTask as DBResearchTask
        from shared.types import TaskStatus

        job_uuid = UUID(str(job.id))
        job_req_id = str(getattr(job, "request_id", uuid4()))

        # Map planner step IDs (e.g. "step_1") to unique task UUIDs
        step_id_to_task_id: dict[str, str] = {step.id: str(uuid4()) for step in plan.steps}
        tasks: dict[str, ResearchTask] = {}

        for step in plan.steps:
            t_id = step_id_to_task_id[step.id]
            # Map depends_on planner step IDs to their corresponding task UUIDs
            mapped_deps = [
                step_id_to_task_id[dep]
                for dep in step.depends_on
                if dep in step_id_to_task_id
            ]
            tasks[t_id] = ResearchTask(
                id=t_id,
                job_id=str(job.id),
                type=step.agent,
                objective=step.description,
                agent=step.agent,
                inputs=step.inputs,
                depends_on=mapped_deps,
                priority=step.priority,
            )

        # Persist tasks using SQLAlchemy models
        db_tasks = [
            DBResearchTask(
                id=UUID(t.id),
                job_id=job_uuid,
                type=t.type,
                objective=t.objective,
                context=t.context,
                agent=t.agent,
                inputs=t.inputs,
                depends_on=t.depends_on,
                priority=t.priority,
                status=t.status.value if hasattr(t.status, "value") else str(t.status),
            )
            for t in tasks.values()
        ]

        async with get_session() as session:
            task_repo = TaskRepository(session)
            await task_repo.create_batch(db_tasks)

        await self._emit(
            str(job.id),
            ResearchEventType.TASKS_CREATED,
            "Research tasks created",
            {
                "task_count": len(db_tasks),
                "tasks": [
                    {
                        "id": str(t.id),
                        "agent": t.agent,
                        "status": t.status,
                        "objective": t.objective,
                    }
                    for t in db_tasks
                ],
            },
        )

        completed: set[str] = set()

        while len(completed) < len(tasks):
            # Find ready tasks whose mapped dependencies are all completed
            ready = [
                t for t in tasks.values()
                if t.id not in completed
                and all(dep in completed for dep in t.depends_on)
            ]

            if not ready:
                raise ValueError("Circular dependency or no ready tasks")

            # Sort ready tasks by priority descending
            ready.sort(key=lambda t: t.priority, reverse=True)

            async with get_session() as session:
                task_repo = TaskRepository(session)
                for task in ready:
                    await task_repo.update_status(UUID(task.id), TaskStatus.RUNNING)
                    await self._emit(
                        str(job.id),
                        ResearchEventType.TASK_STARTED,
                        "Research task started",
                        {
                            "task_id": task.id,
                            "agent": task.agent,
                            "type": task.type,
                            "objective": task.objective,
                            "status": TaskStatus.RUNNING.value,
                        },
                    )

            # Create an isolated context for each ready task
            contexts = [
                self.orchestrator.create_context(str(job.id), t.id, job_req_id)
                for t in ready
            ]

            # Execute tasks in parallel with per-task context
            agent_executions = [
                self.orchestrator.run_agent(t.agent, t, ctx)
                for t, ctx in zip(ready, contexts)
            ]
            results = await asyncio.gather(*agent_executions, return_exceptions=True)

            # Process and persist results
            async with get_session() as session:
                task_repo = TaskRepository(session)
                source_repo = SourceRepository(session)
                evidence_repo = EvidenceRepository(session)

                for task, result in zip(ready, results):
                    task_uuid = UUID(task.id)
                    if isinstance(result, Exception):
                        await task_repo.update_status(task_uuid, TaskStatus.FAILED, str(result))
                        logger.error("Task failed", task_id=task.id, error=str(result))
                        await self._emit(
                            str(job.id),
                            ResearchEventType.TASK_FAILED,
                            "Research task failed",
                            {
                                "task_id": task.id,
                                "agent": task.agent,
                                "type": task.type,
                                "status": TaskStatus.FAILED.value,
                                "error": str(result),
                            },
                        )
                    else:
                        task_output = self._serialize_task_result(result.output)
                        await task_repo.update_status(task_uuid, TaskStatus.COMPLETED, result=task_output)
                        await self._emit(
                            str(job.id),
                            ResearchEventType.TASK_COMPLETED,
                            "Research task completed",
                            {
                                "task_id": task.id,
                                "agent": task.agent,
                                "type": task.type,
                                "status": TaskStatus.COMPLETED.value,
                            },
                        )

                        # Convert and persist sources and evidence
                        if result.output and isinstance(result.output, dict):
                            raw_sources = result.output.get("sources", [])
                            if raw_sources:
                                db_sources = [
                                    self._convert_to_db_source(s, job_uuid)
                                    for s in raw_sources
                                ]
                                await source_repo.create_batch(db_sources)
                                await self._emit(
                                    str(job.id),
                                    ResearchEventType.SOURCES_ADDED,
                                    "Research sources added",
                                    {
                                        "task_id": task.id,
                                        "count": len(db_sources),
                                        "source_ids": [str(s.id) for s in db_sources],
                                    },
                                )

                            raw_evidence = result.output.get("evidence", [])
                            if raw_evidence:
                                db_evidence = [
                                    self._convert_to_db_evidence(ev, job_uuid)
                                    for ev in raw_evidence
                                ]
                                await evidence_repo.create_batch(db_evidence)
                                await self._emit(
                                    str(job.id),
                                    ResearchEventType.EVIDENCE_ADDED,
                                    "Research evidence added",
                                    {
                                        "task_id": task.id,
                                        "count": len(db_evidence),
                                        "evidence_ids": [str(ev.id) for ev in db_evidence],
                                    },
                                )

                    completed.add(task.id)
    
    async def run_verification(self, job: ResearchJob) -> None:
        """Run critic agent to evaluate and verify collected evidence."""
        from uuid import UUID
        from database.connection import get_session
        from database.repositories import EvidenceRepository

        try:
            job_uuid = UUID(str(job.id))
            await self._emit(
                str(job.id),
                ResearchEventType.VERIFICATION_STARTED,
                "Evidence verification started",
            )
            async with get_session() as session:
                evidence_repo = EvidenceRepository(session)
                evidence_list = await evidence_repo.get_by_job(job_uuid)

            if not evidence_list:
                logger.info("No evidence to verify for job", job_id=job.id)
                await self._emit(
                    str(job.id),
                    ResearchEventType.VERIFICATION_COMPLETED,
                    "Evidence verification completed",
                    {"evidence_count": 0, "verified_count": 0},
                )
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
                await self._emit(
                    str(job.id),
                    ResearchEventType.VERIFICATION_COMPLETED,
                    "Evidence verification completed",
                    {
                        "evidence_count": len(evidence_list),
                        "verified_count": len(verifications),
                    },
                )
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
            await self._emit(
                str(job.id),
                ResearchEventType.REPORT_STARTED,
                "Report generation started",
            )

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
                job_id=str(job.id),
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
            context = self.orchestrator.create_context(str(job.id), report_task.id, str(job.request_id))
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
            await self._emit(
                str(job.id),
                ResearchEventType.REPORT_GENERATED,
                "Report generated",
                {"report_id": str(report_model.id)},
            )

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
            await self._emit(
                str(job.id),
                ResearchEventType.JOB_STARTED,
                "Research job started",
                {"status": JobStatus.RUNNING.value},
            )
            
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
            await self._emit(
                str(job.id),
                ResearchEventType.JOB_COMPLETED,
                "Research job completed",
                {"status": JobStatus.COMPLETED.value},
            )
            
        except Exception as e:
            logger.error("Research pipeline failed", job_id=job.id, error=str(e))
            async with get_session() as session:
                repo = ResearchJobRepository(session)
                await repo.update_status(job.id, JobStatus.FAILED, str(e))
            await self._emit(
                str(job.id),
                ResearchEventType.JOB_FAILED,
                "Research job failed",
                {"status": JobStatus.FAILED.value, "error": str(e)},
            )
            raise
        
        return job
