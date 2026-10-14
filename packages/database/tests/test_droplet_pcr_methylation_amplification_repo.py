"""Tests for Phase 486: Autonomous Microfluidic Droplet PCR Digital Methylation Specific Amplification Modeler Repo."""

import pytest
from database.repositories.droplet_pcr_methylation_amplification_repo import DropletPcrMethylationAmplificationRepository


@pytest.mark.asyncio
async def test_droplet_pcr_methylation_amplification_repository(db_session):
    repo = DropletPcrMethylationAmplificationRepository(db_session)

    study = await repo.create_study(
        name="Study_486_Verification",
        target_specimen="Bisulfite-Converted ctDNA in 20,000 Microfluidic Fluorinated Oil Picoliter Droplets",
        analytical_modality="droplet-pcr-methylation-amplification",
        fractional_methylation_abundance_pct=0.045,
        poisson_droplet_partition_occupancy_lambda=0.35,
        false_positive_droplet_count_per_million=0.8,
        target_dna_amplification_efficiency=0.978,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 486 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_486_Verification"
    assert study.fractional_methylation_abundance_pct == 0.045

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Single_Molecule_Droplet_PCR_Epigenetic_Quantitation",
        profile_category="Primary Step",
        quantitative_value=0.045,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Single_Molecule_Droplet_PCR_Epigenetic_Quantitation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="fractional_methylation_abundance_pct",
        observed_value=0.045,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.045

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_486_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
