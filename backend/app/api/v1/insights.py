from fastapi import APIRouter, Query
from sqlalchemy import func, select, update

from app.dependencies import DB, CurrentUser
from app.models.insight import AIInsight
from app.schemas.insight import InsightListResponse, InsightResponse, MarkInsightReadRequest
from app.services import commerce_insight_service

router = APIRouter()


@router.post("/refresh")
async def refresh_insights(current_user: CurrentUser, db: DB):
    count = await commerce_insight_service.refresh_stored_insights(db, current_user.organization_id)
    return {"generated": count, "status": "ok"}


@router.get("", response_model=InsightListResponse)
async def list_insights(
    current_user: CurrentUser,
    db: DB,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, le=50),
    category: str | None = Query(default=None),
    severity: str | None = Query(default=None),
):
    org_id = current_user.organization_id
    query = select(AIInsight).where(
        AIInsight.organization_id == org_id,
        AIInsight.is_dismissed == False,  # noqa: E712
    )

    if category:
        query = query.where(AIInsight.category == category)
    if severity:
        query = query.where(AIInsight.severity == severity)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(AIInsight.generated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = [InsightResponse.model_validate(i) for i in result.scalars().all()]

    return InsightListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/mark-read")
async def mark_insights_read(request: MarkInsightReadRequest, current_user: CurrentUser, db: DB):
    await db.execute(
        update(AIInsight)
        .where(
            AIInsight.id.in_(request.insight_ids),
            AIInsight.organization_id == current_user.organization_id,
        )
        .values(is_read=True)
    )
    return {"status": "ok"}


@router.post("/{insight_id}/dismiss")
async def dismiss_insight(insight_id: str, current_user: CurrentUser, db: DB):
    await db.execute(
        update(AIInsight)
        .where(
            AIInsight.id == insight_id,
            AIInsight.organization_id == current_user.organization_id,
        )
        .values(is_dismissed=True)
    )
    return {"status": "ok"}
