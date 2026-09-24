"""Integration tests for Chromatin Loop API (Phase 152)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_chromatin_loop_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "cell_line_name": "API-K562",
            "chromosome": "chr8",
            "genomic_window_start_bp": 127000000,
            "genomic_window_end_bp": 129000000,
            "resolution_bp": 5000,
        }
        res = await client.post("/api/v1/chromatin-loop/map", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["cell_line_name"] == "API-K562"
        assert len(data["contact_edges"]) >= 3
        assert len(data["tad_boundaries"]) >= 3
