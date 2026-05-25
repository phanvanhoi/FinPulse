from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.integrations.burgerprints.schemas import BurgerPrintsLineItem, BurgerPrintsOrderResult
from app.tests.helpers import (
    connect_burgerprints,
    create_paid_order,
    create_published_campaign,
    signup_seller,
)


@pytest.mark.asyncio
async def test_publish_both_sides_requires_back_design(client: AsyncClient):
    token, _ = await signup_seller(client)
    headers = {"Authorization": f"Bearer {token}"}
    products = (await client.get("/api/v1/products")).json()["products"]
    product = products[0]
    variant_id = product["variants"][0]["id"]

    campaign = (
        await client.post(
            "/api/v1/campaigns",
            headers=headers,
            json={
                "title": "Two-sided Tee",
                "product_id": product["id"],
                "retail_price": 25.00,
                "print_location": "both",
                "variant_prices": [{"variant_id": variant_id, "price": 25.00}],
            },
        )
    ).json()

    import io

    from app.tests.helpers import TEST_PNG

    await client.post(
        f"/api/v1/campaigns/{campaign['id']}/design",
        headers=headers,
        files={"file": ("front.png", io.BytesIO(TEST_PNG), "image/png")},
    )

    publish_resp = await client.post(f"/api/v1/campaigns/{campaign['id']}/publish", headers=headers)
    assert publish_resp.status_code == 400
    assert "back design" in publish_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_duplicate_campaign(client: AsyncClient):
    token, _ = await signup_seller(client)
    headers = {"Authorization": f"Bearer {token}"}
    original = await create_published_campaign(client, token, title="Original Drop")

    duplicate_resp = await client.post(f"/api/v1/campaigns/{original['id']}/duplicate", headers=headers)
    assert duplicate_resp.status_code == 200
    duplicate = duplicate_resp.json()
    assert duplicate["status"] == "draft"
    assert duplicate["title"] == "Original Drop (Copy)"
    assert duplicate["slug"] != original["slug"]
    assert duplicate["design_image_url"] == original["design_image_url"]


@pytest.mark.asyncio
async def test_fulfillment_fails_when_not_connected(client: AsyncClient):
    token, _ = await signup_seller(client)
    campaign = await create_published_campaign(client, token)
    order = await create_paid_order(client, token, campaign)

    from app.services.fulfillment_service import submit_order_to_burgerprints_sync

    result = submit_order_to_burgerprints_sync(order["order_id"])
    assert result["submitted"] is False
    assert result["reason"] == "not_connected"


@pytest.mark.asyncio
async def test_fulfillment_submits_when_connected(client: AsyncClient):
    token, _ = await signup_seller(client)
    await connect_burgerprints(client, token)
    campaign = await create_published_campaign(client, token)
    order = await create_paid_order(client, token, campaign)

    mock_line = BurgerPrintsLineItem(sku="BP-TEST-SKU", quantity=1, design_front_url="http://test/design.png")
    mock_result = BurgerPrintsOrderResult(order_id="BP-12345", status="submitted")

    with patch("app.services.fulfillment_service.build_line_item", return_value=mock_line):
        with patch(
            "app.services.fulfillment_service.BurgerPrintsClient.create_order",
            new=AsyncMock(return_value=mock_result),
        ):
            from app.services.fulfillment_service import submit_order_to_burgerprints_sync

            result = submit_order_to_burgerprints_sync(order["order_id"])

    assert result["submitted"] is True
    assert result["external_order_id"] == "BP-12345"


@pytest.mark.asyncio
async def test_burgerprints_webhook_updates_tracking(client: AsyncClient):
    token, _ = await signup_seller(client)
    await connect_burgerprints(client, token)
    campaign = await create_published_campaign(client, token)
    order = await create_paid_order(client, token, campaign)

    mock_line = BurgerPrintsLineItem(sku="BP-TEST-SKU", quantity=1, design_front_url="http://test/design.png")
    mock_result = BurgerPrintsOrderResult(order_id="BP-WH-001", status="submitted")
    with patch("app.services.fulfillment_service.build_line_item", return_value=mock_line):
        with patch(
            "app.services.fulfillment_service.BurgerPrintsClient.create_order",
            new=AsyncMock(return_value=mock_result),
        ):
            from app.services.fulfillment_service import submit_order_to_burgerprints_sync

            submit_order_to_burgerprints_sync(order["order_id"])

    webhook_resp = await client.post(
        "/api/v1/orders/webhooks/burgerprints",
        json={
            "event": "order_shipped",
            "order_id": "BP-WH-001",
            "tracking_number": "1Z999AA10123456784",
        },
    )
    assert webhook_resp.status_code == 200
    data = webhook_resp.json()
    assert data["updated"] is True
    assert data["fulfillment_status"] == "shipped"


@pytest.mark.asyncio
async def test_stripe_webhook_completes_order(client: AsyncClient, monkeypatch):
    token, _ = await signup_seller(client)
    campaign = await create_published_campaign(client, token, title="Stripe Campaign")
    headers = {"Authorization": f"Bearer {token}"}

    variant_id = campaign["variants"][0]["variant_id"]
    session_id = "stripe-session-12345678"
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
        json={
            "session_id": session_id,
            "customer_email": "stripe-buyer@example.com",
            "customer_name": "Stripe Buyer",
            "shipping": {
                "street_address": "123 Main St",
                "city": "Austin",
                "state": "TX",
                "zipcode": "78701",
                "country": "US",
                "phone_number": "+15551234567",
            },
        },
    )
    order_id = checkout.json()["order_id"]

    monkeypatch.setattr("app.config.settings.STRIPE_SECRET_KEY", "sk_test_fake")
    monkeypatch.setattr("app.config.settings.STRIPE_WEBHOOK_SECRET", "whsec_test")

    fake_event = {
        "type": "checkout.session.completed",
        "data": {"object": {"metadata": {"order_id": order_id}}},
    }

    with patch("stripe.Webhook.construct_event", return_value=fake_event):
        with patch("app.tasks.fulfillment_tasks.submit_order_to_burgerprints.delay"):
            webhook_resp = await client.post(
                "/api/v1/orders/webhooks/stripe",
                content=b"{}",
                headers={"stripe-signature": "sig_test"},
            )

    assert webhook_resp.status_code == 200

    orders = await client.get("/api/v1/orders", headers=headers)
    paid = [o for o in orders.json()["orders"] if o["id"] == order_id]
    assert len(paid) == 1
    assert paid[0]["status"] == "paid"
