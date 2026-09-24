"""
API integration tests for Phase 166: MicroED Structural Engine.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_microed_structural_api_flow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Refine MicroED
        payload = {
            "sample_name": "Lysozyme Sub-micron",
            "voltage_kv": 200.0,
            "rotation_range_deg": 100.0,
            "frames_count": 4,
        }
        res_post = await client.post(
            "/api/v1/microed-structural/refine",
            json=payload,
            headers=auth_headers,
        )
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "experiment_id" in data_post
        exp_id = data_post["experiment_id"]
        assert data_post["resolution_limit_angstrom"] <= 1.0
        assert data_post["r_work"] < 0.20

        # 2. Get experiment
        res_get = await client.get(
            f"/api/v1/microed-structural/experiments/{exp_id}",
            headers=auth_headers,
        )
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == exp_id
        assert data_get["sample_name"] == "Lysozyme Sub-micron"
        assert data_get["frames_count"] == 4
