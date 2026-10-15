"""Tests for Phase 534: Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter."""

import pytest
from research.orchestration.microfluidic_cell_sorting_dielectrophoresis_engine import MicrofluidicCellSortingDielectrophoresisEngine


def test_microfluidic_cell_sorting_dielectrophoresis_engine():
    engine = MicrofluidicCellSortingDielectrophoresisEngine()
    result = engine.analyze(
        target_specimen="Microfluidic Channel with 3D Quadrupole Electrodes for Label-Free Isolation of Metastatic Breast CTCs",
        analytical_modality="microfluidic-dep-cell-sorting",
        input_scale=1.0,
    )

    assert result.target_specimen == "Microfluidic Channel with 3D Quadrupole Electrodes for Label-Free Isolation of Metastatic Breast CTCs"
    assert result.confidence_score >= 0.95
    assert result.target_cell_recovery_purity_pct != 0.0
    assert result.sorting_throughput_cells_per_s != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous High-Throughput 3D " in result.summary_report
