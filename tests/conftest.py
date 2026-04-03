import sys
import fakeredis
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import pytest
from collections.abc import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from main import ap
from app.models import User, Item
from app.database import Base, get_session
from app.api.dependencies import hash_password

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    url=TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(test_engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(test_engine)

@pytest.fixture
def client(db_session):
    def override_get_test_session():
        try:
            yield db_session
        finally:
            pass
    ap.dependency_overrides[get_session] = override_get_test_session

    with TestClient(ap) as test_client:
        yield test_client
    
    ap.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_redis():
    fake = fakeredis.FakeRedis(decode_responses=True)
    with patch("app.core.redis_client.redis_client", fake):
        with patch("app.api.endpoints.posts.redis_client", fake):
            yield fake

@pytest.fixture
def test_user(db_session):
    user = User(
        username= "bazuka",
        email="bazuka@example.com",
        hashed_password=hash_password("123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def user_token(client, test_user):
    response = client.post(
        "/auth/login",
        data={"username": test_user.username, "password": "123"},
    )
    a_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers

@pytest.fixture
def test_item(db_session, test_user):
    item = Item(
        name="apple",
        description="fruit",
        price=10,
        tax=2.5,
        owner_id=test_user.id
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item