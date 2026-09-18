"""API Routes for Multi-Modal Diffusion 3D Protein-Ligand Complex Conformation Generation."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.diffusion_conformation_repo import DiffusionConformationRepository
from research.diffusion.diffusion_conformation_engine import DiffusionConformationEngine

router = APIRouter(prefix="/diffusion-conformation", tags=["Diffusion 3D Complex Conformation"])


class DiffusionGenerateRequest(BaseModel):
    protein_pdb_id: str = Field(..., description="Target protein PDB ID (e.g. 6LU7, 1HSG, 7V28)")
    ligand_smiles: str = Field(..., description="Ligand SMILES formula")
    diffusion_model_variant: str = Field(default="DiffDock_SE3")
    num_diffusion_timesteps: int = Field(default=1000, ge=100, le=5000)
    sampling_temperature: float = Field(default=1.0, ge=0.1, le=2.0)
    num_poses: int = Field(default=5, ge=1, le=20)


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_diffusion_conformations(
    request: DiffusionGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Run SE(3) diffusion model to generate equivariant 3D docking poses."""
    engine = DiffusionConformationEngine()
    result = engine.run_diffusion_docking(
        protein_pdb_id=request.protein_pdb_id,
        ligand_smiles=request.ligand_smiles,
        num_timesteps=request.num_diffusion_timesteps,
        sampling_temperature=request.sampling_temperature,
        model_variant=request.diffusion_model_variant,
        num_poses=request.num_poses,
    )

    repo = DiffusionConformationRepository(db)
    job_info = result["job"]
    job = await repo.create_job(
        protein_pdb_id=job_info["protein_pdb_id"],
        ligand_smiles=job_info["ligand_smiles"],
        diffusion_model_variant=job_info["diffusion_model_variant"],
        num_diffusion_timesteps=job_info["num_diffusion_timesteps"],
        sampling_temperature=job_info["sampling_temperature"],
        total_conformations_generated=job_info["total_conformations_generated"],
        best_confidence_score=job_info["best_confidence_score"],
        status=job_info["status"],
    )

    for pocket in result["pocket_conformations"]:
        await repo.add_pocket_conformation(
            job_id=job.id,
            conformation_rank=pocket["conformation_rank"],
            pocket_center_x=pocket["pocket_center_x"],
            pocket_center_y=pocket["pocket_center_y"],
            pocket_center_z=pocket["pocket_center_z"],
            pocket_volume_angstrom3=pocket["pocket_volume_angstrom3"],
            cavity_druggability_score=pocket["cavity_druggability_score"],
            clash_penalty_score=pocket["clash_penalty_score"],
        )

    for pose in result["docking_poses"]:
        await repo.add_docking_pose(
            job_id=job.id,
            pose_rank=pose["pose_rank"],
            rmsd_to_centroid_angstrom=pose["rmsd_to_centroid_angstrom"],
            vina_affinity_score=pose["vina_affinity_score"],
            se3_confidence_score=pose["se3_confidence_score"],
            num_h_bonds=pose["num_h_bonds"],
            contact_surface_area_angstrom2=pose["contact_surface_area_angstrom2"],
            ligand_coordinates_pdb=pose["ligand_coordinates_pdb"],
        )

    saved_job = await repo.get_job(job.id)
    return {
        "status": "success",
        "id": job.id,
        "protein_pdb_id": job.protein_pdb_id,
        "ligand_smiles": job.ligand_smiles,
        "best_confidence_score": job.best_confidence_score,
        "pocket_conformations_count": len(saved_job.pocket_conformations if saved_job else []),
        "docking_poses_count": len(saved_job.docking_poses if saved_job else []),
    }


@router.get("/jobs")
async def list_diffusion_jobs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """List recent 3D diffusion docking jobs."""
    repo = DiffusionConformationRepository(db)
    jobs = await repo.list_jobs(limit=limit)
    return [
        {
            "id": j.id,
            "protein_pdb_id": j.protein_pdb_id,
            "ligand_smiles": j.ligand_smiles,
            "diffusion_model_variant": j.diffusion_model_variant,
            "best_confidence_score": j.best_confidence_score,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "pocket_conformations_count": len(j.pocket_conformations),
            "docking_poses_count": len(j.docking_poses),
        }
        for j in jobs
    ]


@router.get("/jobs/{job_id}")
async def get_diffusion_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Get complete details and 3D coordinates for a diffusion docking job."""
    repo = DiffusionConformationRepository(db)
    job = await repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Diffusion job not found")

    return {
        "id": job.id,
        "protein_pdb_id": job.protein_pdb_id,
        "ligand_smiles": job.ligand_smiles,
        "diffusion_model_variant": job.diffusion_model_variant,
        "num_diffusion_timesteps": job.num_diffusion_timesteps,
        "best_confidence_score": job.best_confidence_score,
        "pocket_conformations": [
            {
                "id": p.id,
                "conformation_rank": p.conformation_rank,
                "pocket_center": [p.pocket_center_x, p.pocket_center_y, p.pocket_center_z],
                "pocket_volume_angstrom3": p.pocket_volume_angstrom3,
                "cavity_druggability_score": p.cavity_druggability_score,
                "clash_penalty_score": p.clash_penalty_score,
            }
            for p in job.pocket_conformations
        ],
        "docking_poses": [
            {
                "id": dp.id,
                "pose_rank": dp.pose_rank,
                "rmsd_to_centroid_angstrom": dp.rmsd_to_centroid_angstrom,
                "vina_affinity_score": dp.vina_affinity_score,
                "se3_confidence_score": dp.se3_confidence_score,
                "num_h_bonds": dp.num_h_bonds,
                "contact_surface_area_angstrom2": dp.contact_surface_area_angstrom2,
                "ligand_coordinates_pdb": dp.ligand_coordinates_pdb,
            }
            for dp in job.docking_poses
        ],
    }
