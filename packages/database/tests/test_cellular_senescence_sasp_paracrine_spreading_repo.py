"""Tests for Phase 443: Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine Repo."""

import pytest
from database.repositories.cellular_senescence_sasp_paracrine_spreading_repo import CellularSenescenceSaspRepository


@pytest.mark.asyncio
async def test_cellular_senescence_sasp_paracrine_spreading_repository(db_session):
    repo = CellularSenescenceSaspRepository(db_session)

    study = await repo.create_study(
        name="Study_443_Verification",
        target_specimen="Replicative Senescent Human Dermal Fibroblasts in 3D Collagen Microtissue with Bystander Cells",
        analytical_modality="senescence-sasp-spreading",
        sasp_paracrine_diffusion_radius_um=185.0,
        p16_ink4a_induction_fold_change=5.85,
        bystander_senescence_induction_rate=0.385,
        senolytic_depletion_efficacy_score=0.942,
        confidence_score=0.99,
        status="completed",
        summary_report="Phase 443 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_443_Verification"
    assert study.sasp_paracrine_diffusion_radius_um == 185.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="IL6_IL8_Secretory_Bystander_Propagation_Front",
        profile_category="Primary Step",
        quantitative_value=185.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "IL6_IL8_Secretory_Bystander_Propagation_Front"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="sasp_paracrine_diffusion_radius_um",
        observed_value=185.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 185.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_443_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
