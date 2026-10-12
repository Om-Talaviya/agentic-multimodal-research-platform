"""Tests for Phase 420: Autonomous Single-Cell Multi-Modal CITE-seq & TCR Clonotype Immune Synapse Dynamics Deconvolver Repo."""

import pytest
from database.repositories.citeseq_tcr_immune_synapse_repo import CiteseqTcrImmuneSynapseRepository


@pytest.mark.asyncio
async def test_citeseq_tcr_immune_synapse_repository(db_session):
    repo = CiteseqTcrImmuneSynapseRepository(db_session)

    study = await repo.create_study(
        name="Study_420_Verification",
        target_specimen="Human CD8+ Tumor-Infiltrating Lymphocytes with pMHC Multimer",
        analytical_modality="citeseq-tcr-synapse",
        immune_synapse_contact_area_um2=42.6,
        surface_protein_abundance_umi=1420.0,
        tcr_clonotype_affinity_score=0.962,
        cytotoxic_granule_polarization_ratio=0.895,
        confidence_score=0.988,
        status="completed",
        summary_report="Phase 420 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_420_Verification"
    assert study.immune_synapse_contact_area_um2 == 42.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="TCR_CD3_Supramolecular_Activation_Cluster",
        profile_category="Primary Step",
        quantitative_value=42.6,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "TCR_CD3_Supramolecular_Activation_Cluster"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="immune_synapse_contact_area_um2",
        observed_value=42.6,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 42.6

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_420_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
