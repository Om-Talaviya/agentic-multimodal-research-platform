"""FastAPI routes for Phase 467: Autonomous Living Tissue Origami Programmable 4D Cell-Sheet Self-Folding Mechanics Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.tissue_origami_cell_sheet_folding_repo import TissueOrigamiCellSheetFoldingRepository
from research.orchestration.tissue_origami_cell_sheet_folding_engine import TissueOrigamiCellSheetFoldingEngine

router = APIRouter(prefix="/tissue-origami-cell-sheet-folding", tags=["tissue-origami-cell-sheet-folding"])


class AnalyzeTissueOrigamiCellSheetFoldingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Living Tissue Origami Programmable 4D Cell-Sheet Self-Folding Mechanics Simulator Run")
    target_specimen: str = Field(default="Bilayer C2C12 Myoblast / NIH-3T3 Fibroblast Sheet on Thermoresponsive PNIPAM Hydrogel")
    analytical_modality: str = Field(default="4d-tissue-origami-folding")
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


class TissueOrigamiCellSheetFoldingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    mean_curvature_folding_radius_mm: float
    interfacial_shear_delamination_strain: float
    programmable_crease_bending_angle_deg: float
    myotube_uniaxial_prestress_kpa: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=TissueOrigamiCellSheetFoldingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_tissue_origami_cell_sheet_folding(
    req: AnalyzeTissueOrigamiCellSheetFoldingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Living Tissue Origami Programmable 4D Cell-Sheet Self-Folding Mechanics Simulator analysis and persist study."""
    engine = TissueOrigamiCellSheetFoldingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = TissueOrigamiCellSheetFoldingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        mean_curvature_folding_radius_mm=result.mean_curvature_folding_radius_mm,
        interfacial_shear_delamination_strain=result.interfacial_shear_delamination_strain,
        programmable_crease_bending_angle_deg=result.programmable_crease_bending_angle_deg,
        myotube_uniaxial_prestress_kpa=result.myotube_uniaxial_prestress_kpa,
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

    return TissueOrigamiCellSheetFoldingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        mean_curvature_folding_radius_mm=study.mean_curvature_folding_radius_mm,
        interfacial_shear_delamination_strain=study.interfacial_shear_delamination_strain,
        programmable_crease_bending_angle_deg=study.programmable_crease_bending_angle_deg,
        myotube_uniaxial_prestress_kpa=study.myotube_uniaxial_prestress_kpa,
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


@router.get("/studies", response_model=List[TissueOrigamiCellSheetFoldingStudyResponse])
async def list_tissue_origami_cell_sheet_folding_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Living Tissue Origami Programmable 4D Cell-Sheet Self-Folding Mechanics Simulator studies."""
    repo = TissueOrigamiCellSheetFoldingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=TissueOrigamiCellSheetFoldingStudyResponse)
async def get_tissue_origami_cell_sheet_folding_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Living Tissue Origami Programmable 4D Cell-Sheet Self-Folding Mechanics Simulator study by ID."""
    repo = TissueOrigamiCellSheetFoldingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
