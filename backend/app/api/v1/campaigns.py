import uuid

from fastapi import APIRouter, File, Query, UploadFile

from app.dependencies import DB, CurrentUser
from app.models.organization import Organization
from app.schemas.campaign import (
    CampaignCreateRequest,
    CampaignListResponse,
    CampaignResponse,
    CampaignUpdateRequest,
    PublicCampaignResponse,
)
from app.services import campaign_service, store_service

router = APIRouter()


async def _get_store(db, organization_id: uuid.UUID):
    org = await db.get(Organization, organization_id)
    if org is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Organization not found")
    return await store_service.get_or_create_store(db, org)


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(current_user: CurrentUser, db: DB):
    campaigns, total = await campaign_service.list_campaigns(db, current_user.organization_id)
    return CampaignListResponse(
        campaigns=[CampaignResponse(**c) for c in campaigns],
        total=total,
    )


@router.post("", response_model=CampaignResponse)
async def create_campaign(payload: CampaignCreateRequest, current_user: CurrentUser, db: DB):
    store = await _get_store(db, current_user.organization_id)
    campaign = await campaign_service.create_campaign(db, store, payload)
    return CampaignResponse(**campaign)


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: uuid.UUID, current_user: CurrentUser, db: DB):
    campaign = await campaign_service.get_campaign(db, current_user.organization_id, campaign_id)
    return CampaignResponse(**campaign)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: uuid.UUID, payload: CampaignUpdateRequest, current_user: CurrentUser, db: DB
):
    campaign = await campaign_service.update_campaign(db, current_user.organization_id, campaign_id, payload)
    return CampaignResponse(**campaign)


@router.post("/{campaign_id}/design", response_model=CampaignResponse)
async def upload_design(
    campaign_id: uuid.UUID,
    current_user: CurrentUser,
    db: DB,
    file: UploadFile = File(...),
    side: str = Query(default="front", pattern="^(front|back)$"),
):
    await campaign_service.get_campaign(db, current_user.organization_id, campaign_id)
    from app.models.campaign import SalesCampaign

    campaign = await db.get(SalesCampaign, campaign_id)
    if not campaign:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Campaign not found")

    content = await file.read()
    ext = campaign_service.validate_design_file(file.filename or "design.png", file.content_type, len(content))
    await campaign_service.save_campaign_design(campaign, content, ext, side=side)
    await db.flush()
    updated = await campaign_service.get_campaign(db, current_user.organization_id, campaign_id)
    return CampaignResponse(**updated)


@router.post("/{campaign_id}/publish", response_model=CampaignResponse)
async def publish_campaign(campaign_id: uuid.UUID, current_user: CurrentUser, db: DB):
    campaign = await campaign_service.publish_campaign(db, current_user.organization_id, campaign_id)
    return CampaignResponse(**campaign)


@router.post("/{campaign_id}/end", response_model=CampaignResponse)
async def end_campaign(campaign_id: uuid.UUID, current_user: CurrentUser, db: DB):
    campaign = await campaign_service.end_campaign(db, current_user.organization_id, campaign_id)
    return CampaignResponse(**campaign)


@router.get("/public/{slug}", response_model=PublicCampaignResponse)
async def get_public_campaign(slug: str, db: DB):
    campaign = await campaign_service.get_public_campaign(db, slug)
    return PublicCampaignResponse(**campaign)


@router.get("/public/store/{store_slug}/live")
async def list_store_live_campaigns(store_slug: str, db: DB):
    campaigns = await campaign_service.list_live_campaigns_for_store(db, store_slug)
    return {"campaigns": campaigns}
