import pytest
from research.epigenomics.histone_acetylation_engine import (
    HistoneAcetylationEngine,
    HistoneAcetylationRequestInput,
)


def test_histone_acetylation_engine_simulation():
    engine = HistoneAcetylationEngine()
    result = engine.simulate_acetylation_kinetics(
        locus_name="CDKN1A (p21) Promoter",
        genomic_coordinates="chr6:36644000-36650000",
        cell_line="HCT116 Colorectal Carcinoma",
        hdac_inhibitor="Panobinostat (LBH589)",
        inhibitor_dose_um=1.0,
        treatment_duration_hours=24.0,
    )

    assert result.locus_name == "CDKN1A (p21) Promoter"
    assert result.cell_line == "HCT116 Colorectal Carcinoma"
    assert result.predicted_enhancer_activation_fold > 1.0
    assert result.final_h3k27ac_enrichment > 10.0
    assert len(result.time_series_dynamics) == 5
    assert len(result.enzyme_kinetics) == 2
    assert len(result.recommendations) == 3
