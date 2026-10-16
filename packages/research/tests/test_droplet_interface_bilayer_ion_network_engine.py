"""Tests for Phase 567: Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator."""

import pytest
from research.orchestration.droplet_interface_bilayer_ion_network_engine import DropletInterfaceBilayerIonNetworkEngine


def test_droplet_interface_bilayer_ion_network_engine():
    engine = DropletInterfaceBilayerIonNetworkEngine()
    result = engine.analyze(
        target_specimen="Aqueous Microdroplets in Oil with Encapsulated Alpha-Hemolysin Ion Channels arranged in a 3D Interfacial Bio-Conductive Lattice",
        analytical_modality="droplet-interface-bilayer-network",
        input_scale=1.0,
    )

    assert result.target_specimen == "Aqueous Microdroplets in Oil with Encapsulated Alpha-Hemolysin Ion Channels arranged in a 3D Interfacial Bio-Conductive Lattice"
    assert result.confidence_score >= 0.95
    assert result.interfacial_bilayer_electrical_capacitance_uf_cm2 != 0.0
    assert result.single_channel_conductance_quantization_ps != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Synthetic Protocell" in result.summary_report
