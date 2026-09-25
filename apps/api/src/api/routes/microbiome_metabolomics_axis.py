"""FastAPI routes for Phase 182: Gut Microbiome-Host Co-Metabolism Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.microbiome_metabolomics_axis_repo import MicrobiomeMetabolomicsAxisRepository
from research.metabolomics.microbiome_metabolomics_axis_engine import MicrobiomeMetabolomicsAxisEngine

router = APIRouter(prefix="/microbiome-metabolomics-axis", tags=["Microbiome Metabolomics Axis"])


class SimulateMicrobiomeRequest(BaseModel):
    name: str = Field(..., example="Cohort MB-9012 High-Fiber Co-Metabolism Profile")
    cohort_sample_id: str = Field(..., example="SMP-MB-9012")
    dietary_fiber_intake_g_day: float = Field(default=32.0, ge=5.0, le=100.0)
    antibiotic_exposure_days: int = Field(default=0, ge=0, le=30)
    prebiotic_inulin_supplement_g: float = Field(default=5.0, ge=0.0, le=30.0)


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_and_persist_microbiome(
    req: SimulateMicrobiomeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = MicrobiomeMetabolomicsAxisEngine()
    result = engine.simulate_microbiome_metabolomics(
        cohort_sample_id=req.cohort_sample_id,
        dietary_fiber_intake_g_day=req.dietary_fiber_intake_g_day,
        antibiotic_exposure_days=req.antibiotic_exposure_days,
        prebiotic_inulin_supplement_g=req.prebiotic_inulin_supplement_g,
    )

    repo = MicrobiomeMetabolomicsAxisRepository(session)
    study = await repo.create_study(
        name=req.name,
        cohort_sample_id=result.cohort_sample_id,
        dietary_fiber_intake_g_day=result.dietary_fiber_intake_g_day,
        firmicutes_bacteroidetes_ratio=result.firmicutes_bacteroidetes_ratio,
        total_scfa_concentration_mm=result.total_scfa_concentration_mm,
        butyrate_acetate_propionate_ratio=result.butyrate_acetate_propionate_ratio,
        gut_barrier_integrity_score=result.gut_barrier_integrity_score,
        secondary_bile_acid_conversion_rate=result.secondary_bile_acid_conversion_rate,
        shannon_diversity_index=result.shannon_diversity_index,
        status="completed",
        parameters={
            "immunometabolic_homeostasis_index": result.immunometabolic_homeostasis_index,
        },
        summary_report=result.metabolic_recommendation,
    )

    for t in result.taxa_abundances:
        await repo.add_taxa_abundance(
            study_id=study.id,
            taxon_name=t.taxon_name,
            phylum=t.phylum,
            relative_abundance_pct=t.relative_abundance_pct,
            butyrate_synthesis_pathway=t.butyrate_synthesis_pathway,
            mucosal_adherence_index=t.mucosal_adherence_index,
        )

    for s in result.scfa_kinetics:
        await repo.add_scfa_kinetic(
            study_id=study.id,
            metabolite_name=s.metabolite_name,
            lumen_concentration_mm=s.lumen_concentration_mm,
            portal_vein_absorption_rate=s.portal_vein_absorption_rate,
            anti_inflammatory_index=s.anti_inflammatory_index,
            gpr41_43_agonist_potency=s.gpr41_43_agonist_potency,
        )

    return {
        "id": str(study.id),
        "name": study.name,
        "cohort_sample_id": study.cohort_sample_id,
        "total_scfa_concentration_mm": study.total_scfa_concentration_mm,
        "gut_barrier_integrity_score": study.gut_barrier_integrity_score,
        "shannon_diversity_index": study.shannon_diversity_index,
        "immunometabolic_homeostasis_index": result.immunometabolic_homeostasis_index,
        "recommendation": result.metabolic_recommendation,
        "taxa_abundances": [
            {
                "taxon_name": ta.taxon_name,
                "phylum": ta.phylum,
                "relative_abundance_pct": ta.relative_abundance_pct,
                "butyrate_synthesis_pathway": ta.butyrate_synthesis_pathway,
                "mucosal_adherence_index": ta.mucosal_adherence_index,
            }
            for ta in result.taxa_abundances
        ],
        "scfa_kinetics": [
            {
                "metabolite_name": sk.metabolite_name,
                "lumen_concentration_mm": sk.lumen_concentration_mm,
                "portal_vein_absorption_rate": sk.portal_vein_absorption_rate,
                "anti_inflammatory_index": sk.anti_inflammatory_index,
            }
            for sk in result.scfa_kinetics
        ],
    }


@router.get("/studies")
async def list_studies(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = MicrobiomeMetabolomicsAxisRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "cohort_sample_id": s.cohort_sample_id,
            "total_scfa_concentration_mm": s.total_scfa_concentration_mm,
            "gut_barrier_integrity_score": s.gut_barrier_integrity_score,
            "shannon_diversity_index": s.shannon_diversity_index,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]