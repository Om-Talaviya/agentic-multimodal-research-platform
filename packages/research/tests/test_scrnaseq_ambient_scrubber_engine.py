"""Tests for Phase 202: Single-Cell RNA-seq Droplet De-multiplexing & Ambient RNA Scrubber Engine Engine."""

import pytest
from research.genomics.scrnaseq_ambient_scrubber_engine import ScRNASeqAmbientScrubberEngine


def test_scrnaseq_ambient_scrubber_engine():
    engine = ScRNASeqAmbientScrubberEngine()
    result = engine.run_analysis(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="scRNA-seq Ambient RNA Scrubber",
        input_scale=1.0,
    )
    assert getattr(result, "ambient_rna_contamination_fraction") > 0
    assert getattr(result, "doublet_detection_auc") > 0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert result.confidence_score >= 0.95
