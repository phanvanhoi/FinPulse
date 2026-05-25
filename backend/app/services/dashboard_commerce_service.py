import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.campaign import CampaignStatus, SalesCampaign
from app.models.order import Order, OrderItem, OrderStatus
from app.models.organization import Organization
from app.models.store import Store
from app.models.financial import FinancialPeriod, PeriodType
from app.models.marketing import AdCampaign, CampaignMetricsDaily, CampaignStatus as AdCampaignStatus
from app.services import store_service
from app.schemas.dashboard_commerce import (
    CommerceDashboardOverview,
    CommerceInsightPreview,
    CommerceKPIs,
    FinanceSnapshot,
    MarketingSnapshot,
    OrdersByStatus,
    RecentOrderSummary,
    RevenueByDay,
    SetupStatus,
    StoreSummary,
    TopCampaignSummary,
)


def _period_bounds(days: int) -> tuple[date, date]:
    period_end = date.today()
    period_start = period_end - timedelta(days=days - 1)
    return period_start, period_end


def _previous_period_bounds(period_start: date, days: int) -> tuple[date, date]:
    prev_end = period_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)
    return prev_start, prev_end


def _start_of_day(d: date) -> datetime:
    return datetime.combine(d, datetime.min.time(), tzinfo=UTC)


def _end_of_day(d: date) -> datetime:
    return datetime.combine(d, datetime.max.time(), tzinfo=UTC)


def _fill_revenue_by_day(
    daily_map: dict[date, RevenueByDay],
    period_start: date,
    period_end: date,
) -> list[RevenueByDay]:
    result: list[RevenueByDay] = []
    current = period_start
    while current <= period_end:
        if current in daily_map:
            result.append(daily_map[current])
        else:
            result.append(RevenueByDay(date=current, revenue=Decimal("0"), orders=0))
        current += timedelta(days=1)
    return result


async def _sum_paid_revenue(
    db: AsyncSession,
    org_id: uuid.UUID,
    start: date,
    end: date,
) -> Decimal:
    result = await db.execute(
        select(func.coalesce(func.sum(Order.total), 0)).where(
            Order.organization_id == org_id,
            Order.status == OrderStatus.PAID,
            Order.created_at >= _start_of_day(start),
            Order.created_at <= _end_of_day(end),
        )
    )
    return Decimal(str(result.scalar() or 0))


async def get_commerce_overview(
    db: AsyncSession,
    org_id: uuid.UUID,
    period_days: int = 30,
    *,
    include_insights: bool = True,
) -> CommerceDashboardOverview:
    period_start, period_end = _period_bounds(period_days)
    prev_start, prev_end = _previous_period_bounds(period_start, period_days)

    period_filter = (
        Order.organization_id == org_id,
        Order.created_at >= _start_of_day(period_start),
        Order.created_at <= _end_of_day(period_end),
    )

    revenue = await _sum_paid_revenue(db, org_id, period_start, period_end)
    prev_revenue = await _sum_paid_revenue(db, org_id, prev_start, prev_end)

    revenue_change_pct = None
    if prev_revenue > 0:
        revenue_change_pct = ((revenue - prev_revenue) / prev_revenue * Decimal("100")).quantize(Decimal("0.1"))

    orders_count_result = await db.execute(
        select(func.count(Order.id)).where(*period_filter)
    )
    orders_count = orders_count_result.scalar() or 0

    orders_pending_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.organization_id == org_id,
            Order.status == OrderStatus.PENDING,
        )
    )
    orders_pending = orders_pending_result.scalar() or 0

    units_result = await db.execute(
        select(func.coalesce(func.sum(OrderItem.quantity), 0))
        .join(Order, OrderItem.order_id == Order.id)
        .where(
            Order.organization_id == org_id,
            Order.status == OrderStatus.PAID,
            Order.created_at >= _start_of_day(period_start),
            Order.created_at <= _end_of_day(period_end),
        )
    )
    units_sold = int(units_result.scalar() or 0)

    live_result = await db.execute(
        select(func.count(SalesCampaign.id)).where(
            SalesCampaign.organization_id == org_id,
            SalesCampaign.status == CampaignStatus.LIVE,
        )
    )
    live_campaigns = live_result.scalar() or 0

    draft_result = await db.execute(
        select(func.count(SalesCampaign.id)).where(
            SalesCampaign.organization_id == org_id,
            SalesCampaign.status == CampaignStatus.DRAFT,
        )
    )
    draft_campaigns = draft_result.scalar() or 0

    paid_orders_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.organization_id == org_id,
            Order.status == OrderStatus.PAID,
            Order.created_at >= _start_of_day(period_start),
            Order.created_at <= _end_of_day(period_end),
        )
    )
    paid_orders_count = paid_orders_result.scalar() or 0
    avg_order_value = (revenue / paid_orders_count) if paid_orders_count else Decimal("0")

    revenue_by_day_rows = await db.execute(
        select(
            cast(Order.created_at, Date).label("day"),
            func.coalesce(func.sum(Order.total), 0).label("revenue"),
            func.count(Order.id).label("orders"),
        )
        .where(
            Order.organization_id == org_id,
            Order.status == OrderStatus.PAID,
            Order.created_at >= _start_of_day(period_start),
            Order.created_at <= _end_of_day(period_end),
        )
        .group_by(cast(Order.created_at, Date))
        .order_by(cast(Order.created_at, Date))
    )
    daily_map = {
        row.day: RevenueByDay(date=row.day, revenue=Decimal(str(row.revenue)), orders=row.orders)
        for row in revenue_by_day_rows.all()
    }
    revenue_by_day = _fill_revenue_by_day(daily_map, period_start, period_end)

    status_rows = await db.execute(
        select(Order.status, func.count(Order.id))
        .where(*period_filter)
        .group_by(Order.status)
    )
    orders_by_status = [
        OrdersByStatus(status=row[0].value, count=row[1]) for row in status_rows.all()
    ]

    top_campaign_rows = await db.execute(
        select(
            SalesCampaign.id,
            SalesCampaign.title,
            SalesCampaign.slug,
            SalesCampaign.status,
            SalesCampaign.units_sold,
            func.coalesce(func.sum(Order.total), 0).label("revenue"),
        )
        .outerjoin(
            Order,
            (Order.campaign_id == SalesCampaign.id)
            & (Order.status == OrderStatus.PAID)
            & (Order.created_at >= _start_of_day(period_start))
            & (Order.created_at <= _end_of_day(period_end)),
        )
        .where(SalesCampaign.organization_id == org_id)
        .group_by(SalesCampaign.id)
        .order_by(func.coalesce(func.sum(Order.total), 0).desc())
        .limit(5)
    )
    top_campaigns = [
        TopCampaignSummary(
            id=str(row.id),
            title=row.title,
            slug=row.slug,
            status=row.status.value,
            units_sold=row.units_sold,
            revenue=Decimal(str(row.revenue or 0)),
        )
        for row in top_campaign_rows.all()
    ]

    recent_rows = await db.execute(
        select(Order, SalesCampaign.title)
        .outerjoin(SalesCampaign, Order.campaign_id == SalesCampaign.id)
        .where(Order.organization_id == org_id)
        .order_by(Order.created_at.desc())
        .limit(10)
    )
    recent_orders = [
        RecentOrderSummary(
            id=str(order.id),
            customer_email=order.customer_email,
            total=order.total,
            status=order.status.value,
            created_at=order.created_at,
            campaign_title=campaign_title,
        )
        for order, campaign_title in recent_rows.all()
    ]

    store_result = await db.execute(select(Store).where(Store.organization_id == org_id))
    store = store_result.scalar_one_or_none()
    if store is None:
        org_result = await db.execute(select(Organization).where(Organization.id == org_id))
        org = org_result.scalar_one_or_none()
        if org:
            store = await store_service.get_or_create_store(db, org)

    store_summary = None
    has_logo = False
    if store:
        has_logo = bool(store.logo_url)
        base_url = settings.FRONTEND_URL.rstrip("/")
        store_summary = StoreSummary(
            name=store.name,
            slug=store.slug,
            has_logo=has_logo,
            storefront_url=f"{base_url}/store/{store.slug}",
        )

    paid_total_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.organization_id == org_id,
            Order.status == OrderStatus.PAID,
        )
    )
    has_paid_order = (paid_total_result.scalar() or 0) > 0

    setup = SetupStatus(
        has_logo=has_logo,
        has_live_campaign=live_campaigns > 0,
        has_paid_order=has_paid_order,
    )

    kpis = CommerceKPIs(
        revenue=revenue,
        revenue_change_pct=revenue_change_pct,
        orders_count=orders_count,
        orders_pending=orders_pending,
        units_sold=units_sold,
        live_campaigns=live_campaigns,
        draft_campaigns=draft_campaigns,
        avg_order_value=avg_order_value.quantize(Decimal("0.01")),
    )

    insights: list[CommerceInsightPreview] = []
    if include_insights:
        from app.services import commerce_insight_service

        generated_insights = await commerce_insight_service.generate_commerce_insights(db, org_id, period_days)
        insights = [
            CommerceInsightPreview(
                insight_type=i.insight_type.value,
                category=i.category.value,
                title=i.title,
                body_markdown=i.body_markdown,
                severity=i.severity.value,
            )
            for i in generated_insights
        ]

    finance_snapshot = await _build_finance_snapshot(db, org_id, revenue)
    marketing_snapshot = await _build_marketing_snapshot(db, org_id, live_campaigns, units_sold, period_start, period_end)

    return CommerceDashboardOverview(
        period_start=period_start,
        period_end=period_end,
        kpis=kpis,
        revenue_by_day=revenue_by_day,
        orders_by_status=orders_by_status,
        top_campaigns=top_campaigns,
        recent_orders=recent_orders,
        store=store_summary,
        setup=setup,
        insights=insights,
        finance_snapshot=finance_snapshot,
        marketing_snapshot=marketing_snapshot,
    )


async def _build_finance_snapshot(db: AsyncSession, org_id: uuid.UUID, commerce_revenue: Decimal) -> FinanceSnapshot:
    fin_result = await db.execute(
        select(FinancialPeriod)
        .where(FinancialPeriod.organization_id == org_id, FinancialPeriod.period_type == PeriodType.MONTHLY)
        .order_by(FinancialPeriod.end_date.desc())
        .limit(1)
    )
    fin_period = fin_result.scalar_one_or_none()
    if fin_period and fin_period.revenue > 0:
        return FinanceSnapshot(
            revenue=fin_period.revenue,
            net_income=fin_period.net_income,
            cash_on_hand=fin_period.cash_on_hand,
            source="accounting",
            detail="From connected accounting data",
        )
    return FinanceSnapshot(
        revenue=commerce_revenue,
        net_income=None,
        cash_on_hand=None,
        source="commerce",
        detail="From paid orders in your store",
    )


async def _build_marketing_snapshot(
    db: AsyncSession,
    org_id: uuid.UUID,
    live_campaigns: int,
    units_sold: int,
    period_start: date,
    period_end: date,
) -> MarketingSnapshot:
    mkt_result = await db.execute(
        select(
            func.coalesce(func.sum(CampaignMetricsDaily.spend), 0).label("spend"),
            func.coalesce(func.sum(CampaignMetricsDaily.revenue_attributed), 0).label("revenue"),
        )
        .join(AdCampaign, CampaignMetricsDaily.campaign_id == AdCampaign.id)
        .where(
            AdCampaign.organization_id == org_id,
            CampaignMetricsDaily.date >= period_start,
            CampaignMetricsDaily.date <= period_end,
        )
    )
    mkt = mkt_result.one()
    ad_spend = Decimal(str(mkt.spend or 0))
    ad_revenue = Decimal(str(mkt.revenue or 0))

    if ad_spend > 0:
        roas = (ad_revenue / ad_spend) if ad_spend else Decimal("0")
        active_ads = (
            await db.execute(
                select(func.count(AdCampaign.id)).where(
                    AdCampaign.organization_id == org_id,
                    AdCampaign.status == AdCampaignStatus.ACTIVE,
                )
            )
        ).scalar() or 0
        return MarketingSnapshot(
            live_campaigns=active_ads,
            units_sold=units_sold,
            ad_spend=ad_spend,
            overall_roas=roas.quantize(Decimal("0.1")),
            source="ads",
            detail="From connected ad platforms",
        )
    return MarketingSnapshot(
        live_campaigns=live_campaigns,
        units_sold=units_sold,
        ad_spend=None,
        overall_roas=None,
        source="commerce",
        detail="From your sales campaigns",
    )
