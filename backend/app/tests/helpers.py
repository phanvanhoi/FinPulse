"""Shared test fixtures for checkout payloads."""

import uuid
from unittest.mock import patch

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import create_seller_account

TEST_SHIPPING = {
    "street_address": "123 Main St",
    "apt_suite_other": "",
    "city": "Austin",
    "state": "TX",
    "zipcode": "78701",
    "country": "US",
    "phone_number": "+15551234567",
}

TEST_PASSWORD = "securepassword123"

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


async def create_seller_in_db(
    db: AsyncSession,
    *,
    email: str | None = None,
    password: str = TEST_PASSWORD,
    name: str = "Seller",
    org_name: str = "Print Shop",
) -> tuple[str, str, str]:
    """Create seller via service and return (email, password, store_slug)."""
    from sqlalchemy import select

    from app.models.store import Store

    email = email or f"seller-{uuid.uuid4().hex[:8]}@example.com"
    user, org = await create_seller_account(
        db,
        email=email,
        password=password,
        name=name,
        organization_name=org_name,
    )
    await db.flush()
    store = (
        await db.execute(
            select(Store).where(Store.organization_id == user.organization_id)
        )
    ).scalar_one()
    return email, password, store.slug


async def signup_seller(client: AsyncClient, org_name: str = "Print Shop") -> tuple[str, str]:
    """Create seller in DB and login via API (signup endpoint disabled)."""
    from app.core.database import get_db

    override = client.app.dependency_overrides.get(get_db)
    if override is None:
        raise RuntimeError("Test client missing db override")

    async for db in override():
        email, password, store_slug = await create_seller_in_db(db, org_name=org_name)
        break

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    return login.json()["access_token"], store_slug


async def signup_seller_email(client: AsyncClient, email: str, org_name: str = "Print Shop") -> str:
    """Create seller with fixed email and return access token."""
    from app.core.database import get_db

    override = client.app.dependency_overrides.get(get_db)
    if override is None:
        raise RuntimeError("Test client missing db override")

    async for db in override():
        _, password, _ = await create_seller_in_db(db, email=email, org_name=org_name)
        break

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    return login.json()["access_token"]


async def connect_burgerprints(client: AsyncClient, token: str) -> None:
    from unittest.mock import AsyncMock

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

    import io

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
