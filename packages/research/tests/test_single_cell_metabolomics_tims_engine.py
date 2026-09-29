"""Tests for Phase 292: Autonomous Single-Cell Metabolomics Trapped Ion Mobility Spectrometry (TIMS) Flux Deconvolution Engine Engine."""

import pytest
from research.orchestration.single_cell_metabolomics_tims_engine import SingleCellMetabolomicsTimsEngine


def test_single_cell_metabolomics_tims_engine():
    engine = SingleCellMetabolomicsTimsEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-cell-metabolomics-tims",
        input_scale=1.0,
    )
    assert getattr(result, "single_cell_metabolite_coverage_depth") != 0
    assert getattr(result, "cellular_atp_adp_energy_charge_ratio") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
