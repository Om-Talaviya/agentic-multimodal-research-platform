"""API integration tests for CAR-Macrophage Solid Tumor Phagocytosis Engine (Phase 137)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_car_macrophage_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Design CAR-M construct
        payload = {
            "construct_name": "Anti-EGFRvIII CAR-M (Megf10/CD3z)",
            "target_tumor_antigen": "EGFRvIII (Glioblastoma)",
            "scfv_domain": "Mab-139 derived scFv",
            "intracellular_signaling_domain": "Megf10 + FcR-gamma",
            "macrophage_subtype": "M1-Polarized Pro-Inflammatory",
            "target_cell_line": "U87-MG Glioblastoma",
            "effector_to_target_ratio": "3:1",
        }
        res_post = await client.post("/api/v1/car-macrophage/design", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "design_id" in data_post
        assert data_post["construct_name"] == "Anti-EGFRvIII CAR-M (Megf10/CD3z)"
        assert data_post["phagocytosis_efficiency_percent"] > 70.0
        design_id = data_post["design_id"]

        # 2. Retrieve design details
        res_get = await client.get(f"/api/v1/car-macrophage/designs/{design_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == design_id
        assert data_get["construct_name"] == "Anti-EGFRvIII CAR-M (Megf10/CD3z)"
        assert data_get["phagocytosis_records_count"] == 1
        assert data_get["tme_profiles_count"] == 1
