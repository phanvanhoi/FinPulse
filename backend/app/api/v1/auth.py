from datetime import UTC, datetime

from fastapi import APIRouter
from jose import JWTError
from sqlalchemy import select

from app.core.exceptions import BadRequestError, ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.dependencies import DB, CurrentUser
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter()


@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest, db: DB):
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")

    # Create organization
    slug = request.organization_name.lower().replace(" ", "-")
    # Ensure unique slug
    result = await db.execute(select(Organization).where(Organization.slug == slug))
    if result.scalar_one_or_none():
        slug = f"{slug}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"

    org = Organization(name=request.organization_name, slug=slug)
    db.add(org)
    await db.flush()

    # Create user
    user = User(
        organization_id=org.id,
        email=request.email,
        password_hash=hash_password(request.password),
        name=request.name,
        last_login_at=datetime.now(UTC),
    )
    db.add(user)
    await db.flush()

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: DB):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash or not verify_password(request.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedError("Account is deactivated")

    user.last_login_at = datetime.now(UTC)

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: DB):
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise BadRequestError("Invalid token type")
        user_id = payload.get("sub")
    except JWTError:
        raise UnauthorizedError("Invalid or expired refresh token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    return current_user
