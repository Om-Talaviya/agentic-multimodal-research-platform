"""
Phase 133: Cryo-ET Subtomogram Deep Clustering & In-Situ Macromolecular Structure Solver API Route.
"""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.cryoet_clustering_repo import CryoETClusteringRepository
from research.structural.cryoet_clustering_engine import (
    CryoETDeepClusteringEngine,
    SubtomogramInput,
)

router = APIRouter(prefix="/cryoet-clustering", tags=["Cryo-ET Deep Clustering"])


class SubtomogramItem(BaseModel):
    volume_tag: str
    tomogram_id: str
    coord_x: float
    coord_y: float
    coord_z: float
    contrast_snr: float = 1.8


class CryoETClusteringRequest(BaseModel):
    study_name: str = Field(..., example="HeLa Cell Lamella In-Situ Cryo-ET")
    cellular_organism: str = Field(..., example="Homo sapiens")
    subtomograms: Optional[List[SubtomogramItem]] = None
    voxel_size_angstrom: float = Field(default=1.35, example=1.35)
    target_cluster_count: int = Field(default=3, example=3)
    workspace_id: Optional[str] = None


@router.post("/process", status_code=status.HTTP_201_CREATED)
async def process_cryoet_clustering(
    req: CryoETClusteringRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = CryoETDeepClusteringEngine()
    engine_subtomos = (
        [SubtomogramInput(**s.model_dump()) for s in req.subtomograms]
        if req.subtomograms
        else None
    )

    result = engine.process_subtomogram_clustering(
        study_name=req.study_name,
        cellular_organism=req.cellular_organism,
        subtomograms=engine_subtomos,
        voxel_size_angstrom=req.voxel_size_angstrom,
        target_cluster_count=req.target_cluster_count,
    )

    repo = CryoETClusteringRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else uuid.uuid4()

    study = await repo.create_study(
        study_name=result.study_name,
        cellular_organism=result.cellular_organism,
        total_subtomograms_extracted=result.total_volumes_processed,
        voxel_size_angstrom=req.voxel_size_angstrom,
        mean_resolution_angstrom=result.mean_resolution_angstrom,
        metadata_json={
            "fsc_curves": result.fsc_curves,
            "summary_metrics": result.summary_metrics,
            "workspace_id": str(ws_id),
        },
    )

    for vol in result.representative_subtomograms:
        await repo.add_volume(
            study_id=study.id,
            volume_tag=vol["volume_tag"],
            tomogram_id=vol["tomogram_id"],
            coord_x=vol["coord_x"],
            coord_y=vol["coord_y"],
            coord_z=vol["coord_z"],
            signal_to_noise_ratio=vol["signal_to_noise_ratio"],
            cross_correlation_score=vol["cross_correlation_score"],
            assigned_cluster=vol["assigned_cluster"],
        )

    for cl in result.clusters:
        await repo.add_cluster(
            study_id=study.id,
            cluster_label=cl["cluster_label"],
            macromolecule_identity=cl["macromolecule_identity"],
            particle_count=cl["particle_count"],
            fsc_resolution_angstrom=cl["fsc_resolution_angstrom"],
            b_factor_sharpening=cl["b_factor_sharpening"],
            conformational_state=cl["conformational_state"],
        )

    return {
        "status": "SUCCESS",
        "study_id": str(study.id),
        "study_name": study.study_name,
        "mean_resolution_angstrom": study.mean_resolution_angstrom,
        "result": result.model_dump(),
    }


@router.get("/studies/{study_id}")
async def get_study_details(
    study_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        sid = uuid.UUID(study_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid study UUID")

    repo = CryoETClusteringRepository(db)
    study = await repo.get_study(sid)
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    return {
        "id": str(study.id),
        "study_name": study.study_name,
        "cellular_organism": study.cellular_organism,
        "mean_resolution_angstrom": study.mean_resolution_angstrom,
        "volumes_count": len(study.volumes),
        "clusters_count": len(study.clusters),
    }
