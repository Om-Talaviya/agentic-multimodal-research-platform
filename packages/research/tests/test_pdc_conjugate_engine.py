"""
Engine tests for Phase 165: PDC Conjugate.
"""

from research.therapeutics.pdc_conjugate_engine import PDCConjugateEngine


def test_pdc_conjugate_engine():
    engine = PDCConjugateEngine()
    result = engine.evaluate_pdc_construct(
        pdc_name="NGR-ValAla-MMAE",
        homing_peptide="cNGR",
        linker_type="Val-Ala-PABC",
        payload="MMAE",
    )

    assert result.pdc_name == "NGR-ValAla-MMAE"
    assert result.plasma_stability_half_life_hours >= 72.0
    assert result.tumor_cleavage_rate_kcat_km > 0.0
    assert result.therapeutic_index > 10.0
    assert len(result.cleavage_profiles) > 0
    assert len(result.cathepsin_assays) > 0
    assert len(result.recommendations) >= 2
