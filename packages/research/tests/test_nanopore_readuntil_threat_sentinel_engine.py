"""Tests for Phase 305: Autonomous In-Silico Nanopore Adaptive Real-Time Selective Sequencing ReadUntil Bio-Threat Sentinel Engine."""

import pytest
from research.orchestration.nanopore_readuntil_threat_sentinel_engine import NanoporeReaduntilThreatSentinelEngine


def test_nanopore_readuntil_threat_sentinel_engine():
    engine = NanoporeReaduntilThreatSentinelEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="nanopore-readuntil-threat-sentinel",
        input_scale=1.0,
    )
    assert getattr(result, "target_pathogen_enrichment_fold") != 0
    assert getattr(result, "real_time_classification_latency_ms") != 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
