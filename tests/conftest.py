import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:p4ssword@localhost:5432/fastapi_batches_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """
    Create event loop for async tests
    """
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """
    Setup test database
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database) -> AsyncSession:
    """
    Create database session for tests
    """
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """
    Create test client with database session override
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """
    Create test user
    """
    from app.crud.crud_user import user as crud_user
    from app.schemas.user import UserCreate

    user_in = UserCreate(
        email="test@example.com",
        password="testpassword",
        full_name="Test User",
        is_superuser=False,
    )

    user_obj = await crud_user.create(db_session, obj_in=user_in)
    await db_session.commit()
    return user_obj


@pytest.fixture
async def test_superuser(db_session: AsyncSession):
    """
    Create test superuser
    """
    from app.crud.crud_user import user as crud_user
    from app.schemas.user import UserCreate

    user_in = UserCreate(
        email="admin@example.com",
        password="adminpassword",
        full_name="Admin User",
        is_superuser=True,
    )

    user_obj = await crud_user.create(db_session, obj_in=user_in)
    await db_session.commit()
    return user_obj


@pytest.fixture
async def user_token_headers(client: AsyncClient, test_user) -> dict[str, str]:
    """
    Get authentication headers for test user
    """
    login_data = {
        "username": test_user.email,
        "password": "testpassword",
    }

    response = await client.post(f"{settings.API_V1_STR}/login", data=login_data)
    tokens = response.json()
    auth_token = tokens["access_token"]

    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def superuser_token_headers(client: AsyncClient, test_superuser) -> dict[str, str]:
    """
    Get authentication headers for test superuser
    """
    login_data = {
        "username": test_superuser.email,
        "password": "adminpassword",
    }

    response = await client.post(f"{settings.API_V1_STR}/login", data=login_data)
    tokens = response.json()
    auth_token = tokens["access_token"]

    return {"Authorization": f"Bearer {auth_token}"}
