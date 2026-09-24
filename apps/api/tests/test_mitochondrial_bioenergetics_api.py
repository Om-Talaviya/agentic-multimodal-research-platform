"""Integration tests for Mitochondrial Bioenergetics API (Phase 144)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_mitochondrial_bioenergetics_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "cell_line": "SH-SY5Y Neuroblastoma",
            "substrate_type": "Pyruvate/Malate",
            "uncoupler_fccp_concentration_um": 0.75,
            "complex_i_inhibition_pct": 15.0,
        }
        res = await client.post("/api/v1/mitochondrial-bioenergetics/simulate", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["cell_line"] == "SH-SY5Y Neuroblastoma"
        assert len(data["etc_complexes"]) == 5
        assert data["basal_ocr_pmol_min"] > 0
