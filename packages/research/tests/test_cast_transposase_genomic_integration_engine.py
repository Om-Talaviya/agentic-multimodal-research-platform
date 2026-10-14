"""Tests for Phase 501: Autonomous CRISPR-Associated Transposase (CAST) Targeted Large Genomic Cargo Integrator."""

import pytest
from research.orchestration.cast_transposase_genomic_integration_engine import CastTransposaseGenomicIntegrationEngine


def test_cast_transposase_genomic_integration_engine():
    engine = CastTransposaseGenomicIntegrationEngine()
    result = engine.analyze(
        target_specimen="Type V-K CRISPR-Cas12k / TnsA-TnsB-TnsC Transposase Complex with 10kb Cargo Plasmid in Human Cells",
        analytical_modality="cast-transposase-integration",
        input_scale=1.0,
    )

    assert result.target_specimen == "Type V-K CRISPR-Cas12k / TnsA-TnsB-TnsC Transposase Complex with 10kb Cargo Plasmid in Human Cells"
    assert result.confidence_score >= 0.95
    assert result.targeted_insertion_efficiency_pct != 0.0
    assert result.on_target_integration_accuracy_pct != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous CRISPR-Associated T" in result.summary_report
