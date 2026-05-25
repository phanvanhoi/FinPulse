from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class CommerceKPIs(BaseModel):
    revenue: Decimal
    revenue_change_pct: Decimal | None = None
    orders_count: int
    orders_pending: int
    units_sold: int
    live_campaigns: int
    draft_campaigns: int
    avg_order_value: Decimal


class RevenueByDay(BaseModel):
    date: date
    revenue: Decimal
    orders: int


class OrdersByStatus(BaseModel):
    status: str
    count: int


class TopCampaignSummary(BaseModel):
    id: str
    title: str
    slug: str
    status: str
    units_sold: int
    revenue: Decimal


class RecentOrderSummary(BaseModel):
    id: str
    customer_email: str
    total: Decimal
    status: str
    created_at: datetime
    campaign_title: str | None = None


class StoreSummary(BaseModel):
    name: str
    slug: str
    has_logo: bool
    storefront_url: str


class SetupStatus(BaseModel):
    has_logo: bool
    has_live_campaign: bool
    has_paid_order: bool


class CommerceInsightPreview(BaseModel):
    insight_type: str
    category: str
    title: str
    body_markdown: str
    severity: str


class FinanceSnapshot(BaseModel):
    revenue: Decimal
    net_income: Decimal | None = None
    cash_on_hand: Decimal | None = None
    source: str = "commerce"
    detail: str


class MarketingSnapshot(BaseModel):
    live_campaigns: int
    units_sold: int
    ad_spend: Decimal | None = None
    overall_roas: Decimal | None = None
    source: str = "commerce"
    detail: str


class CommerceDashboardOverview(BaseModel):
    period_start: date
    period_end: date
    kpis: CommerceKPIs
    revenue_by_day: list[RevenueByDay]
    orders_by_status: list[OrdersByStatus]
    top_campaigns: list[TopCampaignSummary]
    recent_orders: list[RecentOrderSummary]
    store: StoreSummary | None = None
    setup: SetupStatus
    insights: list[CommerceInsightPreview] = []
    finance_snapshot: FinanceSnapshot | None = None
    marketing_snapshot: MarketingSnapshot | None = None
