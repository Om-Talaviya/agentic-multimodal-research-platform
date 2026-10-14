"""Tests for Phase 513: Autonomous Cross-Species Synthetic Quorum Sensing Interbacterial Commensal Switch Modeler."""

import pytest
from research.orchestration.synthetic_quorum_sensing_cross_species_switch_engine import SyntheticQuorumSensingCrossSpeciesSwitchEngine


def test_synthetic_quorum_sensing_cross_species_switch_engine():
    engine = SyntheticQuorumSensingCrossSpeciesSwitchEngine()
    result = engine.analyze(
        target_specimen="Co-Cultured Synthetic E. coli and B. subtilis Biofilm with AI-2 / CAI-1 Inter-Species Relays",
        analytical_modality="cross-species-quorum-switch",
        input_scale=1.0,
    )

    assert result.target_specimen == "Co-Cultured Synthetic E. coli and B. subtilis Biofilm with AI-2 / CAI-1 Inter-Species Relays"
    assert result.confidence_score >= 0.95
    assert result.interbacterial_signal_induction_threshold_nM != 0.0
    assert result.population_ratio_homeostasis_cv != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Cross-Species Synth" in result.summary_report
