"""Tests for HDX-MS Epitope Mapping API."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_hdx_ms_epitope_api_endpoints(auth_headers: dict) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "study_name": "API HDX-MS Test",
            "target_protein_name": "Spike RBD / mAb",
            "custom_peptides": [
                {
                    "peptide_sequence": "FNCYFPLQSYGFQPTNGVGYQ",
                    "start_residue": 486,
                    "end_residue": 506,
                    "deuterium_uptake_apo_pct": 74.5,
                    "deuterium_uptake_bound_pct": 18.2,
                    "delta_deuterium_protection_pct": 56.3,
                    "confidence_p_value": 0.0001,
                }
            ],
        }
        res = await client.post("/api/v1/hdx-ms-epitope-mapping/map-epitope", json=payload, headers=auth_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["study_name"] == "API HDX-MS Test"
        study_id = data["id"]
        assert len(data["peptides"]) == 1

        # List
        res_list = await client.get("/api/v1/hdx-ms-epitope-mapping/studies", headers=auth_headers)
        assert res_list.status_code == 200
        assert any(s["id"] == study_id for s in res_list.json())

        # Get
        res_get = await client.get(f"/api/v1/hdx-ms-epitope-mapping/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["target_protein_name"] == "Spike RBD / mAb"

        # Delete
        res_del = await client.delete(f"/api/v1/hdx-ms-epitope-mapping/studies/{study_id}", headers=auth_headers)
        assert res_del.status_code == 204
