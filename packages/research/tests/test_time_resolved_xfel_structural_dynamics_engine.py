"""Tests for Phase 557: Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine."""

import pytest
from research.orchestration.time_resolved_xfel_structural_dynamics_engine import TimeResolvedXfelStructuralDynamicsEngine


def test_time_resolved_xfel_structural_dynamics_engine():
    engine = TimeResolvedXfelStructuralDynamicsEngine()
    result = engine.analyze(
        target_specimen="Photoactive Yellow Protein (PYP) Microcrystals probed by 10-fs X-ray Pulses at LCLS-II after 450nm Laser Photolysis",
        analytical_modality="time-resolved-xfel-dynamics",
        input_scale=1.0,
    )

    assert result.target_specimen == "Photoactive Yellow Protein (PYP) Microcrystals probed by 10-fs X-ray Pulses at LCLS-II after 450nm Laser Photolysis"
    assert result.confidence_score >= 0.95
    assert result.femtosecond_temporal_resolution_fs != 0.0
    assert result.chromophore_trans_to_cis_isomerization_time_ps != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Time-Resolved Femto" in result.summary_report
