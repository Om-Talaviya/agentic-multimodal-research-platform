"""Tests for Phase 466: Autonomous Optogenetic Rheotaxis Bacterial Micro-Swarm Bio-Convective Flow Modeler."""

import pytest
from research.orchestration.optogenetic_rheotaxis_micro_swarm_engine import OptogeneticRheotaxisMicroSwarmEngine


def test_optogenetic_rheotaxis_micro_swarm_engine():
    engine = OptogeneticRheotaxisMicroSwarmEngine()
    result = engine.analyze(
        target_specimen="Engineered B. subtilis Swarm with Light-Gated Flagellar Torque Switch in Laminar Microfluidic Channel",
        analytical_modality="optogenetic-rheotaxis-swarm",
        input_scale=1.0,
    )

    assert result.target_specimen == "Engineered B. subtilis Swarm with Light-Gated Flagellar Torque Switch in Laminar Microfluidic Channel"
    assert result.confidence_score >= 0.95
    assert result.micro_swarm_upstream_drift_velocity_um_s != 0.0
    assert result.bioconvective_plume_wavelength_um != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Optogenetic Rheotax" in result.summary_report
