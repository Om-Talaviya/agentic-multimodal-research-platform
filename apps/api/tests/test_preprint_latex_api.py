"""Tests for Phase 124."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_preprint_latex_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"manuscript_title": "Autonomous Multi-Modal In-Silico Scientific Discovery Platform", "journal_target_format": "Nature Biotechnology"}
        res = await client.post("/api/v1/preprint-latex/compile", json=payload, headers=auth_headers)
        assert res.status_code == 201
        mid = res.json()["manuscript_id"]
        res_get = await client.get(f"/api/v1/preprint-latex/manuscripts/{mid}", headers=auth_headers)
        assert res_get.status_code == 200
