"""
FastAPI Router for Phase 163: RNA Thermodynamics & MFE Folding.
"""

import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.rna_thermodynamics_repo import (
    RNAThermodynamicsRepository,
)
from research.rna.rna_thermodynamics_engine import (
    RNAThermodynamicsEngine,
)

router = APIRouter(prefix="/rna-thermodynamics", tags=["RNA Secondary Structure & Thermodynamics"])


class RNAFoldRequest(BaseModel):
    rna_name: str = Field(..., example="SAM-I_Riboswitch_Aptamer")
    sequence: str = Field(
        ...,
        example="GGGAUCGCAGUCUCGAGAGUUGCCAAACCAGCAGCAGCGCUCCUUCUGCGAGAUCCC",
    )
    temperature_celsius: Optional[float] = Field(default=37.0, example=37.0)
    workspace_id: Optional[str] = None


@router.post("/fold", status_code=status.HTTP_201_CREATED)
async def fold_rna_endpoint(
    req: RNAFoldRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = RNAThermodynamicsEngine()
    result = engine.predict_mfe_structure(
        rna_name=req.rna_name,
        sequence=req.sequence,
        temperature_celsius=req.temperature_celsius or 37.0,
    )

    repo = RNAThermodynamicsRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    study = await repo.create_study(
        rna_name=result.rna_name,
        sequence=result.sequence,
        sequence_length=result.sequence_length,
        dot_bracket_structure=result.dot_bracket_structure,
        mfe_delta_g_kcal_mol=result.mfe_delta_g_kcal_mol,
        ensemble_free_energy_kcal_mol=result.ensemble_free_energy_kcal_mol,
        ensemble_defect_score=result.ensemble_defect,
        melting_temperature_tm_celsius=result.melting_temperature_tm_celsius,
        thermodynamic_ruleset="Turner-2004-NearestNeighbor",
        project_id=ws_id,
    )

    for bp in result.base_pair_probabilities:
        await repo.add_base_pair_probability(
            study_id=study.id,
            pos_i=bp.pos_i,
            pos_j=bp.pos_j,
            pairing_probability=bp.pairing_probability,
            base_pair_type=bp.base_pair_type,
        )

    for pk in result.pseudoknots:
        await repo.add_pseudoknot(
            study_id=study.id,
            stem1_range=pk.stem1,
            stem2_range=pk.stem2,
            loop_topology=pk.topology,
            pseudoknot_stability_delta_g_kcal_mol=pk.stability_delta_g_kcal_mol,
        )

    return {
        "status": "SUCCESS",
        "study_id": str(study.id),
        "rna_name": study.rna_name,
        "mfe_delta_g_kcal_mol": study.mfe_delta_g_kcal_mol,
        "dot_bracket_structure": study.dot_bracket_structure,
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

    repo = RNAThermodynamicsRepository(db)
    study = await repo.get_study(sid)
    if not study:
        raise HTTPException(status_code=404, detail="RNA thermodynamics study not found")

    return {
        "id": str(study.id),
        "rna_name": study.rna_name,
        "sequence": study.sequence,
        "dot_bracket_structure": study.dot_bracket_structure,
        "mfe_delta_g_kcal_mol": study.mfe_delta_g_kcal_mol,
        "melting_temperature_tm_celsius": study.melting_temperature_tm_celsius,
        "base_pairs_count": len(study.base_pairs),
        "pseudoknots_count": len(study.pseudoknots),
    }
