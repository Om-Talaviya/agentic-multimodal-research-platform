"""Tests for Phase 243: Autonomous Intact-Cell Cellular Thermal Shift Assay (CETSA) & Target Engagement Deconvolution Engine Engine."""

import pytest
from research.orchestration.cellular_thermal_shift_cetsa_engine import CellularThermalShiftCetsaEngine


def test_cellular_thermal_shift_cetsa_engine():
    engine = CellularThermalShiftCetsaEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cellular-thermal-shift-cetsa",
        input_scale=1.0,
    )
    assert getattr(result, "thermal_shift_delta_tm_celsius") != 0
    assert getattr(result, "target_engagement_apparent_ec50_nM") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
