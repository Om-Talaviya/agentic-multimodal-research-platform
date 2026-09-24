"""
Database repository tests for Phase 163: RNA Thermodynamics.
"""

import pytest
from database.repositories.rna_thermodynamics_repo import RNAThermodynamicsRepository


@pytest.mark.asyncio
async def test_rna_thermodynamics_repo_lifecycle(db_session):
    repo = RNAThermodynamicsRepository(db_session)

    study = await repo.create_study(
        rna_name="Test_SAM_Riboswitch",
        sequence="GGGAUCGCAGUCUCGAGAGUUGCCAAACCAGCAGCAGCGCUCCUUCUGCGAGAUCCC",
        sequence_length=57,
        dot_bracket_structure="((((((((....)))))))).....................................",
        mfe_delta_g_kcal_mol=-18.4,
        ensemble_free_energy_kcal_mol=-19.1,
        ensemble_defect_score=0.045,
        melting_temperature_tm_celsius=74.2,
    )
    assert study.id is not None
    assert study.rna_name == "Test_SAM_Riboswitch"

    bp = await repo.add_base_pair_probability(
        study_id=study.id,
        pos_i=1,
        pos_j=20,
        pairing_probability=0.98,
        base_pair_type="Watson-Crick",
    )
    assert bp.id is not None
    assert bp.pairing_probability == 0.98

    pk = await repo.add_pseudoknot(
        study_id=study.id,
        stem1_range="1-8",
        stem2_range="21-28",
        loop_topology="H-type Pseudoknot",
        pseudoknot_stability_delta_g_kcal_mol=-4.2,
    )
    assert pk.id is not None
    assert pk.loop_topology == "H-type Pseudoknot"

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert len(fetched.base_pairs) == 1
    assert len(fetched.pseudoknots) == 1
