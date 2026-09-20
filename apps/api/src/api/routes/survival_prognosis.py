"""
Phase 110: Clinical-Genomic Survival Prognosis & Multi-Omics Stratification API Routes.
"""
from typing import Dict, Any, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from database.repositories.survival_prognosis_repo import SurvivalPrognosisRepository
from research.clinical.survival_prognosis_engine import SurvivalPrognosisEngine

router = APIRouter(prefix="/survival-prognosis", tags=["Phase 110: Survival Prognosis"])

class SurvivalStratificationRequest(BaseModel):
    model_name: str = Field(..., example="MultiOmics-PanCancer-RiskStratifier")
    cancer_cohort: str = Field("TCGA-LUAD", example="TCGA-LUAD")
    sample_size: int = Field(120, ge=30, le=5000, example=120)
    project_id: Optional[str] = Field(None, example="proj_survival_001")

@router.post("/stratify", status_code=status.HTTP_201_CREATED)
async def stratify_cohort(req: SurvivalStratificationRequest, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Simulates multi-omics cohort survival analysis, fits Cox hazard model, and creates Kaplan-Meier curves.
    """
    engine = SurvivalPrognosisEngine()
    result = engine.simulate_cohort_prognosis(
        model_name=req.model_name,
        cancer_cohort=req.cancer_cohort,
        sample_size=req.sample_size,
        project_id=req.project_id
    )

    repo = SurvivalPrognosisRepository(db)
    model = await repo.create_model(
        model_name=result["model_name"],
        cancer_cohort=result["cancer_cohort"],
        c_index_score=result["c_index_score"],
        hazard_ratio_high_vs_low=result["hazard_ratio_high_vs_low"],
        log_rank_p_value=result["log_rank_p_value"],
        risk_stratification_method=result["risk_stratification_method"],
        features_weights=result["features_weights"],
        project_id=req.project_id
    )

    # Persist patients
    for pt in result["patients"]:
        await repo.add_patient(
            model_id=model.id,
            patient_barcode=pt["patient_barcode"],
            overall_survival_months=pt["overall_survival_months"],
            vital_status=pt["vital_status"],
            risk_group=pt["risk_group"],
            risk_score=pt["risk_score"],
            biomarker_vector=pt["biomarker_vector"]
        )

    # Persist curves
    for cv in result["curves"]:
        await repo.add_curve(
            model_id=model.id,
            risk_tier=cv["risk_tier"],
            time_points_months=cv["time_points_months"],
            survival_probability_km=cv["survival_probability_km"],
            patients_at_risk=cv["patients_at_risk"],
            median_survival_months=cv["median_survival_months"]
        )

    return {
        "status": "success",
        "model_id": str(model.id),
        "data": result
    }

@router.get("/models/{model_id}")
async def get_prognostic_model(model_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    repo = SurvivalPrognosisRepository(db)
    model = await repo.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Prognostic model {model_id} not found")

    patients = await repo.list_patients(model.id)
    curves = await repo.list_curves(model.id)

    return {
        "id": str(model.id),
        "model_name": model.model_name,
        "cancer_cohort": model.cancer_cohort,
        "c_index_score": model.c_index_score,
        "hazard_ratio_high_vs_low": model.hazard_ratio_high_vs_low,
        "log_rank_p_value": model.log_rank_p_value,
        "risk_stratification_method": model.risk_stratification_method,
        "features_weights": model.features_weights,
        "created_at": model.created_at.isoformat() if model.created_at else None,
        "patients_count": len(patients),
        "curves": [
            {
                "id": str(cv.id),
                "risk_tier": cv.risk_tier,
                "time_points_months": cv.time_points_months,
                "survival_probability_km": cv.survival_probability_km,
                "patients_at_risk": cv.patients_at_risk,
                "median_survival_months": cv.median_survival_months,
            }
            for cv in curves
        ]
    }
