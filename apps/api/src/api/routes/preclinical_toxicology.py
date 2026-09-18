"""API Routes for Preclinical Toxicogenomics & ADMET-Safety Risk Analysis."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.preclinical_toxicology_repo import PreclinicalToxicologyRepository
from research.toxicology.toxicogenomics_engine import PreclinicalToxicologyEngine

router = APIRouter(prefix="/preclinical-toxicology", tags=["Preclinical Toxicogenomics & ADMET"])


class CompoundSafetyAssessmentRequest(BaseModel):
    compound_name: str = Field(..., example="Imatinib_Derivative_4a")
    smiles_string: str = Field(..., example="CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5")
    workspace_id: Optional[str] = None


@router.get("/alert-rules")
async def get_structural_alert_rules():
    """Retrieve preclinical structural alert screening rules."""
    return {"rules": PreclinicalToxicologyEngine.STRUCTURAL_ALERT_RULES}


@router.post("/assess", status_code=status.HTTP_201_CREATED)
async def assess_compound_safety(
    request: CompoundSafetyAssessmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Predict toxicogenomic risk endpoints, detect structural tox alerts, and calculate TSI."""
    engine = PreclinicalToxicologyEngine()
    assessment = engine.assess_compound_safety(
        compound_name=request.compound_name,
        smiles=request.smiles_string,
    )

    repo = PreclinicalToxicologyRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    study = await repo.create_study(
        workspace_id=ws_id,
        compound_name=assessment["compound_name"],
        smiles_string=assessment["smiles_string"],
        therapeutic_safety_index=assessment["therapeutic_safety_index"],
        overall_safety_tier=assessment["overall_safety_tier"],
        caco2_permeability_cm_s=assessment["caco2_permeability_cm_s"],
        plasma_protein_binding_pct=assessment["plasma_protein_binding_pct"],
        study_metadata={"risk_summary": assessment["risk_summary"]},
    )

    for ep in assessment["endpoints"]:
        await repo.add_endpoint(
            study_id=study.id,
            endpoint_name=ep["endpoint_name"],
            endpoint_category=ep["endpoint_category"],
            probability_risk=ep["probability_risk"],
            measured_or_predicted_value=ep["measured_or_predicted_value"],
            unit=ep["unit"],
            risk_classification=ep["risk_classification"],
            confidence_score=ep["confidence_score"],
        )

    for alert in assessment["structural_tox_alerts"]:
        await repo.add_tox_alert(
            study_id=study.id,
            alert_name=alert["name"],
            substructure_smarts=alert["smarts"],
            mechanism=alert["mechanism"],
            severity=alert["severity"],
        )

    return {
        "status": "success",
        "study_id": str(study.id),
        "compound_name": study.compound_name,
        "smiles_string": study.smiles_string,
        "therapeutic_safety_index": study.therapeutic_safety_index,
        "overall_safety_tier": study.overall_safety_tier,
        "caco2_permeability_cm_s": study.caco2_permeability_cm_s,
        "plasma_protein_binding_pct": study.plasma_protein_binding_pct,
        "endpoints_count": len(assessment["endpoints"]),
        "structural_alerts_count": len(assessment["structural_tox_alerts"]),
        "risk_summary": assessment["risk_summary"],
        "endpoints": assessment["endpoints"],
        "structural_tox_alerts": assessment["structural_tox_alerts"],
    }


@router.get("/studies/{study_id}")
async def get_study_details(
    study_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve preclinical toxicology study profile and endpoints."""
    try:
        s_uuid = uuid.UUID(study_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid study UUID")

    repo = PreclinicalToxicologyRepository(db)
    study = await repo.get_study(s_uuid)
    if not study:
        raise HTTPException(status_code=404, detail="Preclinical toxicology study not found")

    return {
        "id": str(study.id),
        "compound_name": study.compound_name,
        "smiles_string": study.smiles_string,
        "therapeutic_safety_index": study.therapeutic_safety_index,
        "overall_safety_tier": study.overall_safety_tier,
        "endpoints": [
            {
                "id": str(ep.id),
                "endpoint_name": ep.endpoint_name,
                "category": ep.endpoint_category,
                "risk_class": ep.risk_classification,
                "probability": ep.probability_risk,
                "value": ep.measured_or_predicted_value,
                "unit": ep.unit,
            }
            for ep in study.endpoints
        ],
        "structural_alerts": [
            {
                "id": str(al.id),
                "alert_name": al.alert_name,
                "severity": al.severity,
                "mechanism": al.mechanism,
            }
            for al in study.tox_alerts
        ],
    }
