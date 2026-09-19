"""API integration tests for PK/PD Simulation & PBPK Modeler (Phase 99)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_pkpd_simulation_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Simulate PK/PD regimen
        payload = {
            "drug_name": "Osimertinib",
            "dose_mg": 80.0,
            "route": "ORAL",
            "dosing_interval_hours": 24.0,
            "bioavailability": 0.85,
            "clearance_l_hr": 4.2,
            "vd_central_l": 28.0,
        }
        res_post = await client.post("/api/v1/pkpd-simulation/simulate", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "simulation_id" in data_post
        assert data_post["cmax_ug_ml"] > 0
        assert data_post["therapeutic_window_compliance"] in ["OPTIMAL", "SUBTHERAPEUTIC", "TOXIC_EXCURSION"]
        sim_id = data_post["simulation_id"]

        # 2. Retrieve simulation details
        res_get = await client.get(f"/api/v1/pkpd-simulation/simulations/{sim_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == sim_id
        assert data_get["drug_name"] == "Osimertinib"
        assert len(data_get["tissue_concentrations"]) > 0
        assert len(data_get["pd_effects"]) > 0
