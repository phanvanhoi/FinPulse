import enum
import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class SubscriptionTier(str, enum.Enum):
    FREE_TRIAL = "free_trial"
    STARTER = "starter"
    GROWTH = "growth"
    PRO = "pro"


class Organization(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        default=SubscriptionTier.FREE_TRIAL, nullable=False
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255))
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    connections = relationship("Connection", back_populates="organization", cascade="all, delete-orphan")
    store = relationship("Store", back_populates="organization", uselist=False, cascade="all, delete-orphan")
