"""Tests for Phase 272: Autonomous High-Throughput Chemoproteomics Activity-Based Protein Profiling (ABPP) Covalent Ligand Screen Engine."""

import pytest
from research.orchestration.chemoproteomics_abpp_covalent_screen_engine import ChemoproteomicsAbppCovalentScreenEngine


def test_chemoproteomics_abpp_covalent_screen_engine():
    engine = ChemoproteomicsAbppCovalentScreenEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="chemoproteomics-abpp-covalent-screen",
        input_scale=1.0,
    )
    assert getattr(result, "proteome_wide_covalent_engagement_selectivity") != 0
    assert getattr(result, "ligandable_cystiene_residue_count") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
