"""Tests for Phase 414: Autonomous Cryo-FIB Milling & In-Situ Lamella Thickness Optimization Engine."""

import pytest
from research.orchestration.cryo_fib_milling_engine import CryoFibMillingEngine


def test_cryo_fib_milling_engine():
    engine = CryoFibMillingEngine()
    result = engine.analyze(
        target_specimen="Vitreous Cellular Cryo-Lamella",
        analytical_modality="cryo-fib-milling",
        input_scale=1.0,
    )

    assert result.target_specimen == "Vitreous Cellular Cryo-Lamella"
    assert result.confidence_score >= 0.95
    assert result.in_situ_lamella_thickness_nm < 150.0
    assert result.curtaining_artifact_suppression_ratio > 0.90
    assert result.gallium_ion_beam_current_pA > 0.0
    assert result.vitreous_ice_preservation_score > 0.90
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Cryo-FIB Milling" in result.summary_report
