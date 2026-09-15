"""Drug Repurposing & Combination Synergy REST API Routes (Phase 45)."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_current_user
from database.models.user import User as DBUser
from database.repositories.drug_synergy_repo import DrugSynergyRepository
from research.drug_synergy_engine import DrugSynergyEngine

router = APIRouter(prefix="/synergy", tags=["Drug Repurposing & Synergy"])

class ScreenRequest(BaseModel):
    title: str = Field(..., description="Screen title")
    disease_indication: str = Field(..., description="Target disease indication (e.g. Glioblastoma, Sorafenib-Resistant HCC)")
    screening_library: str = Field("FDA-Approved & Phase III Clinical Library")
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None

class CandidateDTO(BaseModel):
    id: str
    drug_name: str
    original_indication: str
    proposed_mechanism: str
    connectivity_score: float
    ic50_um: float
    clinical_safety_tier: str
    evidence_publications_count: int

class SynergyDTO(BaseModel):
    id: str
    drug_a: str
    drug_b: str
    zip_synergy_score: float
    bliss_excess_score: float
    loewe_combination_index: float
    synergy_classification: str
    dose_reduction_index: float
    ddi_toxicity_risk: str
    synergy_matrix_2d: Optional[List[List[float]]] = None

class ScreenDTO(BaseModel):
    id: str
    title: str
    disease_indication: str
    screening_library: str
    total_screened: int
    top_candidates_count: int
    status: str
    created_at: str

@router.post("/screens/run", response_model=ScreenDTO, status_code=status.HTTP_201_CREATED)
async def run_repurposing_screen(
    req: ScreenRequest,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = DrugSynergyRepository(db)
    engine = DrugSynergyEngine()

    screen_res = engine.run_repurposing_screen(disease_indication=req.disease_indication)

    screen = await repo.create_screen(
        title=req.title,
        disease_indication=req.disease_indication,
        screening_library=req.screening_library,
        total_screened=screen_res["total_screened"],
        workspace_id=req.workspace_id,
        project_id=req.project_id,
    )

    await repo.add_candidates(screen.id, screen_res["candidates"])
    await repo.add_synergies(screen.id, screen_res["synergies"])

    return ScreenDTO(
        id=str(screen.id),
        title=screen.title,
        disease_indication=screen.disease_indication,
        screening_library=screen.screening_library,
        total_screened=screen.total_screened,
        top_candidates_count=len(screen_res["candidates"]),
        status=screen.status,
        created_at=screen.created_at.isoformat(),
    )

@router.get("/screens", response_model=List[ScreenDTO])
async def list_screens(
    disease_indication: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = DrugSynergyRepository(db)
    screens = await repo.list_screens(disease_indication=disease_indication, limit=limit)
    return [
        ScreenDTO(
            id=str(s.id),
            title=s.title,
            disease_indication=s.disease_indication,
            screening_library=s.screening_library,
            total_screened=s.total_screened,
            top_candidates_count=s.top_candidates_count,
            status=s.status,
            created_at=s.created_at.isoformat(),
        )
        for s in screens
    ]

@router.get("/screens/{screen_id}/candidates", response_model=List[CandidateDTO])
async def get_screen_candidates(
    screen_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = DrugSynergyRepository(db)
    candidates = await repo.get_candidates(screen_id)
    return [
        CandidateDTO(
            id=str(c.id),
            drug_name=c.drug_name,
            original_indication=c.original_indication,
            proposed_mechanism=c.proposed_mechanism,
            connectivity_score=c.connectivity_score,
            ic50_um=c.ic50_um,
            clinical_safety_tier=c.clinical_safety_tier,
            evidence_publications_count=c.evidence_publications_count,
        )
        for c in candidates
    ]

@router.get("/screens/{screen_id}/synergies", response_model=List[SynergyDTO])
async def get_screen_synergies(
    screen_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = DrugSynergyRepository(db)
    synergies = await repo.get_synergies(screen_id)
    return [
        SynergyDTO(
            id=str(s.id),
            drug_a=s.drug_a,
            drug_b=s.drug_b,
            zip_synergy_score=s.zip_synergy_score,
            bliss_excess_score=s.bliss_excess_score,
            loewe_combination_index=s.loewe_combination_index,
            synergy_classification=s.synergy_classification,
            dose_reduction_index=s.dose_reduction_index,
            ddi_toxicity_risk=s.ddi_toxicity_risk,
            synergy_matrix_2d=s.synergy_matrix_2d,
        )
        for s in synergies
    ]

@router.delete("/screens/{screen_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_screen(
    screen_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = DrugSynergyRepository(db)
    deleted = await repo.delete_screen(screen_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Screen not found")
    return None
