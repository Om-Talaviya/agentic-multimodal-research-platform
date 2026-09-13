"""Model Evaluation and Benchmark Leaderboard routes."""
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ai.eval.evaluator import EvaluationReport, LeaderboardEntry, ModelEvaluator
from ai.eval.schemas import DEFAULT_RESEARCH_BENCHMARK, BenchmarkDataset
from ai.gateway.model_gateway import ModelGateway
from ai.router.optimizer import ModelEcosystemOptimizer, PRESET_PROFILES, ProfileType
from api.dependencies import get_db_session, get_model_gateway, get_optional_current_user
from database.repositories.evaluation_repo import ModelEvaluationRepository
from shared.auth import User
from shared.logging import get_logger

router = APIRouter(prefix="/models", tags=["evaluations"])
logger = get_logger(__name__)


class RunEvaluationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_id: str
    benchmark_name: Optional[str] = "research_core_eval_v1"


@router.post("/evaluate", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def evaluate_model(
    payload: RunEvaluationRequest,
    gateway: ModelGateway = Depends(get_model_gateway),
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Trigger an automated benchmark evaluation run across golden test cases."""
    evaluator = ModelEvaluator(gateway)
    report: EvaluationReport = await evaluator.evaluate_model(
        model_id=payload.model_id,
        benchmark=DEFAULT_RESEARCH_BENCHMARK,
    )

    repo = ModelEvaluationRepository(session)
    user_uuid = current_user.id if current_user and hasattr(current_user, "id") and current_user.id else None

    # Persist evaluation and results
    sample_dicts = [
        {
            "sample_id": s.sample_id,
            "category": s.category,
            "prompt": s.prompt,
            "response_text": s.response_text,
            "passed": s.passed,
            "score": s.metrics.get("overall_score", 0.0),
            "metrics": s.metrics,
            "latency_ms": s.latency_ms,
            "prompt_tokens": s.prompt_tokens,
            "completion_tokens": s.completion_tokens,
            "cost_usd": s.cost_usd,
            "error": s.error,
        }
        for s in report.sample_results
    ]

    saved_eval = await repo.create_evaluation(
        model_id=report.model_id,
        provider_name=report.provider_name,
        benchmark_name=report.benchmark_name,
        total_samples=report.total_samples,
        passed_samples=report.passed_samples,
        pass_rate=report.pass_rate,
        overall_score=report.overall_score,
        mean_accuracy=report.mean_accuracy,
        mean_reasoning=report.mean_reasoning,
        mean_faithfulness=report.mean_faithfulness,
        mean_citation_precision=report.mean_citation_precision,
        mean_latency_ms=report.mean_latency_ms,
        total_cost_usd=report.total_cost_usd,
        category_scores=report.category_scores,
        triggered_by=user_uuid,
        sample_results=sample_dicts,
    )

    return saved_eval.to_dict()


@router.get("/evaluations", response_model=List[Dict[str, Any]])
async def list_evaluations(
    model_id: Optional[str] = Query(None),
    provider_name: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    """List historical evaluation runs."""
    repo = ModelEvaluationRepository(session)
    evals = await repo.list_evaluations(
        model_id=model_id,
        provider_name=provider_name,
        limit=limit,
        offset=offset,
    )
    return [e.to_dict() for e in evals]


@router.get("/evaluations/{id}", response_model=Dict[str, Any])
async def get_evaluation_detail(
    id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Get detailed test case breakdown for an evaluation run."""
    repo = ModelEvaluationRepository(session)
    eval_record = await repo.get_evaluation_by_id(id)
    if not eval_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation record '{id}' not found",
        )

    res = eval_record.to_dict()
    res["sample_results"] = [r.to_dict() for r in eval_record.results]
    return res


@router.delete("/evaluations/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evaluation(
    id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete an evaluation record."""
    repo = ModelEvaluationRepository(session)
    deleted = await repo.delete_evaluation(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation record '{id}' not found",
        )
    return None


@router.get("/leaderboard", response_model=List[Dict[str, Any]])
async def get_model_leaderboard(
    gateway: ModelGateway = Depends(get_model_gateway),
    session: AsyncSession = Depends(get_db_session),
):
    """Get aggregated competitive leaderboard ranking all models across evaluations."""
    repo = ModelEvaluationRepository(session)
    latest_evals = await repo.get_latest_evaluations_per_model()
    all_catalog_models = {m.model_id: m for m in gateway.model_registry.list_models()}

    # Compute Pareto frontier on all models
    pareto_frontier = ModelEcosystemOptimizer.find_pareto_frontier(
        candidates=list(all_catalog_models.values()),
    )

    leaderboard: List[Dict[str, Any]] = []

    # Include evaluated models
    seen_models: set[str] = set()
    for rank, eval_rec in enumerate(latest_evals, start=1):
        m_def = all_catalog_models.get(eval_rec.model_id)
        cost_per_1k = ((m_def.input_cost + m_def.output_cost) / 2.0) if m_def else 0.0
        seen_models.add(eval_rec.model_id)

        leaderboard.append({
            "rank": rank,
            "model_id": eval_rec.model_id,
            "provider_name": eval_rec.provider_name,
            "overall_score": eval_rec.overall_score,
            "factual_accuracy": eval_rec.mean_accuracy,
            "reasoning_depth": eval_rec.mean_reasoning,
            "retrieval_faithfulness": eval_rec.mean_faithfulness,
            "citation_precision": eval_rec.mean_citation_precision,
            "mean_latency_ms": eval_rec.mean_latency_ms,
            "cost_per_1k_usd": cost_per_1k,
            "tier": m_def.tier if m_def else "free",
            "is_local": m_def.is_local if m_def else True,
            "is_pareto_optimal": eval_rec.model_id in pareto_frontier,
            "last_evaluated": eval_rec.created_at.isoformat() if eval_rec.created_at else None,
        })

    # Add any non-evaluated catalog models as pending entries
    for m_id, m_def in all_catalog_models.items():
        if m_id not in seen_models:
            cost_per_1k = (m_def.input_cost + m_def.output_cost) / 2.0
            leaderboard.append({
                "rank": len(leaderboard) + 1,
                "model_id": m_id,
                "provider_name": m_def.provider_name,
                "overall_score": 0.0,
                "factual_accuracy": 0.0,
                "reasoning_depth": 0.0,
                "retrieval_faithfulness": 0.0,
                "citation_precision": 0.0,
                "mean_latency_ms": 0.0,
                "cost_per_1k_usd": cost_per_1k,
                "tier": m_def.tier,
                "is_local": m_def.is_local,
                "is_pareto_optimal": m_id in pareto_frontier,
                "last_evaluated": None,
            })

    # Sort leaderboard: evaluated first by score, then non-evaluated
    leaderboard.sort(key=lambda x: (-x["overall_score"], x["cost_per_1k_usd"]))
    for i, item in enumerate(leaderboard, start=1):
        item["rank"] = i

    return leaderboard
