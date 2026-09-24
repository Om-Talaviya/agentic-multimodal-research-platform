"""FastAPI Route for Multi-Objective mRNA Codon Optimization (Phase 153)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.mrna_codon_optimization_repo import mRNACodonRepository
from research.vaccines.mrna_codon_engine import (
    mRNACodonEngine,
    mRNACodonRequest,
    mRNACodonResult,
)

router = APIRouter(prefix="/mrna-codon", tags=["mRNA Codon Optimization"])


@router.post("/optimize", response_model=mRNACodonResult)
async def optimize_mrna_codons(
    payload: mRNACodonRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = mRNACodonEngine()
    result = engine.optimize(payload)

    repo = mRNACodonRepository(db)
    campaign = await repo.create_campaign(
        target_protein_name=result.target_protein_name,
        expression_host=result.expression_host,
        original_cai=result.original_cai,
        optimized_cai=result.optimized_cai,
        gc_content_percent=result.gc_content_percent,
        mfe_secondary_struct_kcal_mol=result.mfe_secondary_struct_kcal_mol,
        uridine_depletion_percent=result.uridine_depletion_percent,
        translation_efficiency_score=result.translation_efficiency_score,
    )

    for v in result.candidate_variants:
        await repo.add_variant(
            campaign_id=campaign.id,
            variant_rank=v.variant_rank,
            mrna_sequence=v.mrna_sequence_preview,
            pareto_fitness_score=v.pareto_fitness_score,
            ribosome_dwell_time_ms=v.ribosome_dwell_time_ms,
            immunogenicity_risk_score=v.immunogenicity_risk_score,
        )

    for c in result.cai_profile_sample:
        await repo.add_cai_point(
            campaign_id=campaign.id,
            codon_position=c.codon_position,
            codon_triplet=c.codon_triplet,
            amino_acid=c.amino_acid,
            relative_adaptiveness=c.relative_adaptiveness,
        )

    return result
