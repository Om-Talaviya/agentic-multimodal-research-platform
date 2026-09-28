"""Tests for Phase 255: Autonomous Single-Cell Proteomics by Mass Spectrometry (scMS) Carrier Proteome Deconvolution Engine Engine."""

import pytest
from research.orchestration.single_cell_mass_spec_proteomics_engine import SingleCellMassSpecProteomicsEngine


def test_single_cell_mass_spec_proteomics_engine():
    engine = SingleCellMassSpecProteomicsEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-cell-mass-spec-proteomics",
        input_scale=1.0,
    )
    assert getattr(result, "quantified_single_cell_protein_depth") != 0
    assert getattr(result, "carrier_channel_ion_bleed_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
