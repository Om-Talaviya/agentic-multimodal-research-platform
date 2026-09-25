"""FastAPI routes for Phase 178: ADC DAR Optimization & Aggregation Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.adc_dar_optimization_repo import ADCDAROptimizationRepository
from research.biologics.adc_dar_optimization_engine import ADCDAROptimizationEngine

router = APIRouter(prefix="/adc-dar-optimization", tags=["ADC DAR Optimization"])


class SimulateDARRequest(BaseModel):
    name: str = Field(..., example="Trastuzumab-MMAE Phase 178 Optimization")
    antibody_name: str = Field(..., example="Trastuzumab (anti-HER2 IgG1)")
    payload_name: str = Field(..., example="Monomethyl Auristatin E (MMAE)")
    target_dar: float = Field(default=4.0, ge=1.0, le=8.0)
    linker_type: str = Field(default="cleavable_val_cit")
    conjugation_chemistry: str = Field(default="cysteine_maleimide")
    payload_logp: float = Field(default=2.8)
    reaction_stoichiometry: float = Field(default=4.5, ge=1.0, le=10.0)


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_and_persist_dar(
    req: SimulateDARRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = ADCDAROptimizationEngine()
    result = engine.simulate_dar_optimization(
        antibody_name=req.antibody_name,
        payload_name=req.payload_name,
        target_dar=req.target_dar,
        linker_type=req.linker_type,
        conjugation_chemistry=req.conjugation_chemistry,
        payload_logp=req.payload_logp,
        reaction_stoichiometry=req.reaction_stoichiometry,
    )

    repo = ADCDAROptimizationRepository(session)
    study = await repo.create_study(
        name=req.name,
        antibody_name=result.antibody_name,
        payload_name=result.payload_name,
        linker_type=result.linker_type,
        conjugation_chemistry=result.conjugation_chemistry,
        target_dar=result.target_dar,
        calculated_mean_dar=result.calculated_mean_dar,
        aggregation_propensity_score=result.aggregation_propensity_score,
        hydrophobicity_index=result.hydrophobicity_index,
        unconjugated_antibody_pct=result.unconjugated_antibody_pct,
        high_dar_overload_pct=result.high_dar_overload_pct,
        status="completed",
        parameters={
            "payload_logp": req.payload_logp,
            "reaction_stoichiometry": req.reaction_stoichiometry,
            "therapeutic_index_multiplier": result.therapeutic_index_multiplier,
        },
        summary_report=result.optimization_recommendation,
    )

    for item in result.species_distribution:
        await repo.add_species_distribution(
            study_id=study.id,
            dar_species=item.dar_species,
            molar_fraction=item.molar_fraction,
            retention_time_min=item.retention_time_min,
            mass_shift_da=item.mass_shift_da,
            relative_clearance_rate=item.relative_clearance_rate,
        )

    for k in result.aggregation_kinetics:
        await repo.add_aggregation_metric(
            study_id=study.id,
            incubation_hours=k.incubation_hours,
            monomer_percentage=k.monomer_percentage,
            high_molecular_weight_pct=k.high_molecular_weight_pct,
            low_molecular_weight_pct=k.low_molecular_weight_pct,
            turbidity_od350=k.turbidity_od350,
        )

    return {
        "id": str(study.id),
        "name": study.name,
        "antibody_name": study.antibody_name,
        "payload_name": study.payload_name,
        "target_dar": study.target_dar,
        "calculated_mean_dar": study.calculated_mean_dar,
        "aggregation_propensity_score": study.aggregation_propensity_score,
        "hydrophobicity_index": study.hydrophobicity_index,
        "unconjugated_antibody_pct": study.unconjugated_antibody_pct,
        "high_dar_overload_pct": study.high_dar_overload_pct,
        "recommendation": result.optimization_recommendation,
        "therapeutic_index_multiplier": result.therapeutic_index_multiplier,
        "species_distribution": [
            {
                "dar_species": s.dar_species,
                "molar_fraction": s.molar_fraction,
                "retention_time_min": s.retention_time_min,
                "mass_shift_da": s.mass_shift_da,
                "relative_clearance_rate": s.relative_clearance_rate,
            }
            for s in result.species_distribution
        ],
        "aggregation_kinetics": [
            {
                "incubation_hours": ak.incubation_hours,
                "monomer_percentage": ak.monomer_percentage,
                "high_molecular_weight_pct": ak.high_molecular_weight_pct,
                "low_molecular_weight_pct": ak.low_molecular_weight_pct,
                "turbidity_od350": ak.turbidity_od350,
            }
            for ak in result.aggregation_kinetics
        ],
    }


@router.get("/studies")
async def list_studies(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = ADCDAROptimizationRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "antibody_name": s.antibody_name,
            "payload_name": s.payload_name,
            "target_dar": s.target_dar,
            "calculated_mean_dar": s.calculated_mean_dar,
            "aggregation_propensity_score": s.aggregation_propensity_score,
            "hydrophobicity_index": s.hydrophobicity_index,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
