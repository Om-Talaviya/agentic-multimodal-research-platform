"""Repository for persisting and querying Agent Evaluations and Step Telemetry."""
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.agent_evaluation import DBAgentEvaluation, DBAgentStepMetric
from shared.logging import get_logger

logger = get_logger(__name__)


class AgentEvaluationRepository:
    """Handles database persistence for agent evaluation scorecards and telemetry."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_evaluation(
        self,
        agent_name: str,
        total_steps: int,
        successful_steps: int,
        failed_steps: int,
        plan_precision: float,
        tool_accuracy: float,
        evidence_coverage: float,
        hallucination_rate: float,
        synthesis_fidelity: float,
        overall_score: float,
        execution_time_ms: int = 0,
        total_tokens: int = 0,
        estimated_cost_usd: float = 0.0,
        findings_audit: Optional[Dict[str, Any]] = None,
        job_id: Optional[UUID] = None,
        evaluated_by: Optional[UUID] = None,
        step_telemetry: Optional[List[Dict[str, Any]]] = None,
    ) -> DBAgentEvaluation:
        """Persist an agent evaluation record with detailed step metrics."""
        eval_record = DBAgentEvaluation(
            agent_name=agent_name,
            job_id=job_id,
            total_steps=total_steps,
            successful_steps=successful_steps,
            failed_steps=failed_steps,
            plan_precision=plan_precision,
            tool_accuracy=tool_accuracy,
            evidence_coverage=evidence_coverage,
            hallucination_rate=hallucination_rate,
            synthesis_fidelity=synthesis_fidelity,
            overall_score=overall_score,
            execution_time_ms=execution_time_ms,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost_usd,
            findings_audit=findings_audit or {},
            evaluated_by=evaluated_by,
        )
        self.session.add(eval_record)
        await self.session.flush()

        if step_telemetry:
            for s in step_telemetry:
                step_obj = DBAgentStepMetric(
                    evaluation_id=eval_record.id,
                    step_index=s.get("step_index", 0),
                    agent_type=s.get("agent_type", agent_name),
                    action_type=s.get("action_type", "execute"),
                    tool_name=s.get("tool_name"),
                    tool_args=s.get("tool_args", {}),
                    tool_output_length=s.get("tool_output_length", 0),
                    success=s.get("success", True),
                    error_message=s.get("error_message"),
                    latency_ms=s.get("latency_ms", 0),
                    tokens_consumed=s.get("tokens_consumed", 0),
                )
                self.session.add(step_obj)

        await self.session.flush()
        return eval_record

    async def get_evaluation_by_id(self, evaluation_id: UUID) -> Optional[DBAgentEvaluation]:
        """Fetch evaluation by ID with loaded step metrics."""
        stmt = (
            select(DBAgentEvaluation)
            .options(selectinload(DBAgentEvaluation.steps))
            .where(DBAgentEvaluation.id == evaluation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_evaluations(
        self,
        agent_name: Optional[str] = None,
        job_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBAgentEvaluation]:
        """List historical agent evaluations with optional filtering."""
        stmt = select(DBAgentEvaluation)
        if agent_name:
            stmt = stmt.where(DBAgentEvaluation.agent_name == agent_name)
        if job_id:
            stmt = stmt.where(DBAgentEvaluation.job_id == job_id)

        stmt = stmt.order_by(desc(DBAgentEvaluation.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_agent_metrics_summary(self) -> Dict[str, Any]:
        """Aggregate system-wide agent quality and hallucination metrics."""
        stmt = select(
            func.count(DBAgentEvaluation.id).label("total_evaluations"),
            func.avg(DBAgentEvaluation.overall_score).label("avg_score"),
            func.avg(DBAgentEvaluation.plan_precision).label("avg_plan_precision"),
            func.avg(DBAgentEvaluation.tool_accuracy).label("avg_tool_accuracy"),
            func.avg(DBAgentEvaluation.evidence_coverage).label("avg_evidence_coverage"),
            func.avg(DBAgentEvaluation.hallucination_rate).label("avg_hallucination_rate"),
            func.avg(DBAgentEvaluation.synthesis_fidelity).label("avg_synthesis_fidelity"),
            func.sum(DBAgentEvaluation.total_tokens).label("total_tokens_consumed"),
            func.sum(DBAgentEvaluation.estimated_cost_usd).label("total_cost_usd"),
        )
        result = await self.session.execute(stmt)
        row = result.first()

        if not row or not row.total_evaluations:
            return {
                "total_evaluations": 0,
                "avg_score": 0.0,
                "avg_plan_precision": 0.0,
                "avg_tool_accuracy": 0.0,
                "avg_evidence_coverage": 0.0,
                "avg_hallucination_rate": 0.0,
                "avg_synthesis_fidelity": 0.0,
                "total_tokens_consumed": 0,
                "total_cost_usd": 0.0,
            }

        return {
            "total_evaluations": int(row.total_evaluations or 0),
            "avg_score": round(float(row.avg_score or 0.0), 4),
            "avg_plan_precision": round(float(row.avg_plan_precision or 0.0), 4),
            "avg_tool_accuracy": round(float(row.avg_tool_accuracy or 0.0), 4),
            "avg_evidence_coverage": round(float(row.avg_evidence_coverage or 0.0), 4),
            "avg_hallucination_rate": round(float(row.avg_hallucination_rate or 0.0), 4),
            "avg_synthesis_fidelity": round(float(row.avg_synthesis_fidelity or 0.0), 4),
            "total_tokens_consumed": int(row.total_tokens_consumed or 0),
            "total_cost_usd": round(float(row.total_cost_usd or 0.0), 6),
        }

    async def delete_evaluation(self, evaluation_id: UUID) -> bool:
        """Delete an agent evaluation record."""
        eval_record = await self.get_evaluation_by_id(evaluation_id)
        if not eval_record:
            return False
        await self.session.delete(eval_record)
        await self.session.flush()
        return True
