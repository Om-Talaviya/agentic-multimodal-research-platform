"""Tests for Phase 127 AntibodyMaturationRepository."""

import pytest
import uuid
from database.repositories.antibody_maturation_repo import AntibodyMaturationRepository


@pytest.mark.asyncio
async def test_antibody_maturation_repo_lifecycle(db_session):
    repo = AntibodyMaturationRepository(db_session)

    # 1. Create campaign
    campaign = await repo.create_campaign(
        candidate_name="mAb-EGFRvIII-Lead-01",
        target_antigen="EGFRvIII Deletion Mutant",
        parental_kd_nm=18.5,
        matured_kd_nm=0.12,
        affinity_fold_improvement=154.2,
        humanness_score_oasis=0.92,
        thermostability_tm_celsius=76.8,
        evolution_rounds=5,
        metadata_json={"expression_system": "CHO-K1"},
    )
    assert campaign.id is not None
    assert campaign.candidate_name == "mAb-EGFRvIII-Lead-01"

    # 2. Add evolution variant
    variant = await repo.add_variant(
        campaign_id=campaign.id,
        variant_id="VAR_CDRH3_Y102W_T104R",
        cdr_region="CDR-H3",
        mutations_summary="Y102W, T104R",
        predicted_binding_energy_ddg=-3.12,
        dissociation_constant_kd_nm=0.12,
        developability_flag=True,
        polyreactivity_risk=0.02,
    )
    assert variant.id is not None
    assert variant.cdr_region == "CDR-H3"

    # 3. Add paratope-epitope contact
    contact = await repo.add_contact(
        campaign_id=campaign.id,
        antibody_residue="Trp102H",
        antigen_residue="Leu314Antigen",
        interaction_type="PiStacking",
        interaction_distance_angstrom=3.15,
        binding_energy_contribution_kcal=-2.25,
    )
    assert contact.id is not None
    assert contact.interaction_type == "PiStacking"

    # 4. Get campaign
    fetched = await repo.get_campaign(campaign.id)
    assert fetched is not None
    assert len(fetched.variants) == 1
    assert len(fetched.contacts) == 1
    assert fetched.variants[0].variant_id == "VAR_CDRH3_Y102W_T104R"

    # 5. List campaigns
    campaigns = await repo.list_campaigns(limit=10)
    assert len(campaigns) >= 1
