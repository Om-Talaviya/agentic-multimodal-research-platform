"""
FastAPI Route Handlers for Phase 47: Cryo-EM Density Map Fitting & Macromolecular Complexes.
"""
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_current_user
from database.models.user import User as DBUser
from database.repositories.cryoem_repo import CryoEMRepository
from research.cryoem_engine import CryoEMModelingEngine

router = APIRouter(prefix="/cryoem", tags=["Cryo-EM Structural Biology (Phase 47)"])

class MapFitRequest(BaseModel):
    title: str = Field(..., example="2.4A Cryo-EM Structure of Human PCSK9-Antibody Complex")
    emdb_id: str = Field(default="EMD-30452", example="EMD-30452")
    pdb_model_id: str = Field(default="7KRR", example="7KRR")
    target_resolution: float = Field(default=2.4, example=2.4)

class DensityMapResponse(BaseModel):
    id: uuid.UUID
    title: str
    emdb_id: str
    nominal_resolution_angstrom: float
    voxel_size_angstrom: float
    box_dimensions: str
    contour_level: float
    fsc_resolution_threshold: float
    status: str
    created_at: Any

    class Config:
        from_attributes = True

@router.post("/fit-map", response_model=DensityMapResponse, status_code=status.HTTP_201_CREATED)
async def fit_and_create_map(
    payload: MapFitRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    engine = CryoEMModelingEngine()
    result = engine.fit_density_map(
        title=payload.title,
        emdb_id=payload.emdb_id,
        pdb_model_id=payload.pdb_model_id,
        target_resolution=payload.target_resolution
    )

    repo = CryoEMRepository(db)
    density_map = await repo.create_density_map(
        title=result["title"],
        emdb_id=result["emdb_id"],
        nominal_resolution=result["nominal_resolution"],
        voxel_size=result["voxel_size"],
        box_dimensions=result["box_dimensions"],
        contour_level=result["contour_level"],
        fsc_resolution=result["fsc_resolution"],
        fsc_curve_data=result["fsc_curve"],
        user_id=current_user.id
    )

    fit = result["fitting"]
    await repo.add_fitting(
        density_map_id=density_map.id,
        pdb_model_id=fit["pdb_model_id"],
        cross_correlation=fit["cross_correlation"],
        molprobity_clashscore=fit["molprobity_clashscore"],
        ramachandran_favored_pct=fit["ramachandran_favored_pct"],
        rotamer_outliers_pct=fit["rotamer_outliers_pct"],
        alpha_helices=fit["alpha_helices"],
        beta_sheets=fit["beta_sheets"],
        fitting_log=fit["fitting_log"]
    )

    comp = result["complex"]
    await repo.add_macromolecular_complex(
        density_map_id=density_map.id,
        complex_name=comp["complex_name"],
        stoichiometry=comp["stoichiometry"],
        buried_surface_area=comp["buried_surface_area"],
        binding_free_energy=comp["binding_free_energy"],
        interface_residue_count=comp["interface_residue_count"],
        interaction_hotspots=comp["hotspots"]
    )

    return density_map

@router.get("/maps", response_model=List[DensityMapResponse])
async def list_maps(
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    repo = CryoEMRepository(db)
    return await repo.list_density_maps(limit=limit)

@router.get("/maps/{map_id}")
async def get_map_details(
    map_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    repo = CryoEMRepository(db)
    m = await repo.get_density_map(map_id)
    if not m:
        raise HTTPException(status_code=404, detail="Cryo-EM density map not found")
    return {
        "id": str(m.id),
        "title": m.title,
        "emdb_id": m.emdb_id,
        "resolution": m.nominal_resolution_angstrom,
        "voxel_size": m.voxel_size_angstrom,
        "box_dimensions": m.box_dimensions,
        "contour_level": m.contour_level,
        "fsc_threshold": m.fsc_resolution_threshold,
        "fsc_curve": m.fsc_curve_data,
        "fittings": [
            {
                "pdb_id": f.pdb_model_id,
                "ccc": f.cross_correlation_coefficient,
                "clashscore": f.molprobity_clashscore,
                "ramachandran_pct": f.ramachandran_favored_pct,
                "alpha_helices": f.alpha_helices_count,
                "beta_sheets": f.beta_sheets_count,
                "log": f.fitting_log
            } for f in m.fittings
        ],
        "complexes": [
            {
                "name": c.complex_name,
                "stoichiometry": c.stoichiometry,
                "bsa": c.buried_surface_area_angstrom2,
                "delta_g": c.binding_free_energy_delta_g,
                "residue_count": c.interface_residue_count,
                "hotspots": c.interaction_hotspots
            } for c in m.complexes
        ]
    }
