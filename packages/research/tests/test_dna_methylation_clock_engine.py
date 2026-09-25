"""Tests for DNA Methylation Clock Engine."""

import pytest
from research.epigenetics.dna_methylation_clock_engine import DNAMethylationClockEngine


def test_dna_methylation_clock_prediction() -> None:
    engine = DNAMethylationClockEngine()

    res = engine.compute_epigenetic_age(
        study_name="Pilot Longevity Cohort",
        sample_identifier="DONOR-101",
        tissue_type="whole_blood",
        chronological_age=45.0,
    )

    assert res["study_name"] == "Pilot Longevity Cohort"
    assert res["chronological_age"] == 45.0
    assert 20.0 <= res["horvath_predicted_age"] <= 80.0
    assert len(res["cpg_markers"]) == 5
    assert len(res["age_metrics"]) == 3
    assert "biological_age_consensus" in res["summary_metrics"]
