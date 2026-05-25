import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_payment_config_public(client: AsyncClient):
    response = await client.get("/api/v1/payments/config")
    assert response.status_code == 200
    data = response.json()
    assert "card_enabled" in data
    assert "paypal_enabled" in data
    assert "mock_enabled" in data
