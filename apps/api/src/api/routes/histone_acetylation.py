"""
Phase 136: Epigenetic Histone Acetylation Dynamics & HAT/HDAC Chromatin Remodeling API Route.
"""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.histone_acetylation_repo import HistoneAcetylationRepository
from research.epigenomics.histone_acetylation_engine import (
    HistoneAcetylationEngine,
)

router = APIRouter(prefix="/histone-acetylation", tags=["Histone Acetylation Dynamics"])


class AcetylationSimulationRequest(BaseModel):
    locus_name: str = Field(..., example="MYC Super-Enhancer Locus")
    genomic_coordinates: str = Field(..., example="chr8:127735434-127736300")
    cell_line: str = Field(..., example="K562 Leukemia")
    hdac_inhibitor: str = Field(default="Vorinostat (SAHA)", example="Vorinostat (SAHA)")
    inhibitor_dose_um: float = Field(default=2.5, example=2.5)
    treatment_duration_hours: float = Field(default=24.0, example=24.0)
    workspace_id: Optional[str] = None


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_acetylation_endpoint(
    req: AcetylationSimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = HistoneAcetylationEngine()
    result = engine.simulate_acetylation_kinetics(
        locus_name=req.locus_name,
        genomic_coordinates=req.genomic_coordinates,
        cell_line=req.cell_line,
        hdac_inhibitor=req.hdac_inhibitor,
        inhibitor_dose_um=req.inhibitor_dose_um,
        treatment_duration_hours=req.treatment_duration_hours,
    )

    repo = HistoneAcetylationRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    model = await repo.create_model(
        project_id=ws_id,
        locus_name=result.locus_name,
        genomic_coordinates=result.genomic_coordinates,
        cell_line_or_tissue=result.cell_line,
        initial_h3k27ac_enrichment=result.time_series_dynamics[0]["h3k27ac_enrichment"],
        hdac_inhibitor_name=result.hdac_inhibitor,
        predicted_enhancer_activation_fold=result.predicted_enhancer_activation_fold,
        metadata_json={
            "brd4_recruitment_fold": result.brd4_recruitment_fold,
            "recommendations": result.recommendations,
        },
    )

    # Add kinetics
    for k in result.enzyme_kinetics:
        await repo.add_enzyme_kinetics(
            model_id=model.id,
            enzyme_type=k["enzyme"],
            catalytic_rate_kcat=k["kcat"],
            michaelis_constant_km_um=k["km_um"],
        )

    # Add time series
    for t in result.time_series_dynamics:
        await repo.add_chromatin_profile(
            model_id=model.id,
            time_point_hours=t["time_point_hours"],
            nucleosome_occupancy_percent=t["nucleosome_occupancy_percent"],
            atac_seq_peak_intensity_rpm=t["atac_seq_intensity_rpm"],
            brd4_bromodomain_recruitment=t["brd4_recruitment_fold"],
        )

    return {
        "status": "SUCCESS",
        "model_id": str(model.id),
        "locus_name": model.locus_name,
        "predicted_enhancer_activation_fold": model.predicted_enhancer_activation_fold,
        "final_h3k27ac_enrichment": result.final_h3k27ac_enrichment,
        "result": result.model_dump(),
    }


@router.get("/models/{model_id}")
async def get_acetylation_model(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        mid = uuid.UUID(model_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid model UUID")

    repo = HistoneAcetylationRepository(db)
    model = await repo.get_model(mid)
    if not model:
        raise HTTPException(status_code=404, detail="Histone acetylation model not found")

    return {
        "id": str(model.id),
        "locus_name": model.locus_name,
        "cell_line_or_tissue": model.cell_line_or_tissue,
        "predicted_enhancer_activation_fold": model.predicted_enhancer_activation_fold,
        "enzyme_kinetics_count": len(model.enzyme_kinetics),
        "chromatin_profiles_count": len(model.chromatin_profiles),
    }
