"""Tests for Whole-Body PBPK API endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_simulate_and_fetch_pbpk_study(auth_headers: dict) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "study_name": "API PBPK Simulation Test",
            "drug_candidate_name": "API-DRUG-X",
            "molecular_weight_da": 380.0,
            "logp": 2.2,
            "plasma_protein_unbound_fraction": 0.12,
            "intrinsic_clearance_ml_min_kg": 18.0,
            "species": "human",
            "administration_route": "oral",
            "dose_mg_kg": 10.0,
            "simulation_time_hours": 24.0,
        }
        res = await client.post("/api/v1/pbpk/simulate", json=payload, headers=auth_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["study_name"] == "API PBPK Simulation Test"
        study_id = data["id"]
        assert len(data["organ_compartments"]) == 9

        # Fetch list
        res_list = await client.get("/api/v1/pbpk/studies", headers=auth_headers)
        assert res_list.status_code == 200
        assert any(s["id"] == study_id for s in res_list.json())

        # Fetch by ID
        res_get = await client.get(f"/api/v1/pbpk/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["drug_candidate_name"] == "API-DRUG-X"

        # Delete
        res_del = await client.delete(f"/api/v1/pbpk/studies/{study_id}", headers=auth_headers)
        assert res_del.status_code == 204
