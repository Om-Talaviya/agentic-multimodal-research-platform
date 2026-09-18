"""API integration tests for Epigenetic Clock & DNA Methylation."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_epigenetic_clock_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get models
        res_models = await client.get("/api/v1/epigenetic-clock/models", headers=auth_headers)
        assert res_models.status_code == 200
        data_models = res_models.json()
        assert "models" in data_models
        assert "Horvath" in data_models["models"]

        # 2. Analyze epigenetic profile
        payload = {
            "sample_name": "Clinical_Subject_049",
            "chronological_age": 48.0,
            "tissue_type": "Whole Blood",
            "gender": "female",
            "clock_model": "Horvath",
            "beta_values": {
                "cg00075967": 0.70,
                "cg16867657": 0.62,
                "cg22454769": 0.85,
            },
        }
        res_post = await client.post("/api/v1/epigenetic-clock/analyze", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "success"
        assert "sample_id" in data_post
        assert "predicted_epigenetic_age" in data_post
        sample_id = data_post["sample_id"]

        # 3. Retrieve sample details
        res_get = await client.get(f"/api/v1/epigenetic-clock/samples/{sample_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == sample_id
        assert data_get["sample_name"] == "Clinical_Subject_049"
        assert len(data_get["clock_results"]) == 1
