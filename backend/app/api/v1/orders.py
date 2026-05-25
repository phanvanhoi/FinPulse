import uuid

from fastapi import APIRouter, Query, Request, Response

from app.config import settings
from app.dependencies import DB, CurrentUser
from app.schemas.order import OrderListResponse, OrderResponse
from app.services import checkout_service

router = APIRouter()


@router.get("", response_model=OrderListResponse)
async def list_orders(
    current_user: CurrentUser,
    db: DB,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, le=50),
):
    orders, total = await checkout_service.list_orders(db, current_user.organization_id, page, page_size)
    return OrderListResponse(orders=[OrderResponse(**o) for o in orders], total=total)


@router.get("/export/csv")
async def export_orders_csv(current_user: CurrentUser, db: DB):
    orders = await checkout_service.list_all_orders(db, current_user.organization_id)
    lines = ["order_id,campaign,customer_email,customer_name,total,status,created_at"]
    for o in orders:
        lines.append(
            ",".join(
                [
                    str(o["id"]),
                    _csv_escape(o.get("campaign_title") or ""),
                    _csv_escape(o["customer_email"]),
                    _csv_escape(o.get("customer_name") or ""),
                    f"{float(o['total']):.2f}",
                    o["status"],
                    o["created_at"].isoformat() if hasattr(o["created_at"], "isoformat") else str(o["created_at"]),
                ]
            )
        )
    content = "\n".join(lines)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="orders-export.csv"'},
    )


def _csv_escape(value: str) -> str:
    if any(c in value for c in [",", '"', "\n"]):
        return f'"{value.replace(chr(34), chr(34) + chr(34))}"'
    return value


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: uuid.UUID, current_user: CurrentUser, db: DB):
    order = await checkout_service.get_order(db, current_user.organization_id, order_id)
    return OrderResponse(**order)


@router.get("/public/{order_id}", response_model=OrderResponse)
async def get_public_order(order_id: uuid.UUID, db: DB):
    order = await checkout_service.get_public_order(db, order_id)
    return OrderResponse(**order)


@router.post("/complete")
async def complete_checkout(
    db: DB,
    order_id: uuid.UUID = Query(...),
    mock: bool = Query(default=False),
):
    order = await checkout_service.complete_order(db, order_id, mock=mock or not settings.STRIPE_SECRET_KEY)
    return {"status": order.status.value, "order_id": str(order.id)}


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: DB):
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_WEBHOOK_SECRET:
        return {"received": True}

    import stripe

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        from app.core.exceptions import BadRequestError

        raise BadRequestError("Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("metadata", {}).get("order_id")
        if order_id:
            await checkout_service.complete_order(db, uuid.UUID(order_id))

    return {"received": True}
