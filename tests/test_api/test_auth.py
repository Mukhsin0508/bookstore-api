import pytest
from httpx import AsyncClient

from ..config_test import test_settings as settings


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "newpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    """Test registration with duplicate email"""
    response = await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": test_user.email,
            "username": "anotheruser",
            "full_name": "Another User",
            "password": "pass123"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user):
    """Test registration with duplicate username"""
    response = await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "another@example.com",
            "username": test_user.username,
            "full_name": "Another User",
            "password": "pass123"
        }
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user):
    """Test user login"""
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Test login with wrong password"""
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={
            "username": test_user.username,
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with a nonexistent user"""
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={
            "username": "nonexistent",
            "password": "somepass"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]