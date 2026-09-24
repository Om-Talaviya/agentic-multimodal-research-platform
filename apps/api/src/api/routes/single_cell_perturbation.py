"""
FastAPI Router for Phase 167: Single-Cell Perturbation & Causal GRN Inversion.
"""

import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.single_cell_perturbation_repo import (
    SingleCellPerturbationRepository,
)
from research.single_cell.single_cell_perturbation_engine import (
    SingleCellPerturbationEngine,
)

router = APIRouter(prefix="/single-cell-perturbation", tags=["Single-Cell Perturbation & Causal GRN"])


class PerturbationScreenRequest(BaseModel):
    study_name: str = Field(..., example="K562_CRISPRi_Kinome_Screen")
    modality: Optional[str] = Field(default="CRISPRi-PerturbSeq", example="CRISPRi-PerturbSeq")
    target_genes: Optional[List[str]] = Field(default=None, example=["MYC", "TP53", "STAT3", "CDK4"])
    workspace_id: Optional[str] = None


@router.post("/screen", status_code=status.HTTP_201_CREATED)
async def screen_perturbations_endpoint(
    req: PerturbationScreenRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = SingleCellPerturbationEngine()
    result = engine.analyze_perturbation_screen(
        study_name=req.study_name,
        modality=req.modality or "CRISPRi-PerturbSeq",
        target_genes=req.target_genes,
    )

    repo = SingleCellPerturbationRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    study = await repo.create_study(
        study_name=result.study_name,
        perturbation_modality=result.modality,
        total_cells_profiled=result.total_cells,
        target_genes_count=result.targets_count,
        energy_distance_shift=result.e_distance,
        causal_network_density=result.network_density,
        project_id=ws_id,
    )

    for te in result.target_effects:
        await repo.add_target_effect(
            study_id=study.id,
            guide_target_gene=te.gene,
            knockdown_efficiency_percent=te.knockdown_efficiency,
            differentially_expressed_genes_count=te.deg_count,
            phenotypic_dispersion_score=te.dispersion,
        )

    for edge in result.grn_edges:
        await repo.add_grn_edge(
            study_id=study.id,
            source_regulator_gene=edge.source,
            target_effector_gene=edge.target,
            causal_weight_beta=edge.beta,
            p_value_fdr=edge.fdr,
            regulation_sign=edge.sign,
        )

    return {
        "status": "SUCCESS",
        "study_id": str(study.id),
        "study_name": study.study_name,
        "total_cells_profiled": study.total_cells_profiled,
        "energy_distance_shift": study.energy_distance_shift,
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

    repo = SingleCellPerturbationRepository(db)
    study = await repo.get_study(sid)
    if not study:
        raise HTTPException(status_code=404, detail="Single-cell perturbation study not found")

    return {
        "id": str(study.id),
        "study_name": study.study_name,
        "perturbation_modality": study.perturbation_modality,
        "total_cells_profiled": study.total_cells_profiled,
        "energy_distance_shift": study.energy_distance_shift,
        "target_effects_count": len(study.target_effects),
        "grn_edges_count": len(study.grn_edges),
    }
