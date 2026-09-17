"""REST API endpoints for Multi-Modal Biomarker Discovery & Signature Extraction."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.models import User
from database.repositories.biomarker_discovery_repo import BiomarkerDiscoveryRepository
from research.biomarkers.biomarker_engine import BiomarkerSignatureExtractorEngine

router = APIRouter(prefix="/api/v1/biomarkers", tags=["Multi-Modal Biomarker Discovery"])
engine = BiomarkerSignatureExtractorEngine()


class FeatureInput(BaseModel):
    feature_name: str
    omics_modality: str
    log2_fold_change: float = 0.0
    adjusted_p_value: float = 0.05
    feature_importance_weight: float = 0.5
    correlation_direction: str = "POSITIVE"


class BiomarkerStudyRequest(BaseModel):
    study_title: str
    disease_indication: str
    cohort_sample_size: int = Field(100, ge=10, le=100000)
    omics_layers: List[str] = ["TRANSCRIPTOMICS", "PROTEOMICS"]
    features: Optional[List[FeatureInput]] = None


@router.post("/studies/extract", status_code=status.HTTP_201_CREATED)
async def extract_biomarker_signature(
    req: BiomarkerStudyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Extracts, cross-validates multi-modal biomarker signatures and stratifies cohorts."""
    repo = BiomarkerDiscoveryRepository(db)

    features_dict = [f.model_dump() for f in req.features] if req.features else None
    eval_res = engine.extract_signature(req.model_dump(), features_dict)

    study = await repo.create_study(
        study_title=eval_res["study_title"],
        disease_indication=eval_res["disease_indication"],
        cohort_sample_size=eval_res["cohort_sample_size"],
        omics_layers_json=eval_res["omics_layers_json"],
        signature_stability_score=eval_res["signature_stability_score"],
        auc_roc_score=eval_res["auc_roc_score"],
        study_metadata_json=eval_res["study_metadata_json"],
    )

    created_features = await repo.add_features(study.id, eval_res["features"])
    created_stratifications = await repo.add_stratifications(study.id, eval_res["stratifications"])

    return {
        "id": study.id,
        "study_title": study.study_title,
        "disease_indication": study.disease_indication,
        "cohort_sample_size": study.cohort_sample_size,
        "omics_layers": study.omics_layers_json,
        "signature_stability_score": study.signature_stability_score,
        "auc_roc_score": study.auc_roc_score,
        "metadata": study.study_metadata_json,
        "features": [
            {
                "id": f.id,
                "feature_name": f.feature_name,
                "omics_modality": f.omics_modality,
                "log2_fold_change": f.log2_fold_change,
                "adjusted_p_value": f.adjusted_p_value,
                "feature_importance_weight": f.feature_importance_weight,
                "correlation_direction": f.correlation_direction,
            }
            for f in created_features
        ],
        "stratifications": [
            {
                "id": s.id,
                "patient_cohort_id": s.patient_cohort_id,
                "prognostic_risk_tier": s.prognostic_risk_tier,
                "response_probability_score": s.response_probability_score,
                "composite_signature_score": s.composite_signature_score,
                "expression_map": s.signature_expression_map_json,
            }
            for s in created_stratifications
        ]
    }


@router.get("/studies")
async def list_studies(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists biomarker discovery studies."""
    repo = BiomarkerDiscoveryRepository(db)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [
        {
            "id": s.id,
            "study_title": s.study_title,
            "disease_indication": s.disease_indication,
            "cohort_sample_size": s.cohort_sample_size,
            "signature_stability_score": s.signature_stability_score,
            "auc_roc_score": s.auc_roc_score,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]


@router.get("/studies/{study_id}")
async def get_study_details(
    study_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Gets detailed biomarker discovery study with features and patient stratifications."""
    repo = BiomarkerDiscoveryRepository(db)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Biomarker discovery study not found")

    features = await repo.get_features_by_study(study_id)
    stratifications = await repo.get_stratifications_by_study(study_id)

    return {
        "id": study.id,
        "study_title": study.study_title,
        "disease_indication": study.disease_indication,
        "cohort_sample_size": study.cohort_sample_size,
        "omics_layers": study.omics_layers_json,
        "signature_stability_score": study.signature_stability_score,
        "auc_roc_score": study.auc_roc_score,
        "metadata": study.study_metadata_json,
        "features": [
            {
                "id": f.id,
                "feature_name": f.feature_name,
                "omics_modality": f.omics_modality,
                "log2_fold_change": f.log2_fold_change,
                "adjusted_p_value": f.adjusted_p_value,
                "feature_importance_weight": f.feature_importance_weight,
                "correlation_direction": f.correlation_direction,
            }
            for f in features
        ],
        "stratifications": [
            {
                "id": s.id,
                "patient_cohort_id": s.patient_cohort_id,
                "prognostic_risk_tier": s.prognostic_risk_tier,
                "response_probability_score": s.response_probability_score,
                "composite_signature_score": s.composite_signature_score,
                "expression_map": s.signature_expression_map_json,
            }
            for s in stratifications
        ]
    }
