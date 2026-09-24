"""
FastAPI Router for Phase 165: Peptide-Drug Conjugate (PDC) Linker Cleavability.
"""

import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.pdc_conjugate_repo import (
    PDCConjugateRepository,
)
from research.therapeutics.pdc_conjugate_engine import (
    PDCConjugateEngine,
)

router = APIRouter(prefix="/pdc-conjugate", tags=["Peptide-Drug Conjugate (PDC) & Linker Kinetics"])


class PDCEvaluationRequest(BaseModel):
    pdc_name: str = Field(..., example="cRGD-ValCit-MMAE")
    homing_peptide_sequence: str = Field(..., example="cyclo(RGDfK)")
    linker_type: Optional[str] = Field(default="Val-Cit-PABC", example="Val-Cit-PABC")
    cytotoxic_payload: Optional[str] = Field(
        default="Monomethyl Auristatin E (MMAE)",
        example="Monomethyl Auristatin E (MMAE)",
    )
    workspace_id: Optional[str] = None


@router.post("/evaluate", status_code=status.HTTP_201_CREATED)
async def evaluate_pdc_endpoint(
    req: PDCEvaluationRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = PDCConjugateEngine()
    result = engine.evaluate_pdc_construct(
        pdc_name=req.pdc_name,
        homing_peptide=req.homing_peptide_sequence,
        linker_type=req.linker_type or "Val-Cit-PABC",
        payload=req.cytotoxic_payload or "Monomethyl Auristatin E (MMAE)",
    )

    repo = PDCConjugateRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    study = await repo.create_study(
        pdc_name=result.pdc_name,
        homing_peptide_sequence=result.homing_peptide,
        linker_type=result.linker_type,
        cytotoxic_payload=result.payload,
        plasma_stability_half_life_hours=result.plasma_stability_half_life_hours,
        tumor_cathepsin_cleavage_rate_kcat_km=result.tumor_cleavage_rate_kcat_km,
        therapeutic_index_ratio=result.therapeutic_index,
        bystander_payload_diffusion_score=result.bystander_score,
        project_id=ws_id,
    )

    for cp in result.cleavage_profiles:
        await repo.add_cleavage_profile(
            study_id=study.id,
            enzyme_target=cp.enzyme,
            cleavage_efficiency_percent=cp.cleavage_efficiency_percent,
            incubation_time_minutes=cp.incubation_time_min,
            intact_conjugate_remaining_percent=cp.intact_percent,
        )

    for ca in result.cathepsin_assays:
        await repo.add_cathepsin_assay(
            study_id=study.id,
            tissue_compartment=ca.compartment,
            enzymatic_activity_units=ca.activity_units,
            payload_release_velocity_nmol_min=ca.release_velocity,
            selectivity_fold_enrichment=ca.selectivity_fold,
        )

    return {
        "status": "SUCCESS",
        "study_id": str(study.id),
        "pdc_name": study.pdc_name,
        "plasma_stability_half_life_hours": study.plasma_stability_half_life_hours,
        "therapeutic_index_ratio": study.therapeutic_index_ratio,
        "result": result.model_dump(),
    }


@router.get("/studies/{study_id}")
async def get_study_endpoint(
    study_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        sid = uuid.UUID(study_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid study UUID")

    repo = PDCConjugateRepository(db)
    study = await repo.get_study(sid)
    if not study:
        raise HTTPException(status_code=404, detail="PDC study not found")

    return {
        "id": str(study.id),
        "pdc_name": study.pdc_name,
        "homing_peptide_sequence": study.homing_peptide_sequence,
        "linker_type": study.linker_type,
        "therapeutic_index_ratio": study.therapeutic_index_ratio,
        "cleavage_profiles_count": len(study.cleavage_profiles),
        "cathepsin_assays_count": len(study.cathepsin_assays),
    }
