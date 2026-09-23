import pytest
from database.repositories.lnp_encapsulation_repo import LNPEncapsulationRepository


@pytest.mark.asyncio
async def test_lnp_encapsulation_repo_lifecycle(db_session):
    repo = LNPEncapsulationRepository(db_session)

    screen = await repo.create_screen(
        formulation_tag="LNP_Screen_Batch_042",
        mrna_payload_name="SARS-CoV-2 Spike / Flu Bivalent mRNA",
        flow_rate_ratio_aqueous_to_organic=3.0,
        total_flow_rate_ml_min=14.0,
        nitrogen_to_phosphate_np_ratio=6.0,
        hydrodynamic_diameter_pdi=0.07,
        particle_size_z_avg_nm=72.4,
        encapsulation_efficiency_percent=95.4,
    )

    assert screen.id is not None
    assert screen.formulation_tag == "LNP_Screen_Batch_042"

    lipid = await repo.add_lipid_component(
        formulation_id=screen.id,
        lipid_type="Ionizable Lipid (ALC-0315)",
        mol_percent=46.3,
        pka_apparent=6.55,
    )
    assert lipid.mol_percent == 46.3

    metric = await repo.add_efficiency_metric(
        formulation_id=screen.id,
        ribogreen_free_rna_fluorescence=120.0,
        ribogreen_total_rna_fluorescence=2600.0,
        calculated_encapsulation_percent=95.4,
        cryo_tem_morphology="Uniform Multivesicular Lamellae",
    )
    assert metric.calculated_encapsulation_percent == 95.4

    retrieved = await repo.get_screen(screen.id)
    assert retrieved is not None
    assert len(retrieved.lipid_components) == 1
    assert len(retrieved.efficiency_metrics) == 1
