"""Tests for CADD Variant Pathogenicity Engine."""

import pytest
from research.genomics.cadd_variant_pathogenicity_engine import CADDVariantPathogenicityEngine


def test_cadd_variant_engine_scoring() -> None:
    engine = CADDVariantPathogenicityEngine()

    res = engine.calculate_cadd_scores(
        study_name="TP53 Hotspot Analysis",
        genome_build="GRCh38",
        target_gene="TP53",
    )

    assert res["study_name"] == "TP53 Hotspot Analysis"
    assert res["variant_count"] == 5
    assert res["mean_phred_score"] > 15.0
    assert len(res["variants"]) == 5
    assert len(res["ensemble_scores"]) == 4
    assert res["variants"][0]["pathogenicity_verdict"] == "pathogenic"
