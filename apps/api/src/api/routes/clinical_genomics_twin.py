"""API Routes for Clinical Genomics Digital Twin & Pharmacogenomics."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.clinical_genomics_twin_repo import ClinicalGenomicsTwinRepository
from research.clinical.genomics_twin_engine import ClinicalGenomicsTwinEngine

router = APIRouter(prefix="/clinical-twin", tags=["Clinical Genomics Digital Twin"])


class PatientTwinEvaluateRequest(BaseModel):
    patient_mrn: str = Field(..., description="Unique Patient Medical Record Number")
    age: int = Field(default=58, ge=0, le=125)
    sex: str = Field(default="FEMALE")
    ancestry: str = Field(default="EUROPEAN")
    diplotypes: Dict[str, str] = Field(
        default_factory=lambda: {
            "CYP2C19": "*2/*2",
            "CYP2D6": "*1/*4",
            "DPYD": "*1/*1",
            "SLCO1B1": "*1/*1",
        }
    )
    target_drug: str = Field(default="Clopidogrel")
    prescribed_dose_mg: float = Field(default=75.0, ge=0.1, le=2000.0)


@router.get("/guidelines-kb")
async def get_pharmacogenomics_kb():
    """Retrieve CPIC Level A pharmacogenomic rules and guidelines."""
    return {"knowledge_base": ClinicalGenomicsTwinEngine.PHARMACOGENOMIC_KNOWLEDGE_BASE}


@router.post("/evaluate", status_code=status.HTTP_201_CREATED)
async def evaluate_clinical_twin(
    request: PatientTwinEvaluateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Evaluate patient pharmacogenomic profile and run digital twin PK simulation."""
    engine = ClinicalGenomicsTwinEngine()
    result = engine.evaluate_patient_twin(
        patient_mrn=request.patient_mrn,
        age=request.age,
        sex=request.sex,
        ancestry=request.ancestry,
        diplotypes=request.diplotypes,
        target_drug=request.target_drug,
        prescribed_dose_mg=request.prescribed_dose_mg,
    )

    repo = ClinicalGenomicsTwinRepository(db)
    p_info = result["profile"]
    
    # Check if patient exists or create new
    profile = await repo.get_profile_by_mrn(request.patient_mrn)
    if not profile:
        profile = await repo.create_profile(
            patient_mrn=p_info["patient_mrn"],
            age=p_info["age"],
            sex=p_info["sex"],
            ancestry=p_info["ancestry"],
            total_star_alleles_called=p_info["total_star_alleles_called"],
            high_risk_drug_interactions_count=p_info["high_risk_drug_interactions_count"],
        )

    for g in result["guidelines"]:
        await repo.add_guideline(
            profile_id=profile.id,
            gene_symbol=g["gene_symbol"],
            diplotype_call=g["diplotype_call"],
            metabolizer_phenotype=g["metabolizer_phenotype"],
            affected_drug_class=g["affected_drug_class"],
            cpic_level=g["cpic_level"],
            clinical_dose_recommendation=g["clinical_dose_recommendation"],
        )

    for s in result["twin_simulations"]:
        await repo.add_twin_simulation(
            profile_id=profile.id,
            drug_administered=s["drug_administered"],
            prescribed_dose_mg=s["prescribed_dose_mg"],
            predicted_auc_ratio=s["predicted_auc_ratio"],
            toxic_accumulation_risk=s["toxic_accumulation_risk"],
            recommended_adjusted_dose_mg=s["recommended_adjusted_dose_mg"],
            alternate_drug_suggestion=s["alternate_drug_suggestion"],
            efficacy_score=s["efficacy_score"],
        )

    saved = await repo.get_profile(profile.id)
    return {
        "status": "success",
        "id": profile.id,
        "patient_mrn": profile.patient_mrn,
        "high_risk_drug_interactions_count": profile.high_risk_drug_interactions_count,
        "guidelines_count": len(saved.guidelines if saved else []),
        "simulations_count": len(saved.twin_simulations if saved else []),
    }


@router.get("/profiles")
async def list_clinical_profiles(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """List recent patient genomic digital twin profiles."""
    repo = ClinicalGenomicsTwinRepository(db)
    profiles = await repo.list_profiles(limit=limit)
    return [
        {
            "id": p.id,
            "patient_mrn": p.patient_mrn,
            "age": p.age,
            "sex": p.sex,
            "high_risk_drug_interactions_count": p.high_risk_drug_interactions_count,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "guidelines_count": len(p.guidelines),
            "simulations_count": len(p.twin_simulations),
        }
        for p in profiles
    ]


@router.get("/profiles/{profile_id}")
async def get_clinical_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Get full details of a patient digital twin profile."""
    repo = ClinicalGenomicsTwinRepository(db)
    profile = await repo.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    return {
        "id": profile.id,
        "patient_mrn": profile.patient_mrn,
        "age": profile.age,
        "sex": profile.sex,
        "ancestry": profile.ancestry,
        "high_risk_drug_interactions_count": profile.high_risk_drug_interactions_count,
        "guidelines": [
            {
                "id": g.id,
                "gene_symbol": g.gene_symbol,
                "diplotype_call": g.diplotype_call,
                "metabolizer_phenotype": g.metabolizer_phenotype,
                "affected_drug_class": g.affected_drug_class,
                "clinical_dose_recommendation": g.clinical_dose_recommendation,
            }
            for g in profile.guidelines
        ],
        "twin_simulations": [
            {
                "id": s.id,
                "drug_administered": s.drug_administered,
                "prescribed_dose_mg": s.prescribed_dose_mg,
                "predicted_auc_ratio": s.predicted_auc_ratio,
                "toxic_accumulation_risk": s.toxic_accumulation_risk,
                "recommended_adjusted_dose_mg": s.recommended_adjusted_dose_mg,
                "alternate_drug_suggestion": s.alternate_drug_suggestion,
                "efficacy_score": s.efficacy_score,
            }
            for s in profile.twin_simulations
        ],
    }
