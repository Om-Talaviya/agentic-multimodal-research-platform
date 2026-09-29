"""Tests for Phase 278: Autonomous De-Novo Peptide-HLA Class I Neoantigen Presentation & TCR Repertoire Cross-Reactivity Predictor Engine."""

import pytest
from research.orchestration.pep_hla_neoantigen_presentation_engine import PepHlaNeoantigenPresentationEngine


def test_pep_hla_neoantigen_presentation_engine():
    engine = PepHlaNeoantigenPresentationEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="pep-hla-neoantigen-presentation",
        input_scale=1.0,
    )
    assert getattr(result, "neoantigen_surface_presentation_probability") != 0
    assert getattr(result, "tcr_cross_reactive_self_similarity_penalty") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
