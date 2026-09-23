"""Tests for Phase 131 BiocomputerLogicRepository."""

import pytest
from database.repositories.biocomputer_logic_repo import BiocomputerLogicRepository


@pytest.mark.asyncio
async def test_biocomputer_logic_repo_lifecycle(db_session):
    repo = BiocomputerLogicRepository(db_session)

    # 1. Create circuit
    circuit = await repo.create_circuit(
        circuit_name="HeLa_HighPrecision_Classifier_v4",
        target_cell_type="Cervical Carcinoma (HeLa)",
        logic_expression="(miR-21 AND NOT miR-141) AND (EpCAM OR Myc)",
        truth_table={
            "inputs": ["miR-21", "miR-141", "EpCAM", "Myc"],
            "positive_states": ["1010", "1011", "1001"],
        },
        gate_count=4,
        noise_margin_db=16.8,
        metadata_json={"chassis": "Human HEK293T / HeLa"},
    )
    assert circuit.id is not None
    assert circuit.circuit_name == "HeLa_HighPrecision_Classifier_v4"
    assert circuit.gate_count == 4

    # 2. Add logic gates
    gate1 = await repo.add_logic_gate(
        circuit_id=circuit.id,
        gate_id="Gate_01_NOT_141",
        gate_type="NOT",
        promoter_repressor_pair="pLacO-LacI_LVA",
        km_uM=1.8,
        hill_n=3.1,
        signal_delay_mins=35.0,
        state_high_output_rfu=5200.0,
        state_low_output_rfu=85.0,
    )
    gate2 = await repo.add_logic_gate(
        circuit_id=circuit.id,
        gate_id="Gate_02_AND_Core",
        gate_type="AND",
        promoter_repressor_pair="pTetO-TetR_SplitGal4",
        km_uM=2.2,
        hill_n=2.9,
        signal_delay_mins=48.0,
        state_high_output_rfu=4900.0,
        state_low_output_rfu=110.0,
    )
    assert gate1.id is not None
    assert gate2.gate_type == "AND"

    # 3. Add cellular classifier
    classifier = await repo.add_classifier(
        circuit_id=circuit.id,
        classifier_name="Cancerous_Cell_Selective_Apoptosis",
        input_biomarkers=["miR-21", "miR-141", "EpCAM", "Myc"],
        output_payload="tBid_Apoptosis_Inducer",
        classification_accuracy=0.974,
        false_positive_rate=0.021,
        auc_roc=0.991,
    )
    assert classifier.id is not None
    assert classifier.output_payload == "tBid_Apoptosis_Inducer"

    # 4. Fetch circuit
    fetched = await repo.get_circuit(circuit.id)
    assert fetched is not None
    assert len(fetched.gates) == 2
    assert len(fetched.classifiers) == 1
    assert fetched.noise_margin_db == 16.8

    # 5. List circuits
    circuits = await repo.list_circuits(limit=10)
    assert len(circuits) >= 1
