"""
Phase 109: High-Dimensional CyTOF & Mass Cytometry API Routes.
"""
from typing import Dict, Any, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from database.repositories.cytof_repo import CyTOFRepository
from research.cytometry.cytof_engine import CyTOFPhenotyperEngine

router = APIRouter(prefix="/cytof", tags=["Phase 109: CyTOF Phenotyper"])

class CyTOFSimulationRequest(BaseModel):
    experiment_name: str = Field(..., example="PBMC-Immune-Atlas-DeepProfile")
    tissue_type: str = Field("PBMC", example="PBMC")
    cell_count: int = Field(5000, ge=100, le=1000000, example=10000)
    cofactor: float = Field(5.0, ge=1.0, le=50.0, example=5.0)
    project_id: Optional[str] = Field(None, example="proj_cytof_001")

@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_cytof(req: CyTOFSimulationRequest, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Simulates a high-dimensional CyTOF run and persists the experiment, channels, and clusters to the database.
    """
    engine = CyTOFPhenotyperEngine()
    result = engine.simulate_cytof_panel(
        experiment_name=req.experiment_name,
        tissue_type=req.tissue_type,
        cell_count=req.cell_count,
        cofactor=req.cofactor,
        project_id=req.project_id
    )

    repo = CyTOFRepository(db)
    exp = await repo.create_experiment(
        experiment_name=result["experiment_name"],
        tissue_type=result["tissue_type"],
        cell_count=result["cell_count"],
        panel_size=result["panel_size"],
        cofactor=result["cofactor"],
        is_compensated=result["is_compensated"],
        project_id=req.project_id
    )

    # Persist channels
    for ch in result["channels"]:
        await repo.add_metal_channel(
            experiment_id=exp.id,
            channel_name=ch["channel_name"],
            metal_isotope=ch["metal_isotope"],
            target_marker=ch["target_marker"],
            mean_intensity=ch["mean_intensity"],
            signal_to_noise=ch["signal_to_noise"],
            spillover_matrix=ch["spillover_matrix"]
        )

    # Persist clusters
    for cl in result["clusters"]:
        await repo.add_cluster(
            experiment_id=exp.id,
            cluster_id=cl["cluster_id"],
            cluster_name=cl["cluster_name"],
            cell_frequency=cl["cell_frequency"],
            marker_enrichment_profile=cl["marker_enrichment_profile"],
            phenograph_k=cl["phenograph_k"],
            tsne_coordinates_2d=cl["tsne_coordinates_sample"]
        )

    return {
        "status": "success",
        "experiment_id": str(exp.id),
        "data": result
    }

@router.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    repo = CyTOFRepository(db)
    exp = await repo.get_experiment(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail=f"CyTOF experiment {experiment_id} not found")

    channels = await repo.list_channels(exp.id)
    clusters = await repo.list_clusters(exp.id)

    return {
        "id": str(exp.id),
        "experiment_name": exp.experiment_name,
        "tissue_type": exp.tissue_type,
        "cell_count": exp.cell_count,
        "panel_size": exp.panel_size,
        "cofactor": exp.cofactor,
        "is_compensated": exp.is_compensated,
        "created_at": exp.created_at.isoformat() if exp.created_at else None,
        "channels": [
            {
                "id": str(ch.id),
                "channel_name": ch.channel_name,
                "metal_isotope": ch.metal_isotope,
                "target_marker": ch.target_marker,
                "mean_intensity": ch.mean_intensity,
                "signal_to_noise": ch.signal_to_noise,
            }
            for ch in channels
        ],
        "clusters": [
            {
                "id": str(cl.id),
                "cluster_id": cl.cluster_id,
                "cluster_name": cl.cluster_name,
                "cell_frequency": cl.cell_frequency,
                "marker_enrichment_profile": cl.marker_enrichment_profile,
                "tsne_coordinates_2d": cl.tsne_coordinates_2d,
            }
            for cl in clusters
        ]
    }
