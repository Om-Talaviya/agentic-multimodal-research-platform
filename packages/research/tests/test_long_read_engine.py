"""Tests for LongReadGenomicsEngine."""
import pytest
from research.genomics.long_read_engine import LongReadGenomicsEngine


def test_long_read_engine_pacbio():
    engine = LongReadGenomicsEngine()
    result = engine.analyze_sequencing_run(
        sample_name="HG002_PacBio",
        platform="PACBIO_HIFI",
        target_gigabases=40.0,
    )

    assert "run" in result
    assert result["run"]["sample_name"] == "HG002_PacBio"
    assert result["run"]["n50_length_bp"] > 10000
    assert result["run"]["mean_phred_quality"] > 30.0

    assert "structural_variants" in result
    assert len(result["structural_variants"]) >= 4
    types = [sv["sv_type"] for sv in result["structural_variants"]]
    assert "DELETION" in types
    assert "INSERTION" in types

    assert "telomeric_profiles" in result
    assert len(result["telomeric_profiles"]) == 14
    for prof in result["telomeric_profiles"]:
        assert prof["hexamer_motif"] == "TTAGGG"
        assert prof["erosion_hazard_level"] in ["LOW", "MODERATE", "CRITICAL"]


def test_long_read_engine_ont():
    engine = LongReadGenomicsEngine()
    result = engine.analyze_sequencing_run(
        sample_name="HG002_ONT_UltraLong",
        platform="ONT_PROMETHION",
        target_gigabases=80.0,
    )

    assert result["run"]["mean_read_length_bp"] > 20000.0
    assert result["run"]["total_gigabases"] == 80.0
