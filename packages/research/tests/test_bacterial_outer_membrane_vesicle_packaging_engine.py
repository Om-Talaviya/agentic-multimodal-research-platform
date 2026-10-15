"""Tests for Phase 530: Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor."""

import pytest
from research.orchestration.bacterial_outer_membrane_vesicle_packaging_engine import BacterialOuterMembraneVesiclePackagingEngine


def test_bacterial_outer_membrane_vesicle_packaging_engine():
    engine = BacterialOuterMembraneVesiclePackagingEngine()
    result = engine.analyze(
        target_specimen="Hyper-Vesiculating Engineered Pseudomonas aeruginosa Strain PAO1 Membrane Fractions",
        analytical_modality="omv-biogenesis-cargo-sorting",
        input_scale=1.0,
    )

    assert result.target_specimen == "Hyper-Vesiculating Engineered Pseudomonas aeruginosa Strain PAO1 Membrane Fractions"
    assert result.confidence_score >= 0.95
    assert result.vesiculation_rate_omv_per_cell_hr != 0.0
    assert result.cargo_virulence_factor_enrichment_ratio != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Bacterial Outer Mem" in result.summary_report
