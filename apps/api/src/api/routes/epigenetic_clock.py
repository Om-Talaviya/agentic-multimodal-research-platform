"""API Routes for Epigenetic Clock & DNA Methylation Age Prediction."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.epigenetic_clock_repo import EpigeneticClockRepository
from research.epigenetics.epigenetic_clock_engine import EpigeneticClockEngine

router = APIRouter(prefix="/epigenetic-clock", tags=["Epigenetic Clock & DNA Methylation"])


class EpigeneticAnalyzeRequest(BaseModel):
    sample_name: str = Field(..., example="Patient_001_Baseline")
    chronological_age: float = Field(..., ge=0.0, le=125.0, example=45.5)
    tissue_type: str = Field(default="Whole Blood", example="Whole Blood")
    gender: str = Field(default="unknown", example="female")
    platform: str = Field(default="Illumina EPIC 850k")
    clock_model: str = Field(default="Horvath", description="Horvath, Hannum, PhenoAge, GrimAge")
    beta_values: Dict[str, float] = Field(default_factory=dict, description="Dictionary of CpG ID -> beta value (0.0 - 1.0)")
    workspace_id: Optional[str] = None


@router.get("/models")
async def get_supported_clock_models():
    """List available epigenetic clock predictive models."""
    return {"models": EpigeneticClockEngine.CLOCK_MODELS, "canonical_cpg_count": len(EpigeneticClockEngine.CANONICAL_CPG_MAP)}


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_epigenetic_sample(
    request: EpigeneticAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Predict epigenetic age, pace of aging, and age acceleration from methylation profile."""
    engine = EpigeneticClockEngine()
    prediction = engine.predict_age(
        chronological_age=request.chronological_age,
        beta_values=request.beta_values,
        clock_model=request.clock_model,
        impute_missing=True,
    )

    repo = EpigeneticClockRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    sample = await repo.create_sample(
        workspace_id=ws_id,
        sample_name=request.sample_name,
        chronological_age=request.chronological_age,
        tissue_type=request.tissue_type,
        gender=request.gender,
        platform=request.platform,
        total_cpgs_profiled=len(request.beta_values) or len(prediction["top_cpg_markers"]),
        sample_metadata={"submitted_by": str(getattr(current_user, "id", "anonymous"))},
    )

    result = await repo.create_clock_result(
        sample_id=sample.id,
        predicted_epigenetic_age=prediction["predicted_epigenetic_age"],
        age_acceleration=prediction["age_acceleration"],
        clock_model=prediction["clock_model"],
        confidence_interval_low=prediction["confidence_interval"]["low"],
        confidence_interval_high=prediction["confidence_interval"]["high"],
        mortality_risk_percentile=prediction["mortality_risk_percentile"],
        model_r_squared=prediction["model_r_squared"],
        cpgs_utilized=prediction["cpgs_utilized"],
        pace_of_aging=prediction["pace_of_aging"],
        analysis_details=prediction["analysis_details"],
        cpg_markers=prediction["top_cpg_markers"],
    )

    return {
        "status": "success",
        "sample_id": str(sample.id),
        "result_id": str(result.id),
        "sample_name": sample.sample_name,
        "chronological_age": sample.chronological_age,
        "predicted_epigenetic_age": result.predicted_epigenetic_age,
        "age_acceleration": result.age_acceleration,
        "pace_of_aging": result.pace_of_aging,
        "confidence_interval": {
            "low": result.confidence_interval_low,
            "high": result.confidence_interval_high,
        },
        "mortality_risk_percentile": result.mortality_risk_percentile,
        "top_cpg_markers": prediction["top_cpg_markers"],
    }


@router.get("/samples/{sample_id}")
async def get_sample_details(
    sample_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve epigenetic sample details and associated clock predictions."""
    try:
        s_uuid = uuid.UUID(sample_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sample UUID")

    repo = EpigeneticClockRepository(db)
    sample = await repo.get_sample(s_uuid)
    if not sample:
        raise HTTPException(status_code=404, detail="Epigenetic sample not found")

    return {
        "id": str(sample.id),
        "sample_name": sample.sample_name,
        "chronological_age": sample.chronological_age,
        "tissue_type": sample.tissue_type,
        "gender": sample.gender,
        "clock_results": [
            {
                "id": str(cr.id),
                "clock_model": cr.clock_model,
                "predicted_epigenetic_age": cr.predicted_epigenetic_age,
                "age_acceleration": cr.age_acceleration,
                "pace_of_aging": cr.pace_of_aging,
                "mortality_risk_percentile": cr.mortality_risk_percentile,
                "markers_count": len(cr.cpg_markers),
            }
            for cr in sample.clock_results
        ],
    }
