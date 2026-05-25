import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class PeriodType(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class FinancialPeriod(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "financial_periods"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period_type: Mapped[PeriodType] = mapped_column(nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Income Statement
    revenue: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    cogs: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    gross_profit: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    operating_expenses: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    net_income: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)

    # Balance Sheet
    total_assets: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    total_liabilities: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    equity: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)

    # Cash
    cash_on_hand: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    accounts_receivable: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    accounts_payable: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)

    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class FinancialTransaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "financial_transactions"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    external_id: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[TransactionType] = mapped_column(nullable=False)
    category: Mapped[str | None] = mapped_column(String(255))
    subcategory: Mapped[str | None] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
