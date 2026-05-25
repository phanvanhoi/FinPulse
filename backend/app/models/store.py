import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class DomainVerificationStatus(str, enum.Enum):
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"


class Store(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "stores"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Branding
    logo_url: Mapped[str | None] = mapped_column(String(500))
    favicon_url: Mapped[str | None] = mapped_column(String(500))

    # Custom domain
    custom_domain: Mapped[str | None] = mapped_column(String(255))
    domain_verification_token: Mapped[str | None] = mapped_column(String(64))
    domain_verification_status: Mapped[DomainVerificationStatus] = mapped_column(
        Enum(DomainVerificationStatus, name="domainverificationstatus"),
        default=DomainVerificationStatus.UNVERIFIED,
        nullable=False,
    )

    # Tips at checkout
    tips_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tip_options: Mapped[list] = mapped_column(JSONB, default=lambda: [10, 15, 20], nullable=False)

    # Tracking
    facebook_pixel_id: Mapped[str | None] = mapped_column(String(50))
    google_analytics_id: Mapped[str | None] = mapped_column(String(50))

    # Abandoned checkout recovery
    abandoned_checkout_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    abandoned_checkout_delay_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    abandoned_checkout_email_subject: Mapped[str | None] = mapped_column(String(255))
    abandoned_checkout_email_body: Mapped[str | None] = mapped_column(Text)

    # Relationships
    organization = relationship("Organization", back_populates="store")
    campaigns = relationship("SalesCampaign", back_populates="store", cascade="all, delete-orphan")
