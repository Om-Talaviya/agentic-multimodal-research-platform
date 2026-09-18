"""Tests for WholeCellMetabolicRepository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.whole_cell_metabolism_repo import WholeCellMetabolicRepository


@pytest.mark.asyncio
async def test_whole_cell_repo_lifecycle(db_session: AsyncSession):
    repo = WholeCellMetabolicRepository(db_session)

    # 1. Create Model
    model = await repo.create_model(
        organism_name="Escherichia coli K-12 MG1655",
        genome_scale_model_id="iML1515",
        total_reactions_count=2712,
        total_metabolites_count=1877,
        total_genes_count=1515,
        biomass_objective_reaction="BIOMASS_Ec_iML1515_core_75p37M",
        carbon_source="GLUCOSE",
        optimal_growth_rate_hr1=0.875,
    )
    assert model.id is not None
    assert model.genome_scale_model_id == "iML1515"
    assert model.optimal_growth_rate_hr1 == 0.875

    # 2. Add Flux State
    flux = await repo.add_flux_state(
        model_id=model.id,
        reaction_id="EX_glc__D_e",
        reaction_name="D-Glucose Exchange",
        flux_value_mmol_gDW_hr=-10.0,
        subsystem="GLYCOLYSIS",
        shadow_price=-0.08,
    )
    assert flux.id is not None
    assert flux.reaction_id == "EX_glc__D_e"

    # 3. Add Simulation Trace
    trace = await repo.add_simulation_trace(
        model_id=model.id,
        time_point_hours=2.0,
        biomass_concentration_g_L=0.25,
        glucose_concentration_g_L=18.5,
        acetate_concentration_g_L=0.05,
        oxygen_uptake_rate=18.2,
        atp_yield_mol_per_mol_glucose=26.4,
    )
    assert trace.id is not None
    assert trace.biomass_concentration_g_L == 0.25

    # 4. Fetch Model
    fetched = await repo.get_model(model.id)
    assert fetched is not None
    assert len(fetched.flux_states) == 1
    assert len(fetched.simulation_traces) == 1

    # 5. List Models
    models = await repo.list_models()
    assert len(models) >= 1
