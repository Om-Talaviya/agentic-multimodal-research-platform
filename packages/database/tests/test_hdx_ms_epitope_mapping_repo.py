"""Tests for HDX-MS Epitope Mapping Repository."""

import pytest
from database.connection import AsyncSession
from database.repositories.hdx_ms_epitope_mapping_repo import HDXMSEpitopeRepository


@pytest.mark.asyncio
async def test_hdx_ms_epitope_repo_crud(db_session: AsyncSession) -> None:
    repo = HDXMSEpitopeRepository(db_session)

    study = await repo.create_study(
        study_name="Test Spike HDX-MS",
        target_protein_name="Spike RBD / mAb",
        peptides_monitored_count=1,
        mean_deuteration_protection_pct=56.3,
        epitope_region_identified="Residues 486-506",
        summary_metrics={"score": 56.3},
        peptides=[
            {
                "peptide_sequence": "FNCYFPLQSYGFQPTNGVGYQ",
                "start_residue": 486,
                "end_residue": 506,
                "deuterium_uptake_apo_pct": 74.5,
                "deuterium_uptake_bound_pct": 18.2,
                "delta_deuterium_protection_pct": 56.3,
                "confidence_p_value": 0.0001,
            }
        ],
        hotspots=[
            {
                "residue_name": "Tyr489",
                "protection_factor_log2": 4.85,
                "solvent_accessibility_change": "buried_upon_binding",
            }
        ],
    )

    assert study.id is not None
    assert study.study_name == "Test Spike HDX-MS"
    assert len(study.peptides) == 1
    assert len(study.hotspots) == 1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.target_protein_name == "Spike RBD / mAb"

    studies = await repo.list_studies()
    assert len(studies) >= 1

    deleted = await repo.delete_study(study.id)
    assert deleted is True

    empty = await repo.get_study(study.id)
    assert empty is None
