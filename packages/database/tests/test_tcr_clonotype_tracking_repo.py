"""Tests for TCR/BCR Clonotype Tracking Repository."""

import pytest
from database.connection import AsyncSession
from database.repositories.tcr_clonotype_tracking_repo import TCRClonotypeRepository


@pytest.mark.asyncio
async def test_tcr_clonotype_repo_crud(db_session: AsyncSession) -> None:
    repo = TCRClonotypeRepository(db_session)

    study = await repo.create_study(
        study_name="Test TCR Repertoire",
        sample_source="TIL",
        repertoire_type="TCR_alpha_beta",
        cell_count=2000,
        shannon_entropy=3.85,
        gini_simpson_index=0.79,
        clonality_score=0.42,
        clonotypes=[
            {
                "cdr3_amino_acid": "CASSLAGGYEQYF",
                "v_gene": "TRBV5-1",
                "j_gene": "TRBJ2-7",
                "clone_frequency": 0.25,
                "expansion_status": "hyperexpanded",
                "antigen_specificity": "Viral_Epitope",
            }
        ],
        diversity_metrics=[
            {
                "metric_name": "Shannon Entropy",
                "metric_value": 3.85,
                "metric_category": "entropy",
            }
        ],
    )

    assert study.id is not None
    assert study.study_name == "Test TCR Repertoire"
    assert len(study.clonotypes) == 1
    assert len(study.diversity_metrics) == 1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.sample_source == "TIL"

    studies = await repo.list_studies()
    assert len(studies) >= 1

    deleted = await repo.delete_study(study.id)
    assert deleted is True

    empty = await repo.get_study(study.id)
    assert empty is None
