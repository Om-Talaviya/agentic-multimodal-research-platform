"""FastAPI routes for RAGAS Groundedness Evaluation and Adversarial Red-Teaming (Phase 51)."""
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.ragas_eval_repo import RagasEvaluationRepository
from research.evaluations.ragas_engine import RagasEvaluationEngine

router = APIRouter(prefix="/evaluations/ragas", tags=["RAGAS Evaluations"])


class SampleInput(BaseModel):
    query: str
    generated_answer: str
    retrieved_contexts: List[str]
    ground_truth: Optional[str] = None


class RedTeamProbeInput(BaseModel):
    attack_category: str
    prompt_payload: str


class RunRagasEvaluationRequest(BaseModel):
    name: str = Field(..., example="Multimodal Scientific Groundedness Benchmark v1")
    description: Optional[str] = None
    target_pipeline_id: Optional[str] = None
    samples: List[SampleInput]
    probes: Optional[List[RedTeamProbeInput]] = None


@router.post("/run", status_code=status.HTTP_201_CREATED)
async def run_ragas_evaluation(
    request: RunRagasEvaluationRequest,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Execute full RAGAS evaluation suite with automated scoring and adversarial probes."""
    engine = RagasEvaluationEngine()
    repo = RagasEvaluationRepository(session)

    samples_data = [s.model_dump() for s in request.samples]
    probes_data = [p.model_dump() for p in request.probes] if request.probes else None

    eval_result = engine.evaluate_benchmark_suite(
        name=request.name,
        samples_data=samples_data,
        probes_data=probes_data,
    )

    suite = await repo.create_suite(
        name=request.name,
        description=request.description,
        target_pipeline_id=request.target_pipeline_id,
        metadata_json={},
    )

    # Save samples
    for sample in eval_result["samples"]:
        await repo.add_sample(
            suite_id=suite.id,
            query=sample["query"],
            generated_answer=sample["generated_answer"],
            ground_truth=sample["ground_truth"],
            retrieved_contexts=sample["retrieved_contexts"],
            faithfulness_score=sample["faithfulness_score"],
            answer_relevancy_score=sample["answer_relevancy_score"],
            context_precision_score=sample["context_precision_score"],
            context_recall_score=sample["context_recall_score"],
            groundedness_score=sample["groundedness_score"],
            hallucination_flag=sample["hallucination_flag"],
        )

    # Save probes
    for probe in eval_result["probes"]:
        await repo.add_probe(
            suite_id=suite.id,
            attack_category=probe["attack_category"],
            prompt_payload=probe["prompt_payload"],
            guardrail_verdict=probe["guardrail_verdict"],
            mitigation_applied=probe["mitigation_applied"],
            is_defense_successful=probe["is_defense_successful"],
            latency_ms=probe["latency_ms"],
        )

    # Update summary metrics
    updated_suite = await repo.update_suite_metrics(
        suite_id=suite.id,
        total_samples=eval_result["total_samples"],
        avg_faithfulness=eval_result["avg_faithfulness"],
        avg_answer_relevancy=eval_result["avg_answer_relevancy"],
        avg_context_precision=eval_result["avg_context_precision"],
        avg_context_recall=eval_result["avg_context_recall"],
        avg_groundedness=eval_result["avg_groundedness"],
        red_team_defense_rate=eval_result["red_team_defense_rate"],
    )

    return {
        "suite": updated_suite.to_dict() if updated_suite else suite.to_dict(),
        "summary": eval_result,
    }


@router.get("/suites")
async def list_ragas_suites(
    limit: int = 50,
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List all evaluated benchmark suites."""
    repo = RagasEvaluationRepository(session)
    suites = await repo.list_suites(limit=limit)
    return [s.to_dict() for s in suites]


@router.get("/suites/{suite_id}")
async def get_ragas_suite_details(
    suite_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Get full evaluation suite details including sample metrics and security probes."""
    repo = RagasEvaluationRepository(session)
    suite = await repo.get_suite(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="RAGAS Evaluation Suite not found")

    samples = await repo.list_samples(suite_id)
    probes = await repo.list_probes(suite_id)

    return {
        "suite": suite.to_dict(),
        "samples": [s.to_dict() for s in samples],
        "probes": [p.to_dict() for p in probes],
    }
