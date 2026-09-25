"""Tests for Phase 182: Gut Microbiome-Host Metabolomics Engine."""

import pytest
from research.metabolomics.microbiome_metabolomics_axis_engine import MicrobiomeMetabolomicsAxisEngine


def test_microbiome_metabolomics_simulation():
    engine = MicrobiomeMetabolomicsAxisEngine()
    result = engine.simulate_microbiome_metabolomics(
        cohort_sample_id="SMP-MB-9012",
        dietary_fiber_intake_g_day=32.0,
        antibiotic_exposure_days=0,
        prebiotic_inulin_supplement_g=5.0,
    )

    assert result.cohort_sample_id == "SMP-MB-9012"
    assert result.total_scfa_concentration_mm > 50.0
    assert result.gut_barrier_integrity_score > 0.7
    assert len(result.taxa_abundances) == 4
    assert len(result.scfa_kinetics) == 3
    assert result.immunometabolic_homeostasis_index > 0.0