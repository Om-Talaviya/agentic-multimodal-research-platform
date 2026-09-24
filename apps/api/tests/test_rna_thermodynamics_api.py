"""
API integration tests for Phase 163: RNA Thermodynamics.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_rna_thermodynamics_api_flow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Fold RNA
        payload = {
            "rna_name": "SAM_Riboswitch_Test",
            "sequence": "GGGAUCGCAGUCUCGAGAGUUGCCAAACCAGCAGCAGCGCUCCUUCUGCGAGAUCCC",
            "temperature_celsius": 37.0,
        }
        res_post = await client.post(
            "/api/v1/rna-thermodynamics/fold",
            json=payload,
            headers=auth_headers,
        )
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "study_id" in data_post
        study_id = data_post["study_id"]
        assert data_post["mfe_delta_g_kcal_mol"] < 0.0

        # 2. Get study
        res_get = await client.get(
            f"/api/v1/rna-thermodynamics/studies/{study_id}",
            headers=auth_headers,
        )
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == study_id
        assert data_get["rna_name"] == "SAM_Riboswitch_Test"
        assert "base_pairs_count" in data_get
