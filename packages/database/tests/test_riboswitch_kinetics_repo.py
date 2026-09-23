import pytest
from database.repositories.riboswitch_kinetics_repo import RiboswitchKineticsRepository


@pytest.mark.asyncio
async def test_riboswitch_kinetics_repo_lifecycle(db_session):
    repo = RiboswitchKineticsRepository(db_session)

    circuit = await repo.create_circuit(
        circuit_name="Synthetic Theophylline ON-Switch",
        target_ligand="Theophylline",
        rna_sequence="GGGAUACCAGCCGAAAGGCCCUUGGCAGCGUCC",
        aptamer_class="Synthetic Theophylline Aptamer",
        expression_platform_type="Hammerhead Ribozyme Cleavage",
        dynamic_range_fold=9.4,
        switching_free_energy_delta_g=-16.8,
    )

    assert circuit.id is not None
    assert circuit.circuit_name == "Synthetic Theophylline ON-Switch"

    struct_apo = await repo.add_secondary_structure(
        circuit_id=circuit.id,
        state_name="Apo (OFF)",
        dot_bracket_notation="(((((((....))))))).......(((((.....)))))",
        minimum_free_energy_mfe=-22.4,
        ensemble_defect_percent=3.8,
    )
    assert struct_apo.state_name == "Apo (OFF)"

    profile = await repo.add_kinetics_profile(
        circuit_id=circuit.id,
        association_rate_k_on=1.2e5,
        dissociation_rate_k_off=0.012,
        equilibrium_dissociation_constant_kd_nm=100.0,
        cotranscriptional_folding_window_nt=40,
    )
    assert profile.equilibrium_dissociation_constant_kd_nm == 100.0

    retrieved = await repo.get_circuit(circuit.id)
    assert retrieved is not None
    assert len(retrieved.secondary_structures) == 1
    assert len(retrieved.ligand_kinetics) == 1
