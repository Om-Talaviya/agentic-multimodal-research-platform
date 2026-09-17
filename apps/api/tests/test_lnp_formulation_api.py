"""Tests for LNP Formulation Simulator API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.src.api.main import app


@pytest.mark.asyncio
async def test_lnp_formulation_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Simulate formulation
        payload = {
            "formulation_name": "mRNA-LNP Candidate A",
            "cargo_type": "mRNA",
            "ionizable_lipid_name": "ALC-0315",
            "np_ratio": 6.0,
            "flow_rate_ratio_aqueous_organic": 3.0,
            "total_flow_rate_ml_min": 12.0,
        }
        res = await client.post("/api/v1/lnp/formulations/simulate", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["formulation_name"] == "mRNA-LNP Candidate A"
        assert len(data["components"]) == 4
        assert "membrane_profile" in data
        assert data["membrane_profile"]["membrane_thickness_angstrom"] > 0
        formulation_id = data["id"]

        # 2. List Formulations
        res_list = await client.get("/api/v1/lnp/formulations", headers=auth_headers)
        assert res_list.status_code == 200
        formulations = res_list.json()
        assert len(formulations) >= 1

        # 3. Get Formulation Details
        res_get = await client.get(f"/api/v1/lnp/formulations/{formulation_id}", headers=auth_headers)
        assert res_get.status_code == 200
        details = res_get.json()
        assert details["id"] == formulation_id
        assert details["ionizable_lipid_name"] == "ALC-0315"
        assert len(details["components"]) == 4
        assert details["membrane_profile"]["endosomal_escape_efficiency_pct"] > 0
