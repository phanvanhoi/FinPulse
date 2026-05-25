import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.campaign import CampaignStatus, SalesCampaign
from app.models.cart import Cart, CartItem, CartStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.models.store import Store
from app.schemas.cart import CheckoutRequest
from app.services import cart_service


async def create_checkout(db: AsyncSession, payload: CheckoutRequest, campaign_slug: str) -> tuple[Order, str]:
    campaign_result = await db.execute(
        select(SalesCampaign)
        .where(SalesCampaign.slug == campaign_slug, SalesCampaign.status == CampaignStatus.LIVE)
        .options(selectinload(SalesCampaign.store), selectinload(SalesCampaign.product))
    )
    campaign = campaign_result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found")

    cart_data = await cart_service.get_cart(db, campaign_slug, payload.session_id)
    store = campaign.store

    subtotal = Decimal(str(cart_data["subtotal"]))
    tip_amount = Decimal("0")
    if payload.tip_percent and store.tips_enabled:
        tip_amount = (subtotal * Decimal(str(payload.tip_percent)) / Decimal("100")).quantize(Decimal("0.01"))

    total = subtotal + tip_amount

    cart_result = await db.execute(
        select(Cart)
        .where(Cart.id == cart_data["id"])
        .options(selectinload(Cart.items).selectinload(CartItem.variant))
    )
    cart = cart_result.scalar_one()
    cart.customer_email = payload.customer_email

    order = Order(
        store_id=store.id,
        campaign_id=campaign.id,
        organization_id=campaign.organization_id,
        customer_email=payload.customer_email,
        customer_name=payload.customer_name,
        shipping_address=payload.shipping_address,
        subtotal=subtotal,
        tip_amount=tip_amount,
        total=total,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    await db.flush()

    for ci in cart.items:
        db.add(
            OrderItem(
                order_id=order.id,
                variant_id=ci.variant_id,
                variant_name=ci.variant.name if ci.variant else "Unknown",
                product_name=campaign.product.name if campaign.product else campaign.title,
                quantity=ci.quantity,
                unit_price=ci.unit_price,
            )
        )

    checkout_url = await _create_stripe_session(order, campaign)
    await db.flush()
    return order, checkout_url


async def _create_stripe_session(order: Order, campaign: SalesCampaign) -> str:
    success_url = f"{settings.FRONTEND_URL}/checkout/success?order_id={order.id}"
    cancel_url = f"{settings.FRONTEND_URL}/campaign/{campaign.slug}"

    if not settings.STRIPE_SECRET_KEY:
        return f"{success_url}&mock=true"

    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        mode="payment",
        customer_email=order.customer_email,
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"{campaign.title} - Order"},
                    "unit_amount": int(order.total * 100),
                },
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"order_id": str(order.id)},
    )
    order.stripe_session_id = session.id
    return session.url


async def complete_order(db: AsyncSession, order_id: uuid.UUID, mock: bool = False) -> Order:
    result = await db.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise NotFoundError("Order not found")
    if order.status == OrderStatus.PAID:
        return order

    if not mock and not settings.STRIPE_SECRET_KEY:
        raise BadRequestError("Payment not configured")

    order.status = OrderStatus.PAID

    if order.campaign_id:
        campaign = await db.get(SalesCampaign, order.campaign_id)
        if campaign:
            units = sum(item.quantity for item in order.items)
            campaign.units_sold += units

    cart_result = await db.execute(
        select(Cart).where(Cart.campaign_id == order.campaign_id, Cart.status == CartStatus.ACTIVE)
    )
    for cart in cart_result.scalars().all():
        cart.status = CartStatus.CHECKED_OUT

    await db.flush()

    from app.tasks.abandoned_cart_tasks import send_order_confirmation_email

    try:
        send_order_confirmation_email.delay(str(order.id))
    except Exception:
        send_order_confirmation_email(str(order.id))

    return order


async def list_orders(db: AsyncSession, organization_id: uuid.UUID, page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
    base = select(Order).where(Order.organization_id == organization_id)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0

    result = await db.execute(
        base.options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    orders = []
    for order in result.scalars().all():
        campaign = await db.get(SalesCampaign, order.campaign_id) if order.campaign_id else None
        orders.append(_order_to_dict(order, campaign.title if campaign else None))
    return orders, total


async def list_all_orders(db: AsyncSession, organization_id: uuid.UUID) -> list[dict]:
    result = await db.execute(
        select(Order)
        .where(Order.organization_id == organization_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    orders = []
    for order in result.scalars().all():
        campaign = await db.get(SalesCampaign, order.campaign_id) if order.campaign_id else None
        orders.append(_order_to_dict(order, campaign.title if campaign else None))
    return orders


async def get_order(db: AsyncSession, organization_id: uuid.UUID, order_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id, Order.organization_id == organization_id)
        .options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise NotFoundError("Order not found")
    campaign = await db.get(SalesCampaign, order.campaign_id) if order.campaign_id else None
    return _order_to_dict(order, campaign.title if campaign else None)


async def get_public_order(db: AsyncSession, order_id: uuid.UUID) -> dict:
    result = await db.execute(select(Order).where(Order.id == order_id).options(selectinload(Order.items)))
    order = result.scalar_one_or_none()
    if not order:
        raise NotFoundError("Order not found")

    campaign = None
    store = None
    if order.campaign_id:
        campaign_result = await db.execute(
            select(SalesCampaign)
            .where(SalesCampaign.id == order.campaign_id)
            .options(selectinload(SalesCampaign.store))
        )
        campaign = campaign_result.scalar_one_or_none()
        store = campaign.store if campaign else None
    if not store:
        store = await db.get(Store, order.store_id)

    data = _order_to_dict(order, campaign.title if campaign else None)
    data["campaign_slug"] = campaign.slug if campaign else None
    data["facebook_pixel_id"] = store.facebook_pixel_id if store else None
    data["google_analytics_id"] = store.google_analytics_id if store else None
    return data


def _order_to_dict(order: Order, campaign_title: str | None) -> dict:
    items = []
    for item in order.items:
        items.append(
            {
                "variant_name": item.variant_name,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "line_total": item.unit_price * item.quantity,
            }
        )
    return {
        "id": order.id,
        "campaign_id": order.campaign_id,
        "campaign_title": campaign_title,
        "customer_email": order.customer_email,
        "customer_name": order.customer_name,
        "subtotal": order.subtotal,
        "tip_amount": order.tip_amount,
        "total": order.total,
        "status": order.status.value,
        "items": items,
        "created_at": order.created_at,
    }
