"""FastAPI routes for Phase 186: Oncology Radiomics & Habitat Imaging Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.radiomics_deep_phenotyping_repo import RadiomicsDeepPhenotypingRepository
from research.imaging.radiomics_deep_phenotyping_engine import RadiomicsDeepPhenotypingEngine

router = APIRouter(prefix="/radiomics-deep-phenotyping", tags=["Oncology Radiomics & Habitat Imaging"])


class SimulateRadiomicsRequest(BaseModel):
    name: str = Field(..., example="GBM Patient 04 Habitat Radiomics Profiling")
    scan_modality: str = Field(default="Multiparametric MRI (T1c, T2, FLAIR, DWI)")
    tumor_type: str = Field(default="Glioblastoma Multiforme")
    gross_tumor_volume_cm3: float = Field(default=48.5, ge=1.0, le=500.0)
    intratumoral_heterogeneity_input: float = Field(default=0.89, ge=0.0, le=1.0)


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_and_persist_radiomics(
    req: SimulateRadiomicsRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = RadiomicsDeepPhenotypingEngine()
    result = engine.simulate_radiomics_extraction(
        scan_modality=req.scan_modality,
        tumor_type=req.tumor_type,
        gross_tumor_volume_cm3=req.gross_tumor_volume_cm3,
        intratumoral_heterogeneity_input=req.intratumoral_heterogeneity_input,
    )

    repo = RadiomicsDeepPhenotypingRepository(session)
    study = await repo.create_study(
        name=req.name,
        scan_modality=result.scan_modality,
        tumor_type=result.tumor_type,
        gross_tumor_volume_cm3=result.gross_tumor_volume_cm3,
        necrotic_core_fraction=result.necrotic_core_fraction,
        active_rim_fraction=result.active_rim_fraction,
        edema_infiltrative_fraction=result.edema_infiltrative_fraction,
        intratumoral_heterogeneity_index=result.intratumoral_heterogeneity_index,
        predicted_overall_survival_months=result.predicted_overall_survival_months,
        status="completed",
        parameters={
            "imaging_biomarker_score": result.imaging_biomarker_score,
        },
        summary_report=result.radiogenomic_prognostic_summary,
    )

    for h in result.habitat_subregions:
        await repo.add_habitat_subregion(
            study_id=study.id,
            subregion_name=h.subregion_name,
            volume_cm3=h.volume_cm3,
            mean_perfusion_ktrans=h.mean_perfusion_ktrans,
            apparent_diffusion_coefficient_adc=h.apparent_diffusion_coefficient_adc,
            hypoxia_pet_avidity_suv=h.hypoxia_pet_avidity_suv,
        )

    for t in result.texture_features:
        await repo.add_texture_feature(
            study_id=study.id,
            feature_class=t.feature_class,
            feature_name=t.feature_name,
            feature_value=t.feature_value,
            ibsi_compliance_flag=t.ibsi_compliance_flag,
            radiogenomic_weight=t.radiogenomic_weight,
        )

    return {
        "id": str(study.id),
        "name": study.name,
        "scan_modality": study.scan_modality,
        "tumor_type": study.tumor_type,
        "gross_tumor_volume_cm3": study.gross_tumor_volume_cm3,
        "intratumoral_heterogeneity_index": study.intratumoral_heterogeneity_index,
        "predicted_overall_survival_months": study.predicted_overall_survival_months,
        "imaging_biomarker_score": result.imaging_biomarker_score,
        "recommendation": result.radiogenomic_prognostic_summary,
        "habitat_subregions": [
            {
                "subregion_name": hs.subregion_name,
                "volume_cm3": hs.volume_cm3,
                "mean_perfusion_ktrans": hs.mean_perfusion_ktrans,
                "apparent_diffusion_coefficient_adc": hs.apparent_diffusion_coefficient_adc,
                "hypoxia_pet_avidity_suv": hs.hypoxia_pet_avidity_suv,
            }
            for hs in result.habitat_subregions
        ],
        "texture_features": [
            {
                "feature_class": tf.feature_class,
                "feature_name": tf.feature_name,
                "feature_value": tf.feature_value,
                "ibsi_compliance_flag": tf.ibsi_compliance_flag,
            }
            for tf in result.texture_features
        ],
    }


@router.get("/studies")
async def list_studies(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = RadiomicsDeepPhenotypingRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "tumor_type": s.tumor_type,
            "gross_tumor_volume_cm3": s.gross_tumor_volume_cm3,
            "predicted_overall_survival_months": s.predicted_overall_survival_months,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]