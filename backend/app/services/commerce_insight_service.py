import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import CampaignStatus, SalesCampaign
from app.models.insight import AIInsight, InsightCategory, InsightSeverity, InsightType
from app.models.order import Order, OrderStatus
from app.services import dashboard_commerce_service


@dataclass
class GeneratedInsight:
    insight_type: InsightType
    category: InsightCategory
    title: str
    body_markdown: str
    severity: InsightSeverity


async def generate_commerce_insights(db: AsyncSession, org_id: uuid.UUID, period_days: int = 30) -> list[GeneratedInsight]:
    overview = await dashboard_commerce_service.get_commerce_overview(db, org_id, period_days)
    kpis = overview.kpis
    setup = overview.setup
    insights: list[GeneratedInsight] = []

    if not setup.has_live_campaign:
        if kpis.draft_campaigns > 0:
            insights.append(
                GeneratedInsight(
                    insight_type=InsightType.RECOMMENDATION,
                    category=InsightCategory.MARKETING,
                    title=f"You have {kpis.draft_campaigns} draft campaign(s) ready to publish",
                    body_markdown=(
                        "Publish a campaign to start selling. Add your design, set pricing, and share the campaign link "
                        "with your audience."
                    ),
                    severity=InsightSeverity.INFO,
                )
            )
        else:
            insights.append(
                GeneratedInsight(
                    insight_type=InsightType.RECOMMENDATION,
                    category=InsightCategory.MARKETING,
                    title="Create your first sales campaign",
                    body_markdown=(
                        "Your storefront is set up but no campaigns are live yet. Create a campaign, upload a design, "
                        "and publish it to start accepting orders."
                    ),
                    severity=InsightSeverity.INFO,
                )
            )

    if kpis.orders_pending > 0:
        insights.append(
            GeneratedInsight(
                insight_type=InsightType.ALERT,
                category=InsightCategory.FINANCIAL,
                title=f"{kpis.orders_pending} order(s) awaiting payment",
                body_markdown=(
                    "These checkout sessions were started but not completed. Follow up with customers or review "
                    "abandoned checkout emails in Storefront settings."
                ),
                severity=InsightSeverity.WARNING,
            )
        )

    if kpis.revenue_change_pct is not None:
        if kpis.revenue_change_pct >= Decimal("10"):
            insights.append(
                GeneratedInsight(
                    insight_type=InsightType.SUMMARY,
                    category=InsightCategory.FINANCIAL,
                    title=f"Revenue up {kpis.revenue_change_pct}% vs prior period",
                    body_markdown=(
                        f"You earned ${kpis.revenue:.2f} in the last {period_days} days with {kpis.orders_count} order(s). "
                        "Keep momentum by promoting your top campaigns."
                    ),
                    severity=InsightSeverity.INFO,
                )
            )
        elif kpis.revenue_change_pct <= Decimal("-10"):
            insights.append(
                GeneratedInsight(
                    insight_type=InsightType.ALERT,
                    category=InsightCategory.FINANCIAL,
                    title=f"Revenue down {abs(kpis.revenue_change_pct)}% vs prior period",
                    body_markdown=(
                        "Sales slowed compared to the previous period. Consider launching a new campaign, "
                        "refreshing designs, or sharing your storefront link on social channels."
                    ),
                    severity=InsightSeverity.WARNING,
                )
            )

    if not setup.has_logo:
        insights.append(
            GeneratedInsight(
                insight_type=InsightType.RECOMMENDATION,
                category=InsightCategory.BLENDED,
                title="Add a logo to build brand trust",
                body_markdown="Upload your store logo in Storefront settings so customers recognize your brand at checkout.",
                severity=InsightSeverity.INFO,
            )
        )

    if overview.top_campaigns:
        top = overview.top_campaigns[0]
        if top.revenue > 0:
            insights.append(
                GeneratedInsight(
                    insight_type=InsightType.SUMMARY,
                    category=InsightCategory.MARKETING,
                    title=f"Top seller: {top.title}",
                    body_markdown=(
                        f'"{top.title}" generated ${top.revenue:.2f} with {top.units_sold} unit(s) sold. '
                        "Consider creating similar campaigns or extending its run dates."
                    ),
                    severity=InsightSeverity.INFO,
                )
            )

    if setup.has_live_campaign and not setup.has_paid_order:
        insights.append(
            GeneratedInsight(
                insight_type=InsightType.RECOMMENDATION,
                category=InsightCategory.BLENDED,
                title="Share your campaign link to get your first sale",
                body_markdown=(
                    "Your campaign is live. Copy the campaign URL from the Campaigns page and share it on social media, "
                    "email, or ads to drive traffic."
                ),
                severity=InsightSeverity.INFO,
            )
        )

    return insights[:6]


async def refresh_stored_insights(db: AsyncSession, org_id: uuid.UUID, period_days: int = 30) -> int:
    """Replace auto-generated commerce insights for this org."""
    generated = await generate_commerce_insights(db, org_id, period_days)

    existing = await db.execute(select(AIInsight).where(AIInsight.organization_id == org_id))
    for row in existing.scalars().all():
        if row.data_context and row.data_context.get("source") == "commerce":
            await db.delete(row)

    now = datetime.now(UTC)
    for item in generated:
        db.add(
            AIInsight(
                organization_id=org_id,
                insight_type=item.insight_type,
                category=item.category,
                title=item.title,
                body_markdown=item.body_markdown,
                severity=item.severity,
                data_context={"source": "commerce"},
                generated_at=now,
            )
        )
    await db.flush()
    return len(generated)


async def ensure_fresh_insights(db: AsyncSession, org_id: uuid.UUID, period_days: int = 30) -> None:
    """Generate insights if none exist from the last 24 hours."""
    recent_cutoff = datetime.now(UTC) - timedelta(hours=24)
    count = (
        await db.execute(
            select(func.count(AIInsight.id)).where(
                AIInsight.organization_id == org_id,
                AIInsight.is_dismissed == False,  # noqa: E712
                AIInsight.generated_at >= recent_cutoff,
            )
        )
    ).scalar() or 0
    if count == 0:
        await refresh_stored_insights(db, org_id, period_days)
