"""Tests for Metabolic Flux FBA API."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_metabolic_flux_fba_api_endpoints(auth_headers: dict) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "study_name": "API Metabolic FBA Test",
            "organism_model": "Human Recon3D",
            "cellular_phenotype": "Warburg Cancer",
            "custom_reactions": [
                {
                    "reaction_id": "R_HEX1",
                    "reaction_name": "Hexokinase",
                    "subsystem": "Glycolysis",
                    "lower_bound": 0.0,
                    "upper_bound": 1000.0,
                    "computed_flux_mmol_gdw_hr": 14.85,
                    "shadow_price": -0.12,
                }
            ],
        }
        res = await client.post("/api/v1/metabolic-flux-fba/simulate", json=payload, headers=auth_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["study_name"] == "API Metabolic FBA Test"
        study_id = data["id"]
        assert len(data["reactions"]) == 1

        # List
        res_list = await client.get("/api/v1/metabolic-flux-fba/studies", headers=auth_headers)
        assert res_list.status_code == 200
        assert any(s["id"] == study_id for s in res_list.json())

        # Get
        res_get = await client.get(f"/api/v1/metabolic-flux-fba/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["organism_model"] == "Human Recon3D"

        # Delete
        res_del = await client.delete(f"/api/v1/metabolic-flux-fba/studies/{study_id}", headers=auth_headers)
        assert res_del.status_code == 204
