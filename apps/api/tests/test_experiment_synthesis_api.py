"""API integration tests for Autonomous AI Lab Co-Pilot & Centennial Synthesis Core (Phase 100)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_experiment_synthesis_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get pipeline stages
        res_stages = await client.get("/api/v1/experiment-synthesis/pipeline-stages", headers=auth_headers)
        assert res_stages.status_code == 200
        data_stages = res_stages.json()
        assert "stages" in data_stages
        assert len(data_stages["stages"]) == 5

        # 2. Run autonomous synthesis campaign
        payload = {
            "campaign_title": "Centennial Autonomous Kinase Discovery",
            "scientific_domain": "Targeted Oncology & Chemical Biology",
            "hypothesis_statement": "CDK4/6 and PI3Kalpha dual inhibition creates lethal cell cycle arrest in PIK3CA-mutant lines.",
        }
        res_post = await client.post("/api/v1/experiment-synthesis/synthesize", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "synthesis_id" in data_post
        assert data_post["completed_stages_count"] == 5
        syn_id = data_post["synthesis_id"]

        # 3. Retrieve campaign details
        res_get = await client.get(f"/api/v1/experiment-synthesis/campaigns/{syn_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == syn_id
        assert data_get["campaign_title"] == "Centennial Autonomous Kinase Discovery"
        assert len(data_get["action_steps"]) == 5
        assert len(data_get["verifications"]) == 3
