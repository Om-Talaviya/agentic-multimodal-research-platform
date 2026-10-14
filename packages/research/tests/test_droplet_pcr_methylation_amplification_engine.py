"""Tests for Phase 486: Autonomous Microfluidic Droplet PCR Digital Methylation Specific Amplification Modeler."""

import pytest
from research.orchestration.droplet_pcr_methylation_amplification_engine import DropletPcrMethylationAmplificationEngine


def test_droplet_pcr_methylation_amplification_engine():
    engine = DropletPcrMethylationAmplificationEngine()
    result = engine.analyze(
        target_specimen="Bisulfite-Converted ctDNA in 20,000 Microfluidic Fluorinated Oil Picoliter Droplets",
        analytical_modality="droplet-pcr-methylation-amplification",
        input_scale=1.0,
    )

    assert result.target_specimen == "Bisulfite-Converted ctDNA in 20,000 Microfluidic Fluorinated Oil Picoliter Droplets"
    assert result.confidence_score >= 0.95
    assert result.fractional_methylation_abundance_pct != 0.0
    assert result.poisson_droplet_partition_occupancy_lambda != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Microfluidic Drople" in result.summary_report
