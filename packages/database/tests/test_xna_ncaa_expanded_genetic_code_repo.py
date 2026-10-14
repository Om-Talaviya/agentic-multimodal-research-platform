"""Tests for Phase 498: Autonomous Xenobiotic Non-Canonical Amino Acid Expanded Genetic Code Ribosome Translator Repo."""

import pytest
from database.repositories.xna_ncaa_expanded_genetic_code_repo import XnaNcaaExpandedGeneticCodeRepository


@pytest.mark.asyncio
async def test_xna_ncaa_expanded_genetic_code_repository(db_session):
    repo = XnaNcaaExpandedGeneticCodeRepository(db_session)

    study = await repo.create_study(
        name="Study_498_Verification",
        target_specimen="Orthogonal Methionyl-tRNA Synthetase / tRNA Pair in Recoded E. coli C321.deltaA with UAG Amber Suppression",
        analytical_modality="expanded-genetic-code-translation",
        ncaa_incorporation_fidelity_pct=99.1,
        amber_uag_suppression_efficiency=0.895,
        orthogonal_synthetase_catalytic_kcat_over_km=18500.0,
        recombinant_protein_expression_yield_mg_per_L=42.5,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 498 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_498_Verification"
    assert study.ncaa_incorporation_fidelity_pct == 99.1

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Azidophenylalanine_Bioorthogonal_Click_Labeling",
        profile_category="Primary Step",
        quantitative_value=99.1,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Azidophenylalanine_Bioorthogonal_Click_Labeling"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="ncaa_incorporation_fidelity_pct",
        observed_value=99.1,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 99.1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_498_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
