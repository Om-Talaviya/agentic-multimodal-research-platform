"""Tests for Phase 448: Autonomous Synthetic Epigenetic Prime-Converter Base Insertion & Inverted Repeat Profiler Repo."""

import pytest
from database.repositories.synthetic_epigenetic_prime_converter_repo import SyntheticEpigeneticPrimeConverterRepository


@pytest.mark.asyncio
async def test_synthetic_epigenetic_prime_converter_repository(db_session):
    repo = SyntheticEpigeneticPrimeConverterRepository(db_session)

    study = await repo.create_study(
        name="Study_448_Verification",
        target_specimen="Engineered PegRNA / Cas9-Nickase Prime Editor Complex on Methylated CpG Island",
        analytical_modality="epigenetic-prime-conversion",
        peg_rna_extension_annealing_tm_celsius=64.2,
        prime_conversion_efficiency_percentage=78.5,
        cpg_demethylation_retention_ratio=0.935,
        insertion_fidelity_indel_free_score=0.982,
        confidence_score=0.99,
        status="completed",
        summary_report="Phase 448 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_448_Verification"
    assert study.peg_rna_extension_annealing_tm_celsius == 64.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="PegRNA_Reverse_Transcriptase_Template_Extension",
        profile_category="Primary Step",
        quantitative_value=64.2,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "PegRNA_Reverse_Transcriptase_Template_Extension"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="prime_conversion_efficiency_percentage",
        observed_value=64.2,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 64.2

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_448_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
