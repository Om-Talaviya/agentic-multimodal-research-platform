"""
API integration tests for Phase 167: Single Cell Perturbation.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_single_cell_perturbation_api_flow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Screen perturbations
        payload = {
            "study_name": "K562_Screen_API_Test",
            "modality": "CRISPRi-PerturbSeq",
            "target_genes": ["MYC", "TP53", "CDK4"],
        }
        res_post = await client.post(
            "/api/v1/single-cell-perturbation/screen",
            json=payload,
            headers=auth_headers,
        )
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "study_id" in data_post
        study_id = data_post["study_id"]
        assert data_post["total_cells_profiled"] == 7200
        assert data_post["energy_distance_shift"] > 0

        # 2. Get study
        res_get = await client.get(
            f"/api/v1/single-cell-perturbation/studies/{study_id}",
            headers=auth_headers,
        )
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == study_id
        assert data_get["study_name"] == "K562_Screen_API_Test"
        assert data_get["target_effects_count"] == 3
