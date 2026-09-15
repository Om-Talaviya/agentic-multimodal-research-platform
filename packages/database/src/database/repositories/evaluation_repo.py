"""Repository for Model Evaluations and Benchmark Results persistence."""
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.evaluation import DBModelBenchmarkResult, DBModelEvaluation
from shared.logging import get_logger

logger = get_logger(__name__)


class ModelEvaluationRepository:
    """Async database repository for model evaluation runs and test results."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_evaluation(
        self,
        model_id: str,
        provider_name: str,
        benchmark_name: str,
        total_samples: int,
        passed_samples: int,
        pass_rate: float,
        overall_score: float,
        mean_accuracy: float,
        mean_reasoning: float,
        mean_faithfulness: float,
        mean_citation_precision: float,
        mean_latency_ms: float,
        total_cost_usd: float,
        category_scores: Dict[str, float],
        triggered_by: Optional[UUID] = None,
        sample_results: Optional[List[Dict[str, Any]]] = None,
    ) -> DBModelEvaluation:
        """Create a new model evaluation record and batch-insert child benchmark results."""
        evaluation = DBModelEvaluation(
            model_id=model_id,
            provider_name=provider_name,
            benchmark_name=benchmark_name,
            total_samples=total_samples,
            passed_samples=passed_samples,
            pass_rate=pass_rate,
            overall_score=overall_score,
            mean_accuracy=mean_accuracy,
            mean_reasoning=mean_reasoning,
            mean_faithfulness=mean_faithfulness,
            mean_citation_precision=mean_citation_precision,
            mean_latency_ms=mean_latency_ms,
            total_cost_usd=total_cost_usd,
            category_scores=category_scores,
            triggered_by=triggered_by,
        )
        self.session.add(evaluation)
        await self.session.flush()

        if sample_results:
            for s in sample_results:
                result = DBModelBenchmarkResult(
                    evaluation_id=evaluation.id,
                    sample_id=s.get("sample_id", ""),
                    category=s.get("category", "general"),
                    prompt=s.get("prompt", ""),
                    response_text=s.get("response_text", ""),
                    passed=s.get("passed", False),
                    score=s.get("score", 0.0),
                    metrics=s.get("metrics", {}),
                    latency_ms=s.get("latency_ms", 0),
                    prompt_tokens=s.get("prompt_tokens", 0),
                    completion_tokens=s.get("completion_tokens", 0),
                    cost_usd=s.get("cost_usd", 0.0),
                    error_message=s.get("error"),
                )
                self.session.add(result)
            await self.session.flush()

        await self.session.commit()
        await self.session.refresh(evaluation)
        return evaluation

    async def get_evaluation_by_id(self, evaluation_id: UUID) -> Optional[DBModelEvaluation]:
        """Fetch evaluation run by ID with eager loaded benchmark results."""
        stmt = (
            select(DBModelEvaluation)
            .options(selectinload(DBModelEvaluation.results))
            .where(DBModelEvaluation.id == evaluation_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_evaluations(
        self,
        model_id: Optional[str] = None,
        provider_name: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBModelEvaluation]:
        """List historical evaluation runs ordered by recency."""
        stmt = select(DBModelEvaluation).order_by(desc(DBModelEvaluation.created_at))
        if model_id:
            stmt = stmt.where(DBModelEvaluation.model_id == model_id)
        if provider_name:
            stmt = stmt.where(DBModelEvaluation.provider_name == provider_name)
        stmt = stmt.offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_latest_evaluations_per_model(self) -> List[DBModelEvaluation]:
        """Retrieve the most recent evaluation run for every unique model to construct the leaderboard."""
        # Query distinct model evaluations ordered by overall score
        all_evals = await self.list_evaluations(limit=200)
        seen_models: set[str] = set()
        latest: List[DBModelEvaluation] = []
        for e in all_evals:
            if e.model_id not in seen_models:
                seen_models.add(e.model_id)
                latest.append(e)

        # Sort descending by overall_score
        latest.sort(key=lambda x: -x.overall_score)
        return latest

    async def delete_evaluation(self, evaluation_id: UUID) -> bool:
        """Delete an evaluation record."""
        evaluation = await self.get_evaluation_by_id(evaluation_id)
        if not evaluation:
            return False
        await self.session.delete(evaluation)
        await self.session.commit()
        return True
