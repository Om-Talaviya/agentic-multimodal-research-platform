"""
FastAPI route for Phase 106: Spatial Lipidomics & Multi-Isotope Imaging Mass Spectrometry.
"""
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from database.repositories.spatial_lipidomics_repo import SpatialLipidomicsRepository
from research.spatial.lipidomics_engine import SpatialLipidomicsEngine

router = APIRouter(prefix="/spatial-lipidomics", tags=["Phase 106: Spatial Lipidomics"])

class SpatialLipidomicsRequest(BaseModel):
    sample_name: str
    tissue_type: str = "Brain Sagittal Section"
    matrix_type: str = "DHB"
    grid_dim: int = Field(default=8, ge=4, le=32)
    custom_mz_list: Optional[List[float]] = None

class LipidSpeciesResponse(BaseModel):
    id: str
    mz_ratio: float
    lipid_species: str
    lipid_class: str
    adduct_type: str
    structural_formula: Optional[str] = None
    mean_intensity: float

class SpatialSpotResponse(BaseModel):
    lipid_species_id: str
    x_coord: int
    y_coord: int
    normalized_intensity: float
    region_annotation: str

class SpatialLipidomicsDatasetResponse(BaseModel):
    id: str
    sample_name: str
    tissue_type: str
    matrix_type: str
    laser_spatial_resolution_um: float
    total_spots: int
    detected_lipid_classes: int
    status: str
    lipid_species: List[Dict[str, Any]] = []
    spatial_spots: List[Dict[str, Any]] = []

@router.post("/process", response_model=SpatialLipidomicsDatasetResponse, status_code=status.HTTP_201_CREATED)
async def process_and_persist_spatial_lipidomics(
    request: SpatialLipidomicsRequest,
    db: AsyncSession = Depends(get_db)
):
    engine = SpatialLipidomicsEngine()
    processed = engine.process_dataset(
        sample_name=request.sample_name,
        tissue_type=request.tissue_type,
        matrix_type=request.matrix_type,
        grid_dim=request.grid_dim,
        custom_mz_list=request.custom_mz_list
    )

    repo = SpatialLipidomicsRepository(db)
    dataset = await repo.create_dataset(
        sample_name=processed["sample_name"],
        tissue_type=processed["tissue_type"],
        matrix_type=processed["matrix_type"],
        laser_spatial_resolution_um=processed["laser_spatial_resolution_um"]
    )

    await repo.add_lipid_species(dataset.id, processed["lipid_species"])
    await repo.add_spatial_spots(dataset.id, processed["spatial_spots"])

    hydrated = await repo.get_dataset(dataset.id)
    if not hydrated:
        raise HTTPException(status_code=500, detail="Failed to retrieve spatial lipidomics dataset")

    return SpatialLipidomicsDatasetResponse(
        id=str(hydrated.id),
        sample_name=hydrated.sample_name,
        tissue_type=hydrated.tissue_type,
        matrix_type=hydrated.matrix_type,
        laser_spatial_resolution_um=hydrated.laser_spatial_resolution_um,
        total_spots=hydrated.total_spots,
        detected_lipid_classes=hydrated.detected_lipid_classes,
        status=hydrated.status,
        lipid_species=[{
            "id": str(s.id),
            "mz_ratio": s.mz_ratio,
            "lipid_species": s.lipid_species,
            "lipid_class": s.lipid_class,
            "adduct_type": s.adduct_type,
            "structural_formula": s.structural_formula,
            "mean_intensity": s.mean_intensity
        } for s in hydrated.lipid_species],
        spatial_spots=[{
            "lipid_species_id": str(sp.lipid_species_id),
            "x_coord": sp.x_coord,
            "y_coord": sp.y_coord,
            "normalized_intensity": sp.normalized_intensity,
            "region_annotation": sp.region_annotation
        } for sp in hydrated.spatial_spots]
    )

@router.get("/datasets", response_model=List[SpatialLipidomicsDatasetResponse])
async def list_spatial_lipidomics_datasets(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    repo = SpatialLipidomicsRepository(db)
    datasets = await repo.list_datasets(limit=limit, offset=offset)
    return [
        SpatialLipidomicsDatasetResponse(
            id=str(d.id),
            sample_name=d.sample_name,
            tissue_type=d.tissue_type,
            matrix_type=d.matrix_type,
            laser_spatial_resolution_um=d.laser_spatial_resolution_um,
            total_spots=d.total_spots,
            detected_lipid_classes=d.detected_lipid_classes,
            status=d.status,
            lipid_species=[],
            spatial_spots=[]
        )
        for d in datasets
    ]

@router.get("/datasets/{dataset_id}", response_model=SpatialLipidomicsDatasetResponse)
async def get_spatial_lipidomics_dataset_detail(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = SpatialLipidomicsRepository(db)
    hydrated = await repo.get_dataset(dataset_id)
    if not hydrated:
        raise HTTPException(status_code=404, detail="Spatial lipidomics dataset not found")

    return SpatialLipidomicsDatasetResponse(
        id=str(hydrated.id),
        sample_name=hydrated.sample_name,
        tissue_type=hydrated.tissue_type,
        matrix_type=hydrated.matrix_type,
        laser_spatial_resolution_um=hydrated.laser_spatial_resolution_um,
        total_spots=hydrated.total_spots,
        detected_lipid_classes=hydrated.detected_lipid_classes,
        status=hydrated.status,
        lipid_species=[{
            "id": str(s.id),
            "mz_ratio": s.mz_ratio,
            "lipid_species": s.lipid_species,
            "lipid_class": s.lipid_class,
            "adduct_type": s.adduct_type,
            "structural_formula": s.structural_formula,
            "mean_intensity": s.mean_intensity
        } for s in hydrated.lipid_species],
        spatial_spots=[{
            "lipid_species_id": str(sp.lipid_species_id),
            "x_coord": sp.x_coord,
            "y_coord": sp.y_coord,
            "normalized_intensity": sp.normalized_intensity,
            "region_annotation": sp.region_annotation
        } for sp in hydrated.spatial_spots]
    )
