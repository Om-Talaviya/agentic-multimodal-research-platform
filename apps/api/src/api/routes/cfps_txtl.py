"""FastAPI Route for Cell-Free Protein Synthesis TX-TL (Phase 157)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.cfps_txtl_kinetics_repo import CFPSTXTLRepository
from research.synthetic_biology.cfps_txtl_engine import (
    CFPSTXTLEngine,
    CFPSTXTLRequest,
    CFPSTXTLResult,
)

router = APIRouter(prefix="/cfps-txtl", tags=["CFPS TX-TL Kinetics"])


@router.post("/simulate", response_model=CFPSTXTLResult)
async def simulate_cfps_reaction(
    payload: CFPSTXTLRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = CFPSTXTLEngine()
    result = engine.simulate_tx_tl(payload)

    repo = CFPSTXTLRepository(db)
    study = await repo.create_study(
        target_protein_name=result.target_protein_name,
        extract_system_type=result.extract_system_type,
        reaction_mode=result.reaction_mode,
        reaction_time_hours=result.reaction_time_hours,
        final_protein_yield_mg_ml=result.final_protein_yield_mg_ml,
        transcription_rate_nt_s=result.transcription_rate_nt_s,
        translation_rate_aa_s=result.translation_rate_aa_s,
        energy_regeneration_efficiency=result.energy_regeneration_efficiency,
    )

    for y in result.yield_trajectories:
        await repo.add_yield_curve_point(
            study_id=study.id,
            time_elapsed_hours=y.time_elapsed_hours,
            mrna_concentration_uM=y.mrna_concentration_uM,
            protein_concentration_mg_ml=y.protein_concentration_mg_ml,
            ribosome_active_fraction=y.ribosome_active_fraction,
        )

    for s in result.substrate_depletions:
        await repo.add_substrate_depletion(
            study_id=study.id,
            substrate_name=s.substrate_name,
            initial_concentration_mM=s.initial_concentration_mM,
            final_concentration_mM=s.final_concentration_mM,
            consumption_rate_mM_h=s.consumption_rate_mM_h,
        )

    return result
