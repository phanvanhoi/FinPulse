import io
import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.helpers import checkout_payload, signup_seller, signup_seller_email


async def _setup_seller_with_paid_order(client: AsyncClient) -> str:
    token, _ = await signup_seller(client, org_name="Dashboard Shop")
    headers = {"Authorization": f"Bearer {token}"}

    products = (await client.get("/api/v1/products")).json()["products"]
    product = products[0]
    variant_id = product["variants"][0]["id"]

    campaign = (
        await client.post(
            "/api/v1/campaigns",
            headers=headers,
            json={
                "title": "Dashboard Campaign",
                "product_id": product["id"],
                "retail_price": 25.00,
                "variant_prices": [{"variant_id": variant_id, "price": 25.00}],
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

    session_id = f"session-{uuid.uuid4().hex[:8]}"
    await client.post(
        "/api/v1/cart/add",
        json={
            "campaign_slug": slug,
            "session_id": session_id,
            "items": [{"variant_id": variant_id, "quantity": 2}],
        },
    )
    checkout = await client.post(
        f"/api/v1/cart/{slug}/checkout",
        json=checkout_payload(session_id),
    )
    order_id = checkout.json()["order_id"]
    with patch("app.tasks.fulfillment_tasks.submit_order_to_burgerprints.delay"):
        await client.post(f"/api/v1/orders/complete?order_id={order_id}&mock=true")

    return token


@pytest.mark.asyncio
async def test_commerce_overview_empty(client: AsyncClient, db_session: AsyncSession):
    from app.tests.helpers import create_seller_in_db, TEST_PASSWORD

    email, password, _ = await create_seller_in_db(
        db_session,
        email=f"new-{uuid.uuid4().hex[:8]}@example.com",
        org_name="Empty Shop",
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    overview = await client.get("/api/v1/dashboard/commerce-overview", headers=headers)
    assert overview.status_code == 200
    data = overview.json()
    assert Decimal(str(data["kpis"]["revenue"])) == Decimal("0")
    assert data["kpis"]["orders_count"] == 0
    assert data["kpis"]["live_campaigns"] == 0
    assert data["setup"]["has_live_campaign"] is False
    assert data["setup"]["has_paid_order"] is False
    assert data["setup"]["burgerprints_connected"] is False
    assert data["setup"]["has_burgerprints_catalog"] is False
    assert data["store"] is not None
    assert len(data["insights"]) >= 1
    assert data["finance_snapshot"]["source"] == "commerce"


@pytest.mark.asyncio
async def test_commerce_overview_with_order(client: AsyncClient):
    token = await _setup_seller_with_paid_order(client)
    headers = {"Authorization": f"Bearer {token}"}

    overview = await client.get("/api/v1/dashboard/commerce-overview", headers=headers)
    assert overview.status_code == 200
    data = overview.json()

    assert Decimal(str(data["kpis"]["revenue"])) == Decimal("50.00")
    assert data["kpis"]["orders_count"] >= 1
    assert data["kpis"]["units_sold"] == 2
    assert data["kpis"]["live_campaigns"] >= 1
    assert data["setup"]["has_live_campaign"] is True
    assert data["setup"]["has_paid_order"] is True
    assert len(data["recent_orders"]) >= 1
    assert len(data["top_campaigns"]) >= 1
    assert len(data["insights"]) >= 1
    assert data["finance_snapshot"]["source"] == "commerce"
    assert data["marketing_snapshot"]["source"] == "commerce"


@pytest.mark.asyncio
async def test_refresh_insights(client: AsyncClient):
    token = await signup_seller_email(
        client, f"insights-{uuid.uuid4().hex[:8]}@example.com", org_name="Insight Shop"
    )
    headers = {"Authorization": f"Bearer {token}"}

    refresh = await client.post("/api/v1/insights/refresh", headers=headers)
    assert refresh.status_code == 200
    assert refresh.json()["generated"] >= 1

    listed = await client.get("/api/v1/insights", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1


@pytest.mark.asyncio
async def test_commerce_overview_period_days(client: AsyncClient):
    token = await signup_seller_email(
        client, f"period-{uuid.uuid4().hex[:8]}@example.com", org_name="Period Shop"
    )
    headers = {"Authorization": f"Bearer {token}"}

    overview = await client.get("/api/v1/dashboard/commerce-overview?period_days=7", headers=headers)
    assert overview.status_code == 200
    data = overview.json()
    start = date.fromisoformat(data["period_start"])
    end = date.fromisoformat(data["period_end"])
    assert (end - start).days == 6
    assert len(data["revenue_by_day"]) == 7
