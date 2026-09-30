"""Tests for Phase 395: Ultra-High Throughput Digital Droplet PCR Copy Number Variation Engine Engine."""

import pytest
from research.orchestration.microfluidic_droplet_pcr_engine import MicrofluidicDropletPcrEngine


def test_microfluidic_droplet_pcr_engine():
    engine = MicrofluidicDropletPcrEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="microfluidic-droplet-pcr",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "droplet_generation_monodispersity_cv_pct") > 0
    assert getattr(result, "cnv_absolute_quantification_precision_pct") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 395" in result.summary_report
