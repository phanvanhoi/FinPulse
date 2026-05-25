import re
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.campaign import CampaignStatus, CampaignVariant, SalesCampaign
from app.models.product import Product, ProductVariant
from app.models.store import Store
from app.schemas.campaign import CampaignCreateRequest, CampaignUpdateRequest, CampaignVariantInput

ALLOWED_DESIGN_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "campaign"


async def _unique_slug(db: AsyncSession, store_id: uuid.UUID, base: str, exclude_id: uuid.UUID | None = None) -> str:
    slug = base
    n = 1
    while True:
        q = select(SalesCampaign).where(SalesCampaign.store_id == store_id, SalesCampaign.slug == slug)
        if exclude_id:
            q = q.where(SalesCampaign.id != exclude_id)
        if (await db.execute(q)).scalar_one_or_none() is None:
            return slug
        n += 1
        slug = f"{base}-{n}"


async def _validate_product_and_variants(
    db: AsyncSession, product_id: uuid.UUID, variant_prices: list[CampaignVariantInput]
) -> Product:
    product = await db.get(Product, product_id, options=[selectinload(Product.variants)])
    if not product:
        raise NotFoundError("Product not found")

    variant_ids = {v.id for v in product.variants}
    for vp in variant_prices:
        if vp.variant_id not in variant_ids:
            raise BadRequestError(f"Variant {vp.variant_id} does not belong to selected product")
    return product


async def _set_campaign_variants(
    db: AsyncSession, campaign: SalesCampaign, variant_prices: list[CampaignVariantInput]
) -> None:
    existing = await db.execute(select(CampaignVariant).where(CampaignVariant.campaign_id == campaign.id))
    for row in existing.scalars().all():
        await db.delete(row)
    await db.flush()

    for vp in variant_prices:
        db.add(CampaignVariant(campaign_id=campaign.id, variant_id=vp.variant_id, price=vp.price))


def _campaign_to_response(campaign: SalesCampaign, product_name: str | None = None) -> dict:
    variants = []
    for item in campaign.items:
        variants.append(
            {
                "variant_id": item.variant_id,
                "variant_name": item.variant.name if item.variant else "",
                "price": item.price,
            }
        )
    return {
        "id": campaign.id,
        "store_id": campaign.store_id,
        "product_id": campaign.product_id,
        "product_name": product_name or (campaign.product.name if campaign.product else None),
        "title": campaign.title,
        "slug": campaign.slug,
        "description": campaign.description,
        "design_image_url": campaign.design_image_url,
        "retail_price": campaign.retail_price,
        "status": campaign.status.value,
        "starts_at": campaign.starts_at,
        "ends_at": campaign.ends_at,
        "units_sold": campaign.units_sold,
        "variants": variants,
        "created_at": campaign.created_at,
        "updated_at": campaign.updated_at,
    }


async def create_campaign(db: AsyncSession, store: Store, payload: CampaignCreateRequest) -> dict:
    product = await _validate_product_and_variants(db, payload.product_id, payload.variant_prices)
    slug = await _unique_slug(db, store.id, slugify(payload.title))

    campaign = SalesCampaign(
        store_id=store.id,
        organization_id=store.organization_id,
        product_id=payload.product_id,
        title=payload.title,
        slug=slug,
        description=payload.description,
        retail_price=payload.retail_price,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        status=CampaignStatus.DRAFT,
    )
    db.add(campaign)
    await db.flush()
    await _set_campaign_variants(db, campaign, payload.variant_prices)
    await db.refresh(campaign, ["items", "product"])
    for item in campaign.items:
        await db.refresh(item, ["variant"])
    return _campaign_to_response(campaign, product.name)


async def list_campaigns(db: AsyncSession, organization_id: uuid.UUID) -> tuple[list[dict], int]:
    query = (
        select(SalesCampaign)
        .where(SalesCampaign.organization_id == organization_id)
        .options(
            selectinload(SalesCampaign.items).selectinload(CampaignVariant.variant),
            selectinload(SalesCampaign.product),
        )
        .order_by(SalesCampaign.created_at.desc())
    )
    result = await db.execute(query)
    campaigns = result.scalars().all()
    items = [_campaign_to_response(c) for c in campaigns]
    return items, len(items)


async def get_campaign(db: AsyncSession, organization_id: uuid.UUID, campaign_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(SalesCampaign)
        .where(SalesCampaign.id == campaign_id, SalesCampaign.organization_id == organization_id)
        .options(
            selectinload(SalesCampaign.items).selectinload(CampaignVariant.variant),
            selectinload(SalesCampaign.product),
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found")
    return _campaign_to_response(campaign)


async def update_campaign(
    db: AsyncSession, organization_id: uuid.UUID, campaign_id: uuid.UUID, payload: CampaignUpdateRequest
) -> dict:
    result = await db.execute(
        select(SalesCampaign)
        .where(SalesCampaign.id == campaign_id, SalesCampaign.organization_id == organization_id)
        .options(selectinload(SalesCampaign.items), selectinload(SalesCampaign.product))
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found")
    if campaign.status == CampaignStatus.ENDED:
        raise BadRequestError("Cannot edit an ended campaign")

    data = payload.model_dump(exclude_unset=True)
    variant_prices = data.pop("variant_prices", None)
    for field, value in data.items():
        setattr(campaign, field, value)

    if variant_prices is not None:
        await _validate_product_and_variants(db, campaign.product_id, variant_prices)
        await _set_campaign_variants(db, campaign, variant_prices)

    await db.flush()
    await db.refresh(campaign, ["items", "product"])
    for item in campaign.items:
        await db.refresh(item, ["variant"])
    return _campaign_to_response(campaign)


async def publish_campaign(db: AsyncSession, organization_id: uuid.UUID, campaign_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(SalesCampaign)
        .where(SalesCampaign.id == campaign_id, SalesCampaign.organization_id == organization_id)
        .options(
            selectinload(SalesCampaign.items).selectinload(CampaignVariant.variant),
            selectinload(SalesCampaign.product),
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found")
    if not campaign.design_image_url:
        raise BadRequestError("Upload a design before publishing")
    if not campaign.items:
        raise BadRequestError("Campaign must have at least one variant price")

    campaign.status = CampaignStatus.LIVE
    if not campaign.starts_at:
        campaign.starts_at = datetime.now(UTC)
    await db.flush()
    return _campaign_to_response(campaign)


async def end_campaign(db: AsyncSession, organization_id: uuid.UUID, campaign_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(SalesCampaign)
        .where(SalesCampaign.id == campaign_id, SalesCampaign.organization_id == organization_id)
        .options(
            selectinload(SalesCampaign.items).selectinload(CampaignVariant.variant),
            selectinload(SalesCampaign.product),
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found")

    campaign.status = CampaignStatus.ENDED
    campaign.ends_at = datetime.now(UTC)
    await db.flush()
    return _campaign_to_response(campaign)


async def get_public_campaign(db: AsyncSession, slug: str) -> dict:
    result = await db.execute(
        select(SalesCampaign)
        .where(SalesCampaign.slug == slug, SalesCampaign.status == CampaignStatus.LIVE)
        .options(
            selectinload(SalesCampaign.items).selectinload(CampaignVariant.variant),
            selectinload(SalesCampaign.product),
            selectinload(SalesCampaign.store),
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign not found")

    now = datetime.now(UTC)
    if campaign.ends_at and campaign.ends_at < now:
        raise NotFoundError("Campaign has ended")

    store = campaign.store
    variants = [
        {"variant_id": i.variant_id, "variant_name": i.variant.name, "price": i.price} for i in campaign.items
    ]
    return {
        "id": campaign.id,
        "title": campaign.title,
        "slug": campaign.slug,
        "description": campaign.description,
        "design_image_url": campaign.design_image_url,
        "retail_price": campaign.retail_price,
        "status": campaign.status.value,
        "starts_at": campaign.starts_at,
        "ends_at": campaign.ends_at,
        "product_name": campaign.product.name,
        "product_image_url": campaign.product.image_url,
        "variants": variants,
        "store_name": store.name,
        "store_slug": store.slug,
        "store_logo_url": store.logo_url,
        "tips_enabled": store.tips_enabled,
        "tip_options": store.tip_options,
        "facebook_pixel_id": store.facebook_pixel_id,
        "google_analytics_id": store.google_analytics_id,
    }


async def list_live_campaigns_for_store(db: AsyncSession, store_slug: str) -> list[dict]:
    result = await db.execute(select(Store).where(Store.slug == store_slug))
    store = result.scalar_one_or_none()
    if not store:
        raise NotFoundError("Store not found")

    now = datetime.now(UTC)
    query = (
        select(SalesCampaign)
        .where(
            SalesCampaign.store_id == store.id,
            SalesCampaign.status == CampaignStatus.LIVE,
        )
        .options(selectinload(SalesCampaign.product))
        .order_by(SalesCampaign.created_at.desc())
    )
    campaigns = (await db.execute(query)).scalars().all()
    live = []
    for c in campaigns:
        if c.ends_at and c.ends_at < now:
            continue
        live.append(
            {
                "id": c.id,
                "title": c.title,
                "slug": c.slug,
                "description": c.description,
                "design_image_url": c.design_image_url,
                "retail_price": c.retail_price,
                "product_name": c.product.name if c.product else "",
            }
        )
    return live


def validate_design_file(filename: str, content_type: str | None, size: int) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_DESIGN_EXTENSIONS:
        raise BadRequestError(f"Unsupported design format. Allowed: {', '.join(sorted(ALLOWED_DESIGN_EXTENSIONS))}")
    if content_type and not content_type.startswith("image/"):
        raise BadRequestError("Design must be an image file")
    if size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise BadRequestError("Design file too large (max 2MB)")
    return ext


async def save_campaign_design(campaign: SalesCampaign, file_bytes: bytes, extension: str) -> str:
    design_dir = Path(settings.UPLOAD_DIR) / "designs"
    design_dir.mkdir(parents=True, exist_ok=True)

    for existing in design_dir.glob(f"{campaign.id}.*"):
        existing.unlink(missing_ok=True)

    filename = f"{campaign.id}{extension}"
    (design_dir / filename).write_bytes(file_bytes)
    url = f"{settings.BACKEND_URL.rstrip('/')}/uploads/designs/{filename}"
    campaign.design_image_url = url
    return url
