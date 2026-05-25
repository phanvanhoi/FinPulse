import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    LIVE = "live"
    ENDED = "ended"


class SalesCampaign(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sales_campaigns"
    __table_args__ = (UniqueConstraint("store_id", "slug", name="uq_store_campaign_slug"),)

    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    design_image_url: Mapped[str | None] = mapped_column(String(500))
    design_back_url: Mapped[str | None] = mapped_column(String(500))
    print_location: Mapped[str] = mapped_column(String(20), default="front", nullable=False)
    retail_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, name="campaignstatus"), default=CampaignStatus.DRAFT, nullable=False
    )
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    units_sold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    store = relationship("Store", back_populates="campaigns")
    product = relationship("Product")
    items = relationship("CampaignVariant", back_populates="campaign", cascade="all, delete-orphan")


class CampaignVariant(Base, UUIDMixin):
    __tablename__ = "campaign_variants"
    __table_args__ = (UniqueConstraint("campaign_id", "variant_id", name="uq_campaign_variant"),)

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    campaign = relationship("SalesCampaign", back_populates="items")
    variant = relationship("ProductVariant")
