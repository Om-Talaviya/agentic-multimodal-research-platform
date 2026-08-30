"""Integration tests for Authentication API endpoints."""

import httpx
import pytest
from main import app


@pytest.mark.asyncio
async def test_auth_login_success_and_me():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login with seeded admin account
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "AdminPassword123!"},
        )
        assert login_resp.status_code == 200
        data = login_resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == "admin"
        assert data["user"]["role"] == "admin"

        token = data["access_token"]
        refresh_tok = data["refresh_token"]

        # 2. Access /api/v1/auth/me with bearer token
        me_resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["username"] == "admin"
        assert me_data["role"] == "admin"

        # 3. Refresh token
        refresh_resp = await client.post(
            "/api/v1/auth/token/refresh",
            json={"refresh_token": refresh_tok},
        )
        assert refresh_resp.status_code == 200
        ref_data = refresh_resp.json()
        assert "access_token" in ref_data


@pytest.mark.asyncio
async def test_auth_login_invalid_credentials():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "WrongPassword!"},
        )
        assert resp.status_code == 401
