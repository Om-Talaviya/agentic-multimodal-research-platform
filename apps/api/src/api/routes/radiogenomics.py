"""API Routes for Radiogenomics & 3D Volumetric Medical Imaging AI Feature Extraction."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.radiogenomics_repo import RadiogenomicsRepository
from research.imaging.radiogenomics_engine import RadiogenomicsEngine

router = APIRouter(prefix="/radiogenomics", tags=["Radiogenomics & 3D Imaging AI"])


class RadiogenomicsExtractRequest(BaseModel):
    patient_id: str = Field(..., description="Unique patient identifier")
    modality: str = Field(default="MRI_T1_CONTRAST", description="Modality: MRI_T1_CONTRAST, MRI_T2_FLAIR, CT_CHEST_CONTRAST, PET_FDG")
    anatomical_region: str = Field(default="BRAIN_GLIOMA", description="Region: BRAIN_GLIOMA, LUNG_NSCLC, BREAST_TUMOR")
    lesion_volume_cm3: float = Field(default=24.5, ge=0.1, le=1000.0)


@router.post("/extract", status_code=status.HTTP_201_CREATED)
async def extract_and_correlate_scan(
    request: RadiogenomicsExtractRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Extract IBSI radiomic features from volumetric scan and predict genomic mutations."""
    engine = RadiogenomicsEngine()
    result = engine.extract_radiomic_features(
        patient_id=request.patient_id,
        modality=request.modality,
        anatomical_region=request.anatomical_region,
        lesion_volume_cm3=request.lesion_volume_cm3,
    )

    repo = RadiogenomicsRepository(db)
    s_info = result["scan"]
    scan = await repo.create_scan(
        patient_id=s_info["patient_id"],
        modality=s_info["modality"],
        anatomical_region=s_info["anatomical_region"],
        voxel_spacing_mm=s_info["voxel_spacing_mm"],
        lesion_volume_cm3=s_info["lesion_volume_cm3"],
        segmentation_mask_status=s_info["segmentation_mask_status"],
    )

    for feat in result["radiomic_features"]:
        await repo.add_radiomic_feature(
            scan_id=scan.id,
            feature_family=feat["family"],
            feature_name=feat["name"],
            feature_value=feat["value"],
            normalized_z_score=feat["z_score"],
        )

    for corr in result["genomic_correlations"]:
        await repo.add_genomic_correlation(
            scan_id=scan.id,
            predicted_genomic_alteration=corr["predicted_genomic_alteration"],
            prediction_probability=corr["prediction_probability"],
            feature_importance_json=corr["feature_importance"],
            clinical_significance=corr["clinical_significance"],
        )

    saved = await repo.get_scan(scan.id)
    return {
        "status": "success",
        "id": scan.id,
        "patient_id": scan.patient_id,
        "modality": scan.modality,
        "anatomical_region": scan.anatomical_region,
        "radiomic_features_count": len(saved.radiomic_features if saved else []),
        "genomic_correlations_count": len(saved.genomic_correlations if saved else []),
    }


@router.get("/scans")
async def list_radiogenomics_scans(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """List recent 3D volumetric radiogenomics scans."""
    repo = RadiogenomicsRepository(db)
    scans = await repo.list_scans(limit=limit)
    return [
        {
            "id": s.id,
            "patient_id": s.patient_id,
            "modality": s.modality,
            "anatomical_region": s.anatomical_region,
            "lesion_volume_cm3": s.lesion_volume_cm3,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "radiomic_features_count": len(s.radiomic_features),
            "genomic_correlations_count": len(s.genomic_correlations),
        }
        for s in scans
    ]


@router.get("/scans/{scan_id}")
async def get_radiogenomics_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Get full radiomic feature vector and genomic mutation predictions."""
    repo = RadiogenomicsRepository(db)
    scan = await repo.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {
        "id": scan.id,
        "patient_id": scan.patient_id,
        "modality": scan.modality,
        "anatomical_region": scan.anatomical_region,
        "voxel_spacing_mm": scan.voxel_spacing_mm,
        "lesion_volume_cm3": scan.lesion_volume_cm3,
        "radiomic_features": [
            {
                "id": f.id,
                "family": f.feature_family,
                "name": f.feature_name,
                "value": f.feature_value,
                "z_score": f.normalized_z_score,
            }
            for f in scan.radiomic_features
        ],
        "genomic_correlations": [
            {
                "id": c.id,
                "predicted_genomic_alteration": c.predicted_genomic_alteration,
                "prediction_probability": c.prediction_probability,
                "clinical_significance": c.clinical_significance,
            }
            for c in scan.genomic_correlations
        ],
    }
