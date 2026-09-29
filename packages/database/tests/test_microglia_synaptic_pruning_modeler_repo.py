"""Tests for Phase 317: Autonomous Microglia-Astrocyte-Neuron Tripartite Synaptic Pruning & Neuro-Inflammatory Flux Modeler Repo."""

import pytest
from database.repositories.microglia_synaptic_pruning_modeler_repo import MicrogliaSynapticPruningModelerRepository


@pytest.mark.asyncio
async def test_microglia_synaptic_pruning_modeler_repository(db_session):
    repo = MicrogliaSynapticPruningModelerRepository(db_session)

    study = await repo.create_study(
        name="Study_317_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="microglia-synaptic-pruning",
        synaptic_elimination_precision_auc=95.8,
        neuroprotective_astrocyte_a2_polarization_ratio=4.6,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 317 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_317_Verification"
    assert getattr(study, "synaptic_elimination_precision_auc") == 95.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Alzheimer_Amyloid_Beta_Complement_Synapse_Pruning_Assay",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Alzheimer_Amyloid_Beta_Complement_Synapse_Pruning_Assay"

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
    assert fetched.name == "Study_317_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
