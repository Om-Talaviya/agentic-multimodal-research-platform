"""Spatial Transcriptomics REST API Routes (Phase 42)."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_current_user
from database.repositories.spatial_repo import SpatialTranscriptomicsRepository
from research.spatial_engine import SpatialTranscriptomicsEngine
from database.models.user import User as DBUser

router = APIRouter(prefix="/spatial", tags=["Spatial Transcriptomics"])

class SpatialAnalyzeRequest(BaseModel):
    title: str = Field(..., description="Dataset title")
    tissue_type: str = Field(..., description="Tissue type (e.g. Glioblastoma, Liver, Breast Carcinoma)")
    technology: str = Field("10x Visium", description="Spatial technology (10x Visium, MERFISH, CosMx)")
    n_spots: int = Field(200, ge=10, le=5000, description="Number of spatial spots/cells to simulate or analyze")
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None
    description: Optional[str] = None

class SpotCoordinateDTO(BaseModel):
    id: str
    spot_barcode: str
    x_coord: float
    y_coord: float
    z_coord: float
    cluster_id: int
    cluster_name: str
    cell_type_annotation: str
    total_counts: int
    n_genes_detected: int
    spatial_domain_id: Optional[str]
    tumor_proximity_score: float

class SpatialDomainDTO(BaseModel):
    id: str
    domain_name: str
    domain_type: str
    color_hex: str
    spot_count: int
    area_percentage: float
    top_marker_genes: Optional[List[str]] = None

class CellCommunicationDTO(BaseModel):
    id: str
    pathway_name: str
    ligand_gene: str
    receptor_gene: str
    source_cluster: str
    target_cluster: str
    communication_score: float
    p_value: float
    interaction_distance_um: float
    is_spatially_constrained: bool

class SpatialDatasetDTO(BaseModel):
    id: str
    title: str
    tissue_type: str
    technology: str
    organism: str
    total_spots: int
    status: str
    description: Optional[str] = None
    created_at: str

@router.post("/analyze", response_model=SpatialDatasetDTO, status_code=status.HTTP_201_CREATED)
async def analyze_spatial_tissue(
    req: SpatialAnalyzeRequest,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SpatialTranscriptomicsRepository(db)
    engine = SpatialTranscriptomicsEngine()
    
    # Run analysis
    analysis_res = engine.analyze_tissue_sample(
        tissue_type=req.tissue_type,
        n_spots=req.n_spots,
        technology=req.technology,
    )
    
    # Create dataset record
    dataset = await repo.create_dataset(
        title=req.title,
        tissue_type=req.tissue_type,
        technology=req.technology,
        workspace_id=req.workspace_id,
        project_id=req.project_id,
        total_spots=len(analysis_res["spots"]),
        description=req.description,
        meta_info=analysis_res["summary"],
    )
    
    # Save spots, domains, and communications
    await repo.add_spots(dataset.id, analysis_res["spots"])
    await repo.add_domains(dataset.id, analysis_res["domains"])
    await repo.add_communications(dataset.id, analysis_res["communications"])
    
    return SpatialDatasetDTO(
        id=str(dataset.id),
        title=dataset.title,
        tissue_type=dataset.tissue_type,
        technology=dataset.technology,
        organism=dataset.organism,
        total_spots=dataset.total_spots,
        status=dataset.status,
        description=dataset.description,
        created_at=dataset.created_at.isoformat(),
    )

@router.get("/datasets", response_model=List[SpatialDatasetDTO])
async def list_spatial_datasets(
    workspace_id: Optional[str] = None,
    project_id: Optional[str] = None,
    tissue_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SpatialTranscriptomicsRepository(db)
    datasets = await repo.list_datasets(workspace_id, project_id, tissue_type, limit, offset)
    return [
        SpatialDatasetDTO(
            id=str(d.id),
            title=d.title,
            tissue_type=d.tissue_type,
            technology=d.technology,
            organism=d.organism,
            total_spots=d.total_spots,
            status=d.status,
            description=d.description,
            created_at=d.created_at.isoformat(),
        )
        for d in datasets
    ]

@router.get("/datasets/{dataset_id}", response_model=SpatialDatasetDTO)
async def get_spatial_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SpatialTranscriptomicsRepository(db)
    d = await repo.get_dataset(dataset_id)
    if not d:
        raise HTTPException(status_code=404, detail="Spatial dataset not found")
    return SpatialDatasetDTO(
        id=str(d.id),
        title=d.title,
        tissue_type=d.tissue_type,
        technology=d.technology,
        organism=d.organism,
        total_spots=d.total_spots,
        status=d.status,
        description=d.description,
        created_at=d.created_at.isoformat(),
    )

@router.get("/datasets/{dataset_id}/spots", response_model=List[SpotCoordinateDTO])
async def get_spatial_spots(
    dataset_id: str,
    cluster_id: Optional[int] = None,
    limit: int = 2000,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SpatialTranscriptomicsRepository(db)
    spots = await repo.get_spots(dataset_id=dataset_id, cluster_id=cluster_id, limit=limit)
    return [
        SpotCoordinateDTO(
            id=str(s.id),
            spot_barcode=s.spot_barcode,
            x_coord=s.x_coord,
            y_coord=s.y_coord,
            z_coord=s.z_coord,
            cluster_id=s.cluster_id,
            cluster_name=s.cluster_name,
            cell_type_annotation=s.cell_type_annotation,
            total_counts=s.total_counts,
            n_genes_detected=s.n_genes_detected,
            spatial_domain_id=s.spatial_domain_id,
            tumor_proximity_score=s.tumor_proximity_score,
        )
        for s in spots
    ]

@router.get("/datasets/{dataset_id}/domains", response_model=List[SpatialDomainDTO])
async def get_spatial_domains(
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SpatialTranscriptomicsRepository(db)
    domains = await repo.get_domains(dataset_id)
    return [
        SpatialDomainDTO(
            id=str(d.id),
            domain_name=d.domain_name,
            domain_type=d.domain_type,
            color_hex=d.color_hex,
            spot_count=d.spot_count,
            area_percentage=d.area_percentage,
            top_marker_genes=d.top_marker_genes,
        )
        for d in domains
    ]

@router.get("/datasets/{dataset_id}/communications", response_model=List[CellCommunicationDTO])
async def get_spatial_communications(
    dataset_id: str,
    pathway_name: Optional[str] = None,
    min_score: float = 0.0,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SpatialTranscriptomicsRepository(db)
    comms = await repo.get_communications(dataset_id, pathway_name, min_score)
    return [
        CellCommunicationDTO(
            id=str(c.id),
            pathway_name=c.pathway_name,
            ligand_gene=c.ligand_gene,
            receptor_gene=c.receptor_gene,
            source_cluster=c.source_cluster,
            target_cluster=c.target_cluster,
            communication_score=c.communication_score,
            p_value=c.p_value,
            interaction_distance_um=c.interaction_distance_um,
            is_spatially_constrained=c.is_spatially_constrained,
        )
        for c in comms
    ]

@router.delete("/datasets/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spatial_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SpatialTranscriptomicsRepository(db)
    deleted = await repo.delete_dataset(dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Spatial dataset not found")
    return None
