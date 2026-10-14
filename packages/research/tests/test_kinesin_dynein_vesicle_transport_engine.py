"""Tests for Phase 474: Autonomous Subcellular Microtubule Kinesin-Dynein Tug-of-War Vesicle Transport Modeler."""

import pytest
from research.orchestration.kinesin_dynein_vesicle_transport_engine import KinesinDyneinVesicleTransportEngine


def test_kinesin_dynein_vesicle_transport_engine():
    engine = KinesinDyneinVesicleTransportEngine()
    result = engine.analyze(
        target_specimen="Vitrified Axonal Microtubule Filament with Dual Kinesin-1 and Cytoplasmic Dynein Vesicle Cargo",
        analytical_modality="kinesin-dynein-tug-of-war",
        input_scale=1.0,
    )

    assert result.target_specimen == "Vitrified Axonal Microtubule Filament with Dual Kinesin-1 and Cytoplasmic Dynein Vesicle Cargo"
    assert result.confidence_score >= 0.95
    assert result.anterograde_retrograde_velocity_ratio != 0.0
    assert result.motor_detachment_stall_force_pN != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Subcellular Microtu" in result.summary_report
