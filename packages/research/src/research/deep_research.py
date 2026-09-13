"""Autonomous Deep Research Engine managing recursive multi-round hypothesis loops, Critic gap audits, and convergence guardrails."""

from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from research.models import (
    Contradiction as ModelContradiction,
    DeepResearchConfig,
    Evidence as ModelEvidence,
    ResearchIteration,
    ResearchJob,
    ResearchPlan,
    ResearchStep,
)
from research.events import ResearchEvent, ResearchEventType
from shared.logging import get_logger

logger = get_logger(__name__)


def utc_now() -> datetime:
    return datetime.now(UTC)


class DeepResearchEngine:
    """Orchestrates recursive research iterations, formulating hypotheses, resolving gaps, and validating convergence."""

    def __init__(self, pipeline: Any) -> None:
        self.pipeline = pipeline
        self.orchestrator = pipeline.orchestrator
        self.event_bus = pipeline.event_bus

    async def _emit_event(
        self,
        job_id: str,
        event_type: ResearchEventType,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish a structured deep research event to the event bus."""
        try:
            await self.event_bus.publish(
                ResearchEvent(
                    job_id=job_id,
                    type=event_type,
                    message=message,
                    data=data or {},
                )
            )
        except Exception as e:
            logger.warning("Failed to emit deep research event", job_id=job_id, event=event_type.value, error=str(e))

    async def execute_deep_research(
        self,
        job: ResearchJob,
        initial_plan: ResearchPlan,
        initial_verif_data: Dict[str, Any],
        config: Optional[DeepResearchConfig] = None,
    ) -> Tuple[Dict[str, Any], List[ResearchIteration]]:
        """Run the autonomous deep research loop across multiple iterations until convergence or max iterations."""
        from database.connection import get_session
        from database.repositories import EvidenceRepository
        from agents.planner.planner_agent import PlannerAgent

        deep_config = config or getattr(initial_plan, "deep_research_config", None) or DeepResearchConfig()
        job_id_str = str(job.id)
        job_uuid = UUID(job_id_str)
        user_id_val = getattr(job, "user_id", None)

        iterations: List[ResearchIteration] = []
        current_verif = dict(initial_verif_data)
        prev_confidence: float = float(current_verif.get("confidence_score", 0.85))

        logger.info(
            "Starting deep research execution loop",
            job_id=job_id_str,
            max_iterations=deep_config.max_iterations,
            min_confidence=deep_config.min_confidence_threshold,
        )

        await self._emit_event(
            job_id_str,
            ResearchEventType.DEEP_RESEARCH_STARTED,
            f"Autonomous Deep Research Engine activated (Max iterations: {deep_config.max_iterations}, Target confidence: {deep_config.min_confidence_threshold})",
            {
                "max_iterations": deep_config.max_iterations,
                "min_confidence_threshold": deep_config.min_confidence_threshold,
                "initial_confidence": prev_confidence,
            },
        )

        # Iteration 0 telemetry (Initial pass)
        init_gaps = current_verif.get("unresolved_gaps", [])
        init_contradictions = current_verif.get("contradictions", [])
        init_hypotheses = current_verif.get("suggested_hypotheses", [])
        init_gap_queries = current_verif.get("gap_queries", [])

        # Check if initial verification already meets convergence
        if prev_confidence >= deep_config.min_confidence_threshold and not init_contradictions and not init_gaps:
            iter_0 = ResearchIteration(
                iteration_index=1,
                hypotheses=init_hypotheses,
                unresolved_gaps=init_gaps,
                gap_queries=init_gap_queries,
                confidence_score=prev_confidence,
                confidence_delta=0.0,
                spawned_task_count=0,
                is_converged=True,
                convergence_reason="initial_threshold_met",
                started_at=utc_now(),
                completed_at=utc_now(),
            )
            iterations.append(iter_0)
            initial_plan.iterations = iterations
            job.iterations = iterations

            await self._emit_event(
                job_id_str,
                ResearchEventType.DEEP_RESEARCH_CONVERGED,
                f"Deep research converged on initial pass with confidence {prev_confidence:.2f}",
                {"iteration": 1, "reason": "initial_threshold_met", "confidence_score": prev_confidence},
            )
            return current_verif, iterations

        # Recursive Multi-Round Loop
        for round_idx in range(1, deep_config.max_iterations + 1):
            iter_started_at = utc_now()
            logger.info("Executing deep research round", job_id=job_id_str, round=round_idx)

            contradictions_raw = current_verif.get("contradictions", [])
            unresolved_gaps = current_verif.get("unresolved_gaps", [])
            gap_queries = current_verif.get("gap_queries", [])
            hypotheses = current_verif.get("suggested_hypotheses", [])

            # Generate default hypothesis if empty
            if not hypotheses and (contradictions_raw or unresolved_gaps):
                if contradictions_raw:
                    hypotheses.append(f"Investigate discrepancy regarding {contradictions_raw[0].get('topic', 'findings')}")
                elif unresolved_gaps:
                    hypotheses.append(f"Investigate missing data: {unresolved_gaps[0]}")

            await self._emit_event(
                job_id_str,
                ResearchEventType.RESEARCH_ITERATION_STARTED,
                f"Starting deep research iteration #{round_idx}",
                {
                    "iteration_index": round_idx,
                    "hypotheses_count": len(hypotheses),
                    "gaps_count": len(unresolved_gaps),
                    "contradictions_count": len(contradictions_raw),
                },
            )

            for hyp in hypotheses:
                await self._emit_event(
                    job_id_str,
                    ResearchEventType.HYPOTHESIS_FORMULATED,
                    f"Formulated hypothesis: {hyp}",
                    {"iteration_index": round_idx, "hypothesis": hyp},
                )

            # Retrieve accumulated DB evidence
            async with get_session() as session:
                evidence_repo = EvidenceRepository(session)
                db_evidence_list = await evidence_repo.get_by_job(job_uuid)

            model_evidence: List[ModelEvidence] = []
            for ev in db_evidence_list:
                model_evidence.append(
                    ModelEvidence(
                        id=str(ev.id),
                        source_id=str(ev.source_id),
                        claim=ev.claim,
                        supporting_text=ev.supporting_text,
                        confidence=ev.confidence,
                        verification_status=ev.verification_status,
                    )
                )

            model_contradictions: List[ModelContradiction] = []
            for c in contradictions_raw:
                if isinstance(c, dict):
                    try:
                        model_contradictions.append(
                            ModelContradiction(
                                topic=c.get("topic", "General Topic"),
                                claim_a=c.get("claim_a", "Claim A"),
                                source_a=c.get("source_a", "Source A"),
                                claim_b=c.get("claim_b", "Claim B"),
                                source_b=c.get("source_b", "Source B"),
                                conflict_type=c.get("conflict_type", "direct_conflict"),
                                explanation=c.get("explanation", "Discrepancy detected"),
                                severity=c.get("severity", "medium"),
                            )
                        )
                    except Exception as parse_c_err:
                        logger.warning("Could not parse contradiction dict", error=str(parse_c_err))
                elif isinstance(c, ModelContradiction):
                    model_contradictions.append(c)

            # Invoke PlannerAgent for dynamic recursive task generation
            planner = PlannerAgent()
            context = self.orchestrator.create_context(
                job_id=job_id_str,
                task_id=str(uuid4()),
                request_id=str(getattr(job, "request_id", uuid4())),
                user_id=str(user_id_val) if user_id_val else None,
            )

            replan_res = await planner.replan(
                current_plan=initial_plan,
                evidence=model_evidence,
                contradictions=model_contradictions,
                context=context,
                unresolved_gaps=unresolved_gaps,
                gap_queries=gap_queries,
                hypotheses=hypotheses,
                iteration_index=round_idx,
            )

            spawned_steps: List[ResearchStep] = []
            if replan_res.success and isinstance(replan_res.output, dict):
                spawned_steps = replan_res.output.get("spawned_steps", [])

            # Cap spawned tasks per round to limit quota/concurrency
            if len(spawned_steps) > deep_config.max_spawned_per_round:
                spawned_steps = spawned_steps[: deep_config.max_spawned_per_round]

            # If no tasks could be spawned, we cannot make further progress
            if not spawned_steps:
                logger.info("No subtasks spawned during iteration", job_id=job_id_str, round=round_idx)
                iter_record = ResearchIteration(
                    iteration_index=round_idx,
                    hypotheses=hypotheses,
                    unresolved_gaps=unresolved_gaps,
                    gap_queries=gap_queries,
                    confidence_score=prev_confidence,
                    confidence_delta=0.0,
                    spawned_task_count=0,
                    is_converged=True,
                    convergence_reason="no_further_actionable_subtasks",
                    started_at=iter_started_at,
                    completed_at=utc_now(),
                )
                iterations.append(iter_record)
                break

            initial_plan.replan_count += 1
            explanation = replan_res.output.get("plan_explanation", f"Iteration #{round_idx} deep investigation")

            await self._emit_event(
                job_id_str,
                ResearchEventType.DAG_REPLANNED,
                f"Deep iteration #{round_idx}: {explanation}",
                {
                    "iteration_index": round_idx,
                    "spawned_steps_count": len(spawned_steps),
                    "explanation": explanation,
                },
            )

            for step in spawned_steps:
                await self._emit_event(
                    job_id_str,
                    ResearchEventType.TASK_SPAWNED,
                    f"Spawned iteration #{round_idx} subtask: {step.name}",
                    {
                        "step_id": step.id,
                        "name": step.name,
                        "agent": step.agent,
                        "iteration_index": round_idx,
                        "is_dynamic": True,
                    },
                )

            # Execute dynamic subtasks
            dynamic_plan = ResearchPlan(
                objective=f"Deep research round #{round_idx}: {explanation}",
                steps=spawned_steps,
                expected_outputs=[],
                replan_count=initial_plan.replan_count,
            )
            await self.pipeline.execute_plan(job, dynamic_plan)

            # Re-run CriticAgent verification on new accumulated evidence
            new_verif = await self.pipeline.run_verification(job)
            current_verif = new_verif
            new_confidence = float(new_verif.get("confidence_score", 0.85))
            conf_delta = round(new_confidence - prev_confidence, 4)

            # Check convergence criteria
            is_converged = False
            convergence_reason: Optional[str] = None

            new_contradictions = new_verif.get("contradictions", [])
            new_gaps = new_verif.get("unresolved_gaps", [])

            if new_confidence >= deep_config.min_confidence_threshold and not new_contradictions:
                is_converged = True
                convergence_reason = "confidence_threshold_met"
            elif round_idx >= deep_config.max_iterations:
                is_converged = True
                convergence_reason = "max_iterations_reached"
            elif conf_delta < deep_config.diminishing_returns_threshold and round_idx > 1 and len(new_contradictions) == 0:
                is_converged = True
                convergence_reason = "diminishing_returns"

            iter_record = ResearchIteration(
                iteration_index=round_idx,
                hypotheses=hypotheses,
                unresolved_gaps=unresolved_gaps,
                gap_queries=gap_queries,
                confidence_score=new_confidence,
                confidence_delta=conf_delta,
                spawned_task_count=len(spawned_steps),
                is_converged=is_converged,
                convergence_reason=convergence_reason,
                started_at=iter_started_at,
                completed_at=utc_now(),
            )
            iterations.append(iter_record)

            await self._emit_event(
                job_id_str,
                ResearchEventType.RESEARCH_ITERATION_COMPLETED,
                f"Completed deep research iteration #{round_idx} (Confidence: {new_confidence:.2f}, Delta: {conf_delta:+.2f})",
                {
                    "iteration_index": round_idx,
                    "confidence_score": new_confidence,
                    "confidence_delta": conf_delta,
                    "spawned_task_count": len(spawned_steps),
                    "is_converged": is_converged,
                    "convergence_reason": convergence_reason,
                },
            )

            prev_confidence = new_confidence
            if is_converged:
                await self._emit_event(
                    job_id_str,
                    ResearchEventType.DEEP_RESEARCH_CONVERGED,
                    f"Deep research converged after {round_idx} iterations ({convergence_reason})",
                    {
                        "total_iterations": round_idx,
                        "final_confidence": new_confidence,
                        "convergence_reason": convergence_reason,
                    },
                )
                break

        initial_plan.iterations = iterations
        job.iterations = iterations
        return current_verif, iterations
