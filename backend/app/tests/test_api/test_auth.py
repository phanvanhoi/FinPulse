import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    response = await client.post("/api/v1/auth/signup", json={
        "email": "test@example.com",
        "password": "securepassword123",
        "name": "Test User",
        "organization_name": "Test Org",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    # First signup
    await client.post("/api/v1/auth/signup", json={
        "email": "dup@example.com",
        "password": "pass123",
        "name": "User 1",
        "organization_name": "Org 1",
    })
    # Duplicate
    response = await client.post("/api/v1/auth/signup", json={
        "email": "dup@example.com",
        "password": "pass456",
        "name": "User 2",
        "organization_name": "Org 2",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    # Signup first
    await client.post("/api/v1/auth/signup", json={
        "email": "login@example.com",
        "password": "mypassword",
        "name": "Login User",
        "organization_name": "Login Org",
    })
    # Login
    response = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "mypassword",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/signup", json={
        "email": "wrong@example.com",
        "password": "correct",
        "name": "Wrong User",
        "organization_name": "Wrong Org",
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "incorrect",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    # Signup
    signup_resp = await client.post("/api/v1/auth/signup", json={
        "email": "me@example.com",
        "password": "pass123",
        "name": "Me User",
        "organization_name": "Me Org",
    })
    token = signup_resp.json()["access_token"]

    # Get me
    response = await client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}",
    })
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
