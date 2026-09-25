"""Tests for AlphaFold Complex Docking Repository."""

import pytest
from database.connection import AsyncSession
from database.repositories.alphafold_complex_docking_repo import AlphaFoldComplexRepository


@pytest.mark.asyncio
async def test_alphafold_complex_repo_crud(db_session: AsyncSession) -> None:
    repo = AlphaFoldComplexRepository(db_session)

    study = await repo.create_study(
        study_name="Test PD-1/PD-L1 Docking",
        target_complex_name="PD-1 / PD-L1 Complex",
        chain_a_name="PDCD1_HUMAN",
        chain_b_name="CD274_HUMAN",
        mean_iptm_score=0.89,
        mean_plddt_interface=91.5,
        buried_surface_area_angstrom2=1840.5,
        summary_metrics={"score": 0.89},
        contacts=[
            {
                "chain_a_residue": "Tyr68",
                "chain_b_residue": "Glu121",
                "inter_residue_distance_angstrom": 2.74,
                "predicted_aligned_error_angstrom": 1.45,
                "interaction_type": "salt_bridge",
                "contact_plddt": 93.4,
            }
        ],
        energy_metrics=[
            {
                "energy_component": "Van der Waals Attractive",
                "value_kcal_mol": -48.2,
                "favorable_flag": "FAVORABLE",
            }
        ],
    )

    assert study.id is not None
    assert study.study_name == "Test PD-1/PD-L1 Docking"
    assert len(study.contacts) == 1
    assert len(study.energy_metrics) == 1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.chain_a_name == "PDCD1_HUMAN"

    studies = await repo.list_studies()
    assert len(studies) >= 1

    deleted = await repo.delete_study(study.id)
    assert deleted is True

    empty = await repo.get_study(study.id)
    assert empty is None
