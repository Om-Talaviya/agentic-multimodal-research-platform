"""FastAPI Route for Single-Cell Spatial Flux Balance (Phase 150)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.single_cell_spatial_flux_repo import SpatialFluxRepository
from research.metabolism.spatial_flux_engine import (
    SpatialFluxEngine,
    SpatialFluxRequest,
    SpatialFluxResult,
)

router = APIRouter(prefix="/spatial-flux", tags=["Spatial Flux Balance"])


@router.post("/solve", response_model=SpatialFluxResult)
async def solve_spatial_flux(
    payload: SpatialFluxRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = SpatialFluxEngine()
    result = engine.solve(payload)

    repo = SpatialFluxRepository(db)
    study = await repo.create_study(
        tissue_sample_id=result.tissue_sample_id,
        organ_context=result.organ_context,
        single_cells_simulated=result.single_cells_simulated,
        mean_glycolytic_flux=result.mean_glycolytic_flux,
        mean_oxphos_flux=result.mean_oxphos_flux,
        lactate_secretion_rate=result.lactate_secretion_rate,
        atp_generation_rate=result.atp_generation_rate,
    )

    for p in result.pathway_fluxes:
        await repo.add_flux_rate(
            study_id=study.id,
            reaction_id=p.reaction_id,
            reaction_name=p.reaction_name,
            subsystem=p.subsystem,
            flux_rate_mmol_gdw_h=p.flux_rate_mmol_gdw_h,
            shadow_price=p.shadow_price,
        )

    for m in result.microdomains:
        await repo.add_microdomain(
            study_id=study.id,
            domain_name=m.domain_name,
            radial_distance_um=m.radial_distance_um,
            oxygen_concentration_uM=m.oxygen_concentration_uM,
            glucose_concentration_mM=m.glucose_concentration_mM,
            warburg_phenotype_score=m.warburg_phenotype_score,
        )

    return result
