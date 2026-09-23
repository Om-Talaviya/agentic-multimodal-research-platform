"""API integration tests for LNP Encapsulation Efficiency Engine (Phase 138)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_lnp_encapsulation_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Formulate LNP
        payload = {
            "formulation_tag": "LNP_Screen_Lead_77",
            "mrna_payload_name": "mRNA-1273 Modified Sequence",
            "flow_rate_ratio": 3.0,
            "total_flow_rate_ml_min": 15.0,
            "np_ratio": 6.0,
            "ionizable_lipid_mol_percent": 50.0,
            "helper_lipid_mol_percent": 10.0,
            "cholesterol_mol_percent": 38.5,
            "peg_lipid_mol_percent": 1.5,
        }
        res_post = await client.post("/api/v1/lnp-encapsulation/formulate", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "screen_id" in data_post
        assert data_post["formulation_tag"] == "LNP_Screen_Lead_77"
        assert data_post["encapsulation_efficiency_percent"] > 90.0
        screen_id = data_post["screen_id"]

        # 2. Retrieve screen details
        res_get = await client.get(f"/api/v1/lnp-encapsulation/screens/{screen_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == screen_id
        assert data_get["formulation_tag"] == "LNP_Screen_Lead_77"
        assert data_get["lipid_components_count"] == 4
        assert data_get["efficiency_metrics_count"] == 1
