"""Tests for Cryo-ET Subtomogram Averaging API."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_cryoet_tomogram_api_endpoints(auth_headers: dict) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "study_name": "API Cryo-ET Test",
            "cellular_context": "Neuronal Synapse",
            "target_complex_name": "AMPAR-TARP",
            "custom_particles": [
                {
                    "particle_id_str": "PTCL_TOMO_001",
                    "x_vox": 512.4,
                    "y_vox": 384.8,
                    "z_vox": 128.0,
                    "euler_rot_deg": 45.2,
                    "euler_tilt_deg": 32.8,
                    "euler_psi_deg": 18.4,
                    "cross_correlation_score": 0.885,
                    "conformational_state": "Resting Closed",
                }
            ],
        }
        res = await client.post("/api/v1/cryoet-subtomogram-tomography/reconstruct", json=payload, headers=auth_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["study_name"] == "API Cryo-ET Test"
        study_id = data["id"]
        assert len(data["particles"]) == 1

        # List
        res_list = await client.get("/api/v1/cryoet-subtomogram-tomography/studies", headers=auth_headers)
        assert res_list.status_code == 200
        assert any(s["id"] == study_id for s in res_list.json())

        # Get
        res_get = await client.get(f"/api/v1/cryoet-subtomogram-tomography/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["target_complex_name"] == "AMPAR-TARP"

        # Delete
        res_del = await client.delete(f"/api/v1/cryoet-subtomogram-tomography/studies/{study_id}", headers=auth_headers)
        assert res_del.status_code == 204
