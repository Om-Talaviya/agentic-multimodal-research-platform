import pytest
from research.chemistry.lnp_encapsulation_engine import (
    LNPEncapsulationEngine,
    LNPFormulationInput,
)


def test_lnp_encapsulation_engine_optimization():
    engine = LNPEncapsulationEngine()
    result = engine.optimize_lnp_formulation(
        formulation_tag="LNP_Lead_01",
        mrna_payload_name="Cas9 mRNA + sgRNA Complex",
        flow_rate_ratio=3.0,
        total_flow_rate_ml_min=12.0,
        np_ratio=6.0,
        ionizable_lipid_mol_percent=50.0,
    )

    assert result.formulation_tag == "LNP_Lead_01"
    assert result.particle_size_z_avg_nm > 50.0
    assert result.polydispersity_index_pdi < 0.15
    assert result.encapsulation_efficiency_percent > 90.0
    assert result.apparent_pka == 6.45
    assert len(result.lipid_composition_breakdown) == 4
    assert len(result.recommendations) == 3
