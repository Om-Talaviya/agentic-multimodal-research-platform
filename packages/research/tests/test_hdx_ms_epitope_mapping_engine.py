"""Tests for HDX-MS Epitope Mapping Engine."""

import pytest
from research.biophysics.hdx_ms_epitope_mapping_engine import HDXMSEpitopeMappingEngine


def test_hdx_ms_epitope_mapping_engine_analysis() -> None:
    engine = HDXMSEpitopeMappingEngine()
    result = engine.map_epitope_protection(
        study_name="Spike RBD mAb HDX-MS Study",
        target_protein_name="Spike RBD / Neutralizing mAb",
    )

    assert result["study_name"] == "Spike RBD mAb HDX-MS Study"
    assert result["peptides_monitored_count"] == 4
    assert result["mean_deuteration_protection_pct"] > 20.0
    assert len(result["peptides"]) == 4
    assert len(result["hotspots"]) >= 4

    # Check peptide properties
    first_pep = result["peptides"][0]
    assert "peptide_sequence" in first_pep
    assert "delta_deuterium_protection_pct" in first_pep
    assert "confidence_p_value" in first_pep
