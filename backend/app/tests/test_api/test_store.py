import io

import pytest
from httpx import AsyncClient


async def _signup_and_get_token(client: AsyncClient) -> str:
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "store@example.com",
            "password": "securepassword123",
            "name": "Store Owner",
            "organization_name": "My Print Shop",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_get_store_creates_default(client: AsyncClient):
    token = await _signup_and_get_token(client)
    response = await client.get("/api/v1/store", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Print Shop"
    assert data["slug"] == "my-print-shop"
    assert data["tips_enabled"] is False
    assert data["tip_options"] == [10, 15, 20]


@pytest.mark.asyncio
async def test_update_store_settings(client: AsyncClient):
    token = await _signup_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.patch(
        "/api/v1/store",
        headers=headers,
        json={
            "tips_enabled": True,
            "tip_options": [10, 15, 20, 25],
            "facebook_pixel_id": "1234567890",
            "google_analytics_id": "G-ABC123",
            "abandoned_checkout_enabled": True,
            "abandoned_checkout_delay_minutes": 30,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tips_enabled"] is True
    assert data["facebook_pixel_id"] == "1234567890"
    assert data["google_analytics_id"] == "G-ABC123"
    assert data["abandoned_checkout_enabled"] is True


@pytest.mark.asyncio
async def test_upload_store_logo(client: AsyncClient):
    token = await _signup_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    await client.get("/api/v1/store", headers=headers)

    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    response = await client.post(
        "/api/v1/store/logo",
        headers=headers,
        files={"file": ("logo.png", io.BytesIO(png_bytes), "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["logo_url"] is not None
    assert "/uploads/logos/" in data["logo_url"]


@pytest.mark.asyncio
async def test_set_custom_domain(client: AsyncClient):
    token = await _signup_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    await client.get("/api/v1/store", headers=headers)

    response = await client.post(
        "/api/v1/store/domain",
        headers=headers,
        json={"custom_domain": "shop.example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["custom_domain"] == "shop.example.com"
    assert data["verification_status"] == "pending"
    assert data["dns_record_name"] == "_finpulse-verify.shop.example.com"
    assert data["verification_token"] is not None


@pytest.mark.asyncio
async def test_public_store_endpoint(client: AsyncClient):
    token = await _signup_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    store_response = await client.get("/api/v1/store", headers=headers)
    slug = store_response.json()["slug"]

    public_response = await client.get(f"/api/v1/store/public/{slug}")
    assert public_response.status_code == 200
    data = public_response.json()
    assert data["slug"] == slug
    assert data["name"] == "My Print Shop"


@pytest.mark.asyncio
async def test_store_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/store")
    assert response.status_code == 401
