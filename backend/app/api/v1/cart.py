from fastapi import APIRouter

from app.dependencies import DB
from app.schemas.cart import AddToCartRequest, CartResponse, CheckoutRequest, CheckoutResponse, SaveEmailRequest
from app.services import cart_service, checkout_service

router = APIRouter()


@router.post("/add", response_model=CartResponse)
async def add_to_cart(payload: AddToCartRequest, db: DB):
    from sqlalchemy import select

    from app.core.exceptions import NotFoundError
    from app.models.campaign import CampaignStatus, SalesCampaign

    result = await db.execute(
        select(SalesCampaign).where(
            SalesCampaign.slug == payload.campaign_slug,
            SalesCampaign.status == CampaignStatus.LIVE,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found or not live")

    cart = await cart_service.set_cart_items(db, campaign, payload.session_id, payload.items)
    return CartResponse(**cart)


@router.put("/update", response_model=CartResponse)
async def update_cart(payload: AddToCartRequest, db: DB):
    return await add_to_cart(payload, db)


@router.get("/{campaign_slug}", response_model=CartResponse)
async def get_cart(campaign_slug: str, session_id: str, db: DB):
    cart = await cart_service.get_cart(db, campaign_slug, session_id)
    return CartResponse(**cart)


@router.post("/{campaign_slug}/save-email")
async def save_cart_email(campaign_slug: str, payload: SaveEmailRequest, db: DB):
    await cart_service.save_cart_email(db, campaign_slug, payload.session_id, payload.customer_email)
    return {"status": "ok"}


@router.post("/{campaign_slug}/checkout", response_model=CheckoutResponse)
async def checkout(campaign_slug: str, payload: CheckoutRequest, db: DB):
    order, checkout_url = await checkout_service.create_checkout(db, payload, campaign_slug)
    return CheckoutResponse(
        checkout_url=checkout_url,
        order_id=order.id,
        payment_provider=order.payment_provider or "mock",
    )
