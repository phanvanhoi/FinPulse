import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.services.auth_service import create_seller_account
from app.tests.helpers import TEST_PASSWORD, create_seller_in_db


@pytest.mark.asyncio
async def test_create_seller_account(db_session: AsyncSession):
    email = f"new-{uuid.uuid4().hex[:8]}@example.com"
    user, org = await create_seller_account(
        db_session,
        email=email,
        password=TEST_PASSWORD,
        name="Test User",
        organization_name="Test Org",
    )
    assert user.email == email
    assert org.name == "Test Org"


@pytest.mark.asyncio
async def test_create_seller_duplicate_email(db_session: AsyncSession):
    email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
    await create_seller_account(
        db_session,
        email=email,
        password=TEST_PASSWORD,
        name="User 1",
        organization_name="Org 1",
    )
    with pytest.raises(ConflictError):
        await create_seller_account(
            db_session,
            email=email,
            password="otherpass123",
            name="User 2",
            organization_name="Org 2",
        )


@pytest.mark.asyncio
async def test_login(client: AsyncClient, db_session: AsyncSession):
    email, password, _ = await create_seller_in_db(db_session, email=f"login-{uuid.uuid4().hex[:8]}@example.com")
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db_session: AsyncSession):
    email, _, _ = await create_seller_in_db(db_session, email=f"wrong-{uuid.uuid4().hex[:8]}@example.com")
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "incorrect"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, db_session: AsyncSession):
    email, password, _ = await create_seller_in_db(db_session, email=f"me-{uuid.uuid4().hex[:8]}@example.com")
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]

    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == email


@pytest.mark.asyncio
async def test_signup_endpoint_removed(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "blocked@example.com",
            "password": TEST_PASSWORD,
            "name": "Blocked",
            "organization_name": "Blocked Org",
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
