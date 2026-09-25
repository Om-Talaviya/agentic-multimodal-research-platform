"""API Router for 3D Cryo-Electron Tomography Subtomogram Averaging Engine."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.cryoet_subtomogram_tomography_repo import CryoETTomogramRepository
from research.structural.cryoet_subtomogram_tomography_engine import CryoETTomogramEngine

router = APIRouter(prefix="/cryoet-subtomogram-tomography", tags=["CryoET Subtomogram Tomography"])


class SubtomogramParticleInput(BaseModel):
    particle_id_str: str = Field("PTCL_TOMO_001", description="Subtomogram particle label")
    x_vox: float = Field(512.4, description="X coordinate in tomogram voxels")
    y_vox: float = Field(384.8, description="Y coordinate in tomogram voxels")
    z_vox: float = Field(128.0, description="Z coordinate in tomogram voxels")
    euler_rot_deg: float = Field(45.2, description="Euler angle Phi rotation (degrees)")
    euler_tilt_deg: float = Field(32.8, description="Euler angle Theta tilt (degrees)")
    euler_psi_deg: float = Field(18.4, description="Euler angle Psi in-plane rotation (degrees)")
    cross_correlation_score: float = Field(0.885, description="3D cross-correlation against reference volume")
    conformational_state: str = Field("Resting Closed", description="Subtomogram structural state classification")


class RunCryoETReconstructionRequest(BaseModel):
    study_name: str = Field(..., description="Name for the Cryo-ET subtomogram averaging study")
    cellular_context: str = Field("Intact Neuronal Synapse (In-Situ)", description="Biological host specimen or in-situ organelle")
    target_complex_name: str = Field("AMPAR-TARP Ion Channel Complex", description="Macromolecular complex name")
    custom_particles: Optional[List[SubtomogramParticleInput]] = None


@router.post("/reconstruct", status_code=status.HTTP_201_CREATED)
async def run_cryoet_reconstruction(
    payload: RunCryoETReconstructionRequest,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Execute 3D subtomogram averaging refinement and Gold-Standard FSC classification."""
    engine = CryoETTomogramEngine()
    particles_data = [p.model_dump() for p in payload.custom_particles] if payload.custom_particles else None

    result = engine.run_subtomogram_averaging(
        study_name=payload.study_name,
        cellular_context=payload.cellular_context,
        target_complex_name=payload.target_complex_name,
        custom_particles=particles_data,
    )

    repo = CryoETTomogramRepository(session)
    saved_study = await repo.create_study(
        study_name=result["study_name"],
        cellular_context=result["cellular_context"],
        target_complex_name=result["target_complex_name"],
        particles_picked_count=result["particles_picked_count"],
        final_fsc_resolution_angstrom=result["final_fsc_resolution_angstrom"],
        angular_search_step_deg=result["angular_search_step_deg"],
        summary_metrics=result["summary_metrics"],
        particles=result["particles"],
        classes=result["classes"],
    )

    return {
        "id": str(saved_study.id),
        "status": "success",
        "study_name": saved_study.study_name,
        "cellular_context": saved_study.cellular_context,
        "target_complex_name": saved_study.target_complex_name,
        "particles_picked_count": saved_study.particles_picked_count,
        "final_fsc_resolution_angstrom": saved_study.final_fsc_resolution_angstrom,
        "angular_search_step_deg": saved_study.angular_search_step_deg,
        "summary_metrics": saved_study.summary_metrics,
        "particles": [
            {
                "id": str(p.id),
                "particle_id_str": p.particle_id_str,
                "x_vox": p.x_vox,
                "y_vox": p.y_vox,
                "z_vox": p.z_vox,
                "euler_rot_deg": p.euler_rot_deg,
                "euler_tilt_deg": p.euler_tilt_deg,
                "euler_psi_deg": p.euler_psi_deg,
                "cross_correlation_score": p.cross_correlation_score,
                "conformational_state": p.conformational_state,
            }
            for p in saved_study.particles
        ],
        "classes": [
            {
                "id": str(c.id),
                "class_number": c.class_number,
                "class_name": c.class_name,
                "particle_occupancy_pct": c.particle_occupancy_pct,
                "resolution_angstrom": c.resolution_angstrom,
                "fsc_cutoff_type": c.fsc_cutoff_type,
            }
            for c in saved_study.classes
        ],
    }


@router.get("/studies", response_model=List[Dict[str, Any]])
async def list_cryoet_studies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List recent Cryo-ET subtomogram studies."""
    repo = CryoETTomogramRepository(session)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [
        {
            "id": str(s.id),
            "study_name": s.study_name,
            "cellular_context": s.cellular_context,
            "target_complex_name": s.target_complex_name,
            "particles_picked_count": s.particles_picked_count,
            "final_fsc_resolution_angstrom": s.final_fsc_resolution_angstrom,
            "created_at": s.created_at,
        }
        for s in studies
    ]


@router.get("/studies/{study_id}")
async def get_cryoet_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve details for a specific Cryo-ET subtomogram averaging study."""
    repo = CryoETTomogramRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryo-ET study with ID '{study_id}' not found.",
        )

    return {
        "id": str(study.id),
        "study_name": study.study_name,
        "cellular_context": study.cellular_context,
        "target_complex_name": study.target_complex_name,
        "particles_picked_count": study.particles_picked_count,
        "final_fsc_resolution_angstrom": study.final_fsc_resolution_angstrom,
        "angular_search_step_deg": study.angular_search_step_deg,
        "summary_metrics": study.summary_metrics,
        "particles": [
            {
                "id": str(p.id),
                "particle_id_str": p.particle_id_str,
                "x_vox": p.x_vox,
                "y_vox": p.y_vox,
                "z_vox": p.z_vox,
                "euler_rot_deg": p.euler_rot_deg,
                "euler_tilt_deg": p.euler_tilt_deg,
                "euler_psi_deg": p.euler_psi_deg,
                "cross_correlation_score": p.cross_correlation_score,
                "conformational_state": p.conformational_state,
            }
            for p in study.particles
        ],
        "classes": [
            {
                "id": str(c.id),
                "class_number": c.class_number,
                "class_name": c.class_name,
                "particle_occupancy_pct": c.particle_occupancy_pct,
                "resolution_angstrom": c.resolution_angstrom,
                "fsc_cutoff_type": c.fsc_cutoff_type,
            }
            for c in study.classes
        ],
        "created_at": study.created_at,
    }


@router.delete("/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cryoet_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a Cryo-ET subtomogram study record by ID."""
    repo = CryoETTomogramRepository(session)
    deleted = await repo.delete_study(study_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryo-ET study with ID '{study_id}' not found.",
        )
