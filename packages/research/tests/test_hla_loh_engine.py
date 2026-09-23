import pytest
from research.genomics.hla_loh_engine import (
    HLALOHImmuneEvasionEngine,
    AlleleInput,
)


def test_hla_loh_engine_default():
    engine = HLALOHImmuneEvasionEngine()
    result = engine.evaluate_hla_loh(
        patient_id="PAT_MEL_401",
        tumor_type="Cutaneous Melanoma",
    )

    assert result.patient_id == "PAT_MEL_401"
    assert result.tumor_type == "Cutaneous Melanoma"
    assert result.total_alleles == 6
    assert result.loh_alleles_count >= 1
    assert result.overall_immune_evasion_index > 0
    assert result.neoantigen_presentation_loss_percent > 0
    assert len(result.rescue_strategies) == 3


def test_hla_loh_engine_no_loh():
    engine = HLALOHImmuneEvasionEngine()
    alleles = [
        AlleleInput(hla_gene="HLA-A", allele_name="HLA-A*01:01", baf_tumor=0.50),
        AlleleInput(hla_gene="HLA-A", allele_name="HLA-A*02:01", baf_tumor=0.50),
    ]
    result = engine.evaluate_hla_loh(
        patient_id="PAT_CRC_102",
        tumor_type="Colorectal Cancer",
        alleles=alleles,
    )

    assert result.loh_alleles_count == 0
    assert result.checkpoint_resistance_risk == "Low Resistance / Full HLA Presentation"
