"""
FastAPI router for Rare Disease Phenotype-to-Genotype HPO Engine (Phase 61).
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.rare_disease_hpo_repo import RareDiseaseHPORepository
from research.hpo.rare_disease_hpo_engine import RareDiseaseHPOEngine

router = APIRouter(prefix="/rare-disease", tags=["Rare Disease Diagnostic Matching"])


class HPOTermInput(BaseModel):
    hpo_id: str = "HP:0001250"
    term_name: str = "Seizures"
    severity_weight: float = 1.0


class CreateCaseRequest(BaseModel):
    case_number: str = Field(default="CASE-RD-2026-101")
    patient_id: str = Field(default="PT-PEDIATRIC-088")
    clinical_summary: str = Field(default="14-month-old infant with refractory febrile seizures and global developmental delay.")
    age_of_onset: str = Field(default="Infantile")
    phenotypes: List[HPOTermInput] = Field(
        default=[
            HPOTermInput(hpo_id="HP:0001250", term_name="Seizures"),
            HPOTermInput(hpo_id="HP:0001263", term_name="Global developmental delay"),
            HPOTermInput(hpo_id="HP:0002069", term_name="Bilateral tonic-clonic seizures"),
            HPOTermInput(hpo_id="HP:0010818", term_name="Febrile seizures"),
        ]
    )


@router.post("/cases", status_code=status.HTTP_201_CREATED)
async def create_rare_disease_case(
    request: CreateCaseRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Executes HPO semantic ontologic matching and causal rare disease gene ranking."""
    repo = RareDiseaseHPORepository(db)
    case = await repo.create_case(
        case_number=request.case_number,
        patient_id=request.patient_id,
        clinical_summary=request.clinical_summary,
        age_of_onset=request.age_of_onset,
    )

    phenotypes_raw = [
        {"hpo_id": p.hpo_id, "term_name": p.term_name, "severity_weight": p.severity_weight}
        for p in request.phenotypes
    ]

    match_result = RareDiseaseHPOEngine.match_case_phenotypes(phenotypes_raw)

    return await repo.add_phenotypes_and_matches(
        case_id=case.id,
        phenotypes_data=match_result["phenotypes"],
        candidate_genes_data=match_result["candidate_genes"],
    )


@router.get("/cases")
async def list_rare_disease_cases(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists rare disease diagnostic cases."""
    repo = RareDiseaseHPORepository(db)
    return await repo.list_cases(limit=limit)


@router.get("/cases/{case_id}")
async def get_rare_disease_case(
    case_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves full case details with mapped HPO phenotypes and prioritized candidate genes."""
    repo = RareDiseaseHPORepository(db)
    case = await repo.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Rare disease diagnostic case not found")
    return case
