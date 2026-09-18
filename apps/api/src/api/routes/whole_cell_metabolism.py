"""API Routes for Whole-Cell Metabolic Flux Simulation."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.whole_cell_metabolism_repo import WholeCellMetabolicRepository
from research.metabolism.whole_cell_engine import WholeCellMetabolicEngine

router = APIRouter(prefix="/whole-cell", tags=["Whole-Cell Metabolic Simulation"])


class WholeCellSimulateRequest(BaseModel):
    model_id: str = Field(default="iML1515", description="Genome-scale model: iML1515, iMM904, iHsa")
    carbon_source: str = Field(default="GLUCOSE")
    initial_glucose_g_L: float = Field(default=20.0, ge=0.5, le=100.0)
    initial_biomass_g_L: float = Field(default=0.1, ge=0.01, le=10.0)
    simulation_duration_hours: float = Field(default=12.0, ge=1.0, le=72.0)
    time_step_hours: float = Field(default=2.0, ge=0.5, le=6.0)


@router.get("/presets")
async def list_model_presets():
    """List available genome-scale metabolic models."""
    return {"models": WholeCellMetabolicEngine.GENOME_SCALE_MODELS}


@router.post("/simulate", status_code=status.HTTP_201_CREATED)
async def run_whole_cell_simulation(
    request: WholeCellSimulateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Run dynamic FBA simulation and persist metabolic fluxes and growth curves."""
    engine = WholeCellMetabolicEngine()
    result = engine.run_dynamic_fba(
        model_id=request.model_id,
        carbon_source=request.carbon_source,
        initial_glucose_g_L=request.initial_glucose_g_L,
        initial_biomass_g_L=request.initial_biomass_g_L,
        simulation_duration_hours=request.simulation_duration_hours,
        time_step_hours=request.time_step_hours,
    )

    repo = WholeCellMetabolicRepository(db)
    m_info = result["model"]
    model = await repo.create_model(
        organism_name=m_info["organism_name"],
        genome_scale_model_id=m_info["genome_scale_model_id"],
        total_reactions_count=m_info["total_reactions_count"],
        total_metabolites_count=m_info["total_metabolites_count"],
        total_genes_count=m_info["total_genes_count"],
        biomass_objective_reaction=m_info["biomass_objective_reaction"],
        carbon_source=m_info["carbon_source"],
        optimal_growth_rate_hr1=m_info["optimal_growth_rate_hr1"],
    )

    for flux in result["flux_states"]:
        await repo.add_flux_state(
            model_id=model.id,
            reaction_id=flux["reaction_id"],
            reaction_name=flux["reaction_name"],
            flux_value_mmol_gDW_hr=flux["flux_value_mmol_gDW_hr"],
            lower_bound=flux["lower_bound"],
            upper_bound=flux["upper_bound"],
            subsystem=flux["subsystem"],
            shadow_price=flux["shadow_price"],
        )

    for trace in result["simulation_traces"]:
        await repo.add_simulation_trace(
            model_id=model.id,
            time_point_hours=trace["time_point_hours"],
            biomass_concentration_g_L=trace["biomass_concentration_g_L"],
            glucose_concentration_g_L=trace["glucose_concentration_g_L"],
            acetate_concentration_g_L=trace["acetate_concentration_g_L"],
            oxygen_uptake_rate=trace["oxygen_uptake_rate"],
            atp_yield_mol_per_mol_glucose=trace["atp_yield_mol_per_mol_glucose"],
        )

    saved = await repo.get_model(model.id)
    return {
        "status": "success",
        "id": model.id,
        "organism": model.organism_name,
        "model_id": model.genome_scale_model_id,
        "growth_rate_hr1": model.optimal_growth_rate_hr1,
        "flux_states_count": len(saved.flux_states if saved else []),
        "simulation_traces_count": len(saved.simulation_traces if saved else []),
    }


@router.get("/models")
async def list_whole_cell_simulations(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """List recent whole-cell metabolic simulation models."""
    repo = WholeCellMetabolicRepository(db)
    models = await repo.list_models(limit=limit)
    return [
        {
            "id": m.id,
            "organism_name": m.organism_name,
            "genome_scale_model_id": m.genome_scale_model_id,
            "carbon_source": m.carbon_source,
            "optimal_growth_rate_hr1": m.optimal_growth_rate_hr1,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "flux_states_count": len(m.flux_states),
            "simulation_traces_count": len(m.simulation_traces),
        }
        for m in models
    ]


@router.get("/models/{model_id}")
async def get_whole_cell_model(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Get complete metabolic flux states and time-series simulation trace."""
    repo = WholeCellMetabolicRepository(db)
    model = await repo.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Whole-cell model not found")

    return {
        "id": model.id,
        "organism_name": model.organism_name,
        "genome_scale_model_id": model.genome_scale_model_id,
        "total_reactions_count": model.total_reactions_count,
        "total_metabolites_count": model.total_metabolites_count,
        "total_genes_count": model.total_genes_count,
        "biomass_objective_reaction": model.biomass_objective_reaction,
        "carbon_source": model.carbon_source,
        "optimal_growth_rate_hr1": model.optimal_growth_rate_hr1,
        "flux_states": [
            {
                "id": f.id,
                "reaction_id": f.reaction_id,
                "reaction_name": f.reaction_name,
                "flux_value_mmol_gDW_hr": f.flux_value_mmol_gDW_hr,
                "subsystem": f.subsystem,
                "shadow_price": f.shadow_price,
            }
            for f in model.flux_states
        ],
        "simulation_traces": [
            {
                "id": t.id,
                "time_point_hours": t.time_point_hours,
                "biomass_concentration_g_L": t.biomass_concentration_g_L,
                "glucose_concentration_g_L": t.glucose_concentration_g_L,
                "acetate_concentration_g_L": t.acetate_concentration_g_L,
                "oxygen_uptake_rate": t.oxygen_uptake_rate,
            }
            for t in model.simulation_traces
        ],
    }
