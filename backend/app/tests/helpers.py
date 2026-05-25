"""Shared test fixtures for checkout payloads."""

import io
import uuid
from unittest.mock import AsyncMock

from httpx import AsyncClient

TEST_SHIPPING = {
    "street_address": "123 Main St",
    "apt_suite_other": "",
    "city": "Austin",
    "state": "TX",
    "zipcode": "78701",
    "country": "US",
    "phone_number": "+15551234567",
}

TEST_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
)


def checkout_payload(session_id: str, email: str = "buyer@example.com", **extra) -> dict:
    return {
        "session_id": session_id,
        "customer_email": email,
        "customer_name": "Test Buyer",
        "shipping": TEST_SHIPPING,
        **extra,
    }


async def signup_seller(client: AsyncClient, org_name: str = "Print Shop") -> tuple[str, str]:
    resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": f"seller-{uuid.uuid4().hex[:8]}@example.com",
            "password": "securepassword123",
            "name": "Seller",
            "organization_name": org_name,
        },
    )
    token = resp.json()["access_token"]
    store = await client.get("/api/v1/store", headers={"Authorization": f"Bearer {token}"})
    return token, store.json()["slug"]


async def create_published_campaign(
    client: AsyncClient,
    token: str,
    *,
    title: str = "Test Campaign",
    print_location: str = "front",
    upload_back: bool = False,
) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    products = (await client.get("/api/v1/products")).json()["products"]
    product = products[0]
    variant_id = product["variants"][0]["id"]

    campaign = (
        await client.post(
            "/api/v1/campaigns",
            headers=headers,
            json={
                "title": title,
                "product_id": product["id"],
                "retail_price": 20.00,
                "print_location": print_location,
                "variant_prices": [{"variant_id": variant_id, "price": 20.00}],
            },
        )
    ).json()

    await client.post(
        f"/api/v1/campaigns/{campaign['id']}/design",
        headers=headers,
        files={"file": ("design.png", io.BytesIO(TEST_PNG), "image/png")},
    )
    if upload_back or print_location in ("back", "both"):
        await client.post(
            f"/api/v1/campaigns/{campaign['id']}/design?side=back",
            headers=headers,
            files={"file": ("back.png", io.BytesIO(TEST_PNG), "image/png")},
        )

    published = (await client.post(f"/api/v1/campaigns/{campaign['id']}/publish", headers=headers)).json()
    return published


async def create_paid_order(client: AsyncClient, token: str, campaign: dict) -> dict:
    from unittest.mock import patch

    variant_id = campaign["variants"][0]["variant_id"]
    session_id = f"session-{uuid.uuid4().hex[:8]}"
    slug = campaign["slug"]

    await client.post(
        "/api/v1/cart/add",
        json={
            "campaign_slug": slug,
            "session_id": session_id,
            "items": [{"variant_id": variant_id, "quantity": 1}],
        },
    )
    checkout = await client.post(
        f"/api/v1/cart/{slug}/checkout",
        json=checkout_payload(session_id),
    )
    order_id = checkout.json()["order_id"]
    with patch("app.tasks.fulfillment_tasks.submit_order_to_burgerprints.delay"):
        complete = await client.post(f"/api/v1/orders/complete?order_id={order_id}&mock=true")
    assert complete.status_code == 200
    return {"order_id": order_id, "status": complete.json()["status"]}


async def connect_burgerprints(client: AsyncClient, token: str) -> None:
    from unittest.mock import patch

    headers = {"Authorization": f"Bearer {token}"}
    with patch(
        "app.services.burgerprints_service.BurgerPrintsClient.verify_api_key",
        new=AsyncMock(return_value=True),
    ):
        resp = await client.post(
            "/api/v1/connections/burgerprints",
            headers=headers,
            json={"api_key": "test-api-key-123"},
        )
    assert resp.status_code == 200
