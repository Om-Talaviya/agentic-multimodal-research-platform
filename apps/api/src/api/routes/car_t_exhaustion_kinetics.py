"""FastAPI routes for Phase 183: CAR-T Exhaustion & Persistence Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.car_t_exhaustion_kinetics_repo import CARTExhaustionKineticsRepository
from research.immunology.car_t_exhaustion_kinetics_engine import CARTExhaustionKineticsEngine

router = APIRouter(prefix="/car-t-exhaustion-kinetics", tags=["CAR-T Exhaustion Kinetics"])


class SimulateCARTRequest(BaseModel):
    name: str = Field(..., example="anti-CD19-41BBz Tscm Persistence Analysis")
    car_construct_name: str = Field(..., example="anti-CD19-41BBz")
    costimulatory_domain: str = Field(default="4-1BB")
    antigen_density: float = Field(default=15000.0, ge=500.0, le=100000.0)
    tonic_signaling_level: str = Field(default="low")
    il2_il15_priming_ratio: float = Field(default=2.5, ge=0.5, le=10.0)


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def simulate_and_persist_car_t(
    req: SimulateCARTRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = CARTExhaustionKineticsEngine()
    result = engine.simulate_exhaustion_kinetics(
        car_construct_name=req.car_construct_name,
        costimulatory_domain=req.costimulatory_domain,
        antigen_density=req.antigen_density,
        tonic_signaling_level=req.tonic_signaling_level,
        il2_il15_priming_ratio=req.il2_il15_priming_ratio,
    )

    repo = CARTExhaustionKineticsRepository(session)
    study = await repo.create_study(
        name=req.name,
        car_construct_name=result.car_construct_name,
        costimulatory_domain=result.costimulatory_domain,
        antigen_density_per_tumor_cell=result.antigen_density_per_tumor_cell,
        tonic_signaling_level=result.tonic_signaling_level,
        t_stem_cell_memory_pct=result.t_stem_cell_memory_pct,
        tox_nr4a_epigenetic_exhaustion_score=result.tox_nr4a_epigenetic_exhaustion_score,
        predicted_persistence_half_life_days=result.predicted_persistence_half_life_days,
        in_vivo_antitumor_efficacy_score=result.in_vivo_antitumor_efficacy_score,
        status="completed",
        parameters={
            "memory_fitness_index": result.memory_fitness_index,
        },
        summary_report=result.therapeutic_recommendation,
    )

    for s in result.differentiation_states:
        await repo.add_differentiation_state(
            study_id=study.id,
            state_name=s.state_name,
            population_percentage=s.population_percentage,
            tcf7_expression_level=s.tcf7_expression_level,
            proliferative_capacity_score=s.proliferative_capacity_score,
            cytolytic_granzyme_b_score=s.cytolytic_granzyme_b_score,
        )

    for m in result.checkpoint_markers:
        await repo.add_checkpoint_marker(
            study_id=study.id,
            marker_symbol=m.marker_symbol,
            surface_density_molecules=m.surface_density_molecules,
            epigenetic_chromatin_accessibility_score=m.epigenetic_chromatin_accessibility_score,
            reversibility_potential_pct=m.reversibility_potential_pct,
        )

    return {
        "id": str(study.id),
        "name": study.name,
        "car_construct_name": study.car_construct_name,
        "costimulatory_domain": study.costimulatory_domain,
        "t_stem_cell_memory_pct": study.t_stem_cell_memory_pct,
        "tox_nr4a_epigenetic_exhaustion_score": study.tox_nr4a_epigenetic_exhaustion_score,
        "predicted_persistence_half_life_days": study.predicted_persistence_half_life_days,
        "in_vivo_antitumor_efficacy_score": study.in_vivo_antitumor_efficacy_score,
        "memory_fitness_index": result.memory_fitness_index,
        "recommendation": result.therapeutic_recommendation,
        "differentiation_states": [
            {
                "state_name": ds.state_name,
                "population_percentage": ds.population_percentage,
                "tcf7_expression_level": ds.tcf7_expression_level,
                "proliferative_capacity_score": ds.proliferative_capacity_score,
                "cytolytic_granzyme_b_score": ds.cytolytic_granzyme_b_score,
            }
            for ds in result.differentiation_states
        ],
        "checkpoint_markers": [
            {
                "marker_symbol": cm.marker_symbol,
                "surface_density_molecules": cm.surface_density_molecules,
                "epigenetic_chromatin_accessibility_score": cm.epigenetic_chromatin_accessibility_score,
                "reversibility_potential_pct": cm.reversibility_potential_pct,
            }
            for cm in result.checkpoint_markers
        ],
    }


@router.get("/studies")
async def list_studies(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = CARTExhaustionKineticsRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "car_construct_name": s.car_construct_name,
            "costimulatory_domain": s.costimulatory_domain,
            "t_stem_cell_memory_pct": s.t_stem_cell_memory_pct,
            "predicted_persistence_half_life_days": s.predicted_persistence_half_life_days,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]