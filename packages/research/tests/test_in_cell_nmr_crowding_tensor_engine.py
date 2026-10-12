"""Tests for Phase 419: Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine."""

import pytest
from research.orchestration.in_cell_nmr_crowding_tensor_engine import InCellNmrCrowdingTensorEngine


def test_in_cell_nmr_crowding_tensor_engine():
    engine = InCellNmrCrowdingTensorEngine()
    result = engine.analyze(
        target_specimen="15N/13C-Enriched Intact E. coli Cytoplasm with Model Protein",
        analytical_modality="in-cell-nmr",
        input_scale=1.0,
    )

    assert result.target_specimen == "15N/13C-Enriched Intact E. coli Cytoplasm with Model Protein"
    assert result.confidence_score >= 0.95
    assert result.chemical_shift_perturbation_ppm > 0.0
    assert result.rotational_correlation_time_ns > 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous In-Cell NMR Macromo" in result.summary_report
