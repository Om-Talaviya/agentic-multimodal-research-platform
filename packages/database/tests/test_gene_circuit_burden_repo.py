import pytest
import pytest_asyncio
from database.models.gene_circuit_burden import DBCircuitBurdenSimulation
from database.repositories.gene_circuit_burden_repo import GeneCircuitBurdenRepository

@pytest.mark.asyncio
async def test_gene_circuit_burden_repository(async_db_session):
    repo = GeneCircuitBurdenRepository(async_db_session)

    # 1. Create simulation
    sim = await repo.create_simulation(
        circuit_name="Toggle-Switch-V3",
        host_organism="E. coli K-12",
        promoter_strength_rpum=1200.0,
        ribosome_allocation_pct=18.5,
        growth_rate_penalty_pct=14.0,
        evolutionary_half_life_generations=42.0,
    )
    assert sim.id is not None
    assert sim.circuit_name == "Toggle-Switch-V3"

    # 2. Add host capacity model
    model = await repo.add_host_capacity_model(
        simulation_id=sim.id,
        free_ribosome_pool_fraction=0.815,
        atp_drain_flux_mmol_gdw_h=3.4,
        chaperone_load_index=0.35,
        metabolic_burden_status="BALANCED",
    )
    assert model.id is not None
    assert model.simulation_id == sim.id

    # 3. Fetch hydrated simulation
    fetched = await repo.get_simulation_by_id(sim.id)
    assert fetched is not None
    assert len(fetched.capacity_models) == 1
    assert fetched.capacity_models[0].metabolic_burden_status == "BALANCED"
