"""API integration tests for Preclinical Toxicogenomics & ADMET."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_preclinical_toxicology_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get alert rules
        res_rules = await client.get("/api/v1/preclinical-toxicology/alert-rules", headers=auth_headers)
        assert res_rules.status_code == 200
        data_rules = res_rules.json()
        assert "rules" in data_rules
        assert len(data_rules["rules"]) > 0

        # 2. Assess compound safety
        payload = {
            "compound_name": "Erlotinib",
            "smiles_string": "COCCOC1=C(C=C2C(=C1)C(=NC=N2)NC3=CC=CC(=C3)C#C)OCCOC",
        }
        res_post = await client.post("/api/v1/preclinical-toxicology/assess", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "success"
        assert "study_id" in data_post
        assert "therapeutic_safety_index" in data_post
        study_id = data_post["study_id"]

        # 3. Retrieve study details
        res_get = await client.get(f"/api/v1/preclinical-toxicology/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == study_id
        assert data_get["compound_name"] == "Erlotinib"
        assert len(data_get["endpoints"]) >= 5
