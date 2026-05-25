import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductVariantResponse(BaseModel):
    id: uuid.UUID
    name: str
    sku: str | None = None
    base_price: Decimal

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    category: str
    image_url: str | None = None
    variants: list[ProductVariantResponse] = []

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
