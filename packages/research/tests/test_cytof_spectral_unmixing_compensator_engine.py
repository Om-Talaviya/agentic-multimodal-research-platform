"""Tests for Phase 284: Autonomous In-Silico High-Dimensional CyTOF Spectral Unmixing & Mass Tag Cross-Talk Compensator Engine."""

import pytest
from research.orchestration.cytof_spectral_unmixing_compensator_engine import CytofSpectralUnmixingCompensatorEngine


def test_cytof_spectral_unmixing_compensator_engine():
    engine = CytofSpectralUnmixingCompensatorEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cytof-spectral-unmixing-compensator",
        input_scale=1.0,
    )
    assert getattr(result, "signal_spillover_reduction_ratio_pct") != 0
    assert getattr(result, "single_cell_channel_cross_talk_residual") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
