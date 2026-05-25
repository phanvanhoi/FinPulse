import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.campaign import CampaignStatus, CampaignVariant, SalesCampaign
from app.models.cart import Cart, CartItem, CartStatus
from app.schemas.cart import CartItemInput


async def _get_live_campaign(db: AsyncSession, slug: str) -> SalesCampaign:
    result = await db.execute(
        select(SalesCampaign)
        .where(SalesCampaign.slug == slug, SalesCampaign.status == CampaignStatus.LIVE)
        .options(
            selectinload(SalesCampaign.items).selectinload(CampaignVariant.variant),
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found or not live")
    return campaign


def _price_map(campaign: SalesCampaign) -> dict[uuid.UUID, Decimal]:
    return {item.variant_id: item.price for item in campaign.items}


async def get_or_create_cart(db: AsyncSession, campaign: SalesCampaign, session_id: str) -> Cart:
    result = await db.execute(
        select(Cart)
        .where(
            Cart.campaign_id == campaign.id,
            Cart.session_id == session_id,
            Cart.status == CartStatus.ACTIVE,
        )
        .options(selectinload(Cart.items).selectinload(CartItem.variant))
    )
    cart = result.scalar_one_or_none()
    if cart:
        return cart

    cart = Cart(campaign_id=campaign.id, session_id=session_id)
    db.add(cart)
    await db.flush()
    return cart


async def set_cart_items(
    db: AsyncSession, campaign: SalesCampaign, session_id: str, items: list[CartItemInput]
) -> dict:
    prices = _price_map(campaign)
    cart = await get_or_create_cart(db, campaign, session_id)

    for existing in list(cart.items):
        await db.delete(existing)
    await db.flush()

    for item in items:
        if item.variant_id not in prices:
            raise BadRequestError(f"Variant {item.variant_id} is not available for this campaign")
        db.add(
            CartItem(
                cart_id=cart.id,
                variant_id=item.variant_id,
                quantity=item.quantity,
                unit_price=prices[item.variant_id],
            )
        )
    await db.flush()
    await db.refresh(cart, ["items"])
    for ci in cart.items:
        await db.refresh(ci, ["variant"])
    return _cart_response(cart, campaign)


async def save_cart_email(db: AsyncSession, campaign_slug: str, session_id: str, email: str) -> None:
    campaign = await _get_live_campaign(db, campaign_slug)
    cart = await get_or_create_cart(db, campaign, session_id)
    cart.customer_email = email
    await db.flush()


async def get_cart(db: AsyncSession, campaign_slug: str, session_id: str) -> dict:
    campaign = await _get_live_campaign(db, campaign_slug)
    result = await db.execute(
        select(Cart)
        .where(
            Cart.campaign_id == campaign.id,
            Cart.session_id == session_id,
            Cart.status == CartStatus.ACTIVE,
        )
        .options(selectinload(Cart.items).selectinload(CartItem.variant))
    )
    cart = result.scalar_one_or_none()
    if not cart or not cart.items:
        raise NotFoundError("Cart is empty")
    return _cart_response(cart, campaign)


def _cart_response(cart: Cart, campaign: SalesCampaign) -> dict:
    items = []
    subtotal = Decimal("0")
    for ci in cart.items:
        line = ci.unit_price * ci.quantity
        subtotal += line
        items.append(
            {
                "variant_id": ci.variant_id,
                "variant_name": ci.variant.name if ci.variant else "",
                "quantity": ci.quantity,
                "unit_price": ci.unit_price,
                "line_total": line,
            }
        )
    return {
        "id": cart.id,
        "campaign_id": campaign.id,
        "campaign_slug": campaign.slug,
        "campaign_title": campaign.title,
        "items": items,
        "subtotal": subtotal,
    }
