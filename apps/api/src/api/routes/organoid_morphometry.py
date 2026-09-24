"""FastAPI Route for 3D Tumor Organoid Morphometry (Phase 147)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.organoid_morphometry_repo import OrganoidMorphometryRepository
from research.imaging.organoid_morphometry_engine import (
    OrganoidMorphometryEngine,
    OrganoidAnalysisRequest,
    OrganoidAnalysisResult,
)

router = APIRouter(prefix="/organoid-morphometry", tags=["Organoid Morphometry"])


@router.post("/analyze", response_model=OrganoidAnalysisResult)
async def analyze_organoid(
    payload: OrganoidAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = OrganoidMorphometryEngine()
    result = engine.analyze(payload)

    repo = OrganoidMorphometryRepository(db)
    study = await repo.create_study(
        study_name=result.study_name,
        tumor_type=result.tumor_type,
        organoid_count=1,
        mean_diameter_um=result.mean_diameter_um,
        mean_volume_um3=result.mean_volume_um3,
        sphericity_index=result.sphericity_index,
        necrotic_core_ratio=result.necrotic_core_ratio,
        hypoxia_gradient_slope=result.hypoxia_gradient_slope,
    )

    for s in result.z_slices:
        await repo.add_z_stack(
            study_id=study.id,
            slice_depth_um=s.depth_um,
            cross_sectional_area_um2=s.area_um2,
            circularity=s.circularity,
            fluorescence_intensity=s.fluorescence_intensity,
            live_dead_ratio=s.live_dead_ratio,
        )

    for d in result.dose_responses:
        await repo.add_dose_response(
            study_id=study.id,
            compound_name=d.compound_name,
            dose_uM=d.dose_uM,
            viability_pct=d.viability_pct,
            invasion_inhibition_pct=d.invasion_inhibition_pct,
            computed_ic50_uM=d.computed_ic50_uM,
        )

    return result
