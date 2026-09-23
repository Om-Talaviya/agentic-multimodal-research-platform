"""API integration tests for Histone Acetylation Dynamics Engine (Phase 136)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_histone_acetylation_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Simulate acetylation dynamics
        payload = {
            "locus_name": "BCL2 Enhancer Domain",
            "genomic_coordinates": "chr18:60985000-60992000",
            "cell_line": "DLBCL Lymphoma Cell Line",
            "hdac_inhibitor": "Tucidinostat (Chidamide)",
            "inhibitor_dose_um": 2.0,
            "treatment_duration_hours": 24.0,
        }
        res_post = await client.post("/api/v1/histone-acetylation/simulate", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "model_id" in data_post
        assert data_post["locus_name"] == "BCL2 Enhancer Domain"
        assert data_post["predicted_enhancer_activation_fold"] > 1.0
        model_id = data_post["model_id"]

        # 2. Retrieve model details
        res_get = await client.get(f"/api/v1/histone-acetylation/models/{model_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == model_id
        assert data_get["locus_name"] == "BCL2 Enhancer Domain"
        assert data_get["enzyme_kinetics_count"] == 2
        assert data_get["chromatin_profiles_count"] == 5
