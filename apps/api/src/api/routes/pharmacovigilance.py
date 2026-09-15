"""
FastAPI Route Handlers for Phase 49: Pharmacovigilance & Safety Signal Detection.
"""
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_current_user
from database.models.user import User as DBUser
from database.repositories.pharmacovigilance_repo import PharmacovigilanceRepository
from research.pharmacovigilance_engine import PharmacovigilanceEngine

router = APIRouter(prefix="/pharmacovigilance", tags=["Pharmacovigilance & Safety Signals (Phase 49)"])

class DetectSignalsRequest(BaseModel):
    drug_name: str = Field(..., example="Trastuzumab Deruxtecan")
    corpus_size: int = Field(default=1250000, example=1250000)

class CorpusResponse(BaseModel):
    id: uuid.UUID
    title: str
    data_sources: List[str]
    total_adverse_reports: int
    status: str
    created_at: Any

    class Config:
        from_attributes = True

@router.post("/detect", response_model=CorpusResponse, status_code=status.HTTP_201_CREATED)
async def detect_safety_signals(
    payload: DetectSignalsRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    engine = PharmacovigilanceEngine()
    result = engine.detect_signals(
        drug_name=payload.drug_name,
        total_corpus_reports=payload.corpus_size
    )

    repo = PharmacovigilanceRepository(db)
    corpus = await repo.create_corpus(
        title=result["title"],
        data_sources=result["data_sources"],
        total_reports=result["total_reports"],
        user_id=current_user.id
    )

    for sig in result["signals"]:
        report = await repo.add_signal(
            corpus_id=corpus.id,
            drug_name=payload.drug_name,
            adverse_reaction_term=sig["adverse_reaction_term"],
            system_organ_class=sig["system_organ_class"],
            case_count=sig["case_count"],
            signal_priority=sig["signal_priority"],
            who_umc_causality=sig["who_umc_causality"],
            clinical_summary=sig["clinical_summary"]
        )
        m = sig["metrics"]
        await repo.add_metrics(
            signal_id=report.id,
            prr=m["prr"],
            ror=m["ror"],
            ror_lower=m["ror_lower"],
            ror_upper=m["ror_upper"],
            ic025=m["ic025"],
            ebgm05=m["ebgm05"],
            chi_sq=m["chi_square"]
        )

    return corpus

@router.get("/corpora", response_model=List[CorpusResponse])
async def list_corpora(
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    repo = PharmacovigilanceRepository(db)
    return await repo.list_corpora(limit=limit)

@router.get("/corpora/{corpus_id}")
async def get_corpus_details(
    corpus_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: DBUser = Depends(get_current_user)
):
    repo = PharmacovigilanceRepository(db)
    c = await repo.get_corpus(corpus_id)
    if not c:
        raise HTTPException(status_code=404, detail="Pharmacovigilance corpus not found")
    return {
        "id": str(c.id),
        "title": c.title,
        "data_sources": c.data_sources,
        "total_reports": c.total_adverse_reports,
        "signals": [
            {
                "id": str(s.id),
                "drug": s.drug_name,
                "reaction": s.adverse_reaction_term,
                "soc": s.system_organ_class,
                "case_count": s.case_count,
                "priority": s.signal_priority,
                "causality": s.who_umc_causality,
                "summary": s.clinical_summary,
                "metrics": [
                    {
                        "prr": m.proportional_reporting_ratio_prr,
                        "ror": m.reporting_odds_ratio_ror,
                        "ror_ci": f"[{m.ror_ci_lower_95} - {m.ror_ci_upper_95}]",
                        "ic025": m.information_component_ic025,
                        "ebgm05": m.ebgm_05,
                        "chi_square": m.chi_square_yates
                    } for m in s.metrics
                ]
            } for s in c.signals
        ]
    }
