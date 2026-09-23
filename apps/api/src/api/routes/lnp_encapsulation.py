"""
Phase 138: High-Throughput Lipid Nanoparticle (LNP) Formulation & mRNA Encapsulation Efficiency API Route.
"""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.lnp_encapsulation_repo import LNPEncapsulationRepository
from research.chemistry.lnp_encapsulation_engine import (
    LNPEncapsulationEngine,
)

router = APIRouter(prefix="/lnp-encapsulation", tags=["High-Throughput LNP Encapsulation"])


class LNPFormulationRequest(BaseModel):
    formulation_tag: str = Field(..., example="LNP_Opt_Screen_09")
    mrna_payload_name: str = Field(
        default="Therapeutic mRNA Vaccine Candidate",
        example="Therapeutic mRNA Vaccine Candidate",
    )
    flow_rate_ratio: float = Field(default=3.0, example=3.0)
    total_flow_rate_ml_min: float = Field(default=12.0, example=12.0)
    np_ratio: float = Field(default=6.0, example=6.0)
    ionizable_lipid_mol_percent: float = Field(default=50.0, example=50.0)
    helper_lipid_mol_percent: float = Field(default=10.0, example=10.0)
    cholesterol_mol_percent: float = Field(default=38.5, example=38.5)
    peg_lipid_mol_percent: float = Field(default=1.5, example=1.5)
    workspace_id: Optional[str] = None


@router.post("/formulate", status_code=status.HTTP_201_CREATED)
async def formulate_lnp_endpoint(
    req: LNPFormulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = LNPEncapsulationEngine()
    result = engine.optimize_lnp_formulation(
        formulation_tag=req.formulation_tag,
        mrna_payload_name=req.mrna_payload_name,
        flow_rate_ratio=req.flow_rate_ratio,
        total_flow_rate_ml_min=req.total_flow_rate_ml_min,
        np_ratio=req.np_ratio,
        ionizable_lipid_mol_percent=req.ionizable_lipid_mol_percent,
        helper_lipid_mol_percent=req.helper_lipid_mol_percent,
        cholesterol_mol_percent=req.cholesterol_mol_percent,
        peg_lipid_mol_percent=req.peg_lipid_mol_percent,
    )

    repo = LNPEncapsulationRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    screen = await repo.create_screen(
        project_id=ws_id,
        formulation_tag=result.formulation_tag,
        mrna_payload_name=result.mrna_payload_name,
        flow_rate_ratio_aqueous_to_organic=req.flow_rate_ratio,
        total_flow_rate_ml_min=req.total_flow_rate_ml_min,
        nitrogen_to_phosphate_np_ratio=req.np_ratio,
        hydrodynamic_diameter_pdi=result.polydispersity_index_pdi,
        particle_size_z_avg_nm=result.particle_size_z_avg_nm,
        encapsulation_efficiency_percent=result.encapsulation_efficiency_percent,
        metadata_json={
            "apparent_pka": result.apparent_pka,
            "zeta_potential": result.stability_zeta_potential_mv,
            "recommendations": result.recommendations,
        },
    )

    # Save lipid components
    for lipid in result.lipid_composition_breakdown:
        await repo.add_lipid_component(
            formulation_id=screen.id,
            lipid_type=lipid["lipid"],
            mol_percent=lipid["mol_percent"],
            pka_apparent=result.apparent_pka if "Ionizable" in lipid["lipid"] else None,
        )

    # Save RiboGreen metrics
    rb = result.ribogreen_assay_metrics
    await repo.add_efficiency_metric(
        formulation_id=screen.id,
        ribogreen_free_rna_fluorescence=rb["free_rna_signal_rfu"],
        ribogreen_total_rna_fluorescence=rb["total_lysed_rna_signal_rfu"],
        calculated_encapsulation_percent=rb["calculated_encapsulation_percent"],
        cryo_tem_morphology="Homogeneous Dense Core",
        in_vivo_transfection_potency_fold=rb["in_vivo_expression_potency_score"],
    )

    return {
        "status": "SUCCESS",
        "screen_id": str(screen.id),
        "formulation_tag": screen.formulation_tag,
        "encapsulation_efficiency_percent": screen.encapsulation_efficiency_percent,
        "particle_size_z_avg_nm": screen.particle_size_z_avg_nm,
        "result": result.model_dump(),
    }


@router.get("/screens/{screen_id}")
async def get_lnp_screen(
    screen_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        sid = uuid.UUID(screen_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid screen UUID")

    repo = LNPEncapsulationRepository(db)
    screen = await repo.get_screen(sid)
    if not screen:
        raise HTTPException(status_code=404, detail="LNP formulation screen not found")

    return {
        "id": str(screen.id),
        "formulation_tag": screen.formulation_tag,
        "particle_size_z_avg_nm": screen.particle_size_z_avg_nm,
        "encapsulation_efficiency_percent": screen.encapsulation_efficiency_percent,
        "lipid_components_count": len(screen.lipid_components),
        "efficiency_metrics_count": len(screen.efficiency_metrics),
    }
