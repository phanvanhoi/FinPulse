import io
import uuid
from decimal import Decimal
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.tests.helpers import checkout_payload


async def _setup_seller(client: AsyncClient) -> tuple[str, str]:
    resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": f"seller-{uuid.uuid4().hex[:8]}@example.com",
            "password": "securepassword123",
            "name": "Seller",
            "organization_name": "Print Shop",
        },
    )
    token = resp.json()["access_token"]
    store = await client.get("/api/v1/store", headers={"Authorization": f"Bearer {token}"})
    return token, store.json()["slug"]


@pytest.mark.asyncio
async def test_product_catalog(client: AsyncClient):
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    products = response.json()["products"]
    assert len(products) >= 3
    assert products[0]["variants"]


@pytest.mark.asyncio
async def test_create_and_publish_campaign(client: AsyncClient):
    token, _ = await _setup_seller(client)
    headers = {"Authorization": f"Bearer {token}"}

    products = (await client.get("/api/v1/products")).json()["products"]
    product = products[0]

    create_resp = await client.post(
        "/api/v1/campaigns",
        headers=headers,
        json={
            "title": "Summer Drop",
            "product_id": product["id"],
            "description": "Limited edition",
            "retail_price": 25.00,
            "variant_prices": [{"variant_id": v["id"], "price": 25.00} for v in product["variants"]],
        },
    )
    assert create_resp.status_code == 200
    campaign = create_resp.json()
    assert campaign["status"] == "draft"

    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    design_resp = await client.post(
        f"/api/v1/campaigns/{campaign['id']}/design",
        headers=headers,
        files={"file": ("design.png", io.BytesIO(png), "image/png")},
    )
    assert design_resp.status_code == 200

    publish_resp = await client.post(f"/api/v1/campaigns/{campaign['id']}/publish", headers=headers)
    assert publish_resp.status_code == 200
    assert publish_resp.json()["status"] == "live"


@pytest.mark.asyncio
async def test_checkout_flow(client: AsyncClient):
    token, _ = await _setup_seller(client)
    headers = {"Authorization": f"Bearer {token}"}

    products = (await client.get("/api/v1/products")).json()["products"]
    product = products[0]
    variant_id = product["variants"][0]["id"]

    campaign = (
        await client.post(
            "/api/v1/campaigns",
            headers=headers,
            json={
                "title": "Checkout Test",
                "product_id": product["id"],
                "retail_price": 20.00,
                "variant_prices": [{"variant_id": variant_id, "price": 20.00}],
            },
        )
    ).json()

    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    await client.post(
        f"/api/v1/campaigns/{campaign['id']}/design",
        headers=headers,
        files={"file": ("design.png", io.BytesIO(png), "image/png")},
    )
    published = (await client.post(f"/api/v1/campaigns/{campaign['id']}/publish", headers=headers)).json()
    slug = published["slug"]

    session_id = "test-session-12345678"
    cart_resp = await client.post(
        "/api/v1/cart/add",
        json={
            "campaign_slug": slug,
            "session_id": session_id,
            "items": [{"variant_id": variant_id, "quantity": 2}],
        },
    )
    assert cart_resp.status_code == 200
    assert Decimal(str(cart_resp.json()["subtotal"])) == Decimal("40.00")

    checkout_resp = await client.post(
        f"/api/v1/cart/{slug}/checkout",
        json=checkout_payload(session_id),
    )
    assert checkout_resp.status_code == 200
    order_id = checkout_resp.json()["order_id"]

    with patch("app.tasks.fulfillment_tasks.submit_order_to_burgerprints.delay"):
        complete_resp = await client.post(f"/api/v1/orders/complete?order_id={order_id}&mock=true")
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "paid"

    orders_resp = await client.get("/api/v1/orders", headers=headers)
    assert orders_resp.status_code == 200
    assert orders_resp.json()["total"] >= 1
