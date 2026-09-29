"""Tests for Phase 337: Autonomous High-Dimensional Cytometry (Mass/Spectral CyTOF) Immune Cell Phenotype Clustering Engine Engine."""

import pytest
from research.orchestration.cytof_mass_cytometry_clustering_engine import CytofMassCytometryClusteringEngine


def test_cytof_mass_cytometry_clustering_engine():
    engine = CytofMassCytometryClusteringEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cytof-mass-cytometry",
        input_scale=1.0,
    )
    assert getattr(result, "immune_subpopulation_silhouette_score") != 0
    assert getattr(result, "isotopic_channel_crosstalk_attenuation_pct") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
