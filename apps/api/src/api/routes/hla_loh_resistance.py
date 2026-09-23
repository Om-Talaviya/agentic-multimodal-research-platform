"""
Phase 135: Cancer Immunogenomics HLA Loss of Heterozygosity (LOH) & Immune Evasion API Route.
"""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.hla_loh_resistance_repo import HLALOHResistanceRepository
from research.genomics.hla_loh_engine import (
    HLALOHImmuneEvasionEngine,
    AlleleInput,
)

router = APIRouter(prefix="/hla-loh", tags=["HLA LOH & Immune Evasion"])


class AlleleItem(BaseModel):
    hla_gene: str
    allele_name: str
    tumor_depth: int = 150
    normal_depth: int = 80
    baf_tumor: float = 0.12
    purity: float = 0.70


class HLALOHRequest(BaseModel):
    patient_id: str = Field(..., example="PAT_MEL_401")
    tumor_type: str = Field(..., example="Cutaneous Melanoma")
    alleles: Optional[List[AlleleItem]] = None
    tumor_purity: float = Field(default=0.65, example=0.65)
    workspace_id: Optional[str] = None


@router.post("/evaluate", status_code=status.HTTP_201_CREATED)
async def evaluate_hla_loh_endpoint(
    req: HLALOHRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = HLALOHImmuneEvasionEngine()
    engine_alleles = (
        [AlleleInput(**a.model_dump()) for a in req.alleles]
        if req.alleles
        else None
    )

    result = engine.evaluate_hla_loh(
        patient_id=req.patient_id,
        tumor_type=req.tumor_type,
        alleles=engine_alleles,
        tumor_purity=req.tumor_purity,
    )

    repo = HLALOHResistanceRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    study = await repo.create_study(
        project_id=ws_id,
        patient_cohort_id=result.patient_id,
        tumor_type=result.tumor_type,
        total_alleles_analyzed=result.total_alleles,
        loh_positive_allele_count=result.loh_alleles_count,
        overall_immune_evasion_index=result.overall_immune_evasion_index,
        checkpoint_resistance_prediction=result.checkpoint_resistance_risk,
        metadata_json={
            "rescue_strategies": result.rescue_strategies,
            "recommendations": result.recommendations,
        },
    )

    # Save allele profiles
    for a in result.allele_details:
        await repo.add_allele_profile(
            study_id=study.id,
            hla_gene=a["hla_gene"],
            allele_identifier=a["allele_name"],
            tumor_copy_number=a["estimated_copy_number"],
            b_allele_frequency_baf=a["baf_tumor"],
            loh_status=a["loh_status"],
        )

    # Save evasion score
    await repo.add_evasion_score(
        study_id=study.id,
        neoantigen_presentation_loss_percent=result.neoantigen_presentation_loss_percent,
        cd8_t_cell_evasion_probability=result.overall_immune_evasion_index,
        nk_cell_activation_potential=0.65,
        recommended_synthetic_rescue=result.rescue_strategies[0],
    )

    return {
        "status": "SUCCESS",
        "study_id": str(study.id),
        "patient_id": study.patient_cohort_id,
        "loh_alleles_count": study.loh_positive_allele_count,
        "checkpoint_resistance_risk": study.checkpoint_resistance_prediction,
        "result": result.model_dump(),
    }


@router.get("/studies/{study_id}")
async def get_hla_loh_study(
    study_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        sid = uuid.UUID(study_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid study UUID")

    repo = HLALOHResistanceRepository(db)
    study = await repo.get_study(sid)
    if not study:
        raise HTTPException(status_code=404, detail="HLA LOH study not found")

    return {
        "id": str(study.id),
        "patient_cohort_id": study.patient_cohort_id,
        "tumor_type": study.tumor_type,
        "loh_positive_allele_count": study.loh_positive_allele_count,
        "allele_profiles_count": len(study.allele_profiles),
        "evasion_scores_count": len(study.evasion_scores),
    }
