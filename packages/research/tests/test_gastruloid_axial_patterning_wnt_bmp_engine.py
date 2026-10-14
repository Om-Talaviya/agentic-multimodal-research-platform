"""Tests for Phase 496: Autonomous Synthetic Organogenesis Gastruloid Axial Patterning & Wnt-BMP Morphogenetic Polarization Engine."""

import pytest
from research.orchestration.gastruloid_axial_patterning_wnt_bmp_engine import GastruloidAxialPatterningWntBmpEngine


def test_gastruloid_axial_patterning_wnt_bmp_engine():
    engine = GastruloidAxialPatterningWntBmpEngine()
    result = engine.analyze(
        target_specimen="3D Aggregated Human Embryonic Stem Cell Gastruloids under Chir99021 Pulse Induction",
        analytical_modality="gastruloid-axial-patterning",
        input_scale=1.0,
    )

    assert result.target_specimen == "3D Aggregated Human Embryonic Stem Cell Gastruloids under Chir99021 Pulse Induction"
    assert result.confidence_score >= 0.95
    assert result.anteroposterior_elongation_aspect_ratio != 0.0
    assert result.bra_t_posterior_polarization_fraction != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synthetic Organogen" in result.summary_report
