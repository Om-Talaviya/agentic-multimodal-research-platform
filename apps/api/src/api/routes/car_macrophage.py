"""
Phase 137: CAR-Macrophage (CAR-M) Solid Tumor Phagocytosis & TME Matrix Degradation API Route.
"""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.car_macrophage_repo import CARMacrophageRepository
from research.immunology.car_macrophage_engine import (
    CARMacrophageEngine,
)

router = APIRouter(prefix="/car-macrophage", tags=["CAR-Macrophage Solid Tumor Engine"])


class CARMacrophageDesignRequest(BaseModel):
    construct_name: str = Field(..., example="CT-0508 Anti-HER2 CAR-M")
    target_tumor_antigen: str = Field(default="HER2 / ERBB2", example="HER2 / ERBB2")
    scfv_domain: str = Field(default="Trastuzumab-derived 4D5", example="Trastuzumab-derived 4D5")
    intracellular_signaling_domain: str = Field(
        default="Megf10 / FcR-gamma",
        example="Megf10 / FcR-gamma",
    )
    macrophage_subtype: str = Field(
        default="M1-Polarized Pro-Inflammatory",
        example="M1-Polarized Pro-Inflammatory",
    )
    target_cell_line: str = Field(default="SK-BR-3 Breast Cancer", example="SK-BR-3 Breast Cancer")
    effector_to_target_ratio: str = Field(default="2:1", example="2:1")
    workspace_id: Optional[str] = None


@router.post("/design", status_code=status.HTTP_201_CREATED)
async def design_car_macrophage_endpoint(
    req: CARMacrophageDesignRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = CARMacrophageEngine()
    result = engine.model_car_macrophage_activity(
        construct_name=req.construct_name,
        target_antigen=req.target_tumor_antigen,
        signaling_domain=req.intracellular_signaling_domain,
        tumor_type=req.target_cell_line,
        e_to_t_ratio=req.effector_to_target_ratio,
    )

    repo = CARMacrophageRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    design = await repo.create_design(
        project_id=ws_id,
        construct_name=result.construct_name,
        target_tumor_antigen=result.target_antigen,
        scfv_domain=req.scfv_domain,
        intracellular_signaling_domain=result.signaling_domain,
        macrophage_subtype=req.macrophage_subtype,
        matrix_degradation_mmp_score=8.4,
        target_phagocytosis_efficiency_percent=result.overall_phagocytosis_efficiency_percent,
        metadata_json={
            "matrix_metalloproteinase_activity": result.matrix_metalloproteinase_activity,
            "recommendations": result.recommendations,
        },
    )

    # Add phagocytosis kinetics
    await repo.add_phagocytosis_record(
        design_id=design.id,
        target_cell_line=req.target_cell_line,
        effector_to_target_ratio=req.effector_to_target_ratio,
        trogocytosis_rate_percent=result.trogocytosis_rate_percent,
        whole_cell_engulfment_rate_percent=result.whole_cell_engulfment_percent,
        antigen_cross_presentation_index=result.antigen_cross_presentation_score,
    )

    # Add TME profile
    tme = result.tme_repolarization_metrics
    await repo.add_tme_profile(
        design_id=design.id,
        tnf_alpha_secretion_pg_ml=tme["tnf_alpha_secretion_pg_ml"],
        il12_secretion_pg_ml=tme["il12_t_cell_co_stim_pg_ml"],
        il10_immunosuppression_fold_reduction=3.8,
        collagen_matrix_clearance_percent=74.0,
    )

    return {
        "status": "SUCCESS",
        "design_id": str(design.id),
        "construct_name": design.construct_name,
        "target_tumor_antigen": design.target_tumor_antigen,
        "phagocytosis_efficiency_percent": design.target_phagocytosis_efficiency_percent,
        "result": result.model_dump(),
    }


@router.get("/designs/{design_id}")
async def get_car_macrophage_design(
    design_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        did = uuid.UUID(design_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid design UUID")

    repo = CARMacrophageRepository(db)
    design = await repo.get_design(did)
    if not design:
        raise HTTPException(status_code=404, detail="CAR-Macrophage design not found")

    return {
        "id": str(design.id),
        "construct_name": design.construct_name,
        "target_tumor_antigen": design.target_tumor_antigen,
        "phagocytosis_efficiency_percent": design.target_phagocytosis_efficiency_percent,
        "phagocytosis_records_count": len(design.phagocytosis_records),
        "tme_profiles_count": len(design.tme_profiles),
    }
