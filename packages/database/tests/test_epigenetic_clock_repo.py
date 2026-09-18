"""Tests for Epigenetic Clock repository."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.epigenetic_clock_repo import EpigeneticClockRepository


@pytest.mark.asyncio
async def test_epigenetic_clock_repo_crud(db_session: AsyncSession):
    repo = EpigeneticClockRepository(db_session)
    ws_id = uuid.uuid4()

    # 1. Create sample
    sample = await repo.create_sample(
        workspace_id=ws_id,
        sample_name="Blood_Donor_42",
        chronological_age=50.0,
        tissue_type="Peripheral Blood Mononuclear Cells",
        gender="male",
        platform="Illumina EPIC 850k",
        total_cpgs_profiled=10,
        sample_metadata={"batch": "B104"},
    )
    assert sample.id is not None
    assert sample.sample_name == "Blood_Donor_42"
    assert sample.chronological_age == 50.0

    # 2. Create clock result with CpG markers
    markers = [
        {
            "cpg_id": "cg00075967",
            "gene_symbol": "ELOVL2",
            "chromosome": "chr6",
            "genomic_coordinate": 11044642,
            "beta_value": 0.65,
            "model_weight": 2.15,
            "contribution_to_age": 1.3975,
        },
        {
            "cpg_id": "cg16867657",
            "gene_symbol": "ELOVL2",
            "chromosome": "chr6",
            "genomic_coordinate": 11044877,
            "beta_value": 0.58,
            "model_weight": 3.42,
            "contribution_to_age": 1.9836,
        },
    ]

    result = await repo.create_clock_result(
        sample_id=sample.id,
        predicted_epigenetic_age=52.4,
        age_acceleration=2.4,
        clock_model="Horvath Multi-Tissue",
        confidence_interval_low=48.2,
        confidence_interval_high=56.6,
        mortality_risk_percentile=62.5,
        model_r_squared=0.96,
        cpgs_utilized=2,
        pace_of_aging=1.096,
        analysis_details={"imputation": False},
        cpg_markers=markers,
    )
    assert result.id is not None
    assert result.predicted_epigenetic_age == 52.4
    assert result.age_acceleration == 2.4

    # 3. Retrieve and verify full hierarchy
    fetched_sample = await repo.get_sample(sample.id)
    assert fetched_sample is not None
    assert len(fetched_sample.clock_results) == 1
    assert len(fetched_sample.clock_results[0].cpg_markers) == 2

    fetched_res = await repo.get_clock_result(result.id)
    assert fetched_res is not None
    assert fetched_res.clock_model == "Horvath Multi-Tissue"
    assert len(fetched_res.cpg_markers) == 2

    # 4. List samples
    samples_list = await repo.list_samples(ws_id)
    assert len(samples_list) == 1
    assert samples_list[0].id == sample.id
