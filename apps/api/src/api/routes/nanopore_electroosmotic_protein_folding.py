"""FastAPI routes for Phase 553: Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.nanopore_electroosmotic_protein_folding_repo import NanoporeElectroosmoticProteinFoldingRepository
from research.orchestration.nanopore_electroosmotic_protein_folding_engine import NanoporeElectroosmoticProteinFoldingEngine

router = APIRouter(prefix="/nanopore-electroosmotic-protein-folding", tags=["nanopore-electroosmotic-protein-folding"])


class AnalyzeNanoporeElectroosmoticProteinFoldingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler Run")
    target_specimen: str = Field(default="Single Bovine Carbonic Anhydrase II trapped in ClyA Biological Nanopore under Variable Transmembrane Voltage Bias")
    analytical_modality: str = Field(default="nanopore-electroosmotic-folding")
    input_scale: float = Field(default=1.0, ge=0.1, le=100.0)


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


class NanoporeElectroosmoticProteinFoldingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    single_molecule_trap_dwell_time_s: float
    electroosmotic_holding_force_pn: float
    unfolding_activation_free_energy_barrier_kt: float
    refolding_transition_rate_per_second: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=NanoporeElectroosmoticProteinFoldingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_nanopore_electroosmotic_protein_folding(
    req: AnalyzeNanoporeElectroosmoticProteinFoldingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler analysis and persist study."""
    engine = NanoporeElectroosmoticProteinFoldingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = NanoporeElectroosmoticProteinFoldingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        single_molecule_trap_dwell_time_s=result.single_molecule_trap_dwell_time_s,
        electroosmotic_holding_force_pn=result.electroosmotic_holding_force_pn,
        unfolding_activation_free_energy_barrier_kt=result.unfolding_activation_free_energy_barrier_kt,
        refolding_transition_rate_per_second=result.refolding_transition_rate_per_second,
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

    return NanoporeElectroosmoticProteinFoldingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        single_molecule_trap_dwell_time_s=study.single_molecule_trap_dwell_time_s,
        electroosmotic_holding_force_pn=study.electroosmotic_holding_force_pn,
        unfolding_activation_free_energy_barrier_kt=study.unfolding_activation_free_energy_barrier_kt,
        refolding_transition_rate_per_second=study.refolding_transition_rate_per_second,
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


@router.get("/studies", response_model=List[NanoporeElectroosmoticProteinFoldingStudyResponse])
async def list_nanopore_electroosmotic_protein_folding_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler studies."""
    repo = NanoporeElectroosmoticProteinFoldingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=NanoporeElectroosmoticProteinFoldingStudyResponse)
async def get_nanopore_electroosmotic_protein_folding_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler study by ID."""
    repo = NanoporeElectroosmoticProteinFoldingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
