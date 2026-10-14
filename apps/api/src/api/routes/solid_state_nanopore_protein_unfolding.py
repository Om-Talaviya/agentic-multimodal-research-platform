"""FastAPI routes for Phase 508: Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.solid_state_nanopore_protein_unfolding_repo import SolidStateNanoporeProteinUnfoldingRepository
from research.orchestration.solid_state_nanopore_protein_unfolding_engine import SolidStateNanoporeProteinUnfoldingEngine

router = APIRouter(prefix="/solid-state-nanopore-protein-unfolding", tags=["solid-state-nanopore-protein-unfolding"])


class AnalyzeSolidStateNanoporeProteinUnfoldingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler Run")
    target_specimen: str = Field(default="Sub-3nm Low-Noise HfO2 Nanopore with ClpX-Coupled Maltose-Binding Protein Translocation")
    analytical_modality: str = Field(default="nanopore-protein-unfolding")
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


class SolidStateNanoporeProteinUnfoldingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    unfolding_energy_barrier_height_kbT: float
    translocation_dwell_time_per_domain_ms: float
    residual_current_fraction_blockade: float
    single_amino_acid_substitutional_snr: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SolidStateNanoporeProteinUnfoldingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_solid_state_nanopore_protein_unfolding(
    req: AnalyzeSolidStateNanoporeProteinUnfoldingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler analysis and persist study."""
    engine = SolidStateNanoporeProteinUnfoldingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SolidStateNanoporeProteinUnfoldingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        unfolding_energy_barrier_height_kbT=result.unfolding_energy_barrier_height_kbT,
        translocation_dwell_time_per_domain_ms=result.translocation_dwell_time_per_domain_ms,
        residual_current_fraction_blockade=result.residual_current_fraction_blockade,
        single_amino_acid_substitutional_snr=result.single_amino_acid_substitutional_snr,
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

    return SolidStateNanoporeProteinUnfoldingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        unfolding_energy_barrier_height_kbT=study.unfolding_energy_barrier_height_kbT,
        translocation_dwell_time_per_domain_ms=study.translocation_dwell_time_per_domain_ms,
        residual_current_fraction_blockade=study.residual_current_fraction_blockade,
        single_amino_acid_substitutional_snr=study.single_amino_acid_substitutional_snr,
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


@router.get("/studies", response_model=List[SolidStateNanoporeProteinUnfoldingStudyResponse])
async def list_solid_state_nanopore_protein_unfolding_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler studies."""
    repo = SolidStateNanoporeProteinUnfoldingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SolidStateNanoporeProteinUnfoldingStudyResponse)
async def get_solid_state_nanopore_protein_unfolding_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler study by ID."""
    repo = SolidStateNanoporeProteinUnfoldingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
