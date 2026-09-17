import pytest
from research.lethality.lethality_engine import SyntheticLethalityEngine

def test_synthetic_lethality_engine():
    engine = SyntheticLethalityEngine()

    # 1. Test Discovery
    partners = engine.discover_synthetic_lethal_partners(
        target_gene="BRCA1",
        tumor_indication="Ovarian Carcinoma",
        ceres_threshold=-0.5,
    )
    assert len(partners) >= 1
    assert any(p["partner_gene"] == "PARP1" for p in partners)
    assert partners[0]["ceres_depmap_delta_score"] < -0.5
    assert partners[0]["synthetic_lethal_p_value"] < 1e-4

    # 2. Test Co-dependency profiles
    profiles = engine.simulate_crispr_dependency_profiles(
        primary_gene="BRCA1",
        partner_gene="PARP1",
        sample_cell_lines_count=5,
    )
    assert len(profiles) == 5
    assert "MDA-MB-436" in [p["cell_line_name"] for p in profiles]
    assert profiles[0]["primary_gene_dependency_score"] < 0.0
