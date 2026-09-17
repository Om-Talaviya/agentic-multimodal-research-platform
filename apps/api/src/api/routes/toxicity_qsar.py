from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.toxicity_qsar_repo import ToxicityQSARRepository
from research.toxicity.toxicity_engine import QSARToxicityEngine

router = APIRouter(prefix="/api/v1/toxicity-qsar", tags=["QSAR Toxicity & Mutagenicity"])

class ToxicityScreenRequest(BaseModel):
    compound_name: str = Field(..., example="Imatinib-Derivative-04")
    smiles_string: str = Field(..., example="Cc1ccc(cc1Nc2nccc(n2)c3cccnc3)NC(=O)c4ccc(cc4)CN5CCN(CC5)C")
    molecular_weight: float = Field(493.6, example=493.6)
    log_p: float = Field(3.2, example=3.2)

@router.post("/screen", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def screen_compound_toxicity(
    request: ToxicityScreenRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Autonomous In-Silico Toxicity & QSAR Mutagenicity Matrix Engine.
    """
    engine = QSARToxicityEngine()
    repo = ToxicityQSARRepository(db)

    # 1. Run QSAR toxicity prediction
    tox = engine.predict_compound_toxicity(
        smiles=request.smiles_string,
        compound_name=request.compound_name,
        mol_weight=request.molecular_weight,
        log_p=request.log_p,
    )

    # 2. Persist screen record
    screen = await repo.create_screen(
        compound_name=request.compound_name,
        smiles_string=request.smiles_string,
        molecular_weight=request.molecular_weight,
        log_p=request.log_p,
        ames_mutagenicity_status=tox["ames_mutagenicity_status"],
        ames_probability_pct=tox["ames_probability_pct"],
        herg_ic50_micromolar=tox["herg_ic50_micromolar"],
        herg_cardiotox_risk=tox["herg_cardiotox_risk"],
        dili_hepatotox_risk=tox["dili_hepatotox_risk"],
        ld50_rat_mg_kg=tox["ld50_rat_mg_kg"],
    )

    # 3. Persist structural alerts
    for alert in tox["structural_alerts"]:
        await repo.add_structural_alert(
            screen_id=screen.id,
            alert_name=alert["alert_name"],
            smarts_pattern=alert["smarts_pattern"],
            toxicophore_category=alert["toxicophore_category"],
            severity_level=alert["severity_level"],
        )

    hydrated = await repo.get_screen_by_id(screen.id)

    return {
        "status": "SUCCESS",
        "screen_id": hydrated.id,
        "compound_name": hydrated.compound_name,
        "smiles_string": hydrated.smiles_string,
        "ames_mutagenicity_status": hydrated.ames_mutagenicity_status,
        "ames_probability_pct": hydrated.ames_probability_pct,
        "herg_ic50_micromolar": hydrated.herg_ic50_micromolar,
        "herg_cardiotox_risk": hydrated.herg_cardiotox_risk,
        "dili_hepatotox_risk": hydrated.dili_hepatotox_risk,
        "ld50_rat_mg_kg": hydrated.ld50_rat_mg_kg,
        "structural_alerts": [
            {
                "alert_name": a.alert_name,
                "smarts_pattern": a.smarts_pattern,
                "toxicophore_category": a.toxicophore_category,
                "severity_level": a.severity_level,
            }
            for a in hydrated.structural_alerts
        ],
    }

@router.get("/screens", response_model=List[Dict[str, Any]])
async def list_toxicity_screens(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = ToxicityQSARRepository(db)
    screens = await repo.list_screens(limit=limit)
    return [
        {
            "id": s.id,
            "compound_name": s.compound_name,
            "ames_mutagenicity_status": s.ames_mutagenicity_status,
            "herg_cardiotox_risk": s.herg_cardiotox_risk,
            "dili_hepatotox_risk": s.dili_hepatotox_risk,
            "alerts_count": len(s.structural_alerts),
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in screens
    ]

@router.get("/screens/{screen_id}", response_model=Dict[str, Any])
async def get_toxicity_screen(
    screen_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    repo = ToxicityQSARRepository(db)
    s = await repo.get_screen_by_id(screen_id)
    if not s:
        raise HTTPException(status_code=404, detail="Toxicity screen not found")
    return {
        "id": s.id,
        "compound_name": s.compound_name,
        "smiles_string": s.smiles_string,
        "molecular_weight": s.molecular_weight,
        "log_p": s.log_p,
        "ames_mutagenicity_status": s.ames_mutagenicity_status,
        "ames_probability_pct": s.ames_probability_pct,
        "herg_ic50_micromolar": s.herg_ic50_micromolar,
        "herg_cardiotox_risk": s.herg_cardiotox_risk,
        "dili_hepatotox_risk": s.dili_hepatotox_risk,
        "ld50_rat_mg_kg": s.ld50_rat_mg_kg,
        "structural_alerts": [
            {
                "id": a.id,
                "alert_name": a.alert_name,
                "smarts_pattern": a.smarts_pattern,
                "toxicophore_category": a.toxicophore_category,
                "severity_level": a.severity_level,
            }
            for a in s.structural_alerts
        ],
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }
