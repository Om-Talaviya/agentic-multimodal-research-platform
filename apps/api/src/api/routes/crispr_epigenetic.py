"""FastAPI Route for Epigenetic CRISPR Editing (Phase 159)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.epigenetic_crispr_editing_repo import EpigeneticCRISPRRepository
from research.epigenetics.crispr_epigenetic_engine import (
    CRISPREpigeneticEngine,
    CRISPREpigeneticRequest,
    CRISPREpigeneticResult,
)

router = APIRouter(prefix="/crispr-epigenetic", tags=["Epigenetic CRISPR Editing"])


@router.post("/edit", response_model=CRISPREpigeneticResult)
async def edit_epigenetics(
    payload: CRISPREpigeneticRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = CRISPREpigeneticEngine()
    result = engine.simulate_epigenetic_editing(payload)

    repo = EpigeneticCRISPRRepository(db)
    study = await repo.create_study(
        target_locus_name=result.target_locus_name,
        catalytic_effector=result.catalytic_effector,
        guide_rna_sequence=result.guide_rna_sequence,
        targeted_cpg_count=result.targeted_cpg_count,
        target_methylation_change_pct=result.target_methylation_change_pct,
        transcriptional_repression_log2fc=result.transcriptional_repression_log2fc,
        mitotic_memory_retention_days=result.mitotic_memory_retention_days,
        off_target_epimutation_rate_pct=result.off_target_epimutation_rate_pct,
    )

    for c in result.cpg_profiles:
        await repo.add_cpg_profile(
            study_id=study.id,
            genomic_coordinate_bp=c.genomic_coordinate_bp,
            baseline_methylation_pct=c.baseline_methylation_pct,
            post_edit_methylation_pct=c.post_edit_methylation_pct,
            bisulfite_read_depth=c.bisulfite_read_depth,
        )

    for o in result.off_targets:
        await repo.add_off_target(
            study_id=study.id,
            off_target_locus=o.off_target_locus,
            mismatch_count=o.mismatch_count,
            methylation_drift_pct=o.methylation_drift_pct,
            safety_classification=o.safety_classification,
        )

    return result
