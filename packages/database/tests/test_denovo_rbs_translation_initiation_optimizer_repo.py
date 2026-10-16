"""Tests for Phase 552: Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer Repo."""

import pytest
from database.repositories.denovo_rbs_translation_initiation_optimizer_repo import DenovoRbsTranslationInitiationOptimizerRepository


@pytest.mark.asyncio
async def test_denovo_rbs_translation_initiation_optimizer_repository(db_session):
    repo = DenovoRbsTranslationInitiationOptimizerRepository(db_session)

    study = await repo.create_study(
        name="Study_552_Verification",
        target_specimen="Synthetic mRNA Polycistronic Operon 5' UTR Shine-Dalgarno Core Library in Escherichia coli BL21(DE3)",
        analytical_modality="de-novo-rbs-optimization",
        translation_initiation_rate_arbitrary_units=48500.0,
        rna_secondary_structure_free_energy_kcal_mol=-14.8,
        shine_dalgarno_16s_rrna_hybridization_energy=-9.4,
        cross_cistronic_translational_coupling_ratio=0.88,
        confidence_score=0.997,
        status="completed",
        summary_report="Phase 552 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_552_Verification"
    assert study.translation_initiation_rate_arbitrary_units == 48500.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Optimal_16S_Ribosomal_AntiSD_Complementary_RBS_Construct",
        profile_category="Primary Step",
        quantitative_value=48500.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Optimal_16S_Ribosomal_AntiSD_Complementary_RBS_Construct"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="translation_initiation_rate_arbitrary_units",
        observed_value=48500.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 48500.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_552_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
