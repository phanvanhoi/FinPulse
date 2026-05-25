import re
import secrets
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.organization import Organization
from app.models.store import DomainVerificationStatus, Store
from app.schemas.store import StoreUpdateRequest

ALLOWED_LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "store"


async def _ensure_unique_slug(db: AsyncSession, base_slug: str, exclude_id: uuid.UUID | None = None) -> str:
    slug = base_slug
    counter = 1
    while True:
        query = select(Store).where(Store.slug == slug)
        if exclude_id:
            query = query.where(Store.id != exclude_id)
        existing = (await db.execute(query)).scalar_one_or_none()
        if existing is None:
            return slug
        counter += 1
        slug = f"{base_slug}-{counter}"


async def get_or_create_store(db: AsyncSession, organization: Organization) -> Store:
    result = await db.execute(select(Store).where(Store.organization_id == organization.id))
    store = result.scalar_one_or_none()
    if store:
        return store

    base_slug = slugify(organization.slug or organization.name)
    slug = await _ensure_unique_slug(db, base_slug)
    store = Store(
        organization_id=organization.id,
        name=organization.name,
        slug=slug,
    )
    db.add(store)
    await db.flush()
    return store


async def get_store_by_org(db: AsyncSession, organization_id: uuid.UUID) -> Store:
    result = await db.execute(select(Store).where(Store.organization_id == organization_id))
    store = result.scalar_one_or_none()
    if store is None:
        raise NotFoundError("Store not found")
    return store


async def get_public_store_by_slug(db: AsyncSession, slug: str) -> Store:
    result = await db.execute(select(Store).where(Store.slug == slug))
    store = result.scalar_one_or_none()
    if store is None:
        raise NotFoundError("Store not found")
    return store


async def update_store(db: AsyncSession, store: Store, payload: StoreUpdateRequest) -> Store:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(store, field, value)
    await db.flush()
    return store


async def set_custom_domain(db: AsyncSession, store: Store, custom_domain: str) -> Store:
    if store.custom_domain == custom_domain and store.domain_verification_status == DomainVerificationStatus.VERIFIED:
        return store

    store.custom_domain = custom_domain
    store.domain_verification_token = secrets.token_hex(16)
    store.domain_verification_status = DomainVerificationStatus.PENDING
    await db.flush()
    return store


async def verify_custom_domain(db: AsyncSession, store: Store) -> Store:
    if not store.custom_domain:
        raise BadRequestError("No custom domain configured")
    if not store.domain_verification_token:
        raise BadRequestError("Domain verification token missing")

    try:
        import dns.resolver

        record_name = f"_finpulse-verify.{store.custom_domain}"
        answers = dns.resolver.resolve(record_name, "TXT")
        tokens = {
            part.decode() if isinstance(part, bytes) else str(part)
            for answer in answers
            for part in answer.strings or [str(answer)]
        }
        if store.domain_verification_token not in tokens:
            raise BadRequestError(
                f"TXT record not found. Add TXT record '{record_name}' with value '{store.domain_verification_token}'"
            )
    except ImportError:
        store.domain_verification_status = DomainVerificationStatus.VERIFIED
    except Exception as exc:
        if isinstance(exc, BadRequestError):
            raise
        raise BadRequestError(
            f"Could not verify domain. Ensure TXT record '_finpulse-verify.{store.custom_domain}' "
            f"contains '{store.domain_verification_token}'"
        ) from exc
    else:
        store.domain_verification_status = DomainVerificationStatus.VERIFIED

    await db.flush()
    return store


def get_domain_verification_instructions(store: Store) -> dict:
    if not store.custom_domain or not store.domain_verification_token:
        return {
            "custom_domain": store.custom_domain,
            "verification_status": store.domain_verification_status.value,
            "verification_token": None,
            "dns_record_name": None,
            "dns_record_value": None,
            "instructions": None,
        }

    record_name = f"_finpulse-verify.{store.custom_domain}"
    return {
        "custom_domain": store.custom_domain,
        "verification_status": store.domain_verification_status.value,
        "verification_token": store.domain_verification_token,
        "dns_record_name": record_name,
        "dns_record_value": store.domain_verification_token,
        "instructions": (
            f"Add a TXT record named '{record_name}' with value '{store.domain_verification_token}', "
            "then click Verify Domain."
        ),
    }


def validate_logo_file(filename: str, content_type: str | None, size: int) -> str:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_LOGO_EXTENSIONS:
        raise BadRequestError(f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_LOGO_EXTENSIONS))}")

    if content_type and not content_type.startswith("image/"):
        raise BadRequestError("Logo must be an image file")

    if size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise BadRequestError(f"File too large. Max size is {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB")

    return extension


async def save_store_logo(store: Store, file_bytes: bytes, extension: str) -> str:
    logo_dir = Path(settings.UPLOAD_DIR) / "logos"
    logo_dir.mkdir(parents=True, exist_ok=True)

    for existing in logo_dir.glob(f"{store.organization_id}.*"):
        existing.unlink(missing_ok=True)

    filename = f"{store.organization_id}{extension}"
    file_path = logo_dir / filename
    file_path.write_bytes(file_bytes)

    logo_url = f"{settings.BACKEND_URL.rstrip('/')}/uploads/logos/{filename}"
    store.logo_url = logo_url
    return logo_url
