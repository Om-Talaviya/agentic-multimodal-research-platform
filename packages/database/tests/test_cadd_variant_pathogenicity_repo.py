"""Tests for CADD Variant Pathogenicity Repository."""

import pytest
from database.connection import AsyncSession
from database.repositories.cadd_variant_pathogenicity_repo import CADDVariantRepository


@pytest.mark.asyncio
async def test_cadd_variant_repo_crud(db_session: AsyncSession) -> None:
    repo = CADDVariantRepository(db_session)

    study = await repo.create_study(
        study_name="Test CADD Scoring",
        genome_build="GRCh38",
        target_gene="TP53",
        variant_count=1,
        mean_phred_score=34.0,
        deleterious_variant_count=1,
        variants=[
            {
                "chromosome": "chr17",
                "position": 7674220,
                "reference_allele": "C",
                "alternate_allele": "T",
                "hgvs_c": "c.743G>A",
                "raw_score": 4.85,
                "phred_score": 34.0,
                "gerp_score": 5.62,
                "phylop_score": 8.12,
                "pathogenicity_verdict": "pathogenic",
            }
        ],
        ensemble_scores=[
            {
                "algorithm_name": "CADD v1.6 PHRED",
                "concordance_rate": 0.94,
                "high_impact_flag": "PASS",
            }
        ],
    )

    assert study.id is not None
    assert study.study_name == "Test CADD Scoring"
    assert len(study.variants) == 1
    assert len(study.ensemble_scores) == 1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.target_gene == "TP53"

    studies = await repo.list_studies()
    assert len(studies) >= 1

    deleted = await repo.delete_study(study.id)
    assert deleted is True

    empty = await repo.get_study(study.id)
    assert empty is None
