"""FastAPI Route for Spatial Proteomics CODEX (Phase 155)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.spatial_proteomics_codex_repo import SpatialProteomicsCODEXRepository
from research.spatial.codex_spatial_proteomics_engine import (
    CODEXSpatialProteomicsEngine,
    SpatialProteomicsCODEXRequest,
    SpatialProteomicsCODEXResult,
)

router = APIRouter(prefix="/spatial-proteomics-codex", tags=["Spatial Proteomics CODEX"])


@router.post("/process", response_model=SpatialProteomicsCODEXResult)
async def process_codex_panel(
    payload: SpatialProteomicsCODEXRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = CODEXSpatialProteomicsEngine()
    result = engine.process_multiplex_panel(payload)

    repo = SpatialProteomicsCODEXRepository(db)
    study = await repo.create_study(
        tissue_sample_name=result.tissue_sample_name,
        organ_tissue_type=result.organ_tissue_type,
        multiplex_panel_size=result.multiplex_panel_size,
        single_cells_segmented=result.single_cells_segmented,
        cellular_neighborhoods_count=result.cellular_neighborhoods_count,
        mean_signal_to_background=result.mean_signal_to_background,
        immune_infiltration_score=result.immune_infiltration_score,
    )

    for m in result.marker_expressions:
        await repo.add_marker_expression(
            study_id=study.id,
            marker_name=m.marker_name,
            cellular_compartment=m.cellular_compartment,
            mean_fluorescence_intensity=m.mean_fluorescence_intensity,
            signal_to_noise_ratio=m.signal_to_noise_ratio,
            positive_cells_percentage=m.positive_cells_percentage,
        )

    for n in result.neighborhood_phenotypes:
        await repo.add_neighborhood_phenotype(
            study_id=study.id,
            neighborhood_cluster_id=n.neighborhood_cluster_id,
            neighborhood_name=n.neighborhood_name,
            dominant_cell_type=n.dominant_cell_type,
            radius_um=n.radius_um,
            cell_density_per_mm2=n.cell_density_per_mm2,
            immunosuppression_index=n.immunosuppression_index,
        )

    return result
