"""Submit paid orders to BurgerPrints for POD fulfillment."""

import asyncio
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.sync_database import SyncSessionLocal
from app.integrations.burgerprints.client import BurgerPrintsClient
from app.integrations.burgerprints.exceptions import BurgerPrintsAPIError, BurgerPrintsAuthError
from app.integrations.burgerprints.mapper import (
    build_create_order_request,
    build_line_item,
    build_shipping_address,
)
from app.models.campaign import SalesCampaign
from app.models.connection import Connection, ConnectionProvider
from app.models.order import FulfillmentStatus, Order, OrderStatus
from app.models.product import ProductVariant
from app.services.burgerprints_service import decode_api_key

FULFILLMENT_PROVIDER = "burger_prints"


def submit_order_to_burgerprints_sync(order_id: str) -> dict:
    with SyncSessionLocal() as session:
        order = session.execute(
            select(Order)
            .where(Order.id == uuid.UUID(order_id))
            .options(selectinload(Order.items))
            .with_for_update()
        ).scalar_one_or_none()

        if not order:
            return {"submitted": False, "reason": "order_not_found"}

        if order.status != OrderStatus.PAID:
            return {"submitted": False, "reason": "order_not_paid"}

        if order.external_order_id:
            return {"submitted": False, "reason": "already_submitted", "external_order_id": order.external_order_id}

        if order.fulfillment_status in (
            FulfillmentStatus.SUBMITTED,
            FulfillmentStatus.UNPAID,
            FulfillmentStatus.IN_PRODUCTION,
            FulfillmentStatus.SHIPPED,
            FulfillmentStatus.DELIVERED,
        ):
            return {"submitted": False, "reason": "already_in_fulfillment"}

        if order.fulfillment_status == FulfillmentStatus.FAILED:
            order.fulfillment_error = None
            order.fulfillment_status = FulfillmentStatus.PENDING

        connection = session.execute(
            select(Connection).where(
                Connection.organization_id == order.organization_id,
                Connection.provider == ConnectionProvider.BURGER_PRINTS,
            )
        ).scalar_one_or_none()

        api_key = decode_api_key(connection.credentials_encrypted) if connection else None
        if not api_key:
            order.fulfillment_provider = FULFILLMENT_PROVIDER
            order.fulfillment_status = FulfillmentStatus.FAILED
            order.fulfillment_error = "BurgerPrints is not connected for this organization"
            session.commit()
            return {"submitted": False, "reason": "not_connected"}

        if order.fulfillment_provider and order.fulfillment_provider != FULFILLMENT_PROVIDER:
            session.commit()
            return {"submitted": False, "reason": "unsupported_provider"}

        campaign = session.get(SalesCampaign, order.campaign_id) if order.campaign_id else None

        try:
            shipping = build_shipping_address(order)
            line_items = []
            print_location = campaign.print_location if campaign else "front"
            for item in order.items:
                variant = session.get(ProductVariant, item.variant_id) if item.variant_id else None
                front_url = item.design_front_url or (campaign.design_image_url if campaign else None)
                back_url = item.design_back_url or (campaign.design_back_url if campaign else None)
                if print_location == "back":
                    front_url, back_url = back_url, None
                elif print_location == "front":
                    back_url = None
                line_items.append(build_line_item(item, variant, front_url, back_url))

            request = build_create_order_request(order, campaign, line_items, shipping)
            client = BurgerPrintsClient(api_key=api_key)
            result = asyncio.run(client.create_order(request))

            order.fulfillment_provider = FULFILLMENT_PROVIDER
            order.external_order_id = result.order_id
            order.fulfillment_status = FulfillmentStatus.SUBMITTED
            order.fulfillment_submitted_at = datetime.now(UTC)
            order.fulfillment_error = None
            session.commit()
            return {"submitted": True, "external_order_id": result.order_id, "status": result.status}

        except (BurgerPrintsAuthError, BurgerPrintsAPIError, ValueError) as exc:
            order.fulfillment_provider = FULFILLMENT_PROVIDER
            order.fulfillment_status = FulfillmentStatus.FAILED
            order.fulfillment_error = str(exc)
            session.commit()
            return {"submitted": False, "reason": "api_error", "error": str(exc)}


def apply_burgerprints_webhook_sync(payload: dict) -> dict:
    """Update order fulfillment state from BurgerPrints webhook payload."""
    external_id = str(
        payload.get("order_id")
        or payload.get("id")
        or (payload.get("data") or {}).get("order_id")
        or (payload.get("data") or {}).get("id")
        or ""
    )
    if not external_id:
        return {"updated": False, "reason": "missing_order_id"}

    event = (payload.get("event") or payload.get("type") or "").lower()
    tracking = payload.get("tracking_number") or (payload.get("data") or {}).get("tracking_number")

    with SyncSessionLocal() as session:
        order = session.execute(
            select(Order).where(Order.external_order_id == external_id)
        ).scalar_one_or_none()
        if not order:
            return {"updated": False, "reason": "order_not_found"}

        if "paid" in event:
            order.fulfillment_status = FulfillmentStatus.UNPAID
        elif "processed" in event or "printing" in event:
            order.fulfillment_status = FulfillmentStatus.IN_PRODUCTION
        elif "delivered" in event:
            order.fulfillment_status = FulfillmentStatus.DELIVERED
        elif "cancel" in event:
            order.fulfillment_status = FulfillmentStatus.CANCELLED
        elif tracking:
            order.fulfillment_status = FulfillmentStatus.SHIPPED
            order.tracking_number = str(tracking)

        session.commit()
        return {"updated": True, "order_id": str(order.id), "fulfillment_status": order.fulfillment_status.value}
