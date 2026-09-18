"""Tests for Synthetic Gene Circuit repository."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.synthetic_gene_circuit_repo import SyntheticGeneCircuitRepository


@pytest.mark.asyncio
async def test_synthetic_gene_circuit_repo_crud(db_session: AsyncSession):
    repo = SyntheticGeneCircuitRepository(db_session)
    ws_id = uuid.uuid4()

    # 1. Create circuit
    circuit = await repo.create_circuit(
        workspace_id=ws_id,
        circuit_name="CRISPR_NOR_Gate_v1",
        logic_function="NOR",
        chassis_organism="Escherichia coli K-12",
        input_signals=["aTc", "IPTG"],
        output_reporter="sfGFP",
        assembly_standard="Golden Gate (MoClo)",
        plasmid_size_bp=5200,
        on_off_dynamic_range=18.4,
        circuit_metadata={"author": "SynBioAgent"},
    )
    assert circuit.id is not None
    assert circuit.circuit_name == "CRISPR_NOR_Gate_v1"
    assert circuit.logic_function == "NOR"

    # 2. Add Gate
    gate = await repo.add_gate(
        circuit_id=circuit.id,
        gate_name="Gate_Tandem_Inverter",
        gate_type="TANDEM_REPRESSION",
        promoter_part="pTet_pLac",
        repressor_activator="TetR_LacI",
        rbs_strength=1.2,
        hill_coefficient_n=2.3,
        kd_dissociation_uM=0.18,
        overhang_5p="GGAG",
        overhang_3p="CGCT",
    )
    assert gate.id is not None
    assert gate.gate_name == "Gate_Tandem_Inverter"

    # 3. Add Kinetics trace
    trace = await repo.add_kinetics_trace(
        circuit_id=circuit.id,
        state_condition="State_[0,0]",
        simulation_duration_min=360.0,
        steady_state_expression_au=120.5,
        response_half_time_min=35.0,
        time_series_data=[{"time_min": 0, "expression_au": 0.0}, {"time_min": 360, "expression_au": 120.5}],
    )
    assert trace.id is not None
    assert trace.state_condition == "State_[0,0]"

    # 4. Retrieve circuit with gates and traces
    fetched_circuit = await repo.get_circuit(circuit.id)
    assert fetched_circuit is not None
    assert len(fetched_circuit.gates) == 1
    assert len(fetched_circuit.kinetics_traces) == 1

    # 5. List circuits
    circuits = await repo.list_circuits(ws_id)
    assert len(circuits) == 1
    assert circuits[0].id == circuit.id
