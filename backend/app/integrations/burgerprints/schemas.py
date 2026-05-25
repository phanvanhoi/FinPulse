from decimal import Decimal

from pydantic import BaseModel, Field


class BurgerPrintsShippingAddress(BaseModel):
    full_name: str
    email: str
    phone_number: str
    country: str
    state: str
    city: str
    street_address: str
    apt_suite_other: str = ""
    zipcode: str


class BurgerPrintsLineItem(BaseModel):
    sku: str
    quantity: int = Field(ge=1)
    design_front_url: str | None = None
    design_back_url: str | None = None
    mockup_front_url: str | None = None
    mockup_back_url: str | None = None


class BurgerPrintsCreateOrderRequest(BaseModel):
    shipping_name: BurgerPrintsShippingAddress
    line_items: list[BurgerPrintsLineItem] = Field(min_length=1)
    reference_id: str | None = None


class BurgerPrintsOrderResult(BaseModel):
    order_id: str
    status: str | None = None
    raw: dict | None = None


class BurgerPrintsSkuRow(BaseModel):
    """One row from a BurgerPrints SKU CSV export."""

    product_name: str
    product_code: str
    color: str
    size: str
    fulfillment_location: str
    provider_sku: str
    base_price: Decimal | None = None
    category: str = "apparel"
