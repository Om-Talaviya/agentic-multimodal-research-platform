"""Tests for Phase 402: Liquid Biopsy ctDNA Methylation & Tissue-of-Origin Deconvolver Engine."""

import pytest
from research.orchestration.circulating_tumor_dna_methylation_engine import CirculatingTumorDnaMethylationEngine


def test_circulating_tumor_dna_methylation_engine():
    engine = CirculatingTumorDnaMethylationEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="liquid-biopsy-ctdna-methylation",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "tissue_of_origin_classification_accuracy_pct") > 0
    assert getattr(result, "ctdna_limit_of_detection_allele_fraction_ppm") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 402" in result.summary_report
