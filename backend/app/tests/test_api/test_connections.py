from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.integrations.burgerprints.exceptions import BurgerPrintsAuthError


from app.tests.helpers import signup_seller_email


async def _signup_token(client: AsyncClient, email: str) -> str:
    return await signup_seller_email(client, email)


@pytest.mark.asyncio
async def test_burgerprints_status_not_connected(client: AsyncClient):
    token = await _signup_token(client, "bp@example.com")
    response = await client.get(
        "/api/v1/connections/burgerprints/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is False
    assert data["connection_id"] is None


@pytest.mark.asyncio
async def test_connect_burgerprints(client: AsyncClient):
    token = await _signup_token(client, email="bp-connect@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    with patch(
        "app.services.burgerprints_service.BurgerPrintsClient.verify_api_key",
        new=AsyncMock(return_value=True),
    ):
        response = await client.post(
            "/api/v1/connections/burgerprints",
            headers=headers,
            json={"api_key": "test-api-key-123"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "burger_prints"
    assert data["status"] == "active"

    status = await client.get("/api/v1/connections/burgerprints/status", headers=headers)
    assert status.json()["connected"] is True


@pytest.mark.asyncio
async def test_connect_burgerprints_invalid_key(client: AsyncClient):
    token = await _signup_token(client, email="bp-invalid@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    with patch(
        "app.services.burgerprints_service.BurgerPrintsClient.verify_api_key",
        side_effect=BurgerPrintsAuthError("Invalid BurgerPrints API key"),
    ):
        response = await client.post(
            "/api/v1/connections/burgerprints",
            headers=headers,
            json={"api_key": "bad-key"},
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_disconnect_burgerprints_not_connected(client: AsyncClient):
    token = await _signup_token(client, email="bp-none@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.delete("/api/v1/connections/burgerprints", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_disconnect_burgerprints(client: AsyncClient):
    token = await _signup_token(client, email="bp-disconnect@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    with patch(
        "app.services.burgerprints_service.BurgerPrintsClient.verify_api_key",
        new=AsyncMock(return_value=True),
    ):
        await client.post(
            "/api/v1/connections/burgerprints",
            headers=headers,
            json={"api_key": "test-api-key-456"},
        )

    response = await client.delete("/api/v1/connections/burgerprints", headers=headers)
    assert response.status_code == 200

    status = await client.get("/api/v1/connections/burgerprints/status", headers=headers)
    assert status.json()["connected"] is False
