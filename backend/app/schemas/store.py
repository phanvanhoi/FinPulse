import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class StoreResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    slug: str
    logo_url: str | None = None
    favicon_url: str | None = None
    custom_domain: str | None = None
    domain_verification_status: str
    domain_verification_token: str | None = None
    tips_enabled: bool
    tip_options: list[int | float]
    facebook_pixel_id: str | None = None
    google_analytics_id: str | None = None
    abandoned_checkout_enabled: bool
    abandoned_checkout_delay_minutes: int
    abandoned_checkout_email_subject: str | None = None
    abandoned_checkout_email_body: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StoreUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    tips_enabled: bool | None = None
    tip_options: list[int | float] | None = None
    facebook_pixel_id: str | None = Field(default=None, max_length=50)
    google_analytics_id: str | None = Field(default=None, max_length=50)
    abandoned_checkout_enabled: bool | None = None
    abandoned_checkout_delay_minutes: int | None = Field(default=None, ge=15, le=1440)
    abandoned_checkout_email_subject: str | None = Field(default=None, max_length=255)
    abandoned_checkout_email_body: str | None = None

    @field_validator("tip_options")
    @classmethod
    def validate_tip_options(cls, value: list[int | float] | None) -> list[int | float] | None:
        if value is None:
            return value
        if not value:
            raise ValueError("At least one tip option is required")
        if any(option <= 0 for option in value):
            raise ValueError("Tip options must be positive")
        return value


class SetDomainRequest(BaseModel):
    custom_domain: str = Field(min_length=3, max_length=255)

    @field_validator("custom_domain")
    @classmethod
    def normalize_domain(cls, value: str) -> str:
        domain = value.strip().lower()
        if domain.startswith("http://") or domain.startswith("https://"):
            raise ValueError("Domain should not include protocol")
        if "/" in domain:
            raise ValueError("Domain should not include path")
        return domain


class DomainVerificationResponse(BaseModel):
    custom_domain: str
    verification_status: str
    verification_token: str | None = None
    dns_record_name: str | None = None
    dns_record_value: str | None = None
    instructions: str | None = None


class PublicStoreResponse(BaseModel):
    name: str
    slug: str
    logo_url: str | None = None
    facebook_pixel_id: str | None = None
    google_analytics_id: str | None = None

    model_config = {"from_attributes": True}
