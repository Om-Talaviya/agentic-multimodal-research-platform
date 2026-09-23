"""Tests for Phase 131 BiocomputerLogicEngine."""

import pytest
from research.synthetic.biocomputer_logic_engine import (
    BiocomputerLogicEngine,
    BiomarkerThreshold,
)


def test_biocomputer_logic_simulation_flow():
    engine = BiocomputerLogicEngine()

    biomarkers = [
        BiomarkerThreshold(marker_name="miR-21", target_state=True, threshold_rfu=1200.0),
        BiomarkerThreshold(marker_name="miR-141", target_state=False, threshold_rfu=800.0),
        BiomarkerThreshold(marker_name="EpCAM", target_state=True, threshold_rfu=2500.0),
    ]

    res = engine.simulate_circuit(
        circuit_name="Hepatoma_MultiMarker_Classifier",
        target_cell_type="Hepatocellular Carcinoma",
        biomarkers=biomarkers,
        logic_expression="(miR-21 AND NOT miR-141) AND EpCAM",
        payload="Diphtheria_Toxin_A_Actuator",
    )

    assert res.circuit_name == "Hepatoma_MultiMarker_Classifier"
    assert res.truth_table["total_states"] == 8
    assert len(res.truth_table["states"]) == 8
    assert len(res.gates) == 3
    assert res.classifier_metrics["classification_accuracy"] >= 0.90
    assert res.classifier_metrics["auc_roc"] >= 0.95
    assert len(res.signal_transfer_curve) == 10
    assert len(res.recommendations) > 0
