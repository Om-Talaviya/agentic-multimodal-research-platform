"""Integration tests for Membrane Permeability API (Phase 140)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_membrane_permeability_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "molecule_name": "Atenolol",
            "smiles": "CC(C)NCC(O)COC1=CC=C(C=C1)CC(N)=O",
            "molecular_weight": 266.34,
            "logp": 0.16,
            "tpsa": 84.58,
            "h_bond_donors": 3,
            "h_bond_acceptors": 4,
            "rotatable_bonds": 7,
        }
        res = await client.post("/api/v1/membrane-permeability/evaluate", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["molecule_name"] == "Atenolol"
        assert "papp_cm_per_s" in data
        assert len(data["diffusivity_profile"]) == 7
