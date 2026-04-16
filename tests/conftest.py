import logging
import sys
from pathlib import Path

from fakeredis import FakeAsyncRedis

sys.path.insert(0, str(Path(__file__).parent.parent))
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.database import Base, get_async_session
from app.models import Item, User
from main import ap

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    url=TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestSession = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine, expire_on_commit=False)

@pytest.fixture
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSession() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(db_session):
    async def override_get_test_session():
        try:
            yield db_session
        finally:
            pass
    ap.dependency_overrides[get_async_session] = override_get_test_session

    async with AsyncClient(transport=ASGITransport(app=ap), base_url="http://test") as test_client:
        yield test_client
    
    ap.dependency_overrides.clear()

@pytest.fixture(autouse=True)
async def mock_redis():
    fake = FakeAsyncRedis(decode_responses=True)
    with patch("app.core.redis_client.redis_client", fake):
        with patch("app.api.endpoints.posts.redis_client", fake):
            yield fake

@pytest.fixture(autouse=True)
def supress_logs():
    logging.disable(logging.WARNING)
    yield
    logging.disable(logging.NOTSET)

@pytest.fixture
async def test_user(db_session: AsyncSession):
    user = User(
        username= "bazuka",
        email="bazuka@example.com",
        hashed_password=hash_password("123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def user_token(client: AsyncClient, test_user: User):
    response = await client.post(
        "/auth/login",
        data={"username": test_user.username, "password": "123"},
    )
    a_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers

@pytest.fixture
async def test_item(db_session: AsyncSession, test_user: User):
    item = Item(
        name="apple",
        description="fruit",
        price=10,
        tax=2.5,
        owner_id=test_user.id
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item