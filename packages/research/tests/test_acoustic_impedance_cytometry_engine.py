"""Tests for Phase 475: Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier."""

import pytest
from research.orchestration.acoustic_impedance_cytometry_engine import AcousticImpedanceCytometryEngine


def test_acoustic_impedance_cytometry_engine():
    engine = AcousticImpedanceCytometryEngine()
    result = engine.analyze(
        target_specimen="High-Throughput Microfluidic Coplanar Electrode Microchannel with Circulating Tumor Cell Suspensions",
        analytical_modality="acoustic-impedance-cytometry",
        input_scale=1.0,
    )

    assert result.target_specimen == "High-Throughput Microfluidic Coplanar Electrode Microchannel with Circulating Tumor Cell Suspensions"
    assert result.confidence_score >= 0.95
    assert result.dielectric_membrane_capacitance_uF_per_cm2 != 0.0
    assert result.cytoplasm_conductivity_S_per_m != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Multiplexed Bio-Aco" in result.summary_report
