"""
API integration tests for Phase 162: Spatial Microdissection.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_spatial_microdissection_api_flow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Deconvolve spots
        payload = {
            "sample_name": "VisiumHD_Breast_Cancer_Sample1",
            "tissue_type": "Invasive Ductal Carcinoma",
            "spot_grid_size": 3,
            "resolution_nm": 100.0,
        }
        res_post = await client.post(
            "/api/v1/spatial-microdissection/deconvolve",
            json=payload,
            headers=auth_headers,
        )
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "session_id" in data_post
        session_id = data_post["session_id"]
        assert data_post["total_spots_analyzed"] == 9
        assert data_post["mean_cell_type_entropy"] > 0

        # 2. Get session
        res_get = await client.get(
            f"/api/v1/spatial-microdissection/sessions/{session_id}",
            headers=auth_headers,
        )
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == session_id
        assert data_get["deconvolutions_count"] == 9
        assert data_get["niche_boundaries_count"] == 2
