from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.dependencies import DB, CurrentUser
from app.models.financial import FinancialPeriod, PeriodType
from app.models.marketing import AdCampaign, CampaignMetricsDaily, CampaignStatus
from app.schemas.dashboard import (
    CampaignPerformance,
    DashboardOverview,
    FinancialSummary,
    MarketingSummary,
)

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    current_user: CurrentUser,
    db: DB,
    period_start: date = Query(default=None),
    period_end: date = Query(default=None),
):
    org_id = current_user.organization_id

    if not period_end:
        period_end = date.today()
    if not period_start:
        period_start = period_end - timedelta(days=30)

    # Fetch latest financial period
    fin_result = await db.execute(
        select(FinancialPeriod)
        .where(
            FinancialPeriod.organization_id == org_id,
            FinancialPeriod.period_type == PeriodType.MONTHLY,
        )
        .order_by(FinancialPeriod.end_date.desc())
        .limit(1)
    )
    fin_period = fin_result.scalar_one_or_none()

    # Aggregate marketing metrics for period
    mkt_result = await db.execute(
        select(
            func.sum(CampaignMetricsDaily.spend).label("total_spend"),
            func.sum(CampaignMetricsDaily.impressions).label("total_impressions"),
            func.sum(CampaignMetricsDaily.clicks).label("total_clicks"),
            func.sum(CampaignMetricsDaily.conversions).label("total_conversions"),
            func.sum(CampaignMetricsDaily.revenue_attributed).label("total_revenue"),
        )
        .join(AdCampaign, CampaignMetricsDaily.campaign_id == AdCampaign.id)
        .where(
            AdCampaign.organization_id == org_id,
            CampaignMetricsDaily.date >= period_start,
            CampaignMetricsDaily.date <= period_end,
        )
    )
    mkt = mkt_result.one()

    # Count active campaigns
    active_count = await db.execute(
        select(func.count(AdCampaign.id)).where(
            AdCampaign.organization_id == org_id,
            AdCampaign.status == CampaignStatus.ACTIVE,
        )
    )

    total_spend = mkt.total_spend or Decimal("0")
    total_clicks = mkt.total_clicks or 0
    total_impressions = mkt.total_impressions or 0
    total_conversions = mkt.total_conversions or 0
    total_mkt_revenue = mkt.total_revenue or Decimal("0")

    revenue = fin_period.revenue if fin_period else Decimal("0")
    expenses = fin_period.operating_expenses if fin_period else Decimal("0")
    net_income = fin_period.net_income if fin_period else Decimal("0")
    gross_profit = fin_period.gross_profit if fin_period else Decimal("0")

    financial = FinancialSummary(
        revenue=revenue,
        expenses=expenses,
        net_income=net_income,
        gross_margin_pct=(gross_profit / revenue * 100) if revenue else Decimal("0"),
        cash_on_hand=fin_period.cash_on_hand if fin_period else Decimal("0"),
        accounts_receivable=fin_period.accounts_receivable if fin_period else Decimal("0"),
        accounts_payable=fin_period.accounts_payable if fin_period else Decimal("0"),
    )

    marketing = MarketingSummary(
        total_spend=total_spend,
        total_impressions=total_impressions,
        total_clicks=total_clicks,
        total_conversions=total_conversions,
        avg_cpc=(total_spend / total_clicks) if total_clicks else Decimal("0"),
        avg_ctr=(Decimal(total_clicks) / Decimal(total_impressions) * 100) if total_impressions else Decimal("0"),
        overall_roas=(total_mkt_revenue / total_spend) if total_spend else Decimal("0"),
        active_campaigns=active_count.scalar() or 0,
    )

    return DashboardOverview(
        period_start=period_start,
        period_end=period_end,
        financial=financial,
        marketing=marketing,
        marketing_spend_pct_of_revenue=(total_spend / revenue * 100) if revenue else None,
        estimated_cac=(total_spend / total_conversions) if total_conversions else None,
    )


@router.get("/campaigns", response_model=list[CampaignPerformance])
async def get_campaign_performance(
    current_user: CurrentUser,
    db: DB,
    period_start: date = Query(default=None),
    period_end: date = Query(default=None),
    limit: int = Query(default=20, le=100),
):
    org_id = current_user.organization_id

    if not period_end:
        period_end = date.today()
    if not period_start:
        period_start = period_end - timedelta(days=30)

    result = await db.execute(
        select(
            AdCampaign.id,
            AdCampaign.name,
            AdCampaign.platform,
            AdCampaign.status,
            func.sum(CampaignMetricsDaily.spend).label("spend"),
            func.sum(CampaignMetricsDaily.impressions).label("impressions"),
            func.sum(CampaignMetricsDaily.clicks).label("clicks"),
            func.sum(CampaignMetricsDaily.conversions).label("conversions"),
            func.sum(CampaignMetricsDaily.revenue_attributed).label("revenue"),
        )
        .join(CampaignMetricsDaily, AdCampaign.id == CampaignMetricsDaily.campaign_id)
        .where(
            AdCampaign.organization_id == org_id,
            CampaignMetricsDaily.date >= period_start,
            CampaignMetricsDaily.date <= period_end,
        )
        .group_by(AdCampaign.id)
        .order_by(func.sum(CampaignMetricsDaily.spend).desc())
        .limit(limit)
    )

    campaigns = []
    for row in result.all():
        spend = row.spend or Decimal("0")
        revenue = row.revenue or Decimal("0")
        campaigns.append(
            CampaignPerformance(
                campaign_id=str(row.id),
                campaign_name=row.name,
                platform=row.platform.value,
                spend=spend,
                impressions=row.impressions or 0,
                clicks=row.clicks or 0,
                conversions=row.conversions or 0,
                roas=(revenue / spend) if spend else Decimal("0"),
                status=row.status.value,
            )
        )
    return campaigns
