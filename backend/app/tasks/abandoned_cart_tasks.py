"""Celery tasks for abandoned checkout recovery."""

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.abandoned_cart_tasks.process_abandoned_checkouts")
def process_abandoned_checkouts():
    from app.services.abandoned_cart_service import process_abandoned_checkouts as _process

    return _process()


@celery_app.task(name="app.tasks.abandoned_cart_tasks.send_order_confirmation_email")
def send_order_confirmation_email(order_id: str):
    from uuid import UUID

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.core.sync_database import SyncSessionLocal
    from app.models.campaign import SalesCampaign
    from app.models.order import Order
    from app.services.email_service import send_order_confirmation

    with SyncSessionLocal() as session:
        order = session.execute(
            select(Order).where(Order.id == UUID(order_id)).options(selectinload(Order.items))
        ).scalar_one_or_none()
        if not order or order.status.value != "paid":
            return {"sent": False}

        campaign = session.get(SalesCampaign, order.campaign_id) if order.campaign_id else None
        title = campaign.title if campaign else "Your order"
        items_summary = "\n".join(
            f"- {i.product_name} ({i.variant_name}) x{i.quantity} — ${i.unit_price * i.quantity:.2f}"
            for i in order.items
        )
        sent = send_order_confirmation(
            to_email=order.customer_email,
            customer_name=order.customer_name,
            order_id=str(order.id),
            campaign_title=title,
            total=f"{order.total:.2f}",
            items_summary=items_summary,
        )
        return {"sent": sent, "order_id": order_id}
