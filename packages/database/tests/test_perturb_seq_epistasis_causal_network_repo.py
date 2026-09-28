"""Tests for Phase 262: Autonomous High-Throughput Perturb-seq Deep Causal Gene Regulatory Network Inversion & Epistasis Engine Repo."""

import pytest
from database.repositories.perturb_seq_epistasis_causal_network_repo import PerturbSeqEpistasisCausalNetworkRepository


@pytest.mark.asyncio
async def test_perturb_seq_epistasis_causal_network_repository(db_session):
    repo = PerturbSeqEpistasisCausalNetworkRepository(db_session)

    study = await repo.create_study(
        name="Study_262_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="perturb-seq-epistasis-causal-network",
        causal_edge_reconstruction_precision_pct=94.8,
        epistasis_synergy_detection_power=92.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 262 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_262_Verification"
    assert getattr(study, "causal_edge_reconstruction_precision_pct") == 94.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="DDR_Pathway_Combinatorial_CRISPRi_Epistasis_Matrix",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "DDR_Pathway_Combinatorial_CRISPRi_Epistasis_Matrix"

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
    assert fetched.name == "Study_262_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
