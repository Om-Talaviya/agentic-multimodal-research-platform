"""FastAPI routes for Phase 536: Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cryoet_organelle_membrane_curvature_stress_repo import CryoetOrganelleMembraneCurvatureStressRepository
from research.orchestration.cryoet_organelle_membrane_curvature_stress_engine import CryoetOrganelleMembraneCurvatureStressEngine

router = APIRouter(prefix="/cryoet-organelle-membrane-curvature-stress", tags=["cryoet-organelle-membrane-curvature-stress"])


class AnalyzeCryoetOrganelleMembraneCurvatureStressRequest(BaseModel):
    name: str = Field(..., example="Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler Run")
    target_specimen: str = Field(default="Vitrified Primary Murine Hepatocyte Lamella showing In-Situ MAM (Mitochondria-Associated ER Membrane) Junctions")
    analytical_modality: str = Field(default="cryoet-organelle-membrane-stress")
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


class CryoetOrganelleMembraneCurvatureStressStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    membrane_bending_modulus_kbT: float
    mam_intermembrane_contact_distance_nm: float
    principal_curvature_radius_nm: float
    lipid_packing_defect_density_per_nm2: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CryoetOrganelleMembraneCurvatureStressStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cryoet_organelle_membrane_curvature_stress(
    req: AnalyzeCryoetOrganelleMembraneCurvatureStressRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler analysis and persist study."""
    engine = CryoetOrganelleMembraneCurvatureStressEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CryoetOrganelleMembraneCurvatureStressRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        membrane_bending_modulus_kbT=result.membrane_bending_modulus_kbT,
        mam_intermembrane_contact_distance_nm=result.mam_intermembrane_contact_distance_nm,
        principal_curvature_radius_nm=result.principal_curvature_radius_nm,
        lipid_packing_defect_density_per_nm2=result.lipid_packing_defect_density_per_nm2,
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

    return CryoetOrganelleMembraneCurvatureStressStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        membrane_bending_modulus_kbT=study.membrane_bending_modulus_kbT,
        mam_intermembrane_contact_distance_nm=study.mam_intermembrane_contact_distance_nm,
        principal_curvature_radius_nm=study.principal_curvature_radius_nm,
        lipid_packing_defect_density_per_nm2=study.lipid_packing_defect_density_per_nm2,
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


@router.get("/studies", response_model=List[CryoetOrganelleMembraneCurvatureStressStudyResponse])
async def list_cryoet_organelle_membrane_curvature_stress_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler studies."""
    repo = CryoetOrganelleMembraneCurvatureStressRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CryoetOrganelleMembraneCurvatureStressStudyResponse)
async def get_cryoet_organelle_membrane_curvature_stress_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler study by ID."""
    repo = CryoetOrganelleMembraneCurvatureStressRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
