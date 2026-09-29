"""Tests for Phase 291: Autonomous CRISPR-Cas12a (Cpf1) Multiplexed Trans-Cleavage Single-Nucleotide Polymorphism Sentinel Repo."""

import pytest
from database.repositories.crispr_cas12a_multiplexed_snp_repo import CrisprCas12aMultiplexedSnpRepository


@pytest.mark.asyncio
async def test_crispr_cas12a_multiplexed_snp_repository(db_session):
    repo = CrisprCas12aMultiplexedSnpRepository(db_session)

    study = await repo.create_study(
        name="Study_291_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-cas12a-multiplexed-snp",
        single_nucleotide_discrimination_ratio=56.4,
        ssdna_trans_cleavage_rate_kcat_km=14000000.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 291 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_291_Verification"
    assert getattr(study, "single_nucleotide_discrimination_ratio") == 56.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Oncogenic_KRAS_Codon_12_Multiplex_SNP_Discrimination",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Oncogenic_KRAS_Codon_12_Multiplex_SNP_Discrimination"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_291_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
