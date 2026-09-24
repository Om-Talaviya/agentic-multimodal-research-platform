"""FastAPI Route for Glycomics Microarray (Phase 148)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.glycan_microarray_repo import GlycanMicroarrayRepository
from research.glycomics.glycan_microarray_engine import (
    GlycanMicroarrayEngine,
    GlycanScreenRequest,
    GlycanScreenResult,
)

router = APIRouter(prefix="/glycan-microarray", tags=["Glycomics Microarray"])


@router.post("/screen", response_model=GlycanScreenResult)
async def screen_glycan_microarray(
    payload: GlycanScreenRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = GlycanMicroarrayEngine()
    result = engine.analyze(payload)

    repo = GlycanMicroarrayRepository(db)
    screen = await repo.create_screen(
        target_lectin_name=result.target_lectin_name,
        organism_source=result.organism_source,
        array_spots_count=result.spots_evaluated,
        mean_signal_to_noise=result.mean_signal_to_noise,
        primary_epitope_motif=result.primary_epitope_motif,
        kd_apparent_nM=result.kd_apparent_nM,
    )

    for s in result.top_binding_spots:
        await repo.add_spot_record(
            screen_id=screen.id,
            glycan_iupac=s.glycan_iupac,
            spot_index=s.spot_index,
            fluorescence_rfu=s.fluorescence_rfu,
            z_score=s.z_score,
            relative_affinity=s.relative_affinity,
        )

    for m in result.motif_enrichments:
        await repo.add_specificity_profile(
            screen_id=screen.id,
            glycan_motif=m.motif_name,
            enrichment_fold=m.enrichment_fold,
            p_value_log10=m.p_value_log10,
            selectivity_index=m.selectivity_index,
        )

    return result
