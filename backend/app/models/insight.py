import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin


class InsightType(str, enum.Enum):
    ALERT = "alert"
    RECOMMENDATION = "recommendation"
    SUMMARY = "summary"
    ANOMALY = "anomaly"


class InsightCategory(str, enum.Enum):
    FINANCIAL = "financial"
    MARKETING = "marketing"
    BLENDED = "blended"


class InsightSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AIInsight(Base, UUIDMixin):
    __tablename__ = "ai_insights"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    insight_type: Mapped[InsightType] = mapped_column(nullable=False)
    category: Mapped[InsightCategory] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[InsightSeverity] = mapped_column(default=InsightSeverity.INFO)
    data_context: Mapped[dict | None] = mapped_column(JSONB)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AlertOperator(str, enum.Enum):
    LT = "lt"
    GT = "gt"
    CHANGE_PCT = "change_pct"


class AlertConfig(Base, UUIDMixin):
    __tablename__ = "alerts_config"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    operator: Mapped[AlertOperator] = mapped_column(nullable=False)
    threshold_value: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_channels: Mapped[dict | None] = mapped_column(JSONB, default=lambda: ["in_app", "email"])
