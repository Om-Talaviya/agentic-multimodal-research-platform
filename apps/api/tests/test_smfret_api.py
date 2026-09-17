"""Tests for Single-Molecule FRET (smFRET) Kinetics API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_smfret_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Analyze smFRET experiment
        payload = {
            "experiment_title": "SAM-I Riboswitch Dynamic Switching",
            "macromolecule_name": "SAM-I Riboswitch",
            "donor_fluorophore": "Cy3",
            "acceptor_fluorophore": "Cy5",
            "forster_radius_angstrom": 54.0,
            "acquisition_rate_hz": 100.0,
        }
        res = await client.post("/api/v1/smfret/experiments/analyze", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["experiment_title"] == "SAM-I Riboswitch Dynamic Switching"
        assert len(data["states"]) == 3
        assert len(data["traces"]) >= 1
        exp_id = data["id"]

        # 2. List Experiments
        res_list = await client.get("/api/v1/smfret/experiments", headers=auth_headers)
        assert res_list.status_code == 200
        experiments = res_list.json()
        assert len(experiments) >= 1

        # 3. Get Experiment Details
        res_get = await client.get(f"/api/v1/smfret/experiments/{exp_id}", headers=auth_headers)
        assert res_get.status_code == 200
        details = res_get.json()
        assert details["id"] == exp_id
        assert details["macromolecule_name"] == "SAM-I Riboswitch"
        assert len(details["states"]) == 3
        assert len(details["traces"]) >= 1
