"""Tests for Phase 567: Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator Repo."""

import pytest
from database.repositories.droplet_interface_bilayer_ion_network_repo import DropletInterfaceBilayerIonNetworkRepository


@pytest.mark.asyncio
async def test_droplet_interface_bilayer_ion_network_repository(db_session):
    repo = DropletInterfaceBilayerIonNetworkRepository(db_session)

    study = await repo.create_study(
        name="Study_567_Verification",
        target_specimen="Aqueous Microdroplets in Oil with Encapsulated Alpha-Hemolysin Ion Channels arranged in a 3D Interfacial Bio-Conductive Lattice",
        analytical_modality="droplet-interface-bilayer-network",
        interfacial_bilayer_electrical_capacitance_uf_cm2=0.72,
        single_channel_conductance_quantization_ps=980.0,
        inter_droplet_signal_transmission_speed_mm_s=2.8,
        multi_nodal_droplet_network_stability_hours=96.0,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 567 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_567_Verification"
    assert study.interfacial_bilayer_electrical_capacitance_uf_cm2 == 0.72

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Alpha_Hemolysin_Pore_Interfacial_Lipid_Bilayer_Node",
        profile_category="Primary Step",
        quantitative_value=0.72,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Alpha_Hemolysin_Pore_Interfacial_Lipid_Bilayer_Node"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="interfacial_bilayer_electrical_capacitance_uf_cm2",
        observed_value=0.72,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.72

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_567_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
