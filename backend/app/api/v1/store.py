import uuid

from fastapi import APIRouter, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import DB, CurrentUser
from app.models.organization import Organization
from app.schemas.store import (
    DomainVerificationResponse,
    PublicStoreResponse,
    SetDomainRequest,
    StoreResponse,
    StoreUpdateRequest,
)
from app.services import store_service

router = APIRouter()


async def _get_org_store(db: AsyncSession, organization_id: uuid.UUID):
    org = await db.get(Organization, organization_id)
    if org is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Organization not found")
    return await store_service.get_or_create_store(db, org)


@router.get("", response_model=StoreResponse)
async def get_store(current_user: CurrentUser, db: DB):
    store = await _get_org_store(db, current_user.organization_id)
    return store


@router.patch("", response_model=StoreResponse)
async def update_store(payload: StoreUpdateRequest, current_user: CurrentUser, db: DB):
    store = await _get_org_store(db, current_user.organization_id)
    store = await store_service.update_store(db, store, payload)
    return store


@router.post("/logo", response_model=StoreResponse)
async def upload_logo(current_user: CurrentUser, db: DB, file: UploadFile = File(...)):
    store = await _get_org_store(db, current_user.organization_id)

    content = await file.read()
    extension = store_service.validate_logo_file(file.filename or "logo.png", file.content_type, len(content))
    await store_service.save_store_logo(store, content, extension)
    await db.flush()
    return store


@router.post("/domain", response_model=DomainVerificationResponse)
async def set_custom_domain(payload: SetDomainRequest, current_user: CurrentUser, db: DB):
    store = await _get_org_store(db, current_user.organization_id)
    store = await store_service.set_custom_domain(db, store, payload.custom_domain)
    return DomainVerificationResponse(**store_service.get_domain_verification_instructions(store))


@router.get("/domain/verification", response_model=DomainVerificationResponse)
async def get_domain_verification(current_user: CurrentUser, db: DB):
    store = await _get_org_store(db, current_user.organization_id)
    return DomainVerificationResponse(**store_service.get_domain_verification_instructions(store))


@router.post("/domain/verify", response_model=DomainVerificationResponse)
async def verify_custom_domain(current_user: CurrentUser, db: DB):
    store = await _get_org_store(db, current_user.organization_id)
    store = await store_service.verify_custom_domain(db, store)
    return DomainVerificationResponse(**store_service.get_domain_verification_instructions(store))


@router.get("/public/{slug}", response_model=PublicStoreResponse)
async def get_public_store(slug: str, db: DB):
    store = await store_service.get_public_store_by_slug(db, slug)
    return store
