"""FastAPI Route for TCR-pMHC Affinity (Phase 145)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.tcr_pmhc_repo import TCRpMHCRepository
from research.immunology.tcr_pmhc_engine import (
    TCRpMHCAffinityEngine,
    TCRpMHCPredictionRequest,
    TCRpMHCPredictionResult,
)

router = APIRouter(prefix="/tcr-pmhc", tags=["TCR-pMHC Affinity"])


@router.post("/predict", response_model=TCRpMHCPredictionResult)
async def predict_tcr_pmhc_affinity(
    payload: TCRpMHCPredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = TCRpMHCAffinityEngine()
    result = engine.predict(payload)

    repo = TCRpMHCRepository(db)
    study = await repo.create_study(
        tcr_name=result.tcr_name,
        cdr3_alpha_seq=payload.cdr3_alpha_seq,
        cdr3_beta_seq=payload.cdr3_beta_seq,
        target_peptide=result.target_peptide,
        hla_allele=result.hla_allele,
        binding_affinity_kd_um=result.binding_kd_um,
        immunogenicity_score=result.immunogenicity_score,
    )

    for ot in result.cross_reactivity_scan:
        await repo.add_cross_reactivity_record(
            study_id=study.id,
            self_peptide_seq=ot.self_peptide,
            tissue_expression=ot.tissue,
            predicted_cross_kd_um=ot.cross_kd_um,
            off_target_risk_level=ot.risk_level,
        )

    return result
