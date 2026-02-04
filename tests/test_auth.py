import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """
    Test successful login
    """
    login_data = {
        "username": test_user.email,
        "password": "testpassword",
    }

    response = await client.post(f"{settings.API_V1_STR}/login", data=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """
    Test login with wrong password
    """
    login_data = {
        "username": test_user.email,
        "password": "wrongpassword",
    }

    response = await client.post(f"{settings.API_V1_STR}/login", data=login_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """
    Test login with nonexistent user
    """
    login_data = {
        "username": "nonexistent@example.com",
        "password": "somepassword",
    }

    response = await client.post(f"{settings.API_V1_STR}/login", data=login_data)
    assert response.status_code == 400
