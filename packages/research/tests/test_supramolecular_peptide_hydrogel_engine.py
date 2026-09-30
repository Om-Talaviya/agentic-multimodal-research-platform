"""Tests for Phase 403: Autonomous Injectable Supramolecular Peptide Shear-Thinning Biomaterial Modeler Engine."""

import pytest
from research.orchestration.supramolecular_peptide_hydrogel_engine import SupramolecularPeptideHydrogelEngine


def test_supramolecular_peptide_hydrogel_engine():
    engine = SupramolecularPeptideHydrogelEngine()
    result = engine.analyze(
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="supramolecular-peptide-hydrogel",
        input_scale=1.0,
    )

    assert result.target_specimen == "Human Patient Cohort Sample"
    assert result.confidence_score >= 0.95
    assert getattr(result, "storage_modulus_g_prime_plateau_pascals") > 0
    assert getattr(result, "shear_thinning_recovery_half_time_seconds") > 0
    assert len(result.item_profiles) == 3
    assert len(result.metric_traces) == 3
    assert "Phase 403" in result.summary_report
