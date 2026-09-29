"""Tests for Phase 334: Autonomous Single-Cell Proteomic Thermal Shift Assay (PISA) Drug-Target Engagement Decoupler Engine."""

import pytest
from research.orchestration.pisa_thermal_shift_assay_engine import PisaThermalShiftAssayEngine


def test_pisa_thermal_shift_assay_engine():
    engine = PisaThermalShiftAssayEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="pisa-thermal-shift",
        input_scale=1.0,
    )
    assert getattr(result, "thermal_melting_point_shift_delta_tm_celsius") != 0
    assert getattr(result, "target_engagement_apparent_kd_nm") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
