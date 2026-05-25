from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class FinancialSummary(BaseModel):
    revenue: Decimal
    expenses: Decimal
    net_income: Decimal
    gross_margin_pct: Decimal
    cash_on_hand: Decimal
    accounts_receivable: Decimal
    accounts_payable: Decimal
    cash_runway_days: int | None = None
    revenue_change_pct: Decimal | None = None


class MarketingSummary(BaseModel):
    total_spend: Decimal
    total_impressions: int
    total_clicks: int
    total_conversions: int
    avg_cpc: Decimal
    avg_ctr: Decimal
    overall_roas: Decimal
    active_campaigns: int
    spend_change_pct: Decimal | None = None


class DashboardOverview(BaseModel):
    period_start: date
    period_end: date
    financial: FinancialSummary
    marketing: MarketingSummary
    marketing_spend_pct_of_revenue: Decimal | None = None
    estimated_cac: Decimal | None = None


class CampaignPerformance(BaseModel):
    campaign_id: str
    campaign_name: str
    platform: str
    spend: Decimal
    impressions: int
    clicks: int
    conversions: int
    roas: Decimal
    status: str
