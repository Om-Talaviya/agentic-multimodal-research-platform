"""REST API endpoints for Systematic Literature Reviews (SLR) and PRISMA Meta-Analysis."""

from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.user import User
from database.repositories.literature_repo import LiteratureRepository
from research.literature.meta_analysis import (
    EffectSizeCalculator,
    HeterogeneityEngine,
    PooledEffectEstimator,
    PRISMAFlowTracker,
    RiskOfBiasEvaluator,
    SLROrchestrator,
)
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/literature", tags=["Literature Reviews & Meta-Analysis"])


# ---------------- Schemas ----------------

class CreateReviewPayload(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    research_question: str = Field(..., min_length=5)
    protocol_type: str = Field(default="PRISMA-2020")
    pico_framework: Optional[Dict[str, Any]] = None
    search_strategy: Optional[Dict[str, Any]] = None
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


class AddCriterionPayload(BaseModel):
    criterion_type: str = Field(..., pattern="^(inclusion|exclusion)$")
    description: str = Field(..., min_length=3)
    category: str = Field(default="general")
    order_index: int = Field(default=0)


class AddCandidatesPayload(BaseModel):
    studies: List[Dict[str, Any]] = Field(..., min_length=1)



class ScreenCandidatePayload(BaseModel):
    screening_status: str = Field(..., pattern="^(identified|title_abstract_screened|full_text_screened|included|excluded)$")
    exclusion_reason: Optional[str] = None
    relevance_score: Optional[float] = None
    methodology_type: Optional[str] = None
    sample_size: Optional[int] = None
    effect_size: Optional[float] = None
    variance: Optional[float] = None


class RunMetaAnalysisPayload(BaseModel):
    synthesis_name: str = Field(..., min_length=3)
    effect_metric: str = Field(default="hedges_g")
    model_type: str = Field(default="random_effects", pattern="^(fixed_effect|random_effects)$")


class RiskOfBiasPayload(BaseModel):
    candidate_id: uuid.UUID
    selection_bias: str = Field(default="low_risk", pattern="^(low_risk|some_concerns|high_risk)$")
    confounding_bias: str = Field(default="low_risk", pattern="^(low_risk|some_concerns|high_risk)$")
    measurement_bias: str = Field(default="low_risk", pattern="^(low_risk|some_concerns|high_risk)$")
    reporting_bias: str = Field(default="low_risk", pattern="^(low_risk|some_concerns|high_risk)$")
    overall_risk: str = Field(default="low_risk", pattern="^(low_risk|some_concerns|high_risk)$")
    justification_notes: Optional[str] = None
    evaluated_by: str = "expert_reviewer"


# ---------------- Review Endpoints ----------------

@router.post("/reviews", status_code=status.HTTP_201_CREATED)
async def create_literature_review(
    payload: CreateReviewPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Create a new Systematic Literature Review."""
    repo = LiteratureRepository(session)
    review = await repo.create_literature_review(
        user_id=current_user.id,
        title=payload.title,
        research_question=payload.research_question,
        protocol_type=payload.protocol_type,
        pico_framework=payload.pico_framework,
        search_strategy=payload.search_strategy,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
    )
    return {
        "id": str(review.id),
        "title": review.title,
        "research_question": review.research_question,
        "protocol_type": review.protocol_type,
        "current_phase": review.current_phase,
        "pico_framework": review.pico_framework,
        "search_strategy": review.search_strategy,
        "total_identified": review.total_identified,
        "total_screened": review.total_screened,
        "total_eligible": review.total_eligible,
        "total_included": review.total_included,
        "total_excluded": review.total_excluded,
        "created_at": review.created_at.isoformat(),
    }


@router.get("/reviews")
async def list_literature_reviews(
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    current_phase: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List SLR reviews with optional filtering."""
    repo = LiteratureRepository(session)
    reviews = await repo.list_literature_reviews(
        user_id=current_user.id if not workspace_id else None,
        workspace_id=workspace_id,
        project_id=project_id,
        current_phase=current_phase,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "research_question": r.research_question,
            "protocol_type": r.protocol_type,
            "current_phase": r.current_phase,
            "total_identified": r.total_identified,
            "total_screened": r.total_screened,
            "total_eligible": r.total_eligible,
            "total_included": r.total_included,
            "total_excluded": r.total_excluded,
            "created_at": r.created_at.isoformat(),
        }
        for r in reviews
    ]


@router.get("/reviews/{review_id}")
async def get_literature_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch complete SLR details including criteria, candidates, and meta-analyses."""
    repo = LiteratureRepository(session)
    review = await repo.get_literature_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Literature review not found")

    return {
        "id": str(review.id),
        "title": review.title,
        "research_question": review.research_question,
        "protocol_type": review.protocol_type,
        "current_phase": review.current_phase,
        "pico_framework": review.pico_framework,
        "search_strategy": review.search_strategy,
        "total_identified": review.total_identified,
        "total_screened": review.total_screened,
        "total_eligible": review.total_eligible,
        "total_included": review.total_included,
        "total_excluded": review.total_excluded,
        "criteria": [
            {
                "id": str(c.id),
                "criterion_type": c.criterion_type,
                "category": c.category,
                "description": c.description,
                "order_index": c.order_index,
                "is_active": c.is_active,
            }
            for c in review.criteria
        ],
        "candidates": [
            {
                "id": str(s.id),
                "title": s.title,
                "authors": s.authors,
                "publication_year": s.publication_year,
                "venue": s.venue,
                "doi": s.doi,
                "url": s.url,
                "screening_status": s.screening_status,
                "exclusion_reason": s.exclusion_reason,
                "relevance_score": s.relevance_score,
                "methodology_type": s.methodology_type,
                "sample_size": s.sample_size,
                "effect_size": s.effect_size,
                "variance": s.variance,
                "standard_error": s.standard_error,
                "risk_of_bias": {
                    "overall_risk": s.risk_of_bias.overall_risk,
                    "selection_bias": s.risk_of_bias.selection_bias,
                    "confounding_bias": s.risk_of_bias.confounding_bias,
                    "measurement_bias": s.risk_of_bias.measurement_bias,
                    "reporting_bias": s.risk_of_bias.reporting_bias,
                } if s.risk_of_bias else None,
            }
            for s in review.candidates
        ],
        "meta_analyses": [
            {
                "id": str(m.id),
                "synthesis_name": m.synthesis_name,
                "effect_metric": m.effect_metric,
                "model_type": m.model_type,
                "total_studies_analyzed": m.total_studies_analyzed,
                "pooled_effect_size": m.pooled_effect_size,
                "pooled_ci_lower": m.pooled_ci_lower,
                "pooled_ci_upper": m.pooled_ci_upper,
                "i_squared": m.i_squared,
                "p_value": m.pooled_p_value,
                "created_at": m.created_at.isoformat(),
            }
            for m in review.meta_analyses
        ],
        "created_at": review.created_at.isoformat(),
    }


@router.delete("/reviews/{review_id}", status_code=status.HTTP_200_OK)
async def delete_literature_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Delete a literature review and all associated candidates and analyses."""
    repo = LiteratureRepository(session)
    deleted = await repo.delete_literature_review(review_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Literature review not found")
    return {"message": "Literature review successfully deleted", "id": str(review_id)}


# ---------------- Criteria Endpoints ----------------

@router.post("/reviews/{review_id}/criteria", status_code=status.HTTP_201_CREATED)
async def add_criterion(
    review_id: uuid.UUID,
    payload: AddCriterionPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Add inclusion or exclusion criterion to review."""
    repo = LiteratureRepository(session)
    criterion = await repo.add_criterion(
        review_id=review_id,
        criterion_type=payload.criterion_type,
        description=payload.description,
        category=payload.category,
        order_index=payload.order_index,
    )
    return {
        "id": str(criterion.id),
        "review_id": str(criterion.review_id),
        "criterion_type": criterion.criterion_type,
        "category": criterion.category,
        "description": criterion.description,
        "order_index": criterion.order_index,
        "is_active": criterion.is_active,
    }


# ---------------- Candidate Study Endpoints ----------------

@router.post("/reviews/{review_id}/candidates", status_code=status.HTTP_201_CREATED)
async def add_candidate_studies(
    review_id: uuid.UUID,
    payload: AddCandidatesPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Batch add candidate studies to review."""
    repo = LiteratureRepository(session)
    studies = await repo.add_candidate_studies(review_id, payload.studies)
    return {
        "message": f"Added {len(studies)} candidate studies",
        "review_id": str(review_id),
        "added_count": len(studies),
    }


@router.patch("/reviews/{review_id}/candidates/{candidate_id}")
async def screen_candidate_study(
    review_id: uuid.UUID,
    candidate_id: uuid.UUID,
    payload: ScreenCandidatePayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Update screening decision and extracted metrics for a candidate study."""
    repo = LiteratureRepository(session)
    candidate = await repo.update_candidate_screening(
        candidate_id=candidate_id,
        screening_status=payload.screening_status,
        exclusion_reason=payload.exclusion_reason,
        relevance_score=payload.relevance_score,
        methodology_type=payload.methodology_type,
        sample_size=payload.sample_size,
        effect_size=payload.effect_size,
        variance=payload.variance,
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate study not found")

    return {
        "id": str(candidate.id),
        "review_id": str(candidate.review_id),
        "title": candidate.title,
        "screening_status": candidate.screening_status,
        "exclusion_reason": candidate.exclusion_reason,
        "effect_size": candidate.effect_size,
        "variance": candidate.variance,
        "sample_size": candidate.sample_size,
    }


# ---------------- Risk of Bias Endpoints ----------------

@router.post("/reviews/{review_id}/risk-of-bias", status_code=status.HTTP_201_CREATED)
async def evaluate_risk_of_bias(
    review_id: uuid.UUID,
    payload: RiskOfBiasPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Record or update risk of bias assessment for a study."""
    repo = LiteratureRepository(session)
    rob = await repo.save_risk_of_bias(
        candidate_id=payload.candidate_id,
        selection_bias=payload.selection_bias,
        confounding_bias=payload.confounding_bias,
        measurement_bias=payload.measurement_bias,
        reporting_bias=payload.reporting_bias,
        overall_risk=payload.overall_risk,
        justification_notes=payload.justification_notes,
        evaluated_by=payload.evaluated_by,
    )
    return {
        "id": str(rob.id),
        "candidate_id": str(rob.candidate_id),
        "selection_bias": rob.selection_bias,
        "confounding_bias": rob.confounding_bias,
        "measurement_bias": rob.measurement_bias,
        "reporting_bias": rob.reporting_bias,
        "overall_risk": rob.overall_risk,
        "evaluated_by": rob.evaluated_by,
    }


# ---------------- Meta-Analysis Endpoints ----------------

@router.post("/reviews/{review_id}/meta-analysis", status_code=status.HTTP_201_CREATED)
async def run_meta_analysis(
    review_id: uuid.UUID,
    payload: RunMetaAnalysisPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Run quantitative meta-analysis calculation on included studies with extracted metrics."""
    repo = LiteratureRepository(session)
    review = await repo.get_literature_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Literature review not found")

    included_studies = [
        {
            "id": str(c.id),
            "title": c.title,
            "authors": c.authors,
            "publication_year": c.publication_year,
            "sample_size": c.sample_size,
            "effect_size": c.effect_size,
            "variance": c.variance,
        }
        for c in review.candidates
        if c.screening_status == "included" and c.effect_size is not None and c.variance is not None
    ]

    if not included_studies:
        raise HTTPException(
            status_code=400,
            detail="No included studies with effect_size and variance found for meta-analysis.",
        )

    meta_result = SLROrchestrator.run_meta_analysis(
        studies=included_studies,
        synthesis_name=payload.synthesis_name,
        effect_metric=payload.effect_metric,
        model_type=payload.model_type,
    )

    report = await repo.save_meta_analysis_report(
        review_id=review_id,
        synthesis_name=payload.synthesis_name,
        effect_metric=payload.effect_metric,
        model_type=payload.model_type,
        total_studies_analyzed=meta_result["total_studies_analyzed"],
        pooled_effect_size=meta_result["pooled_effect_size"],
        pooled_ci_lower=meta_result["pooled_ci_lower"],
        pooled_ci_upper=meta_result["pooled_ci_upper"],
        pooled_p_value=meta_result["pooled_p_value"],
        z_score=meta_result["z_score"],
        q_statistic=meta_result["q_statistic"],
        degrees_of_freedom=meta_result["degrees_of_freedom"],
        i_squared=meta_result["i_squared"],
        tau_squared=meta_result["tau_squared"],
        forest_plot_data=meta_result["forest_plot_data"],
        summary_markdown=meta_result["summary_markdown"],
    )

    return {
        "id": str(report.id),
        "review_id": str(report.review_id),
        "synthesis_name": report.synthesis_name,
        "effect_metric": report.effect_metric,
        "model_type": report.model_type,
        "total_studies_analyzed": report.total_studies_analyzed,
        "pooled_effect_size": report.pooled_effect_size,
        "pooled_ci_lower": report.pooled_ci_lower,
        "pooled_ci_upper": report.pooled_ci_upper,
        "pooled_p_value": report.pooled_p_value,
        "z_score": report.z_score,
        "i_squared": report.i_squared,
        "q_statistic": report.q_statistic,
        "forest_plot_data": report.forest_plot_data,
        "summary_markdown": report.summary_markdown,
    }


# ---------------- PRISMA Flow & Platform Metrics ----------------

@router.get("/reviews/{review_id}/prisma-flow")
async def get_prisma_flow(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Retrieve PRISMA 2020 flow nodes and metrics for an SLR."""
    repo = LiteratureRepository(session)
    review = await repo.get_literature_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Literature review not found")

    exclusion_reasons: Dict[str, int] = {}
    for c in review.candidates:
        if c.screening_status == "excluded" and c.exclusion_reason:
            exclusion_reasons[c.exclusion_reason] = exclusion_reasons.get(c.exclusion_reason, 0) + 1

    flow = PRISMAFlowTracker.generate_flow_summary(
        identified=review.total_identified,
        screened=review.total_screened,
        eligible=review.total_eligible,
        included=review.total_included,
        excluded=review.total_excluded,
        exclusion_reasons=exclusion_reasons,
    )
    return flow


@router.get("/metrics")
async def get_slr_platform_metrics(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Query aggregate SLR platform metrics."""
    repo = LiteratureRepository(session)
    return await repo.get_slr_metrics()
