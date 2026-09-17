import pytest
import pytest_asyncio
from database.models.flow_cytometry import DBFlowCytometryExperiment
from database.repositories.flow_cytometry_repo import FlowCytometryRepository

@pytest.mark.asyncio
async def test_flow_cytometry_repository(async_db_session):
    repo = FlowCytometryRepository(async_db_session)

    # 1. Create experiment
    exp = await repo.create_experiment(
        experiment_name="CAR-T CD4/CD8 Expansion",
        sample_id="SMP-TEST-FLOW-01",
        cell_type="CAR-T",
        total_event_count=50000,
    )
    assert exp.id is not None
    assert exp.sample_id == "SMP-TEST-FLOW-01"

    # 2. Add gating step
    gate = await repo.add_gating_step(
        experiment_id=exp.id,
        gate_name="Lymphocytes",
        x_channel="FSC-A",
        y_channel="SSC-A",
        polygon_vertices_json=[[10000, 5000], [50000, 5000], [50000, 40000], [10000, 40000]],
        gated_event_count=42500,
        population_pct_of_parent=85.0,
        population_pct_of_total=85.0,
    )
    assert gate.id is not None
    assert gate.experiment_id == exp.id

    # 3. Add Z'-factor metric
    z_metric = await repo.add_z_prime_metric(
        experiment_id=exp.id,
        plate_id="PLT-384-TEST",
        positive_control_mean=95.0,
        positive_control_sd=2.1,
        negative_control_mean=4.0,
        negative_control_sd=0.8,
        z_prime_factor=0.82,
        assay_quality_status="EXCELLENT_ASSAY",
    )
    assert z_metric.id is not None

    # 4. Fetch hydrated experiment
    fetched = await repo.get_experiment_by_id(exp.id)
    assert fetched is not None
    assert len(fetched.gates) == 1
    assert len(fetched.z_prime_metrics) == 1
    assert fetched.gates[0].gate_name == "Lymphocytes"
