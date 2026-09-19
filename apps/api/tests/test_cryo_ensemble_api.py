"""API integration tests for Cryo-EM Flexible Backbone Ensemble Generator (Phase 97)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_cryo_ensemble_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Generate ensemble landscape
        payload = {
            "target_protein": "GLP-1R / G-protein Complex",
            "pdb_reference_id": "7EVM",
            "density_map_resolution_angstrom": 2.65,
            "num_states": 4,
        }
        res_post = await client.post("/api/v1/cryo-ensemble/generate", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "ensemble_id" in data_post
        assert "flexibility_rmsd_angstrom" in data_post
        ensemble_id = data_post["ensemble_id"]

        # 2. Retrieve ensemble details
        res_get = await client.get(f"/api/v1/cryo-ensemble/ensembles/{ensemble_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == ensemble_id
        assert data_get["target_protein"] == "GLP-1R / G-protein Complex"
        assert len(data_get["states"]) == 4
        assert len(data_get["transitions"]) == 3
