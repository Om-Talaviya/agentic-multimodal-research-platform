"""API Routes for High-Content Phenotypic Screening & Cell Painting Assays."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.phenotypic_screening_repo import PhenotypicScreeningRepository
from research.imaging.phenotypic_screening_engine import PhenotypicScreeningEngine

router = APIRouter(prefix="/phenotypic-screening", tags=["Phenotypic Screening & Single-Cell Morphometry"])


class WellProfileRequest(BaseModel):
    well_position: str = Field(..., example="B04")
    compound_name: str = Field(..., example="Paclitaxel")
    concentration_uM: float = Field(default=10.0, ge=0.001)
    is_control: bool = Field(default=False)
    raw_measurements: Optional[List[Dict[str, float]]] = None


class PlateScreeningRequest(BaseModel):
    plate_name: str = Field(..., example="HCS_Plate_PrimaryScreen_01")
    format: str = Field(default="384-well")
    cell_line: str = Field(default="U2OS")
    imaging_magnification: str = Field(default="20x")
    wells: List[WellProfileRequest]
    workspace_id: Optional[str] = None


@router.get("/signatures")
async def get_moa_signatures():
    """List reference Mechanism-of-Action (MoA) phenotypic signatures."""
    return {"signatures": PhenotypicScreeningEngine.MOA_SIGNATURES}


@router.post("/plates", status_code=status.HTTP_201_CREATED)
async def screen_plate(
    request: PlateScreeningRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Analyze and persist multi-well high-content Cell Painting screening plate."""
    engine = PhenotypicScreeningEngine()
    repo = PhenotypicScreeningRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    plate = await repo.create_plate(
        workspace_id=ws_id,
        plate_name=request.plate_name,
        format=request.format,
        cell_line=request.cell_line,
        imaging_magnification=request.imaging_magnification,
        total_wells=len(request.wells),
    )

    created_wells = []
    for w in request.wells:
        analysis = engine.analyze_well_morphology(
            well_position=w.well_position,
            compound_name=w.compound_name,
            concentration_uM=w.concentration_uM,
            is_control=w.is_control,
            raw_cell_measurements=w.raw_measurements,
        )

        well_record = await repo.add_well_profile(
            plate_id=plate.id,
            well_position=w.well_position,
            compound_name=w.compound_name,
            concentration_uM=w.concentration_uM,
            is_control=w.is_control,
            cell_count=analysis["morphological_profile"]["cell_count"],
            viability_pct=analysis["morphological_profile"]["estimated_viability_pct"],
            predicted_moa=analysis["predicted_moa"],
            moa_confidence=analysis["moa_confidence"],
            phenotypic_activity_score=analysis["phenotypic_activity_score"],
            morphological_profile=analysis["morphological_profile"],
            single_cells=analysis["single_cells"],
        )
        created_wells.append({
            "id": str(well_record.id),
            "well_position": well_record.well_position,
            "compound_name": well_record.compound_name,
            "predicted_moa": well_record.predicted_moa,
            "moa_confidence": well_record.moa_confidence,
            "phenotypic_activity_score": well_record.phenotypic_activity_score,
            "viability_pct": well_record.viability_pct,
        })

    return {
        "status": "success",
        "plate_id": str(plate.id),
        "plate_name": plate.plate_name,
        "cell_line": plate.cell_line,
        "wells_processed": len(created_wells),
        "wells": created_wells,
    }


@router.get("/plates/{plate_id}")
async def get_plate_details(
    plate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve plate and well morphometric profiles."""
    try:
        p_uuid = uuid.UUID(plate_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plate UUID")

    repo = PhenotypicScreeningRepository(db)
    plate = await repo.get_plate(p_uuid)
    if not plate:
        raise HTTPException(status_code=404, detail="Cell Painting plate not found")

    return {
        "id": str(plate.id),
        "plate_name": plate.plate_name,
        "format": plate.format,
        "cell_line": plate.cell_line,
        "wells_count": len(plate.wells),
        "wells": [
            {
                "id": str(w.id),
                "well_position": w.well_position,
                "compound_name": w.compound_name,
                "concentration_uM": w.concentration_uM,
                "predicted_moa": w.predicted_moa,
                "moa_confidence": w.moa_confidence,
                "phenotypic_activity_score": w.phenotypic_activity_score,
                "single_cells_count": len(w.single_cells),
            }
            for w in plate.wells
        ],
    }
