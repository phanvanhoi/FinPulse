"""Abandoned checkout recovery and pending order reminders."""

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.sync_database import SyncSessionLocal
from app.models.campaign import SalesCampaign
from app.models.cart import Cart, CartItem, CartStatus
from app.models.order import Order, OrderStatus
from app.models.store import Store
from app.services.email_service import send_abandoned_checkout_email

logger = logging.getLogger(__name__)


def _cart_summary(cart: Cart) -> str:
    lines = []
    for item in cart.items:
        name = item.variant.name if item.variant else "Item"
        lines.append(f"- {name} x{item.quantity} @ ${item.unit_price}")
    return "\n".join(lines) if lines else "Your selected items"


def process_abandoned_checkouts() -> dict:
    stats = {"carts_emailed": 0, "orders_emailed": 0, "errors": 0}

    with SyncSessionLocal() as session:
        now = datetime.now(UTC)

        cart_query = (
            select(Cart)
            .join(SalesCampaign, Cart.campaign_id == SalesCampaign.id)
            .join(Store, SalesCampaign.store_id == Store.id)
            .where(
                Cart.status == CartStatus.ACTIVE,
                Cart.customer_email.isnot(None),
                Cart.abandoned_email_sent_at.is_(None),
                Store.abandoned_checkout_enabled.is_(True),
            )
            .options(
                selectinload(Cart.items).selectinload(CartItem.variant),
                selectinload(Cart.campaign).selectinload(SalesCampaign.store),
            )
        )
        carts = session.execute(cart_query).scalars().unique().all()

        for cart in carts:
            store = cart.campaign.store if cart.campaign else None
            if not store or not cart.items:
                continue

            delay = store.abandoned_checkout_delay_minutes
            cutoff = now - timedelta(minutes=delay)
            updated = cart.updated_at
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=UTC)
            if updated > cutoff:
                continue

            try:
                recovery_url = f"{settings.FRONTEND_URL}/campaign/{cart.campaign.slug}"
                send_abandoned_checkout_email(
                    to_email=cart.customer_email,
                    store_name=store.name,
                    campaign_title=cart.campaign.title,
                    recovery_url=recovery_url,
                    subject_template=store.abandoned_checkout_email_subject,
                    body_template=store.abandoned_checkout_email_body,
                    cart_summary=_cart_summary(cart),
                )
                cart.abandoned_email_sent_at = now
                cart.status = CartStatus.ABANDONED
                stats["carts_emailed"] += 1
            except Exception:
                logger.exception("Failed to send abandoned cart email for cart %s", cart.id)
                stats["errors"] += 1

        order_query = (
            select(Order)
            .join(Store, Order.store_id == Store.id)
            .where(
                Order.status == OrderStatus.PENDING,
                Order.recovery_email_sent_at.is_(None),
                Store.abandoned_checkout_enabled.is_(True),
            )
            .options(selectinload(Order.items))
        )
        orders = session.execute(order_query).scalars().all()

        for order in orders:
            store = session.get(Store, order.store_id)
            if not store:
                continue

            delay = store.abandoned_checkout_delay_minutes
            cutoff = now - timedelta(minutes=delay)
            created = order.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=UTC)
            if created > cutoff:
                continue

            campaign = session.get(SalesCampaign, order.campaign_id) if order.campaign_id else None
            if not campaign:
                continue

            try:
                recovery_url = f"{settings.FRONTEND_URL}/campaign/{campaign.slug}"
                items_summary = "\n".join(
                    f"- {i.product_name} ({i.variant_name}) x{i.quantity}" for i in order.items
                )
                send_abandoned_checkout_email(
                    to_email=order.customer_email,
                    store_name=store.name,
                    campaign_title=campaign.title,
                    recovery_url=recovery_url,
                    subject_template=store.abandoned_checkout_email_subject,
                    body_template=store.abandoned_checkout_email_body,
                    cart_summary=items_summary,
                )
                order.recovery_email_sent_at = now
                stats["orders_emailed"] += 1
            except Exception:
                logger.exception("Failed to send pending order recovery for order %s", order.id)
                stats["errors"] += 1

        session.commit()

    logger.info("Abandoned checkout processing: %s", stats)
    return stats
