import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.core.security import get_password_hash
from app.database import Base, get_db
from app.main import app
from app.models import User, Book


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/bookstore"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session( engine ) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client( db_session: AsyncSession ) -> AsyncGenerator[AsyncClient, None]:
    """Create test client"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user( db_session: AsyncSession ) -> User:
    """Create test user"""
    user = User(
        email="test@example.com", username="testuser", full_name="Test User",
        hashed_password=get_password_hash("testpass123"), is_active=True, is_superuser=False, )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin( db_session: AsyncSession ) -> User:
    """Create test admin user"""
    user = User(
        email="admin@example.com", username="adminuser", full_name="Admin User",
        hashed_password=get_password_hash("adminpass123"), is_active=True, is_superuser=True, )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_book( db_session: AsyncSession ) -> Book:
    """Create test book"""
    book = Book(
        title="Test Book", description="A test book description", price=29.99, image_url="https://example.com/book.jpg",
        stock_quantity=10, )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)
    return book


@pytest.fixture
async def auth_headers_user( client: AsyncClient, test_user: User ) -> dict:
    """Get auth headers for test user"""
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login", json={"username":"testuser", "password":"testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization":f"Bearer {token}"}


@pytest.fixture
async def auth_headers_admin( client: AsyncClient, test_admin: User ) -> dict:
    """Get auth headers for test admin"""
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login", json={"username":"adminuser", "password":"adminpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization":f"Bearer {token}"}