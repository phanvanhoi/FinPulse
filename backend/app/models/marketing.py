import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class AdPlatform(str, enum.Enum):
    GOOGLE_ADS = "google_ads"
    META_ADS = "meta_ads"


class CampaignStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    REMOVED = "removed"
    ENDED = "ended"


class AdCampaign(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ad_campaigns"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    connection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("connections.id", ondelete="CASCADE"), nullable=False
    )
    platform: Mapped[AdPlatform] = mapped_column(nullable=False)
    external_campaign_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(default=CampaignStatus.ACTIVE)
    objective: Mapped[str | None] = mapped_column(String(255))
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Relationships
    daily_metrics = relationship("CampaignMetricsDaily", back_populates="campaign", cascade="all, delete-orphan")


class CampaignMetricsDaily(Base, UUIDMixin):
    __tablename__ = "campaign_metrics_daily"
    __table_args__ = (
        UniqueConstraint("campaign_id", "date", name="uq_campaign_date"),
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ad_campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    spend: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    revenue_attributed: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # Calculated metrics (stored for query performance)
    cpc: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    ctr: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    roas: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))

    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    campaign = relationship("AdCampaign", back_populates="daily_metrics")
