"""Tests for Phase 346: Autonomous Pharmacogenomic HLA-Allele Drug Hypersensitivity & Adverse Reaction Profiler Engine."""

import pytest
from research.orchestration.hla_drug_hypersensitivity_profiler_engine import HlaDrugHypersensitivityProfilerEngine


def test_hla_drug_hypersensitivity_profiler_engine():
    engine = HlaDrugHypersensitivityProfilerEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="hla-drug-hypersensitivity",
        input_scale=1.0,
    )
    assert getattr(result, "hla_allele_adverse_hypersensitivity_risk_score") != 0
    assert getattr(result, "altered_peptide_repertoire_binding_affinity_nm") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
