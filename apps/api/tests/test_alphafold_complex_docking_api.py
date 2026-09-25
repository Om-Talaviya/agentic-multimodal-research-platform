"""Tests for AlphaFold Complex Docking API."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_alphafold_complex_api_endpoints(auth_headers: dict) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "study_name": "API AlphaFold Docking Test",
            "target_complex_name": "PD-1 / PD-L1 Complex",
            "chain_a_name": "PDCD1_HUMAN",
            "chain_b_name": "CD274_HUMAN",
            "custom_contacts": [
                {
                    "chain_a_residue": "Tyr68",
                    "chain_b_residue": "Glu121",
                    "inter_residue_distance_angstrom": 2.74,
                    "predicted_aligned_error_angstrom": 1.45,
                    "interaction_type": "salt_bridge",
                    "contact_plddt": 93.4,
                }
            ],
        }
        res = await client.post("/api/v1/alphafold-complex-docking/predict", json=payload, headers=auth_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["study_name"] == "API AlphaFold Docking Test"
        study_id = data["id"]
        assert len(data["contacts"]) == 1

        # List
        res_list = await client.get("/api/v1/alphafold-complex-docking/studies", headers=auth_headers)
        assert res_list.status_code == 200
        assert any(s["id"] == study_id for s in res_list.json())

        # Get
        res_get = await client.get(f"/api/v1/alphafold-complex-docking/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["target_complex_name"] == "PD-1 / PD-L1 Complex"

        # Delete
        res_del = await client.delete(f"/api/v1/alphafold-complex-docking/studies/{study_id}", headers=auth_headers)
        assert res_del.status_code == 204
