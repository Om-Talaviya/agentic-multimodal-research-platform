"""
Phase 134: Non-Coding RNA Riboswitch Kinetic Switch Simulator & Aptamer Free-Energy Folding API Route.
"""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.riboswitch_kinetics_repo import RiboswitchKineticsRepository
from research.rna_biology.riboswitch_kinetics_engine import (
    RiboswitchKineticsEngine,
)

router = APIRouter(prefix="/riboswitch-kinetics", tags=["Riboswitch Kinetics Simulator"])


class RiboswitchSimulationRequest(BaseModel):
    circuit_name: str = Field(..., example="Engineered SAM-I Riboswitch ON-Gate")
    target_ligand: str = Field(..., example="S-Adenosylmethionine (SAM)")
    rna_sequence: str = Field(
        ...,
        example="GGGAUACCAGCCGAAAGGCCCUUGGCAGCGUCCGAGUGUAGUGUCCAGUAGGCCU",
    )
    aptamer_class: str = Field(default="SAM-I", example="SAM-I")
    expression_platform_type: str = Field(
        default="Rho-Independent Terminator",
        example="Rho-Independent Terminator",
    )
    transcription_speed_nt_per_sec: float = Field(default=25.0, example=25.0)
    temperature_celsius: float = Field(default=37.0, example=37.0)
    workspace_id: Optional[str] = None


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_riboswitch_switch(
    req: RiboswitchSimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = RiboswitchKineticsEngine()
    result = engine.simulate_kinetic_switch(
        circuit_name=req.circuit_name,
        target_ligand=req.target_ligand,
        rna_sequence=req.rna_sequence,
        aptamer_class=req.aptamer_class,
        transcription_speed_nt_per_sec=req.transcription_speed_nt_per_sec,
        temperature_celsius=req.temperature_celsius,
    )

    repo = RiboswitchKineticsRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    circuit = await repo.create_circuit(
        project_id=ws_id,
        circuit_name=result.circuit_name,
        target_ligand=result.target_ligand,
        rna_sequence=req.rna_sequence,
        aptamer_class=req.aptamer_class,
        expression_platform_type=req.expression_platform_type,
        dynamic_range_fold=result.dynamic_range_fold,
        switching_free_energy_delta_g=result.switching_free_energy_delta_g,
        metadata_json={
            "cotranscriptional_trajectory": result.cotranscriptional_trajectory,
            "recommendations": result.recommendations,
        },
    )

    # Add Apo structure
    await repo.add_secondary_structure(
        circuit_id=circuit.id,
        state_name=result.apo_state["state_name"],
        dot_bracket_notation=result.apo_state["dot_bracket_notation"],
        minimum_free_energy_mfe=result.apo_state["minimum_free_energy_mfe"],
        ensemble_defect_percent=result.apo_state["ensemble_defect_percent"],
        pseudoknot_present=result.apo_state["pseudoknot_present"],
    )

    # Add Holo structure
    await repo.add_secondary_structure(
        circuit_id=circuit.id,
        state_name=result.holo_state["state_name"],
        dot_bracket_notation=result.holo_state["dot_bracket_notation"],
        minimum_free_energy_mfe=result.holo_state["minimum_free_energy_mfe"],
        ensemble_defect_percent=result.holo_state["ensemble_defect_percent"],
        pseudoknot_present=result.holo_state["pseudoknot_present"],
    )

    # Add Kinetics profile
    kp = result.kinetics_profile
    await repo.add_kinetics_profile(
        circuit_id=circuit.id,
        association_rate_k_on=kp["association_rate_k_on"],
        dissociation_rate_k_off=kp["dissociation_rate_k_off"],
        equilibrium_dissociation_constant_kd_nm=kp["equilibrium_dissociation_constant_kd_nm"],
        cotranscriptional_folding_window_nt=kp["cotranscriptional_folding_window_nt"],
    )

    return {
        "status": "SUCCESS",
        "circuit_id": str(circuit.id),
        "circuit_name": circuit.circuit_name,
        "dynamic_range_fold": circuit.dynamic_range_fold,
        "switching_free_energy_delta_g": circuit.switching_free_energy_delta_g,
        "result": result.model_dump(),
    }


@router.get("/circuits/{circuit_id}")
async def get_riboswitch_circuit(
    circuit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        cid = uuid.UUID(circuit_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid circuit UUID")

    repo = RiboswitchKineticsRepository(db)
    circuit = await repo.get_circuit(cid)
    if not circuit:
        raise HTTPException(status_code=404, detail="Riboswitch circuit not found")

    return {
        "id": str(circuit.id),
        "circuit_name": circuit.circuit_name,
        "target_ligand": circuit.target_ligand,
        "dynamic_range_fold": circuit.dynamic_range_fold,
        "secondary_structures_count": len(circuit.secondary_structures),
        "ligand_kinetics_count": len(circuit.ligand_kinetics),
    }
