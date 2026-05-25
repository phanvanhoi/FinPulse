import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CampaignVariantInput(BaseModel):
    variant_id: uuid.UUID
    price: Decimal = Field(gt=0)


class CampaignCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    product_id: uuid.UUID
    description: str | None = None
    retail_price: Decimal = Field(gt=0)
    variant_prices: list[CampaignVariantInput] = Field(min_length=1)
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class CampaignUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    retail_price: Decimal | None = Field(default=None, gt=0)
    variant_prices: list[CampaignVariantInput] | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class CampaignVariantResponse(BaseModel):
    variant_id: uuid.UUID
    variant_name: str
    price: Decimal

    model_config = {"from_attributes": True}


class CampaignResponse(BaseModel):
    id: uuid.UUID
    store_id: uuid.UUID
    product_id: uuid.UUID
    product_name: str | None = None
    title: str
    slug: str
    description: str | None = None
    design_image_url: str | None = None
    retail_price: Decimal
    status: str
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    units_sold: int
    variants: list[CampaignVariantResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CampaignListResponse(BaseModel):
    campaigns: list[CampaignResponse]
    total: int


class PublicCampaignResponse(BaseModel):
    id: uuid.UUID
    title: str
    slug: str
    description: str | None = None
    design_image_url: str | None = None
    retail_price: Decimal
    status: str
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    product_name: str
    product_image_url: str | None = None
    variants: list[CampaignVariantResponse]
    store_name: str
    store_slug: str
    store_logo_url: str | None = None
    tips_enabled: bool
    tip_options: list[int | float]
    facebook_pixel_id: str | None = None
    google_analytics_id: str | None = None

    model_config = {"from_attributes": True}
