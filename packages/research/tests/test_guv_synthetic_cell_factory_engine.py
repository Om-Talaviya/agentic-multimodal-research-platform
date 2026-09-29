"""Tests for Phase 303: Autonomous Cell-Free Protein Synthesis Compartmentalized Giant Unilamellar Vesicle (GUV) Synthetic Cell Factory Engine."""

import pytest
from research.orchestration.guv_synthetic_cell_factory_engine import GuvSyntheticCellFactoryEngine


def test_guv_synthetic_cell_factory_engine():
    engine = GuvSyntheticCellFactoryEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="guv-synthetic-cell-factory",
        input_scale=1.0,
    )
    assert getattr(result, "intra_vesicle_protein_yield_uM") != 0
    assert getattr(result, "membrane_integrity_retention_half_life_days") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
