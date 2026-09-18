"""Tests for Preclinical Toxicology repository."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.preclinical_toxicology_repo import PreclinicalToxicologyRepository


@pytest.mark.asyncio
async def test_preclinical_toxicology_repo_crud(db_session: AsyncSession):
    repo = PreclinicalToxicologyRepository(db_session)
    ws_id = uuid.uuid4()

    # 1. Create study
    study = await repo.create_study(
        workspace_id=ws_id,
        compound_name="Candidate_Lead_07",
        smiles_string="CC(=O)NC1=CC=C(C=C1)O",
        therapeutic_safety_index=84.5,
        overall_safety_tier="FAVORABLE",
        caco2_permeability_cm_s=2.1e-5,
        plasma_protein_binding_pct=76.2,
        study_metadata={"assay_type": "In Vitro Tier 1"},
    )
    assert study.id is not None
    assert study.compound_name == "Candidate_Lead_07"
    assert study.therapeutic_safety_index == 84.5

    # 2. Add Endpoint
    ep = await repo.add_endpoint(
        study_id=study.id,
        endpoint_name="hERG Cardiotoxicity",
        endpoint_category="Cardiotoxicity",
        probability_risk=0.15,
        measured_or_predicted_value=18.4,
        unit="uM IC50",
        risk_classification="LOW",
        confidence_score=0.92,
    )
    assert ep.id is not None
    assert ep.endpoint_name == "hERG Cardiotoxicity"

    # 3. Add Structural alert
    alert = await repo.add_tox_alert(
        study_id=study.id,
        alert_name="Phenolic Metabolite",
        substructure_smarts="c1ccccc1O",
        mechanism="Glucuronidation/Sulfation pathway",
        severity="LOW",
    )
    assert alert.id is not None
    assert alert.alert_name == "Phenolic Metabolite"

    # 4. Retrieve study with endpoints and alerts
    fetched_study = await repo.get_study(study.id)
    assert fetched_study is not None
    assert len(fetched_study.endpoints) == 1
    assert len(fetched_study.tox_alerts) == 1

    # 5. List studies
    studies = await repo.list_studies(ws_id)
    assert len(studies) == 1
    assert studies[0].id == study.id
