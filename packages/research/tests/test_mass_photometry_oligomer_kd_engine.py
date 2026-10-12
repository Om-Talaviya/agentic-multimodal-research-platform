"""Tests for Phase 426: Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator."""

import pytest
from research.orchestration.mass_photometry_oligomer_kd_engine import MassPhotometryOligomerKdEngine


def test_mass_photometry_oligomer_kd_engine():
    engine = MassPhotometryOligomerKdEngine()
    result = engine.analyze(
        target_specimen="Native Macromolecular Assembly on Glass Coverslip Surface",
        analytical_modality="mass-photometry-kd",
        input_scale=1.0,
    )

    assert result.target_specimen == "Native Macromolecular Assembly on Glass Coverslip Surface"
    assert result.confidence_score >= 0.95
    assert result.molecular_mass_kda > 0.0
    assert result.equilibrium_dissociation_constant_nM > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Mass Photometry Mac" in result.summary_report
