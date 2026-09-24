"""FastAPI Route for Spatial RNA Velocity (Phase 146)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.spatial_rna_velocity_repo import SpatialRNAVelocityRepository
from research.spatial.spatial_rna_velocity_engine import (
    SpatialRNAVelocityEngine,
    SpatialVelocitySimulationRequest,
    SpatialVelocitySimulationResult,
)

router = APIRouter(prefix="/spatial-rna-velocity", tags=["Spatial RNA Velocity"])


@router.post("/simulate", response_model=SpatialVelocitySimulationResult)
async def simulate_spatial_velocity(
    payload: SpatialVelocitySimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = SpatialRNAVelocityEngine()
    result = engine.simulate(payload)

    repo = SpatialRNAVelocityRepository(db)
    study = await repo.create_study(
        tissue_sample_name=result.tissue_sample,
        developmental_stage=result.developmental_stage,
        spot_count=result.spots_simulated,
        mean_velocity_magnitude=result.mean_speed,
        coherence_score=result.directionality_coherence,
    )

    for s in result.spots:
        await repo.add_vector_spot(
            study_id=study.id,
            spot_index=s.spot_id,
            x_coord_um=s.x,
            y_coord_um=s.y,
            vx_vector=s.vx,
            vy_vector=s.vy,
            cell_type_annotation=s.cell_state,
        )

    for f in result.streamlines:
        await repo.add_streamline(
            study_id=study.id,
            streamline_id=f.flow_id,
            origin_cell_state=f.source_state,
            terminal_cell_state=f.dest_state,
            pseudotime_length=f.pseudotime,
        )

    return result
