"""Tests for DNA Methylation Clock Repository."""

import pytest
from database.connection import AsyncSession
from database.repositories.dna_methylation_clock_repo import DNAMethylationClockRepository


@pytest.mark.asyncio
async def test_dna_methylation_clock_repo_crud(db_session: AsyncSession) -> None:
    repo = DNAMethylationClockRepository(db_session)

    study = await repo.create_study(
        study_name="Epigenetic Age Validation",
        sample_identifier="DONOR-9912",
        tissue_type="whole_blood",
        chronological_age=50.0,
        horvath_predicted_age=48.5,
        hannum_predicted_age=49.1,
        phenoage_predicted_age=47.9,
        grimage_mortality_risk_score=0.18,
        age_acceleration_delta=-1.5,
        cpg_markers=[
            {
                "cpg_probe_id": "cg02228185",
                "target_gene": "ASPA",
                "chromosome": "chr17",
                "genomic_coordinate": 3387820,
                "beta_value": 0.42,
                "clock_weight": 1.45,
            }
        ],
        age_metrics=[
            {
                "clock_algorithm": "Horvath Multi-Tissue 353-CpG",
                "predicted_epigenetic_age": 48.5,
                "acceleration_residual": -1.5,
                "mortality_hazard_ratio": 0.92,
            }
        ],
    )

    assert study.id is not None
    assert study.study_name == "Epigenetic Age Validation"
    assert len(study.cpg_markers) == 1
    assert len(study.age_metrics) == 1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.sample_identifier == "DONOR-9912"

    studies = await repo.list_studies()
    assert len(studies) >= 1

    deleted = await repo.delete_study(study.id)
    assert deleted is True

    empty = await repo.get_study(study.id)
    assert empty is None
