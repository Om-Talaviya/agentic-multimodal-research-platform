"""FastAPI routes for Phase 558: Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.single_molecule_chromatin_nucleosome_unwrapping_repo import SingleMoleculeChromatinNucleosomeUnwrappingRepository
from research.orchestration.single_molecule_chromatin_nucleosome_unwrapping_engine import SingleMoleculeChromatinNucleosomeUnwrappingEngine

router = APIRouter(prefix="/single-molecule-chromatin-nucleosome-unwrapping", tags=["single-molecule-chromatin-nucleosome-unwrapping"])


class AnalyzeSingleMoleculeChromatinNucleosomeUnwrappingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler Run")
    target_specimen: str = Field(default="Reconstituted 12-Nucleosome Chromatin Array with Widom 601 positioning sequences stretched via Dual-Beam Optical Tweezers")
    analytical_modality: str = Field(default="chromatin-force-spectroscopy")
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


class SingleMoleculeChromatinNucleosomeUnwrappingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    outer_turn_unwrapping_force_threshold_pn: float
    inner_turn_cooperative_rupture_force_pn: float
    histone_octamer_dissociation_work_kcal_mol: float
    unwrapped_dna_contour_length_release_nm: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SingleMoleculeChromatinNucleosomeUnwrappingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_single_molecule_chromatin_nucleosome_unwrapping(
    req: AnalyzeSingleMoleculeChromatinNucleosomeUnwrappingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler analysis and persist study."""
    engine = SingleMoleculeChromatinNucleosomeUnwrappingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SingleMoleculeChromatinNucleosomeUnwrappingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        outer_turn_unwrapping_force_threshold_pn=result.outer_turn_unwrapping_force_threshold_pn,
        inner_turn_cooperative_rupture_force_pn=result.inner_turn_cooperative_rupture_force_pn,
        histone_octamer_dissociation_work_kcal_mol=result.histone_octamer_dissociation_work_kcal_mol,
        unwrapped_dna_contour_length_release_nm=result.unwrapped_dna_contour_length_release_nm,
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

    return SingleMoleculeChromatinNucleosomeUnwrappingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        outer_turn_unwrapping_force_threshold_pn=study.outer_turn_unwrapping_force_threshold_pn,
        inner_turn_cooperative_rupture_force_pn=study.inner_turn_cooperative_rupture_force_pn,
        histone_octamer_dissociation_work_kcal_mol=study.histone_octamer_dissociation_work_kcal_mol,
        unwrapped_dna_contour_length_release_nm=study.unwrapped_dna_contour_length_release_nm,
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


@router.get("/studies", response_model=List[SingleMoleculeChromatinNucleosomeUnwrappingStudyResponse])
async def list_single_molecule_chromatin_nucleosome_unwrapping_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler studies."""
    repo = SingleMoleculeChromatinNucleosomeUnwrappingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SingleMoleculeChromatinNucleosomeUnwrappingStudyResponse)
async def get_single_molecule_chromatin_nucleosome_unwrapping_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler study by ID."""
    repo = SingleMoleculeChromatinNucleosomeUnwrappingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
