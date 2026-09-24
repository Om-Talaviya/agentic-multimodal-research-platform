"""FastAPI Route for Aptamer Evolution (Phase 143)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.aptamer_evolution_repo import AptamerEvolutionRepository
from research.nucleic.aptamer_evolution_engine import (
    AptamerEvolutionEngine,
    SELEXEvolutionRequest,
    SELEXEvolutionResult,
)

router = APIRouter(prefix="/aptamer-evolution", tags=["Aptamer Evolution"])


@router.post("/evolve", response_model=SELEXEvolutionResult)
async def evolve_aptamer(
    payload: SELEXEvolutionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = AptamerEvolutionEngine()
    result = engine.evolve(payload)

    repo = AptamerEvolutionRepository(db)
    camp = await repo.create_campaign(
        target_protein_name=result.target_protein_name,
        aptamer_type=result.aptamer_type,
        initial_pool_size=1000000,
        selection_rounds=result.total_rounds_simulated,
        top_kd_nanomolar=result.top_lead.kd_nm,
        consensus_motif=result.consensus_motif,
    )

    for traj in result.evolution_trajectory:
        await repo.add_round_sequence(
            campaign_id=camp.id,
            round_number=traj.round_num,
            sequence_string=traj.top_sequence,
            enrichment_fold=traj.fold_enrichment,
            secondary_structure_dot_bracket="((((....))))",
            free_energy_kcal_mol=-12.5,
        )

    await repo.add_binding_record(
        campaign_id=camp.id,
        aptamer_lead_id=result.top_lead.lead_id,
        target_epitope_residues="Basic Patch Surface Residues",
        kd_nanomolar=result.top_lead.kd_nm,
        off_target_selectivity_ratio=result.top_lead.specificity_ratio,
    )

    return result
