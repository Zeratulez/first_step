from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.api.dependencies import hash_password
from app.models import User
from tests.utils.utils import random_lower_string

def create_random_user(db_session: Session):
    user = User(
        username=random_lower_string(),
        email=f"{random_lower_string()}@{random_lower_string()}.com",
        hashed_password=hash_password("123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def random_user_token(db_session: Session, client: TestClient):
    user = create_random_user(db_session)
    response = client.post(
        "/auth/login",
        data={"username": user.username, "password": "123"},
    )
    a_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers