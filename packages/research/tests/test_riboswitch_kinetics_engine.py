import pytest
from research.rna_biology.riboswitch_kinetics_engine import (
    RiboswitchKineticsEngine,
    RiboswitchSimulationInput,
)


def test_riboswitch_kinetics_engine_simulation():
    engine = RiboswitchKineticsEngine()
    result = engine.simulate_kinetic_switch(
        circuit_name="Synthetic FMN Riboswitch Sensor",
        target_ligand="Flavin Mononucleotide (FMN)",
        rna_sequence="GGACUUCGGUCCAGUCCUUGGAACCCGGUUCAUGCCGAAGUCC",
        aptamer_class="FMN Aptamer",
        transcription_speed_nt_per_sec=30.0,
    )

    assert result.circuit_name == "Synthetic FMN Riboswitch Sensor"
    assert result.target_ligand == "Flavin Mononucleotide (FMN)"
    assert result.rna_sequence_length == len("GGACUUCGGUCCAGUCCUUGGAACCCGGUUCAUGCCGAAGUCC")
    assert result.dynamic_range_fold > 0
    assert result.apo_state["minimum_free_energy_mfe"] < 0
    assert result.holo_state["pseudoknot_present"] == "YES"
    assert result.kinetics_profile["equilibrium_dissociation_constant_kd_nm"] == 57.1
    assert len(result.cotranscriptional_trajectory) > 0
    assert len(result.recommendations) == 3
