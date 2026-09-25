"""Tests for siRNA Thermodynamics API."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_sirna_thermodynamics_api_endpoints(auth_headers: dict) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "study_name": "API siRNA Test Study",
            "target_mrna_transcript": "NM_000546.6 (TP53)",
            "target_gene": "TP53",
            "duplex_candidates": [
                {
                    "guide_strand_sequence": "5'-UUGAGGAACUGUGAAUUUGAG-3'",
                    "passenger_strand_sequence": "5'-CAAAUUCACAGUUCCUCAAUU-3'",
                    "delta_g_5p_kcal_mol": -6.8,
                    "delta_g_3p_kcal_mol": -9.4,
                    "seed_region_tm_celsius": 48.2,
                    "chemical_mod_pattern": "2OMe_2F_phosphorothioate",
                }
            ],
        }
        res = await client.post("/api/v1/sirna-thermodynamics/evaluate", json=payload, headers=auth_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["study_name"] == "API siRNA Test Study"
        study_id = data["id"]
        assert len(data["duplexes"]) == 1

        # List
        res_list = await client.get("/api/v1/sirna-thermodynamics/studies", headers=auth_headers)
        assert res_list.status_code == 200
        assert any(s["id"] == study_id for s in res_list.json())

        # Get
        res_get = await client.get(f"/api/v1/sirna-thermodynamics/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["target_gene"] == "TP53"

        # Delete
        res_del = await client.delete(f"/api/v1/sirna-thermodynamics/studies/{study_id}", headers=auth_headers)
        assert res_del.status_code == 204
