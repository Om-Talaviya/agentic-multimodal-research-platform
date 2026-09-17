"""REST API endpoints for Cryo-Electron Tomography (Cryo-ET) Subtomogram Averaging."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.models import User
from database.repositories.cryoet_subtomogram_repo import CryoETSubtomogramRepository
from research.cryoet.subtomogram_engine import CryoETSubtomogramEngine

router = APIRouter(prefix="/api/v1/cryoet", tags=["Cryo-ET Subtomogram Averaging & In-Situ Biology"])
engine = CryoETSubtomogramEngine()


class ParticleInput(BaseModel):
    particle_index: int
    coord_x: float
    coord_y: float
    coord_z: float
    euler_phi: float = 0.0
    euler_theta: float = 0.0
    euler_psi: float = 0.0
    cross_correlation_score: float = 0.75
    class_assignment: str = "CLASS_1"


class DatasetReconstructionRequest(BaseModel):
    sample_name: str
    specimen_organism: str = "Saccharomyces cerevisiae"
    cellular_compartment: str = "CYTOSOL"
    tilt_angle_min: float = Field(-60.0, ge=-90.0, le=0.0)
    tilt_angle_max: float = Field(60.0, ge=0.0, le=90.0)
    total_tilt_images: int = Field(41, ge=10, le=121)
    pixel_size_angstrom: float = Field(1.35, ge=0.5, le=10.0)
    nominal_defocus_um: float = Field(-2.5, ge=-10.0, le=0.0)
    particles: Optional[List[ParticleInput]] = None


@router.post("/datasets/reconstruct", status_code=status.HTTP_201_CREATED)
async def reconstruct_cryoet_dataset(
    req: DatasetReconstructionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reconstructs 3D tomogram, extracts subtomogram particles, performs averaging and FSC resolution analysis."""
    repo = CryoETSubtomogramRepository(db)

    particles_dict = [p.model_dump() for p in req.particles] if req.particles else None
    eval_res = engine.reconstruct_and_average(req.model_dump(), particles_dict)

    dataset = await repo.create_dataset(
        sample_name=eval_res["sample_name"],
        specimen_organism=eval_res["specimen_organism"],
        cellular_compartment=eval_res["cellular_compartment"],
        tilt_angle_min=eval_res["tilt_angle_min"],
        tilt_angle_max=eval_res["tilt_angle_max"],
        total_tilt_images=eval_res["total_tilt_images"],
        pixel_size_angstrom=eval_res["pixel_size_angstrom"],
        nominal_defocus_um=eval_res["nominal_defocus_um"],
        tomogram_dimensions_json=eval_res["tomogram_dimensions_json"],
        dataset_metadata_json=eval_res["dataset_metadata_json"],
    )

    created_particles = await repo.add_particles(dataset.id, eval_res["particles"])

    ref = eval_res["refinement"]
    created_ref = await repo.add_refinement(
        dataset_id=dataset.id,
        class_name=ref["class_name"],
        particles_averaged_count=ref["particles_averaged_count"],
        estimated_resolution_angstrom=ref["estimated_resolution_angstrom"],
        fsc_0143_spatial_frequency=ref["fsc_0143_spatial_frequency"],
        b_factor_sharpening=ref["b_factor_sharpening"],
        fsc_curve_json=ref["fsc_curve_json"],
    )

    return {
        "id": dataset.id,
        "sample_name": dataset.sample_name,
        "specimen_organism": dataset.specimen_organism,
        "cellular_compartment": dataset.cellular_compartment,
        "pixel_size_angstrom": dataset.pixel_size_angstrom,
        "total_particles": len(created_particles),
        "refinement": {
            "id": created_ref.id,
            "class_name": created_ref.class_name,
            "particles_averaged_count": created_ref.particles_averaged_count,
            "estimated_resolution_angstrom": created_ref.estimated_resolution_angstrom,
            "fsc_0143_spatial_frequency": created_ref.fsc_0143_spatial_frequency,
            "b_factor_sharpening": created_ref.b_factor_sharpening,
            "fsc_curve": created_ref.fsc_curve_json,
        },
        "metadata": dataset.dataset_metadata_json,
    }


@router.get("/datasets")
async def list_datasets(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists Cryo-ET datasets."""
    repo = CryoETSubtomogramRepository(db)
    datasets = await repo.list_datasets(limit=limit, offset=offset)
    return [
        {
            "id": d.id,
            "sample_name": d.sample_name,
            "specimen_organism": d.specimen_organism,
            "cellular_compartment": d.cellular_compartment,
            "pixel_size_angstrom": d.pixel_size_angstrom,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in datasets
    ]


@router.get("/datasets/{dataset_id}")
async def get_dataset_details(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gets complete Cryo-ET dataset with subtomogram particles and 3D refinement metrics."""
    repo = CryoETSubtomogramRepository(db)
    dataset = await repo.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Cryo-ET dataset not found")

    particles = await repo.get_particles_by_dataset(dataset_id)
    refinements = await repo.get_refinements_by_dataset(dataset_id)

    return {
        "id": dataset.id,
        "sample_name": dataset.sample_name,
        "specimen_organism": dataset.specimen_organism,
        "cellular_compartment": dataset.cellular_compartment,
        "tilt_angle_min": dataset.tilt_angle_min,
        "tilt_angle_max": dataset.tilt_angle_max,
        "total_tilt_images": dataset.total_tilt_images,
        "pixel_size_angstrom": dataset.pixel_size_angstrom,
        "nominal_defocus_um": dataset.nominal_defocus_um,
        "tomogram_dimensions": dataset.tomogram_dimensions_json,
        "metadata": dataset.dataset_metadata_json,
        "particles": [
            {
                "id": p.id,
                "particle_index": p.particle_index,
                "coord_x": p.coord_x,
                "coord_y": p.coord_y,
                "coord_z": p.coord_z,
                "euler_phi": p.euler_phi,
                "euler_theta": p.euler_theta,
                "euler_psi": p.euler_psi,
                "cross_correlation_score": p.cross_correlation_score,
                "class_assignment": p.class_assignment,
            }
            for p in particles
        ],
        "refinements": [
            {
                "id": r.id,
                "class_name": r.class_name,
                "particles_averaged_count": r.particles_averaged_count,
                "estimated_resolution_angstrom": r.estimated_resolution_angstrom,
                "fsc_0143_spatial_frequency": r.fsc_0143_spatial_frequency,
                "b_factor_sharpening": r.b_factor_sharpening,
                "fsc_curve": r.fsc_curve_json,
            }
            for r in refinements
        ]
    }
