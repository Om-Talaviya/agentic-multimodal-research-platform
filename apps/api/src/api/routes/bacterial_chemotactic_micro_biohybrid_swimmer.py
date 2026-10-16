"""FastAPI route for Phase 568: Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.bacterial_chemotactic_micro_biohybrid_swimmer_repo import BacterialChemotacticMicroBiohybridSwimmerRepository
from research.orchestration.bacterial_chemotactic_micro_biohybrid_swimmer_engine import BacterialChemotacticMicroBiohybridSwimmerEngine

router = APIRouter(prefix="/bacterial-chemotactic-micro-biohybrid-swimmer", tags=["Phase 568 - Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator"])


class BacterialChemotacticMicroBiohybridSwimmerAnalyzeRequest(BaseModel):
    name: str = Field(default="Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator Study")
    target_specimen: Optional[str] = Field(default="Engineered Escherichia coli MG1655 Flagellar Micro-Biohybrid Swimmers in Attractant Aspartate Microfluidic Gradient")
    analytical_modality: Optional[str] = Field(default="bacterial-chemotactic-biohybrid-simulation")
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


class BacterialChemotacticMicroBiohybridSwimmerStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    chemotactic_drift_velocity_um_s: float
    run_tumble_frequency_ratio: float
    target_accumulation_index: float
    flagellar_motor_torque_efficiency: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []


@router.post("/analyze", response_model=BacterialChemotacticMicroBiohybridSwimmerStudyResponse)
async def analyze_bacterial_chemotactic_micro_biohybrid_swimmer(
    req: BacterialChemotacticMicroBiohybridSwimmerAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute autonomous analysis for Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator."""
    engine = BacterialChemotacticMicroBiohybridSwimmerEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = BacterialChemotacticMicroBiohybridSwimmerRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        chemotactic_drift_velocity_um_s=result.chemotactic_drift_velocity_um_s,
        run_tumble_frequency_ratio=result.run_tumble_frequency_ratio,
        target_accumulation_index=result.target_accumulation_index,
        flagellar_motor_torque_efficiency=result.flagellar_motor_torque_efficiency,
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

    return BacterialChemotacticMicroBiohybridSwimmerStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        chemotactic_drift_velocity_um_s=study.chemotactic_drift_velocity_um_s,
        run_tumble_frequency_ratio=study.run_tumble_frequency_ratio,
        target_accumulation_index=study.target_accumulation_index,
        flagellar_motor_torque_efficiency=study.flagellar_motor_torque_efficiency,
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


@router.get("/studies", response_model=List[BacterialChemotacticMicroBiohybridSwimmerStudyResponse])
async def list_bacterial_chemotactic_micro_biohybrid_swimmer_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator studies."""
    repo = BacterialChemotacticMicroBiohybridSwimmerRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=BacterialChemotacticMicroBiohybridSwimmerStudyResponse)
async def get_bacterial_chemotactic_micro_biohybrid_swimmer_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Engineered Bacterial Chemotactic Micro-Biohybrid Swimmer Targeted Navigation & Tumble-Run Kinetics Simulator study by ID."""
    repo = BacterialChemotacticMicroBiohybridSwimmerRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
