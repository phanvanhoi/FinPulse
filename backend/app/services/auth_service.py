"""Auth service — seller account creation (admin/script only)."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.models.organization import Organization
from app.models.user import User
from app.services import store_service


async def _ensure_unique_org_slug(db: AsyncSession, base: str) -> str:
    slug = base
    if (await db.execute(select(Organization).where(Organization.slug == slug))).scalar_one_or_none():
        slug = f"{base}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    return slug


async def create_seller_account(
    db: AsyncSession,
    *,
    email: str,
    password: str,
    name: str,
    organization_name: str,
    create_store: bool = True,
) -> tuple[User, Organization]:
    """
    Create organization + seller user. Optionally create storefront.
    Used by admin scripts — public signup is disabled.
    """
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")

    base_slug = organization_name.lower().replace(" ", "-")
    slug = await _ensure_unique_org_slug(db, base_slug)

    org = Organization(name=organization_name, slug=slug)
    db.add(org)
    await db.flush()

    user = User(
        organization_id=org.id,
        email=email,
        password_hash=hash_password(password),
        name=name,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    if create_store:
        await store_service.get_or_create_store(db, org)

    return user, org
