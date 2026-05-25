import uuid
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class CartItemInput(BaseModel):
    variant_id: uuid.UUID
    quantity: int = Field(ge=1, le=99)


class AddToCartRequest(BaseModel):
    campaign_slug: str
    session_id: str = Field(min_length=8, max_length=64)
    items: list[CartItemInput] = Field(min_length=1)


class UpdateCartRequest(BaseModel):
    session_id: str
    items: list[CartItemInput]


class CartItemResponse(BaseModel):
    variant_id: uuid.UUID
    variant_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class CartResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    campaign_slug: str
    campaign_title: str
    items: list[CartItemResponse]
    subtotal: Decimal


class SaveEmailRequest(BaseModel):
    session_id: str = Field(min_length=8, max_length=64)
    customer_email: EmailStr


class ShippingAddressInput(BaseModel):
    street_address: str = Field(min_length=1)
    apt_suite_other: str = ""
    city: str = Field(min_length=1)
    state: str = Field(min_length=1)
    zipcode: str = Field(min_length=1)
    country: str = Field(default="US", min_length=2, max_length=2)
    phone_number: str = Field(min_length=5)


class CheckoutRequest(BaseModel):
    session_id: str
    customer_email: EmailStr
    customer_name: str | None = None
    shipping: ShippingAddressInput
    shipping_address: str | None = None
    tip_percent: float | None = Field(default=None, ge=0, le=100)


class CheckoutResponse(BaseModel):
    checkout_url: str
    order_id: uuid.UUID
