import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductVariantResponse(BaseModel):
    id: uuid.UUID
    name: str
    sku: str | None = None
    base_price: Decimal
    provider_sku: str | None = None
    color: str | None = None

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    category: str
    image_url: str | None = None
    fulfillment_provider: str | None = None
    external_product_code: str | None = None
    fulfillment_location: str | None = None
    variants: list[ProductVariantResponse] = []

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
