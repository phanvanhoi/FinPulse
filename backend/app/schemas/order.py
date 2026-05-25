import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    variant_name: str
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    provider_sku: str | None = None

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID | None = None
    campaign_title: str | None = None
    campaign_slug: str | None = None
    customer_email: str
    customer_name: str | None = None
    subtotal: Decimal
    tip_amount: Decimal
    total: Decimal
    status: str
    fulfillment_provider: str | None = None
    external_order_id: str | None = None
    fulfillment_status: str | None = None
    fulfillment_error: str | None = None
    tracking_number: str | None = None
    fulfillment_submitted_at: datetime | None = None
    items: list[OrderItemResponse]
    created_at: datetime
    facebook_pixel_id: str | None = None
    google_analytics_id: str | None = None

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int
