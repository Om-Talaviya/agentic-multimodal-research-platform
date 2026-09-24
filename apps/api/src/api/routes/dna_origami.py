"""FastAPI Route for DNA Origami Nanorobot (Phase 149)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.dna_origami_nanorobot_repo import DNAOrigamiRepository
from research.nanotech.dna_origami_engine import (
    DNAOrigamiEngine,
    DNAOrigamiDesignRequest,
    DNAOrigamiDesignResult,
)

router = APIRouter(prefix="/dna-origami", tags=["DNA Origami"])


@router.post("/design", response_model=DNAOrigamiDesignResult)
async def design_dna_origami(
    payload: DNAOrigamiDesignRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = DNAOrigamiEngine()
    result = engine.design(payload)

    repo = DNAOrigamiRepository(db)
    campaign = await repo.create_campaign(
        nanorobot_name=result.nanorobot_name,
        geometry_type=result.geometry_type,
        scaffold_type=result.scaffold_type,
        staple_strands_count=result.staple_strands_count,
        predicted_melting_temp_c=result.predicted_melting_temp_c,
        folding_yield_percent=result.folding_yield_percent,
        cargo_cavity_volume_nm3=result.cargo_cavity_volume_nm3,
        latch_trigger_affinity_nM=result.latch_trigger_affinity_nM,
    )

    for s in result.staple_strands:
        await repo.add_staple(
            campaign_id=campaign.id,
            strand_index=s.strand_index,
            sequence_5to3=s.sequence_5to3,
            length_nt=s.length_nt,
            tm_celsius=s.tm_celsius,
            crossover_count=s.crossover_count,
        )

    for l in result.latch_mechanisms:
        await repo.add_latch(
            campaign_id=campaign.id,
            target_biomarker=l.target_biomarker,
            aptamer_sequence=l.aptamer_sequence,
            opening_half_life_min=l.opening_half_life_min,
            selectivity_ratio=l.selectivity_ratio,
        )

    return result
