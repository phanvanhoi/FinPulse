"""Tests for abandoned checkout recovery."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.cart import Cart, CartStatus
from app.models.store import Store
from app.services.abandoned_cart_service import process_abandoned_checkouts


async def _create_live_campaign(client: AsyncClient) -> tuple[str, str, str]:
    email = f"seller-{uuid.uuid4().hex[:8]}@example.com"
    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "password": "securepassword123",
            "name": "Seller",
            "organization_name": "Recovery Shop",
        },
    )
    token = signup.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    await client.patch(
        "/api/v1/store",
        headers=headers,
        json={
            "abandoned_checkout_enabled": True,
            "abandoned_checkout_delay_minutes": 15,
            "abandoned_checkout_email_subject": "Come back to [Store Name]!",
            "abandoned_checkout_email_body": "Complete your order: [Checkout Link]",
        },
    )

    product = (await client.get("/api/v1/products")).json()["products"][0]
    variant_id = product["variants"][0]["id"]
    campaign = (
        await client.post(
            "/api/v1/campaigns",
            headers=headers,
            json={
                "title": "Recovery Campaign",
                "product_id": product["id"],
                "retail_price": 25.00,
                "variant_prices": [{"variant_id": variant_id, "price": 25.00}],
            },
        )
    ).json()

    import io

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
    return published["slug"], variant_id, token


@pytest.mark.asyncio
async def test_save_cart_email(client: AsyncClient, db_session):
    slug, variant_id, _ = await _create_live_campaign(client)
    session_id = "recovery-session-12345678"

    await client.post(
        "/api/v1/cart/add",
        json={
            "campaign_slug": slug,
            "session_id": session_id,
            "items": [{"variant_id": variant_id, "quantity": 1}],
        },
    )

    resp = await client.post(
        f"/api/v1/cart/{slug}/save-email",
        json={"session_id": session_id, "customer_email": "abandoned@example.com"},
    )
    assert resp.status_code == 200

    result = await db_session.execute(select(Cart).where(Cart.session_id == session_id))
    cart = result.scalar_one()
    assert cart.customer_email == "abandoned@example.com"


@pytest.mark.asyncio
async def test_abandoned_checkout_recovery(client: AsyncClient, db_session):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.config import settings
    import app.services.abandoned_cart_service as abandoned_module

    slug, variant_id, _ = await _create_live_campaign(client)
    session_id = "abandoned-session-1234567"

    await client.post(
        "/api/v1/cart/add",
        json={
            "campaign_slug": slug,
            "session_id": session_id,
            "items": [{"variant_id": variant_id, "quantity": 1}],
        },
    )
    await client.post(
        f"/api/v1/cart/{slug}/save-email",
        json={"session_id": session_id, "customer_email": "abandoned@example.com"},
    )

    result = await db_session.execute(select(Cart).where(Cart.session_id == session_id))
    cart = result.scalar_one()
    cart.updated_at = datetime.now(UTC) - timedelta(minutes=30)
    await db_session.commit()

    test_sync_url = settings.DATABASE_URL_SYNC.replace("/finpulse", "/finpulse_test")
    test_sync_session = sessionmaker(bind=create_engine(test_sync_url))
    original = abandoned_module.SyncSessionLocal
    abandoned_module.SyncSessionLocal = test_sync_session
    try:
        stats = process_abandoned_checkouts()
    finally:
        abandoned_module.SyncSessionLocal = original

    assert stats["carts_emailed"] >= 1

    await db_session.refresh(cart)
    assert cart.abandoned_email_sent_at is not None
    assert cart.status == CartStatus.ABANDONED


@pytest.mark.asyncio
async def test_order_confirmation_on_complete(client: AsyncClient):
    slug, variant_id, token = await _create_live_campaign(client)
    session_id = "confirm-session-123456789"

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
        json={
            "session_id": session_id,
            "customer_email": "buyer@example.com",
            "customer_name": "Buyer",
            "shipping_address": "123 St",
        },
    )
    order_id = checkout.json()["order_id"]

    complete = await client.post(f"/api/v1/orders/complete?order_id={order_id}&mock=true")
    assert complete.status_code == 200
    assert complete.json()["status"] == "paid"

    public = await client.get(f"/api/v1/orders/public/{order_id}")
    assert public.status_code == 200
    data = public.json()
    assert data["campaign_slug"] == slug
    assert "facebook_pixel_id" in data
