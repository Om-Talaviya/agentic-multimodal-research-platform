"""Tests for Phase 436: Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine."""

import pytest
from research.orchestration.single_molecule_magnetic_resonance_nv_center_engine import SingleMoleculeNvCenterNmrEngine


def test_single_molecule_magnetic_resonance_nv_center_engine():
    engine = SingleMoleculeNvCenterNmrEngine()
    result = engine.analyze(
        target_specimen="Diamond Nitrogen-Vacancy (NV) Center Nanocrystal with Surface Immobilized Ferritin",
        analytical_modality="nv-center-nanoscale-nmr",
        input_scale=1.0,
    )

    assert result.target_specimen == "Diamond Nitrogen-Vacancy (NV) Center Nanocrystal with Surface Immobilized Ferritin"
    assert result.confidence_score >= 0.95
    assert result.spin_coherence_time_t2_us > 0.0
    assert result.magnetic_sensitivity_nT_per_sqrthz > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Diamond NV-Center N" in result.summary_report
