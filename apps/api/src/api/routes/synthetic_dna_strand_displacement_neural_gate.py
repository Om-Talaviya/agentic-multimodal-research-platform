"""FastAPI route for Phase 570: Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.synthetic_dna_strand_displacement_neural_gate_repo import SyntheticDnaStrandDisplacementNeuralGateRepository
from research.orchestration.synthetic_dna_strand_displacement_neural_gate_engine import SyntheticDnaStrandDisplacementNeuralGateEngine

router = APIRouter(prefix="/synthetic-dna-strand-displacement-neural-gate", tags=["Phase 570 - Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine"])


class SyntheticDnaStrandDisplacementNeuralGateAnalyzeRequest(BaseModel):
    name: str = Field(default="Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine Study")
    target_specimen: Optional[str] = Field(default="Toehold-Mediated 4-Input 2-Class DNA Strand Displacement Reaction Network in Tris-Acetate-EDTA Buffer")
    analytical_modality: Optional[str] = Field(default="dsd-molecular-neural-classification")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


class ItemProfileResponse(BaseModel):
    item_name: str
    profile_category: str
    quantitative_value: float
    log2_fold_change: float
    significance_score: float


class MetricTraceResponse(BaseModel):
    metric_dimension: str
    observed_value: float
    z_score: float
    p_value: float


class SyntheticDnaStrandDisplacementNeuralGateStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    toehold_exchange_rate_constant_m_s: float
    signal_to_leakage_ratio: float
    winner_take_all_convergence_time_s: float
    decision_boundary_sharpness: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []


@router.post("/analyze", response_model=SyntheticDnaStrandDisplacementNeuralGateStudyResponse)
async def analyze_synthetic_dna_strand_displacement_neural_gate(
    req: SyntheticDnaStrandDisplacementNeuralGateAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute autonomous analysis for Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine."""
    engine = SyntheticDnaStrandDisplacementNeuralGateEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SyntheticDnaStrandDisplacementNeuralGateRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        toehold_exchange_rate_constant_m_s=result.toehold_exchange_rate_constant_m_s,
        signal_to_leakage_ratio=result.signal_to_leakage_ratio,
        winner_take_all_convergence_time_s=result.winner_take_all_convergence_time_s,
        decision_boundary_sharpness=result.decision_boundary_sharpness,
        confidence_score=result.confidence_score,
        status="completed",
        summary_report=result.summary_report,
    )

    for item in result.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=item.item_name,
            profile_category=item.profile_category,
            quantitative_value=item.quantitative_value,
            log2_fold_change=item.log2_fold_change,
            significance_score=item.significance_score,
        )

    for trace in result.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=trace.metric_dimension,
            observed_value=trace.observed_value,
            z_score=trace.z_score,
            p_value=trace.p_value,
        )

    return SyntheticDnaStrandDisplacementNeuralGateStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        toehold_exchange_rate_constant_m_s=study.toehold_exchange_rate_constant_m_s,
        signal_to_leakage_ratio=study.signal_to_leakage_ratio,
        winner_take_all_convergence_time_s=study.winner_take_all_convergence_time_s,
        decision_boundary_sharpness=study.decision_boundary_sharpness,
        confidence_score=study.confidence_score,
        status=study.status,
        summary_report=study.summary_report,
        item_profiles=[
            ItemProfileResponse(
                item_name=it.item_name,
                profile_category=it.profile_category,
                quantitative_value=it.quantitative_value,
                log2_fold_change=it.log2_fold_change,
                significance_score=it.significance_score,
            ) for it in result.item_profiles
        ],
        metric_traces=[
            MetricTraceResponse(
                metric_dimension=tr.metric_dimension,
                observed_value=tr.observed_value,
                z_score=tr.z_score,
                p_value=tr.p_value,
            ) for tr in result.metric_traces
        ],
    )


@router.get("/studies", response_model=List[SyntheticDnaStrandDisplacementNeuralGateStudyResponse])
async def list_synthetic_dna_strand_displacement_neural_gate_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine studies."""
    repo = SyntheticDnaStrandDisplacementNeuralGateRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SyntheticDnaStrandDisplacementNeuralGateStudyResponse)
async def get_synthetic_dna_strand_displacement_neural_gate_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic DNA Strand Displacement (DSD) Molecular Neural Network Winner-Take-All Classifier Engine study by ID."""
    repo = SyntheticDnaStrandDisplacementNeuralGateRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
