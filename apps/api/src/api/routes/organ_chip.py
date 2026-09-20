"""
FastAPI route for Phase 108: Organ-on-a-Chip Microphysiological Fluidic Dynamics.
"""
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from database.repositories.organ_chip_repo import OrganChipRepository
from research.biophysics.organ_chip_engine import MicrofluidicBiochipEngine

router = APIRouter(prefix="/organ-chip", tags=["Phase 108: Organ-on-a-Chip Fluidics"])

class OrganChipSimulationRequest(BaseModel):
    chip_name: str
    organ_type: str = "BLOOD_BRAIN_BARRIER"
    flow_rate_ul_min: float = Field(default=30.0, ge=1.0, le=500.0)
    viscosity_cp: float = Field(default=1.0, ge=0.5, le=5.0)
    channel_length_mm: float = Field(default=20.0, ge=5.0, le=100.0)

class MicrofluidicChannelResponse(BaseModel):
    channel_name: str
    width_um: float
    height_um: float
    length_mm: float
    flow_velocity_mm_s: float
    reynolds_number: float

class ShearStressProfileResponse(BaseModel):
    axial_position_mm: float
    wall_shear_stress: float
    drug_permeation_pct: float
    tight_junction_expression: float

class OrganChipSimulationResponse(BaseModel):
    id: str
    chip_name: str
    organ_type: str
    fluid_viscosity_cp: float
    perfusion_flow_rate_ul_min: float
    shear_stress_dyn_cm2: float
    endothelial_barrier_integrity_teer: float
    status: str
    channels: List[Dict[str, Any]] = []
    shear_profiles: List[Dict[str, Any]] = []

@router.post("/simulate", response_model=OrganChipSimulationResponse, status_code=status.HTTP_201_CREATED)
async def simulate_and_persist_organ_chip(
    request: OrganChipSimulationRequest,
    db: AsyncSession = Depends(get_db)
):
    engine = MicrofluidicBiochipEngine()
    sim = engine.simulate_organ_chip(
        chip_name=request.chip_name,
        organ_type=request.organ_type,
        flow_rate_ul_min=request.flow_rate_ul_min,
        viscosity_cp=request.viscosity_cp,
        channel_length_mm=request.channel_length_mm
    )

    repo = OrganChipRepository(db)
    sim_entity = await repo.create_simulation(
        chip_name=sim["chip_name"],
        organ_type=sim["organ_type"],
        fluid_viscosity_cp=sim["fluid_viscosity_cp"],
        perfusion_flow_rate_ul_min=sim["perfusion_flow_rate_ul_min"],
        shear_stress_dyn_cm2=sim["shear_stress_dyn_cm2"],
        endothelial_barrier_integrity_teer=sim["endothelial_barrier_integrity_teer"]
    )

    await repo.add_channels(sim_entity.id, sim["channels"])
    await repo.add_shear_profiles(sim_entity.id, sim["shear_profiles"])

    hydrated = await repo.get_simulation(sim_entity.id)
    if not hydrated:
        raise HTTPException(status_code=500, detail="Failed to retrieve organ-on-chip simulation")

    return OrganChipSimulationResponse(
        id=str(hydrated.id),
        chip_name=hydrated.chip_name,
        organ_type=hydrated.organ_type,
        fluid_viscosity_cp=hydrated.fluid_viscosity_cp,
        perfusion_flow_rate_ul_min=hydrated.perfusion_flow_rate_ul_min,
        shear_stress_dyn_cm2=hydrated.shear_stress_dyn_cm2,
        endothelial_barrier_integrity_teer=hydrated.endothelial_barrier_integrity_teer,
        status=hydrated.status,
        channels=[{
            "channel_name": ch.channel_name,
            "width_um": ch.width_um,
            "height_um": ch.height_um,
            "length_mm": ch.length_mm,
            "flow_velocity_mm_s": ch.flow_velocity_mm_s,
            "reynolds_number": ch.reynolds_number
        } for ch in hydrated.channels],
        shear_profiles=[{
            "axial_position_mm": p.axial_position_mm,
            "wall_shear_stress": p.wall_shear_stress,
            "drug_permeation_pct": p.drug_permeation_pct,
            "tight_junction_expression": p.tight_junction_expression
        } for p in hydrated.shear_profiles]
    )

@router.get("/simulations", response_model=List[OrganChipSimulationResponse])
async def list_organ_chip_simulations(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    repo = OrganChipRepository(db)
    sims = await repo.list_simulations(limit=limit, offset=offset)
    return [
        OrganChipSimulationResponse(
            id=str(s.id),
            chip_name=s.chip_name,
            organ_type=s.organ_type,
            fluid_viscosity_cp=s.fluid_viscosity_cp,
            perfusion_flow_rate_ul_min=s.perfusion_flow_rate_ul_min,
            shear_stress_dyn_cm2=s.shear_stress_dyn_cm2,
            endothelial_barrier_integrity_teer=s.endothelial_barrier_integrity_teer,
            status=s.status,
            channels=[],
            shear_profiles=[]
        )
        for s in sims
    ]

@router.get("/simulations/{simulation_id}", response_model=OrganChipSimulationResponse)
async def get_organ_chip_simulation_detail(
    simulation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = OrganChipRepository(db)
    hydrated = await repo.get_simulation(simulation_id)
    if not hydrated:
        raise HTTPException(status_code=404, detail="Organ-on-chip simulation not found")

    return OrganChipSimulationResponse(
        id=str(hydrated.id),
        chip_name=hydrated.chip_name,
        organ_type=hydrated.organ_type,
        fluid_viscosity_cp=hydrated.fluid_viscosity_cp,
        perfusion_flow_rate_ul_min=hydrated.perfusion_flow_rate_ul_min,
        shear_stress_dyn_cm2=hydrated.shear_stress_dyn_cm2,
        endothelial_barrier_integrity_teer=hydrated.endothelial_barrier_integrity_teer,
        status=hydrated.status,
        channels=[{
            "channel_name": ch.channel_name,
            "width_um": ch.width_um,
            "height_um": ch.height_um,
            "length_mm": ch.length_mm,
            "flow_velocity_mm_s": ch.flow_velocity_mm_s,
            "reynolds_number": ch.reynolds_number
        } for ch in hydrated.channels],
        shear_profiles=[{
            "axial_position_mm": p.axial_position_mm,
            "wall_shear_stress": p.wall_shear_stress,
            "drug_permeation_pct": p.drug_permeation_pct,
            "tight_junction_expression": p.tight_junction_expression
        } for p in hydrated.shear_profiles]
    )
