"""FastAPI routes for Phase 403: Autonomous Injectable Supramolecular Peptide Shear-Thinning Biomaterial Modeler Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.supramolecular_peptide_hydrogel_repo import SupramolecularPeptideHydrogelRepository
from research.orchestration.supramolecular_peptide_hydrogel_engine import SupramolecularPeptideHydrogelEngine

router = APIRouter(prefix="/supramolecular-peptide-hydrogel", tags=["supramolecular-peptide-hydrogel"])


class AnalyzeSupramolecularPeptideHydrogelRequest(BaseModel):
    name: str = Field(..., example="Autonomous Autonomous Injectable Supramolecular Peptide Shear-Thinning Biomaterial Modeler Run")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="supramolecular-peptide-hydrogel")
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


class SupramolecularPeptideHydrogelStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    storage_modulus_g_prime_plateau_pascals: float
    shear_thinning_recovery_half_time_seconds: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SupramolecularPeptideHydrogelStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_supramolecular_peptide_hydrogel(
    req: AnalyzeSupramolecularPeptideHydrogelRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Injectable Supramolecular Peptide Shear-Thinning Biomaterial Modeler analysis and persist study record."""
    engine = SupramolecularPeptideHydrogelEngine()
    analysis = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SupramolecularPeptideHydrogelRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=analysis.target_specimen,
        analytical_modality=analysis.analytical_modality,
        storage_modulus_g_prime_plateau_pascals=getattr(analysis, "storage_modulus_g_prime_plateau_pascals"),
        shear_thinning_recovery_half_time_seconds=getattr(analysis, "shear_thinning_recovery_half_time_seconds"),
        confidence_score=analysis.confidence_score,
        status="completed",
        summary_report=analysis.summary_report,
    )

    for it in analysis.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=it.item_name,
            profile_category=it.profile_category,
            quantitative_value=it.quantitative_value,
            log2_fold_change=it.log2_fold_change,
            significance_score=it.significance_score,
        )

    for tr in analysis.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=tr.metric_dimension,
            observed_value=tr.observed_value,
            z_score=tr.z_score,
            p_value=tr.p_value,
        )

    return SupramolecularPeptideHydrogelStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        storage_modulus_g_prime_plateau_pascals=getattr(study, "storage_modulus_g_prime_plateau_pascals"),
        shear_thinning_recovery_half_time_seconds=getattr(study, "shear_thinning_recovery_half_time_seconds"),
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
            ) for it in analysis.item_profiles
        ],
        metric_traces=[
            MetricTraceResponse(
                metric_dimension=tr.metric_dimension,
                observed_value=tr.observed_value,
                z_score=tr.z_score,
                p_value=tr.p_value,
            ) for tr in analysis.metric_traces
        ],
    )


@router.get("/studies", response_model=List[SupramolecularPeptideHydrogelStudyResponse])
async def list_supramolecular_peptide_hydrogel_studies(
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List historical Autonomous Injectable Supramolecular Peptide Shear-Thinning Biomaterial Modeler studies."""
    repo = SupramolecularPeptideHydrogelRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        SupramolecularPeptideHydrogelStudyResponse(
            id=s.id,
            name=s.name,
            target_specimen=s.target_specimen,
            analytical_modality=s.analytical_modality,
            storage_modulus_g_prime_plateau_pascals=getattr(s, "storage_modulus_g_prime_plateau_pascals"),
            shear_thinning_recovery_half_time_seconds=getattr(s, "shear_thinning_recovery_half_time_seconds"),
            confidence_score=s.confidence_score,
            status=s.status,
            summary_report=s.summary_report,
            item_profiles=[],
            metric_traces=[],
        ) for s in studies
    ]


@router.get("/studies/{study_id}", response_model=SupramolecularPeptideHydrogelStudyResponse)
async def get_supramolecular_peptide_hydrogel_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve details for a single Autonomous Injectable Supramolecular Peptide Shear-Thinning Biomaterial Modeler study."""
    repo = SupramolecularPeptideHydrogelRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return SupramolecularPeptideHydrogelStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        storage_modulus_g_prime_plateau_pascals=getattr(study, "storage_modulus_g_prime_plateau_pascals"),
        shear_thinning_recovery_half_time_seconds=getattr(study, "shear_thinning_recovery_half_time_seconds"),
        confidence_score=study.confidence_score,
        status=study.status,
        summary_report=study.summary_report,
        item_profiles=[],
        metric_traces=[],
    )
