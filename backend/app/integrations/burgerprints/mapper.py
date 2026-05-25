"""Map FinPulse domain objects to BurgerPrints API payloads."""

from app.integrations.burgerprints.schemas import (
    BurgerPrintsCreateOrderRequest,
    BurgerPrintsLineItem,
    BurgerPrintsShippingAddress,
)
from app.models.campaign import SalesCampaign
from app.models.order import Order, OrderItem
from app.models.product import ProductVariant


def build_shipping_address(order: Order) -> BurgerPrintsShippingAddress:
    details = order.shipping_details or {}
    if not details:
        raise ValueError(f"Order {order.id} is missing structured shipping details")

    return BurgerPrintsShippingAddress(
        full_name=order.customer_name or details.get("full_name") or "Customer",
        email=order.customer_email,
        phone_number=details.get("phone_number") or "",
        country=details.get("country") or "US",
        state=details.get("state") or "",
        city=details.get("city") or "",
        street_address=details.get("street_address") or "",
        apt_suite_other=details.get("apt_suite_other") or "",
        zipcode=details.get("zipcode") or "",
    )


def build_line_item(
    order_item: OrderItem,
    variant: ProductVariant | None,
    design_front_url: str | None,
    design_back_url: str | None,
) -> BurgerPrintsLineItem:
    sku = order_item.provider_sku or (variant.provider_sku if variant else None)
    if not sku:
        raise ValueError(f"Order item {order_item.id} has no BurgerPrints provider SKU")

    return BurgerPrintsLineItem(
        sku=sku,
        quantity=order_item.quantity,
        design_front_url=order_item.design_front_url or design_front_url,
        design_back_url=order_item.design_back_url or design_back_url,
    )


def build_create_order_request(
    order: Order,
    campaign: SalesCampaign | None,
    line_items: list[BurgerPrintsLineItem],
    shipping: BurgerPrintsShippingAddress,
) -> BurgerPrintsCreateOrderRequest:
    return BurgerPrintsCreateOrderRequest(
        shipping_name=shipping,
        line_items=line_items,
        reference_id=str(order.id),
    )


def format_shipping_address_text(details: dict) -> str:
    parts = [
        details.get("street_address"),
        details.get("apt_suite_other"),
        details.get("city"),
        details.get("state"),
        details.get("zipcode"),
        details.get("country"),
    ]
    return ", ".join(p for p in parts if p)
