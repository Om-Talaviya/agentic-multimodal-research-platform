"""
FastAPI Router for Phase 166: MicroED Structural Engine.
"""

import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.microed_structural_repo import (
    MicroEDStructuralRepository,
)
from research.structural.microed_structural_engine import (
    MicroEDStructuralEngine,
)

router = APIRouter(prefix="/microed-structural", tags=["Micro-Crystal Electron Diffraction (MicroED)"])


class MicroEDRefinementRequest(BaseModel):
    sample_name: str = Field(..., example="Bovine Trypsin")
    voltage_kv: Optional[float] = Field(default=200.0, example=200.0)
    rotation_range_deg: Optional[float] = Field(default=120.0, example=120.0)
    frames_count: Optional[int] = Field(default=5, example=5)
    workspace_id: Optional[str] = None


@router.post("/refine", status_code=status.HTTP_201_CREATED)
async def refine_microed_endpoint(
    req: MicroEDRefinementRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = MicroEDStructuralEngine()
    result = engine.simulate_microed_refinement(
        sample_name=req.sample_name,
        voltage_kv=req.voltage_kv or 200.0,
        rotation_range=req.rotation_range_deg or 120.0,
        frames_count=req.frames_count or 5,
    )

    repo = MicroEDStructuralRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    exp = await repo.create_experiment(
        sample_name=result.sample_name,
        crystal_system=result.crystal_system,
        electron_voltage_kv=result.electron_voltage_kv,
        total_rotation_range_degrees=result.rotation_range_deg,
        resolution_limit_angstrom=result.resolution_angstrom,
        completeness_percent=result.completeness_percent,
        r_work=result.r_work,
        r_free=result.r_free,
        project_id=ws_id,
    )

    for fr in result.frames:
        await repo.add_diffraction_frame(
            experiment_id=exp.id,
            frame_number=fr.frame_number,
            tilt_angle_degrees=fr.tilt_angle_deg,
            observed_reflections_count=fr.reflections_count,
            mean_intensity_sigma_ratio=fr.i_over_sigma,
        )

    for ref in result.refinements:
        await repo.add_refinement(
            experiment_id=exp.id,
            refinement_cycle=ref.cycle,
            ramachandran_favored_percent=ref.ramachandran_favored,
            clashscore=ref.clashscore,
            electrostatic_potential_peak_density=ref.electrostatic_potential_peak,
        )

    return {
        "status": "SUCCESS",
        "experiment_id": str(exp.id),
        "sample_name": exp.sample_name,
        "resolution_limit_angstrom": exp.resolution_limit_angstrom,
        "r_work": exp.r_work,
        "r_free": exp.r_free,
        "result": result.model_dump(),
    }


@router.get("/experiments/{experiment_id}")
async def get_experiment_endpoint(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        eid = uuid.UUID(experiment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid experiment UUID")

    repo = MicroEDStructuralRepository(db)
    exp = await repo.get_experiment(eid)
    if not exp:
        raise HTTPException(status_code=404, detail="MicroED experiment not found")

    return {
        "id": str(exp.id),
        "sample_name": exp.sample_name,
        "crystal_system": exp.crystal_system,
        "resolution_limit_angstrom": exp.resolution_limit_angstrom,
        "completeness_percent": exp.completeness_percent,
        "frames_count": len(exp.frames),
        "refinements_count": len(exp.refinements),
    }
