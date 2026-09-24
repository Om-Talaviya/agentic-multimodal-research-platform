"""
Engine tests for Phase 163: RNA Thermodynamics & MFE Folding.
"""

from research.rna.rna_thermodynamics_engine import RNAThermodynamicsEngine


def test_rna_thermodynamics_engine():
    engine = RNAThermodynamicsEngine()
    result = engine.predict_mfe_structure(
        rna_name="tRNA_Phe_Yeast",
        sequence="GCGGAUUUAGCUCAGUUGGGAGAGCGCCAGACUGAAGAUCUGGAGGUCCUGUGUUCGAUCCACAGAAUUCGCACCA",
        temperature_celsius=37.0,
    )

    assert result.rna_name == "tRNA_Phe_Yeast"
    assert result.sequence_length == len("GCGGAUUUAGCUCAGUUGGGAGAGCGCCAGACUGAAGAUCUGGAGGUCCUGUGUUCGAUCCACAGAAUUCGCACCA")
    assert result.mfe_delta_g_kcal_mol < 0.0
    assert result.melting_temperature_tm_celsius > 0.0
    assert len(result.base_pair_probabilities) > 0
    assert len(result.recommendations) >= 2
