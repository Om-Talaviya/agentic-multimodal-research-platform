"""API integration tests for CAR-NK & SynNotch Cell Circuit Designer (Phase 96)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_car_nk_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get costimulatory domains
        res_domains = await client.get("/api/v1/car-nk/costimulatory-domains", headers=auth_headers)
        assert res_domains.status_code == 200
        data_domains = res_domains.json()
        assert "domains" in data_domains
        assert "2B4_plus_41BB" in data_domains["domains"]

        # 2. Design CAR-NK construct
        payload = {
            "construct_name": "CAR_NK_Mesothelin_SynNotch_v1",
            "primary_target": "Mesothelin",
            "costimulatory_domain": "2B4_plus_41BB",
            "synnotch_sensor_antigen": "EpCAM",
            "gate_type": "AND_GATE",
            "armored_cytokine": "IL-15",
        }
        res_post = await client.post("/api/v1/car-nk/design", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "design_id" in data_post
        assert data_post["cytotoxicity_score"] > 80.0
        design_id = data_post["design_id"]

        # 3. Retrieve design details
        res_get = await client.get(f"/api/v1/car-nk/designs/{design_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == design_id
        assert data_get["construct_name"] == "CAR_NK_Mesothelin_SynNotch_v1"
        assert len(data_get["synnotch_gates"]) > 0
        assert len(data_get["cytokines"]) > 0
