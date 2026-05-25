import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ConnectionProvider(str, enum.Enum):
    QUICKBOOKS = "quickbooks"
    XERO = "xero"
    GOOGLE_ADS = "google_ads"
    META_ADS = "meta_ads"


class ConnectionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class Connection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "connections"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[ConnectionProvider] = mapped_column(nullable=False)
    provider_account_id: Mapped[str | None] = mapped_column(String(255))
    credentials_encrypted: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ConnectionStatus] = mapped_column(default=ConnectionStatus.ACTIVE, nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)

    # Relationships
    organization = relationship("Organization", back_populates="connections")
    sync_jobs = relationship("SyncJob", back_populates="connection", cascade="all, delete-orphan")
