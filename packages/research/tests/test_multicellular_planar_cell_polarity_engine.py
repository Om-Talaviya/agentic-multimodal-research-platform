"""Tests for Phase 459: Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine."""

import pytest
from research.orchestration.multicellular_planar_cell_polarity_engine import MulticellularPlanarCellPolarityEngine


def test_multicellular_planar_cell_polarity_engine():
    engine = MulticellularPlanarCellPolarityEngine()
    result = engine.analyze(
        target_specimen="Engineered Epithelial Monolayer with Frizzled-6/Vangl2 Core Protein Polarized Ensembles",
        analytical_modality="planar-cell-polarity-segregation",
        input_scale=1.0,
    )

    assert result.target_specimen == "Engineered Epithelial Monolayer with Frizzled-6/Vangl2 Core Protein Polarized Ensembles"
    assert result.confidence_score >= 0.95
    assert result.asymmetric_crescent_enrichment_ratio != 0.0
    assert result.nematic_order_director_coherence != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synthetic Multicell" in result.summary_report
