"""Tests for Phase 185: Tumor Neoantigen Engine."""

import pytest
from research.immunology.neoantigen_hla_presentation_engine import NeoantigenHLAPresentationEngine


def test_neoantigen_hla_presentation_simulation():
    engine = NeoantigenHLAPresentationEngine()
    result = engine.simulate_neoantigen_presentation(
        patient_tumor_id="TUMOR-MEL-402",
        patient_hla_alleles="HLA-A*02:01, HLA-A*24:02, HLA-B*07:02",
        somatic_mutations_count=45,
    )

    assert result.patient_tumor_id == "TUMOR-MEL-402"
    assert len(result.peptide_candidates) == 3
    assert len(result.hla_predictions) == 3
    assert result.mrna_vaccine_tier1_candidates_count >= 1
    assert result.immunogenic_fitness_score > 0.0