"""API Routes for CAR-NK & Immuno-Oncology SynNotch Cell Circuit Designer (Phase 96)."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.car_nk_repo import CarNkDesignRepository
from research.cell_therapy.car_nk_engine import CarNkDesignEngine

router = APIRouter(prefix="/car-nk", tags=["CAR-NK & SynNotch Designer"])


class CarNkDesignRequest(BaseModel):
    construct_name: str = Field(..., example="NK_SynNotch_Mesothelin_v1")
    primary_target: str = Field(..., example="Mesothelin")
    costimulatory_domain: str = Field(default="2B4_plus_41BB", example="2B4_plus_41BB")
    synnotch_sensor_antigen: Optional[str] = Field(default="EpCAM", example="EpCAM")
    gate_type: str = Field(default="AND_GATE", example="AND_GATE")
    armored_cytokine: str = Field(default="IL-15", example="IL-15")
    workspace_id: Optional[str] = None


@router.get("/costimulatory-domains")
async def get_costimulatory_domains():
    """Retrieve characterized NK-specific costimulatory domains and efficacy profiles."""
    return {"domains": CarNkDesignEngine.CO_STIMULATORY_PROFILES}


@router.post("/design", status_code=status.HTTP_201_CREATED)
async def design_car_nk_circuit(
    request: CarNkDesignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Design, optimize, and simulate an armored SynNotch CAR-NK cell therapeutic construct."""
    engine = CarNkDesignEngine()
    result = engine.design_car_nk(
        construct_name=request.construct_name,
        primary_target=request.primary_target,
        costimulatory_domain=request.costimulatory_domain,
        synnotch_sensor_antigen=request.synnotch_sensor_antigen,
        gate_type=request.gate_type,
        armored_cytokine=request.armored_cytokine,
    )

    repo = CarNkDesignRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    design = await repo.create_design(
        workspace_id=ws_id,
        construct_name=result["construct_name"],
        primary_target=result["primary_target"],
        costimulatory_domain=result["costimulatory_domain"],
        signaling_domain=result["signaling_domain"],
        cytotoxicity_score=result["cytotoxicity_score"],
        persistence_index=result["persistence_index"],
        exhaustion_resistance_score=result["exhaustion_resistance_score"],
        off_tumor_safety_margin=result["off_tumor_safety_margin"],
        design_metadata={"rationale": result["rationale"]},
    )

    for gate in result["synnotch_gates"]:
        await repo.add_synnotch_gate(
            car_nk_id=design.id,
            gate_type=gate["gate_type"],
            sensor_antigen=gate["sensor_antigen"],
            actuator_payload=gate["actuator_payload"],
            specificity_enrichment=gate["specificity_enrichment"],
            leaky_expression_pct=gate["leaky_expression_pct"],
        )

    for cyt in result["cytokines"]:
        await repo.add_cytokine_profile(
            car_nk_id=design.id,
            cytokine_name=cyt["cytokine_name"],
            secretion_level_pg_ml=cyt["secretion_level_pg_ml"],
            is_armored_payload=cyt["is_armored_payload"],
        )

    return {
        "status": "SUCCESS",
        "design_id": str(design.id),
        "construct_name": design.construct_name,
        "primary_target": design.primary_target,
        "cytotoxicity_score": design.cytotoxicity_score,
        "persistence_index": design.persistence_index,
        "off_tumor_safety_margin": design.off_tumor_safety_margin,
        "synnotch_gates": result["synnotch_gates"],
        "cytokines": result["cytokines"],
        "rationale": result["rationale"],
    }


@router.get("/designs/{design_id}")
async def get_car_nk_design(
    design_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve full CAR-NK design including SynNotch logic and cytokine profiles."""
    repo = CarNkDesignRepository(db)
    try:
        did = uuid.UUID(design_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid design UUID format")

    design = await repo.get_design(did)
    if not design:
        raise HTTPException(status_code=404, detail="CAR-NK design not found")

    return {
        "id": str(design.id),
        "construct_name": design.construct_name,
        "primary_target": design.primary_target,
        "costimulatory_domain": design.costimulatory_domain,
        "cytotoxicity_score": design.cytotoxicity_score,
        "persistence_index": design.persistence_index,
        "off_tumor_safety_margin": design.off_tumor_safety_margin,
        "synnotch_gates": [
            {
                "gate_type": g.gate_type,
                "sensor_antigen": g.sensor_antigen,
                "actuator_payload": g.actuator_payload,
                "specificity_enrichment": g.specificity_enrichment,
            }
            for g in design.synnotch_gates
        ],
        "cytokines": [
            {
                "cytokine_name": c.cytokine_name,
                "secretion_level_pg_ml": c.secretion_level_pg_ml,
                "is_armored_payload": c.is_armored_payload,
            }
            for c in design.cytokines
        ],
    }
